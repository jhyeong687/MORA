// Torque-driven simulation. Parameters and PD gains come from R4/engine.py.
#include <algorithm>
#include <array>
#include <cmath>
#include <deque>
#include <mutex>
#include <string>
#include <gz/common/Console.hh>
#include <gz/plugin/Register.hh>
#include <gz/sim/System.hh>
#include <gz/sim/Model.hh>
#include <gz/sim/components/JointPosition.hh>
#include <gz/sim/components/JointVelocity.hh>
#include <gz/sim/components/JointForceCmd.hh>
#include <gz/transport/Node.hh>
#include <gz/msgs/twist.pb.h>
#include <gz/msgs/double.pb.h>
#include <gz/msgs/odometry.pb.h>
#include <gz/msgs/pose_v.pb.h>
#include <gz/msgs/model.pb.h>

namespace r4 {
class MotorSystem : public gz::sim::System,
                    public gz::sim::ISystemConfigure,
                    public gz::sim::ISystemPreUpdate,
                    public gz::sim::ISystemPostUpdate {
  std::array<std::string,8> names{"axle_left", "axle_right", "shoulder_pan",
    "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"};
  std::array<gz::sim::Entity,8> joints{};
  std::array<double,8> targets{}, torque{}, lower{}, upper{};
  std::array<double,8> stalls{}, speeds{}, caps{}, deadbands{}, coulomb{};
  struct Command {double due; int index; double a,b;};
  std::deque<Command> pending;
  std::array<double,6> kp{15,24,22,14,9,8}, kd{.20,.34,.27,.18,.11,.08};
  gz::transport::Node node;
  gz::transport::Node::Publisher odomPub, tfPub, statePub;
  std::mutex mutex;
  double now=0, lastCommand=-100, requestedV=0, requestedW=0, v=0, w=0;
  double x=0,y=0,yaw=0,lastL=0,lastR=0,lastPub=0;
  bool initialized=false, ready=false, rated=false;
  double armVoltage=12, radius=.033, separation=.16;
  // Effective encoder geometry may be identified independently of command
  // kinematics. Never change the physical wheel dimensions to fit odometry.
  double odomRadius=.033, odomSeparation=.16;
  double latency=.04,encoderStep=2*M_PI/4096;

  static void Stamp(gz::msgs::Header *h, double t) {
    auto ns=static_cast<int64_t>(std::llround(t*1e9));
    h->mutable_stamp()->set_sec(ns/1000000000);
    h->mutable_stamp()->set_nsec(ns%1000000000);
  }
  static void Frame(gz::msgs::Header *h,const std::string &parent,
                    const std::string &child) {
    auto d=h->add_data();d->set_key("frame_id");d->add_value(parent);
    d=h->add_data();d->set_key("child_frame_id");d->add_value(child);
  }
 public:
  void Configure(const gz::sim::Entity &entity,
      const std::shared_ptr<const sdf::Element> &sdf,
      gz::sim::EntityComponentManager &ecm,gz::sim::EventManager &) override {
    gz::sim::Model model(entity);
    armVoltage=sdf->Get<double>("arm_voltage",12).first;
    rated=sdf->Get<bool>("rated_arm_cap",true).first;
    latency=sdf->Get<double>("command_latency",.04).first;
    radius=sdf->Get<double>("wheel_radius",.033).first;
    separation=sdf->Get<double>("wheel_separation",.16).first;
    odomRadius=sdf->Get<double>("odom_wheel_radius",radius).first;
    odomSeparation=sdf->Get<double>("odom_wheel_separation",separation).first;
    if (odomRadius<=0 || odomSeparation<=0) {
      gzerr<<"Invalid encoder odometry geometry\n";return;
    }
    encoderStep=sdf->Get<double>("encoder_step",2*M_PI/4096).first;
    size_t i=0;
    for(const auto &name:names) {
      auto joint=model.JointByName(ecm,name);joints[i++]=joint;
      if(joint==gz::sim::kNullEntity) {gzerr<<"Missing R4 motor joint "<<name<<"\n";return;}
      if(!ecm.Component<gz::sim::components::JointPosition>(joint))
        ecm.CreateComponent(joint,gz::sim::components::JointPosition());
      if(!ecm.Component<gz::sim::components::JointVelocity>(joint))
        ecm.CreateComponent(joint,gz::sim::components::JointVelocity());
      ecm.CreateComponent(joint,gz::sim::components::JointForceCmd({0}));
    }
    auto modelSdf=sdf->GetParent();
    for(i=0;i<8;++i) {
      lower[i]=-1e100;upper[i]=1e100;
      stalls[i]=i<2?1.4:(armVoltage>=11?2.942:1.912);
      speeds[i]=i<2?5.969026:(armVoltage>=11?4.712389:5.445427);
      caps[i]=(i>=2&&rated)?(armVoltage>=11?.981:.4903):stalls[i];
      if(modelSdf && modelSdf->HasElement("joint")) {
        for(auto j=modelSdf->GetElement("joint");j;j=j->GetNextElement("joint")) {
          if(j->Get<std::string>("name")==names[i] && j->HasElement("axis")) {
            auto axis=j->GetElement("axis");
            if(axis->HasElement("limit")) {
              lower[i]=axis->GetElement("limit")->Get<double>("lower",-1e100).first;
              upper[i]=axis->GetElement("limit")->Get<double>("upper",1e100).first;
            }
          }
        }
      }
    }
    auto parameters=sdf->Clone();
    if(parameters->HasElement("motor")) {
      for(auto m=parameters->GetElement("motor");m;m=m->GetNextElement("motor")) {
        auto name=m->Get<std::string>("name");
        for(i=0;i<8;++i)if(name==names[i]) {
          stalls[i]=m->Get<double>("stall_torque",stalls[i]).first;
          speeds[i]=m->Get<double>("no_load_speed",speeds[i]).first;
          caps[i]=m->Get<double>("torque_cap",caps[i]).first;
          deadbands[i]=m->Get<double>("deadband",0).first;
          coulomb[i]=m->Get<double>("coulomb_friction",0).first;
          if(i>=2){kp[i-2]=m->Get<double>("kp",kp[i-2]).first;
            kd[i-2]=m->Get<double>("kd",kd[i-2]).first;}
        }
      }
    }
    node.Subscribe("/cmd_vel", &MotorSystem::OnVelocity,this);
    for(i=2;i<8;++i) {
      std::function<void(const gz::msgs::Double &)> callback=[this,i](const gz::msgs::Double &m) {
        if(!std::isfinite(m.data()))return;
        std::lock_guard<std::mutex> lock(mutex);
        pending.push_back({now+latency,static_cast<int>(i),std::clamp(m.data(),lower[i],upper[i]),0});
      };
      node.Subscribe("/arm/"+names[i],callback);
    }
    odomPub=node.Advertise<gz::msgs::Odometry>("/odom");
    tfPub=node.Advertise<gz::msgs::Pose_V>("/tf");
    statePub=node.Advertise<gz::msgs::Model>("/motor_states");
    ready=true;
    gzmsg<<"R4: eight torque-driven motors, arm "<<armVoltage<<" V, rated cap "<<rated<<"\n";
  }
  void OnVelocity(const gz::msgs::Twist &msg) {
    if(!std::isfinite(msg.linear().x())||!std::isfinite(msg.angular().z()))return;
    std::lock_guard<std::mutex> lock(mutex);
    pending.push_back({now+latency,-1,std::clamp(msg.linear().x(),-.15,.15),
      std::clamp(msg.angular().z(),-.8,.8)});
  }
  void PreUpdate(const gz::sim::UpdateInfo &info,
                 gz::sim::EntityComponentManager &ecm) override {
    if(!ready||info.paused)return;
    double dt=std::chrono::duration<double>(info.dt).count();
    std::lock_guard<std::mutex> lock(mutex);
    now=std::chrono::duration<double>(info.simTime).count();
    if(dt<=0)return;
    while(!pending.empty()&&pending.front().due<=now){auto c=pending.front();pending.pop_front();
      if(c.index<0){requestedV=c.a;requestedW=c.b;lastCommand=now;}
      else targets[c.index]=c.a;}
    // Commands expire in simulation time, including when wall-clock RTF is low.
    auto ramp=[](double a,double b,double step){return a+std::clamp(b-a,-step,step);};
    bool stale=now-lastCommand>.5;
    v=ramp(v,stale?0:requestedV,.15*dt);
    w=ramp(w,stale?0:requestedW,.8*dt);
    targets[0]=(v-separation*.5*w)/radius;
    targets[1]=(v+separation*.5*w)/radius;
    // Preserve curvature while limiting both wheel speeds to 57 rpm.
    double scale=std::max({1.,std::abs(targets[0])/speeds[0],std::abs(targets[1])/speeds[1]});
    targets[0]/=scale;targets[1]/=scale;
    for(size_t i=0;i<8;++i) {
      auto pos=ecm.Component<gz::sim::components::JointPosition>(joints[i]);
      auto vel=ecm.Component<gz::sim::components::JointVelocity>(joints[i]);
      if(!pos||!vel||pos->Data().empty()||vel->Data().empty())continue;
      double q=pos->Data()[0],dq=vel->Data()[0];
      double stall=stalls[i],speed=speeds[i],cap=caps[i];
      double positive=std::min(cap,stall*std::clamp(1-dq/speed,0.,1.));
      double negative=std::min(cap,stall*std::clamp(1+dq/speed,0.,1.));
      double error=targets[i]-(i<2?dq:q);
      if(std::abs(error)<deadbands[i])error=0;
      double command=i<2?.32*error:kp[i-2]*error-kd[i-2]*dq;
      double friction=std::abs(dq)>.0001?std::copysign(coulomb[i],dq):0;
      torque[i]=std::clamp(command,-negative,positive)-friction;
      ecm.Component<gz::sim::components::JointForceCmd>(joints[i])->Data()={torque[i]};
    }
  }
  void PostUpdate(const gz::sim::UpdateInfo &info,
                  const gz::sim::EntityComponentManager &ecm) override {
    if(!ready||info.paused)return;
    double t=std::chrono::duration<double>(info.simTime).count();
    std::array<double,8> q{},dq{};
    for(size_t i=0;i<8;++i) {
      auto p=ecm.Component<gz::sim::components::JointPosition>(joints[i]);
      auto d=ecm.Component<gz::sim::components::JointVelocity>(joints[i]);
      if(!p||!d||p->Data().empty()||d->Data().empty())return;
      q[i]=p->Data()[0];dq[i]=d->Data()[0];
    }
    double encL=std::round(q[0]/encoderStep)*encoderStep;
    double encR=std::round(q[1]/encoderStep)*encoderStep;
    if(!initialized){lastL=encL;lastR=encR;initialized=true;}
    double dl=(encL-lastL)*odomRadius,dr=(encR-lastR)*odomRadius;
    double da=(dr-dl)/odomSeparation,ds=(dr+dl)*.5;
    double distance=std::abs(da)>1e-8?ds*std::sin(da*.5)/(da*.5):ds;
    x+=distance*std::cos(yaw+da*.5);y+=distance*std::sin(yaw+da*.5);yaw+=da;
    lastL=encL;lastR=encR;
    if(t-lastPub<.02-1e-9)return;
    lastPub=t;
    gz::msgs::Odometry odom;Stamp(odom.mutable_header(),t);
    Frame(odom.mutable_header(),"odom","base_footprint");
    auto pose=odom.mutable_pose();pose->mutable_position()->set_x(x);pose->mutable_position()->set_y(y);
    pose->mutable_orientation()->set_z(std::sin(yaw*.5));pose->mutable_orientation()->set_w(std::cos(yaw*.5));
    odom.mutable_twist()->mutable_linear()->set_x((dq[0]+dq[1])*odomRadius*.5);
    odom.mutable_twist()->mutable_angular()->set_z((dq[1]-dq[0])*odomRadius/odomSeparation);
    odomPub.Publish(odom);
    gz::msgs::Pose_V tf;Stamp(tf.mutable_header(),t);
    auto transform=tf.add_pose();*transform=*pose;Stamp(transform->mutable_header(),t);
    Frame(transform->mutable_header(),"odom","base_footprint");tfPub.Publish(tf);
    gz::msgs::Model state;Stamp(state.mutable_header(),t);
    for(size_t i=0;i<8;++i){auto j=state.add_joint();j->set_name(names[i]);
      j->mutable_axis1()->set_position(q[i]);j->mutable_axis1()->set_velocity(dq[i]);
      j->mutable_axis1()->set_force(torque[i]);}
    statePub.Publish(state);
  }
};
}
GZ_ADD_PLUGIN(r4::MotorSystem,gz::sim::System,
  r4::MotorSystem::ISystemConfigure,r4::MotorSystem::ISystemPreUpdate,
  r4::MotorSystem::ISystemPostUpdate)
GZ_ADD_PLUGIN_ALIAS(r4::MotorSystem,"r4::MotorSystem")
