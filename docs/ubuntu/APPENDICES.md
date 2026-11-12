# 부록 A. 현재 설정 원문과 조건 선택

다음은 보고서 생성 시점의 현재 파일이다. 과거 trial의 설정은 해당 trial의 configuration/source snapshot을 우선한다. 특히 최신 calibration YAML의 provenance metadata는 수치 검증 후 보강됐으며 검증 trial의 snapshot과 숫자는 같다.

## slam/experiment.yaml

SHA-256: `bc28dc8ab5b0c79f1a64d4de57b28288dbd6064e9b22d4f3682e1e83389394da`

```text
# All hardware identities are inferred from the imported geometry and official BOM.
# None of these numbers is a measurement of the user's physical robot.
profile: so101_7v4
simulation_odometry_calibrations:
  carry: calibration/carry_simulation.yaml
seed: 42
physics_step: 0.001
base:
  model: TurtleBot3 Burger
  wheel_radius: 0.033
  wheel_separation: 0.160
  tire_friction: 0.70
  encoder_counts: 4096
  command_latency: 0.040  # Assumed; replace from a step response measurement.
  rotor_inertia_proxy: 0.00012  # Isotropic body inertia proxy, not identified rotor inertia.
arm:
  role: follower
  gear_ratio: 345
  rotor_inertia_proxy: 0.00055
  rated_torque_cap: true
  profiles:
    so101_7v4: {voltage: 7.4, stall_torque: 1.912, no_load_rpm: 52.0, torque_cap: 0.4903}
    imported_12v: {voltage: 12.0, stall_torque: 2.942, no_load_rpm: 45.0, torque_cap: 0.981}
  # The standard kit can run on a 5V supply. The 7.4V profile is a datasheet
  # reference, NOT a prediction of 5V performance. No invented 5V rating is used.
motors:
  axle_left: {model: XL430-W250-T, voltage: 11.1, gear_ratio: 258.5, stall_torque: 1.4, no_load_rpm: 57.0, torque_cap: 1.4, deadband: 0.01, coulomb_friction: 0.0}
  axle_right: {model: XL430-W250-T, voltage: 11.1, gear_ratio: 258.5, stall_torque: 1.4, no_load_rpm: 57.0, torque_cap: 1.4, deadband: 0.01, coulomb_friction: 0.0}
  shoulder_pan: {model: STS3215-C001, kp: 15.0, kd: 0.20, deadband: 0.001534, coulomb_friction: 0.0}
  shoulder_lift: {model: STS3215-C001, kp: 24.0, kd: 0.34, deadband: 0.001534, coulomb_friction: 0.0}
  elbow_flex: {model: STS3215-C001, kp: 22.0, kd: 0.27, deadband: 0.001534, coulomb_friction: 0.0}
  wrist_flex: {model: STS3215-C001, kp: 14.0, kd: 0.18, deadband: 0.001534, coulomb_friction: 0.0}
  wrist_roll: {model: STS3215-C001, kp: 9.0, kd: 0.11, deadband: 0.001534, coulomb_friction: 0.0}
  gripper: {model: STS3215-C001, kp: 8.0, kd: 0.08, deadband: 0.001534, coulomb_friction: 0.0}
lidar:
  model: LDS-02
  hz: 5.0
  samples: 360
  min_range: 0.16
  max_range: 8.0
  gaussian_stddev: 0.01 # Baseline only; not a complete LDS-02 error model.
  stress_relative_stddev: 0.03
  stress_dropout_probability: 0.01
  transport_delay: 0.04
spawn: [-1.2, -1.0, 0.0]
slam:
  # Process rotation-only scans too; distance-only gating left the final turn
  # dependent on drifting encoders. This does not feed truth into SLAM.
  check_min_dist_and_heading_precisely: true
  minimum_travel_distance: 0.03
  minimum_travel_heading: 0.02
```

## slam/carry.yaml

SHA-256: `8381fb136d01c2d0bdcef0678ec41defa473bcbef5cb9a34c0d94b53506ca76f`

```text
name: already_held_payload_navigation_v1
payload:
  size: [0.032, 0.032, 0.032]
  mass: 0.010
  center_in_tool: [-0.016, 0.0, -0.012]
  gripper_joint: 0.06
  attachment: fixed_joint_initial_fixture
mapping_side: 1.0
navigation:
  inflation_radius: 0.19
  max_speed: 0.08
  map_arrival_tolerance: 0.03
  evaluation_position_tolerance: 0.10
  evaluation_heading_tolerance_deg: 15
waypoints:
  - {name: pickup_standby, world: [-1.50, -0.12, 1.5707963267948966]}
  - {name: transit, world: [0.0, -0.70, 0.0]}
  - {name: delivery_standby, world: [1.30, -0.70, 1.5707963267948966]}
```

## slam/pick_place.yaml

SHA-256: `03423fb51084998ddc820cc8baac54afe0c4976b2a25f6f99416957baff777ed`

```text
# Reproducible simulated task. Coordinates below define the scene and goals,
# not a runtime simulator-truth feed to navigation or object detection.
name: tabletop_transfer_v1
object:
  name: task_cube
  size: [0.032, 0.032, 0.032]
  mass: 0.010
  xyz: [-1.50, 0.272, 0.276]
  color: [0.95, 0.035, 0.025, 1.0]
tables:
  - {name: pickup_table, center: [-1.50, 0.45], size: [0.50, 0.40], top_height: 0.26}
  - {name: delivery_table, center: [1.30, -0.25], size: [0.50, 0.40], top_height: 0.26}
pickup_base_world: [-1.50, 0.0, 1.5707963267948966]
delivery_base_world: [1.30, -0.67, 1.5707963267948966]
delivery_object_world: [1.30, -0.40, 0.276]
mapping_side: 1.0
navigation:
  speed: 0.08
  inflation_radius: 0.19
  waypoint_tolerance: 0.035
  # A low 2D lidar sees legs rather than the tabletop. These surveyed furniture
  # footprints are explicit keep-out priors, not observations invented by SLAM.
  use_configured_table_keepouts: true
grasp:
  mode: physical_finger_friction
  # Leave 7 mm clearance from the fixed finger during insertion. Closure
  # moves the cube into the fixed pad instead of striking its front edge.
  cube_center_in_tool: [-0.023, 0.0, -0.012]
  open_joint: 0.40
  close_joint: -0.20
  closing_speed: 0.08
  hold_compression_rad: 0.04
  lift_distance: 0.09
perception:
  mode: rgb_cube_template_with_scene_prior
  rgb_topic: /wrist_cam/image
  known_cube_size_and_table_height: true
  depth_sensor_required: false
```

## slam/calibration/carry_simulation.yaml

SHA-256: `f1e660181745ddc877c3c69009c10d492defb997ed33b24d53ba553c64956031`

```text
kind: simulation_identification
hardware_calibrated: false
wheel_radius: 0.032999241791190966
wheel_separation: 0.17799008683790468
identified_utc: '2026-11-12T05:25:05.027558+00:00'
source_trial: /workspace/r4_lab/slam/results/research_20261112/odometry_identification_01
scenario: carry
payload_mass_kg: 0.01
tire_friction: 0.7
seed: 42
radius_forward_reverse_m:
- 0.03299931358476568
- 0.0329991698607
separation_ccw_cw_m:
- 0.17799327591438754
- 0.1779868977614218
scope: Effective encoder odometry for this simulation condition; independent waypoint
  validation required.
profile: so101_7v4
nominal_wheel_radius: 0.033
nominal_wheel_separation: 0.16
```

## slam/generated/slam.yaml

SHA-256: `7040ed365e31ecb4dc208544341b411e7c65c0ffe8e6a0d951b5ded964606bf9`

```text
slam_toolbox:
  ros__parameters:
    angle_variance_penalty: 1.0
    base_frame: base_footprint
    ceres_dogleg_type: TRADITIONAL_DOGLEG
    ceres_linear_solver: SPARSE_NORMAL_CHOLESKY
    ceres_loss_function: None
    ceres_preconditioner: SCHUR_JACOBI
    ceres_trust_strategy: LEVENBERG_MARQUARDT
    check_min_dist_and_heading_precisely: true
    coarse_angle_resolution: 0.0349
    coarse_search_angle_offset: 0.349
    correlation_search_space_dimension: 0.5
    correlation_search_space_resolution: 0.01
    correlation_search_space_smear_deviation: 0.1
    debug_logging: false
    distance_variance_penalty: 0.5
    do_loop_closing: true
    enable_interactive_mode: false
    fine_search_angle_offset: 0.00349
    link_match_minimum_response_fine: 0.1
    link_scan_maximum_distance: 1.5
    loop_match_maximum_variance_coarse: 3.0
    loop_match_minimum_chain_size: 5
    loop_match_minimum_response_coarse: 0.35
    loop_match_minimum_response_fine: 0.45
    loop_search_maximum_distance: 3.0
    loop_search_space_dimension: 8.0
    loop_search_space_resolution: 0.05
    loop_search_space_smear_deviation: 0.03
    map_frame: map
    map_update_interval: 1.0
    max_laser_range: 8.0
    min_laser_range: 0.18
    min_pass_through: 2
    minimum_angle_penalty: 0.9
    minimum_distance_penalty: 0.5
    minimum_time_interval: 0.15
    minimum_travel_distance: 0.03
    minimum_travel_heading: 0.02
    mode: mapping
    occupancy_threshold: 0.1
    odom_frame: odom
    resolution: 0.025
    restamp_tf: false
    scan_buffer_maximum_scan_distance: 10.0
    scan_buffer_size: 20
    scan_topic: /scan
    solver_plugin: solver_plugins::CeresSolver
    stack_size_to_use: 40000000
    tf_buffer_duration: 30.0
    throttle_scans: 1
    transform_publish_period: 0.02
    transform_timeout: 0.5
    use_map_saver: true
    use_response_expansion: true
    use_scan_barycenter: true
    use_scan_matching: true
    use_sim_time: true
```

## slam/hardware_interface.yaml

SHA-256: `158fe670f1723b4643d3a426932b27727a0a55fdd6d3ab7eb7f758a3302219cb`

```text
# Target interface contract, NOT a measured hardware calibration or launch file.
use_sim_time: false
base_frame: base_footprint
odometry_frame: odom
topics:
  laser_scan: /scan
  odometry: /odom
  velocity_command: /cmd_vel
cmd_vel_type: detect_from_driver  # Twist or TwistStamped; check_real_base reports it.
tf_required: [odom_to_base, base_to_actual_laser_frame]
initial_trial_limits:
  linear_speed_m_s: 0.05
  angular_speed_rad_s: 0.3
  command_period_s: 0.05
  watchdog_s: 0.3
simulation_truth_available: false
simulation_odometry_calibration_allowed: false
physical_calibration_status: pending_hardware_measurement
```

## slam/env.sh

SHA-256: `6d8c4dda393f332d374e384e1a6a95c9829e682ae8cb14b8bdbadb8729c12a99`

```text
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=46
unset ROS_LOCALHOST_ONLY
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
export GZ_PARTITION=r4_slam
R4_LAB_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export GZ_SIM_RESOURCE_PATH="$R4_LAB_ROOT${GZ_SIM_RESOURCE_PATH:+:$GZ_SIM_RESOURCE_PATH}"
export GZ_SIM_SYSTEM_PLUGIN_PATH="$R4_LAB_ROOT/slam/build${GZ_SIM_SYSTEM_PLUGIN_PATH:+:$GZ_SIM_SYSTEM_PLUGIN_PATH}"
```

## start_slam

SHA-256: `2666b463613659ada9546a16c3ee128e31214ede21c2fab2c4bceb2bde2bfcb2`

```text
#!/usr/bin/env bash
set -eo pipefail
TASK_ROOT="$(cd "$(dirname "$0")" && pwd)"
source "$TASK_ROOT/slam/env.sh"
gui=true
rviz=true
profile=so101_7v4
stress=false
scenario=slam
spawn_args=()
calibration_args=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --headless) gui=false; rviz=false; shift ;;
    --no-rviz) rviz=false; shift ;;
    --profile) profile="$2"; shift 2 ;;
    --stress) stress=true; shift ;;
    --scenario) scenario="$2"; shift 2 ;;
    --spawn) spawn_args=(--spawn "$2" "$3" "$4"); shift 4 ;;
    --odom-calibration) calibration_args=(--odom-calibration "$2"); shift 2 ;;
    *) echo "Usage: $0 [--headless] [--no-rviz] [--profile so101_7v4|imported_12v] [--stress] [--scenario slam|pick_place|carry] [--spawn X Y YAW] [--odom-calibration FILE]"; exit 2 ;;
  esac
done
python3 "$TASK_ROOT/slam/prepare.py" --profile "$profile" --scenario "$scenario" "${spawn_args[@]}" "${calibration_args[@]}"
if [[ "$rviz" == true ]]; then python3 "$TASK_ROOT/slam/prepare_rviz.py"; fi
cmake -S "$TASK_ROOT/slam" -B "$TASK_ROOT/slam/build" > "$TASK_ROOT/slam/build-configure.log"
cmake --build "$TASK_ROOT/slam/build" -j 4
exec ros2 launch "$TASK_ROOT/slam/experiment.launch.py" gui:="$gui" rviz:="$rviz" stress:="$stress"
```

## start_carry

SHA-256: `d823ad3d4cc623f0654e5509531b8ddcfe4900404f13b442afd168747e62516e`

```text
#!/usr/bin/env bash
set -e
TASK_ROOT="$(cd "$(dirname "$0")" && pwd)"
exec "$TASK_ROOT/start_slam" --scenario carry "$@"
```

## test_carry

SHA-256: `e814d271b6832983cd876221d16603861faafa1c8270bc411aba7a8a557ba511`

```text
#!/usr/bin/env bash
set -e
TASK_ROOT="$(cd "$(dirname "$0")" && pwd)"
source "$TASK_ROOT/slam/env.sh"
exec python3 "$TASK_ROOT/slam/run_carry.py" "$@"
```

## check_real_base

SHA-256: `0149a3d554449ed6444d4cc612565d2a46fe3fa9771c4023e599099964a29627`

```text
#!/usr/bin/env bash
# Read-only check. Does not launch simulation, drivers or a motion controller.
set -eo pipefail
TASK_ROOT="$(cd "$(dirname "$0")" && pwd)"
source /opt/ros/jazzy/setup.bash
if [[ -z "${ROS_DOMAIN_ID:-}" ]]; then
  echo 'Set ROS_DOMAIN_ID to the same value as the physical TurtleBot first.' >&2
  exit 2
fi
# Undo the lab's simulation-only localhost setting for this process only.
unset ROS_LOCALHOST_ONLY GZ_PARTITION
if [[ "${ROS_AUTOMATIC_DISCOVERY_RANGE:-}" == LOCALHOST ]]; then
  export ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET
fi
exec python3 "$TASK_ROOT/slam/audit_base.py" "$@"
```

# 부록 B. 소스 코드 탐색 지도

코드 원문은 동봉 snapshot에 포함한다. 아래 line number는 현재 파일 기준이며 과거 stack trace의 행 번호와 다를 수 있다. 다음 Codex는 함수를 실제로 읽고 변경 조건을 확인해야 한다.

## slam/arm_kinematics.py

3,672 bytes · SHA-256 `57d3a364004557e2e9aa6cd79d25b0c5dcb9b9b5d7553340ac50b3687b7d3cf9`

| 행 | 함수 | 인자 |
|---:|---|---|
| 12 | transform | `xyz=(0, 0, 0), rpy=(0, 0, 0)` |
| 18 | __init__ | `self, path=ROOT / 'generated/r4.urdf'` |
| 32 | fk | `self, q` |
| 48 | solve | `self, position, seed=None, tool_axis=None, axis_index=0, tcp_offset=None, tool_x=None` |
| 54 | residual | `q` |


## slam/audit_base.py

8,275 bytes · SHA-256 `84cdca0e0d8cef0c950ef6b6a22043b0e40407965d5510b827bfc7106a601dea`

| 행 | 함수 | 인자 |
|---:|---|---|
| 25 | __init__ | `self, args` |
| 34 | receive | `self, topic, msg` |
| 49 | check_transforms | `self` |
| 62 | request_parameters | `self` |
| 75 | result | `self` |
| 118 | main | `` |


## slam/calibrate_odometry.py

5,336 bytes · SHA-256 `0a998cb33055d9118dc87628ffe8d386287d5ba52b466dde8e81773b641ec749`

| 행 | 함수 | 인자 |
|---:|---|---|
| 21 | __init__ | `self, out` |
| 25 | receive | `self, topic, msg` |
| 35 | perform_calibration | `self` |
| 43 | identify | `self` |
| 80 | main | `` |


## slam/capture_visuals.py

5,036 bytes · SHA-256 `f012c956c144f89178b009bd7973e2a06540b2b9593053f7a5ddbd913ef478fd`

| 행 | 함수 | 인자 |
|---:|---|---|
| 19 | composite_capture | `window` |
| 63 | main | `` |


## slam/experiment.launch.py

4,575 bytes · SHA-256 `ec7066fbc452132241ce13e4507243eff730094f26f8697be0a66c4ddb46ba69`

| 행 | 함수 | 인자 |
|---:|---|---|
| 16 | simulation_exit | `event, context` |
| 21 | generate_launch_description | `` |


## slam/grid_planner.py

2,480 bytes · SHA-256 `818607c512bc4c31b105bbe7464d84341ebee4f9890473a87a710a1d8a065659`

| 행 | 함수 | 인자 |
|---:|---|---|
| 8 | plan_grid | `message, start, goal, table_rectangles=(), radius=0.18` |
| 18 | cell | `p` |
| 21 | point | `c` |
| 23 | valid | `c` |
| 43 | visible | `a, b` |


## slam/plot_calibration_comparison.py

1,991 bytes · SHA-256 `a0dcee356446de512557d654a5741915f41359b0700d6d30446bd08e8f86751f`

| 행 | 함수 | 인자 |
|---:|---|---|


## slam/plot_carry_results.py

3,105 bytes · SHA-256 `e990916941296260e3eeaa7ad86a8c621ab9c4ca5edba89f5e5b15b005858c40`

| 행 | 함수 | 인자 |
|---:|---|---|
| 14 | main | `` |


## slam/plot_results.py

3,933 bytes · SHA-256 `876d620b7454b603e9af25e6a537be290137fed0feb3aad509c5e65c48745995`

| 행 | 함수 | 인자 |
|---:|---|---|
| 16 | main | `` |
| 28 | align | `poses` |


## slam/prepare.py

19,248 bytes · SHA-256 `18d009511b6407a6f732f079cda59571c7c12572349d9d1a552fc5f7d2c67b55`

| 행 | 함수 | 인자 |
|---:|---|---|
| 15 | put | `parent, name, value` |
| 23 | matrix | `text` |
| 34 | origin | `parent, transform` |
| 41 | box | `world, name, xyz, size, color` |
| 54 | add_pick_place | `world, robot` |
| 109 | add_carried_payload | `world, robot` |
| 132 | main | `` |


## slam/prepare_rviz.py

2,680 bytes · SHA-256 `dc671a3be85eeb17cd75881fcc6e4469d47f2235f335206120bb62aea5e71052`

| 행 | 함수 | 인자 |
|---:|---|---|
| 16 | main | `` |


## slam/record_visuals.py

5,856 bytes · SHA-256 `60baec8012d460cdb6f932a4e427dc53ba7c421a4f1b5a5235893d1fa17ae304`

| 행 | 함수 | 인자 |
|---:|---|---|
| 21 | main | `` |
| 43 | stop | `*_` |


## slam/run_carry.py

9,317 bytes · SHA-256 `104677fa903ca4c0b8ecc5742767ce64703a9b1cd458b41cb03bc8ec8ac9aa10`

| 행 | 함수 | 인자 |
|---:|---|---|
| 29 | __init__ | `self, out` |
| 39 | sim | `self` |
| 41 | command | `self, v=0.0, w=0.0` |
| 43 | publish_targets | `self` |
| 48 | wait | `self, seconds` |
| 54 | mark | `self, stage, **extra` |
| 61 | world_to_map | `self, xy` |
| 65 | publish_waypoints | `self` |
| 80 | navigate | `self, waypoint` |
| 122 | perform | `self` |
| 129 | main | `` |


## slam/run_experiment.py

17,269 bytes · SHA-256 `f96d9a8d5fe45c86e20de1134bcf02109e1328d285c2b740b7937b5e0afe6514`

| 행 | 함수 | 인자 |
|---:|---|---|
| 25 | yaw | `q` |
| 29 | wrap | `a` |
| 34 | __init__ | `self, out, capture=False, control_frame='odom'` |
| 64 | receive_map | `self, msg` |
| 67 | receive | `self, topic, msg` |
| 84 | command | `self, v=0.0, w=0.0` |
| 89 | sample | `self` |
| 117 | spin | `self` |
| 124 | capture | `self, label` |
| 134 | check_feedback | `self` |
| 141 | ready | `self` |
| 151 | drive | `self, length` |
| 201 | control_pose | `self` |
| 218 | report | `self, completed, error, driving=False, side=None, emit=True` |
| 287 | main | `` |


## slam/run_pick_place.py

20,260 bytes · SHA-256 `706087047a701809b6e8c1e3aba2af842d06b9784dec9dfa614ccb936c093efd`

| 행 | 함수 | 인자 |
|---:|---|---|
| 33 | __init__ | `self, out` |
| 49 | object_eval | `self, m` |
| 55 | contact | `self, m, finger` |
| 65 | sim | `self` |
| 67 | joints | `self` |
| 71 | publish_targets | `self` |
| 84 | command | `self, v=0.0, w=0.0` |
| 86 | wait | `self, seconds` |
| 92 | mark | `self, stage, **extra` |
| 101 | world_to_map | `self, xy` |
| 105 | scene_target_in_base | `self, world` |
| 111 | navigate | `self, world_goal, label` |
| 138 | hold_base | `self` |
| 141 | move_arm | `self, target, settle=1.0` |
| 155 | move_tcp | `self, point, gripper=None` |
| 173 | close_gripper | `self` |
| 198 | rgb_target | `self, prior` |
| 214 | project | `state` |
| 229 | perform | `self, grasp_only=False` |
| 288 | main | `` |


## slam/scan_pipeline.py

2,972 bytes · SHA-256 `339aa3f6d24d2461bd8fc1381dbcd9449c4e1a76a1b9f887bab722e5c6d321cd`

| 행 | 함수 | 인자 |
|---:|---|---|
| 18 | __init__ | `self` |
| 33 | receive | `self, msg` |
| 49 | flush | `self` |
| 63 | main | `` |


## slam/select_research.py

6,870 bytes · SHA-256 `3489578d04ec80786db1e872769f4fd6534f8612120c9901a7795cdb3a95535a`

| 행 | 함수 | 인자 |
|---:|---|---|
| 18 | excerpt | `source, target, intervals` |
| 65 | main | `` |


## slam/test_arm.py

6,503 bytes · SHA-256 `6fca2d4ea3398fe670703cc059df00db4c971f3a476d550f4fe77b854c06635b`

| 행 | 함수 | 인자 |
|---:|---|---|
| 24 | __init__ | `self, out` |
| 34 | receive | `self, m` |
| 38 | sim | `self` |
| 40 | tick | `self` |
| 62 | run_phase | `self, label, target, ramp=1.5, hold=1.0` |
| 75 | main | `` |


## slam/verify_pick_place.py

2,468 bytes · SHA-256 `e22135bfc77f812fbd8be6a621e8e611bdd8e1fadb5e8364b432711cd8153f6d`

| 행 | 함수 | 인자 |
|---:|---|---|
| 9 | main | `` |


## slam/MotorSystem.cc — 원문

명령 kinematics, encoder geometry, torque cap과 timeout이 들어 있는 핵심 구현이다. 아래는 현재 전체 원문이다.

```cpp
001 // Torque-driven simulation. Parameters and PD gains come from R4/engine.py.
002 #include <algorithm>
003 #include <array>
004 #include <cmath>
005 #include <deque>
006 #include <mutex>
007 #include <string>
008 #include <gz/common/Console.hh>
009 #include <gz/plugin/Register.hh>
010 #include <gz/sim/System.hh>
011 #include <gz/sim/Model.hh>
012 #include <gz/sim/components/JointPosition.hh>
013 #include <gz/sim/components/JointVelocity.hh>
014 #include <gz/sim/components/JointForceCmd.hh>
015 #include <gz/transport/Node.hh>
016 #include <gz/msgs/twist.pb.h>
017 #include <gz/msgs/double.pb.h>
018 #include <gz/msgs/odometry.pb.h>
019 #include <gz/msgs/pose_v.pb.h>
020 #include <gz/msgs/model.pb.h>
021 
022 namespace r4 {
023 class MotorSystem : public gz::sim::System,
024                     public gz::sim::ISystemConfigure,
025                     public gz::sim::ISystemPreUpdate,
026                     public gz::sim::ISystemPostUpdate {
027   std::array<std::string,8> names{"axle_left", "axle_right", "shoulder_pan",
028     "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"};
029   std::array<gz::sim::Entity,8> joints{};
030   std::array<double,8> targets{}, torque{}, lower{}, upper{};
031   std::array<double,8> stalls{}, speeds{}, caps{}, deadbands{}, coulomb{};
032   struct Command {double due; int index; double a,b;};
033   std::deque<Command> pending;
034   std::array<double,6> kp{15,24,22,14,9,8}, kd{.20,.34,.27,.18,.11,.08};
035   gz::transport::Node node;
036   gz::transport::Node::Publisher odomPub, tfPub, statePub;
037   std::mutex mutex;
038   double now=0, lastCommand=-100, requestedV=0, requestedW=0, v=0, w=0;
039   double x=0,y=0,yaw=0,lastL=0,lastR=0,lastPub=0;
040   bool initialized=false, ready=false, rated=false;
041   double armVoltage=12, radius=.033, separation=.16;
042   // Effective encoder geometry may be identified independently of command
043   // kinematics. Never change the physical wheel dimensions to fit odometry.
044   double odomRadius=.033, odomSeparation=.16;
045   double latency=.04,encoderStep=2*M_PI/4096;
046 
047   static void Stamp(gz::msgs::Header *h, double t) {
048     auto ns=static_cast<int64_t>(std::llround(t*1e9));
049     h->mutable_stamp()->set_sec(ns/1000000000);
050     h->mutable_stamp()->set_nsec(ns%1000000000);
051   }
052   static void Frame(gz::msgs::Header *h,const std::string &parent,
053                     const std::string &child) {
054     auto d=h->add_data();d->set_key("frame_id");d->add_value(parent);
055     d=h->add_data();d->set_key("child_frame_id");d->add_value(child);
056   }
057  public:
058   void Configure(const gz::sim::Entity &entity,
059       const std::shared_ptr<const sdf::Element> &sdf,
060       gz::sim::EntityComponentManager &ecm,gz::sim::EventManager &) override {
061     gz::sim::Model model(entity);
062     armVoltage=sdf->Get<double>("arm_voltage",12).first;
063     rated=sdf->Get<bool>("rated_arm_cap",true).first;
064     latency=sdf->Get<double>("command_latency",.04).first;
065     radius=sdf->Get<double>("wheel_radius",.033).first;
066     separation=sdf->Get<double>("wheel_separation",.16).first;
067     odomRadius=sdf->Get<double>("odom_wheel_radius",radius).first;
068     odomSeparation=sdf->Get<double>("odom_wheel_separation",separation).first;
069     if (odomRadius<=0 || odomSeparation<=0) {
070       gzerr<<"Invalid encoder odometry geometry\n";return;
071     }
072     encoderStep=sdf->Get<double>("encoder_step",2*M_PI/4096).first;
073     size_t i=0;
074     for(const auto &name:names) {
075       auto joint=model.JointByName(ecm,name);joints[i++]=joint;
076       if(joint==gz::sim::kNullEntity) {gzerr<<"Missing R4 motor joint "<<name<<"\n";return;}
077       if(!ecm.Component<gz::sim::components::JointPosition>(joint))
078         ecm.CreateComponent(joint,gz::sim::components::JointPosition());
079       if(!ecm.Component<gz::sim::components::JointVelocity>(joint))
080         ecm.CreateComponent(joint,gz::sim::components::JointVelocity());
081       ecm.CreateComponent(joint,gz::sim::components::JointForceCmd({0}));
082     }
083     auto modelSdf=sdf->GetParent();
084     for(i=0;i<8;++i) {
085       lower[i]=-1e100;upper[i]=1e100;
086       stalls[i]=i<2?1.4:(armVoltage>=11?2.942:1.912);
087       speeds[i]=i<2?5.969026:(armVoltage>=11?4.712389:5.445427);
088       caps[i]=(i>=2&&rated)?(armVoltage>=11?.981:.4903):stalls[i];
089       if(modelSdf && modelSdf->HasElement("joint")) {
090         for(auto j=modelSdf->GetElement("joint");j;j=j->GetNextElement("joint")) {
091           if(j->Get<std::string>("name")==names[i] && j->HasElement("axis")) {
092             auto axis=j->GetElement("axis");
093             if(axis->HasElement("limit")) {
094               lower[i]=axis->GetElement("limit")->Get<double>("lower",-1e100).first;
095               upper[i]=axis->GetElement("limit")->Get<double>("upper",1e100).first;
096             }
097           }
098         }
099       }
100     }
101     auto parameters=sdf->Clone();
102     if(parameters->HasElement("motor")) {
103       for(auto m=parameters->GetElement("motor");m;m=m->GetNextElement("motor")) {
104         auto name=m->Get<std::string>("name");
105         for(i=0;i<8;++i)if(name==names[i]) {
106           stalls[i]=m->Get<double>("stall_torque",stalls[i]).first;
107           speeds[i]=m->Get<double>("no_load_speed",speeds[i]).first;
108           caps[i]=m->Get<double>("torque_cap",caps[i]).first;
109           deadbands[i]=m->Get<double>("deadband",0).first;
110           coulomb[i]=m->Get<double>("coulomb_friction",0).first;
111           if(i>=2){kp[i-2]=m->Get<double>("kp",kp[i-2]).first;
112             kd[i-2]=m->Get<double>("kd",kd[i-2]).first;}
113         }
114       }
115     }
116     node.Subscribe("/cmd_vel", &MotorSystem::OnVelocity,this);
117     for(i=2;i<8;++i) {
118       std::function<void(const gz::msgs::Double &)> callback=[this,i](const gz::msgs::Double &m) {
119         if(!std::isfinite(m.data()))return;
120         std::lock_guard<std::mutex> lock(mutex);
121         pending.push_back({now+latency,static_cast<int>(i),std::clamp(m.data(),lower[i],upper[i]),0});
122       };
123       node.Subscribe("/arm/"+names[i],callback);
124     }
125     odomPub=node.Advertise<gz::msgs::Odometry>("/odom");
126     tfPub=node.Advertise<gz::msgs::Pose_V>("/tf");
127     statePub=node.Advertise<gz::msgs::Model>("/motor_states");
128     ready=true;
129     gzmsg<<"R4: eight torque-driven motors, arm "<<armVoltage<<" V, rated cap "<<rated<<"\n";
130   }
131   void OnVelocity(const gz::msgs::Twist &msg) {
132     if(!std::isfinite(msg.linear().x())||!std::isfinite(msg.angular().z()))return;
133     std::lock_guard<std::mutex> lock(mutex);
134     pending.push_back({now+latency,-1,std::clamp(msg.linear().x(),-.15,.15),
135       std::clamp(msg.angular().z(),-.8,.8)});
136   }
137   void PreUpdate(const gz::sim::UpdateInfo &info,
138                  gz::sim::EntityComponentManager &ecm) override {
139     if(!ready||info.paused)return;
140     double dt=std::chrono::duration<double>(info.dt).count();
141     std::lock_guard<std::mutex> lock(mutex);
142     now=std::chrono::duration<double>(info.simTime).count();
143     if(dt<=0)return;
144     while(!pending.empty()&&pending.front().due<=now){auto c=pending.front();pending.pop_front();
145       if(c.index<0){requestedV=c.a;requestedW=c.b;lastCommand=now;}
146       else targets[c.index]=c.a;}
147     // Commands expire in simulation time, including when wall-clock RTF is low.
148     auto ramp=[](double a,double b,double step){return a+std::clamp(b-a,-step,step);};
149     bool stale=now-lastCommand>.5;
150     v=ramp(v,stale?0:requestedV,.15*dt);
151     w=ramp(w,stale?0:requestedW,.8*dt);
152     targets[0]=(v-separation*.5*w)/radius;
153     targets[1]=(v+separation*.5*w)/radius;
154     // Preserve curvature while limiting both wheel speeds to 57 rpm.
155     double scale=std::max({1.,std::abs(targets[0])/speeds[0],std::abs(targets[1])/speeds[1]});
156     targets[0]/=scale;targets[1]/=scale;
157     for(size_t i=0;i<8;++i) {
158       auto pos=ecm.Component<gz::sim::components::JointPosition>(joints[i]);
159       auto vel=ecm.Component<gz::sim::components::JointVelocity>(joints[i]);
160       if(!pos||!vel||pos->Data().empty()||vel->Data().empty())continue;
161       double q=pos->Data()[0],dq=vel->Data()[0];
162       double stall=stalls[i],speed=speeds[i],cap=caps[i];
163       double positive=std::min(cap,stall*std::clamp(1-dq/speed,0.,1.));
164       double negative=std::min(cap,stall*std::clamp(1+dq/speed,0.,1.));
165       double error=targets[i]-(i<2?dq:q);
166       if(std::abs(error)<deadbands[i])error=0;
167       double command=i<2?.32*error:kp[i-2]*error-kd[i-2]*dq;
168       double friction=std::abs(dq)>.0001?std::copysign(coulomb[i],dq):0;
169       torque[i]=std::clamp(command,-negative,positive)-friction;
170       ecm.Component<gz::sim::components::JointForceCmd>(joints[i])->Data()={torque[i]};
171     }
172   }
173   void PostUpdate(const gz::sim::UpdateInfo &info,
174                   const gz::sim::EntityComponentManager &ecm) override {
175     if(!ready||info.paused)return;
176     double t=std::chrono::duration<double>(info.simTime).count();
177     std::array<double,8> q{},dq{};
178     for(size_t i=0;i<8;++i) {
179       auto p=ecm.Component<gz::sim::components::JointPosition>(joints[i]);
180       auto d=ecm.Component<gz::sim::components::JointVelocity>(joints[i]);
181       if(!p||!d||p->Data().empty()||d->Data().empty())return;
182       q[i]=p->Data()[0];dq[i]=d->Data()[0];
183     }
184     double encL=std::round(q[0]/encoderStep)*encoderStep;
185     double encR=std::round(q[1]/encoderStep)*encoderStep;
186     if(!initialized){lastL=encL;lastR=encR;initialized=true;}
187     double dl=(encL-lastL)*odomRadius,dr=(encR-lastR)*odomRadius;
188     double da=(dr-dl)/odomSeparation,ds=(dr+dl)*.5;
189     double distance=std::abs(da)>1e-8?ds*std::sin(da*.5)/(da*.5):ds;
190     x+=distance*std::cos(yaw+da*.5);y+=distance*std::sin(yaw+da*.5);yaw+=da;
191     lastL=encL;lastR=encR;
192     if(t-lastPub<.02-1e-9)return;
193     lastPub=t;
194     gz::msgs::Odometry odom;Stamp(odom.mutable_header(),t);
195     Frame(odom.mutable_header(),"odom","base_footprint");
196     auto pose=odom.mutable_pose();pose->mutable_position()->set_x(x);pose->mutable_position()->set_y(y);
197     pose->mutable_orientation()->set_z(std::sin(yaw*.5));pose->mutable_orientation()->set_w(std::cos(yaw*.5));
198     odom.mutable_twist()->mutable_linear()->set_x((dq[0]+dq[1])*odomRadius*.5);
199     odom.mutable_twist()->mutable_angular()->set_z((dq[1]-dq[0])*odomRadius/odomSeparation);
200     odomPub.Publish(odom);
201     gz::msgs::Pose_V tf;Stamp(tf.mutable_header(),t);
202     auto transform=tf.add_pose();*transform=*pose;Stamp(transform->mutable_header(),t);
203     Frame(transform->mutable_header(),"odom","base_footprint");tfPub.Publish(tf);
204     gz::msgs::Model state;Stamp(state.mutable_header(),t);
205     for(size_t i=0;i<8;++i){auto j=state.add_joint();j->set_name(names[i]);
206       j->mutable_axis1()->set_position(q[i]);j->mutable_axis1()->set_velocity(dq[i]);
207       j->mutable_axis1()->set_force(torque[i]);}
208     statePub.Publish(state);
209   }
210 };
211 }
212 GZ_ADD_PLUGIN(r4::MotorSystem,gz::sim::System,
213   r4::MotorSystem::ISystemConfigure,r4::MotorSystem::ISystemPreUpdate,
214   r4::MotorSystem::ISystemPostUpdate)
215 GZ_ADD_PLUGIN_ALIAS(r4::MotorSystem,"r4::MotorSystem")
```

# 부록 C. 실험별 최종 상태와 원본 위치

기계 판독용 전체 metrics/events/perception과 object 요약은 metadata/experiment_registry.json에 들어 있다. 아래는 원본에서 직접 뽑은 판정 요약이다. 누락된 필드는 시험 종류에 따라 정의되지 않은 것이다.

## arm_joint_smoke

경로: `slam/results/research_20261112/arm_joint_smoke`


| 필드 | 원본 값 |
|---|---|
| completed | False |
| small_motion_pass | False |
| error | Missing simulation joint states or clock |


## arm_joint_smoke_retry

경로: `slam/results/research_20261112/arm_joint_smoke_retry`


| 필드 | 원본 값 |
|---|---|
| completed | True |
| small_motion_pass | True |
| error | None |


## baseline_12m_fresh

경로: `slam/results/research_20261112/baseline_12m_fresh`


| 필드 | 원본 값 |
|---|---|
| completed | True |
| test_kind | square_loop |
| acceptance_version | 2 |
| baseline_pass | False |
| hardware_calibrated | False |
| scan_messages | 319 |
| trajectory_samples | 616 |
| slam_ate_rmse_m | 0.005823268175809401 |
| slam_heading_rmse_deg | 3.9230372176255885 |
| truth_path_length_m | 4.651239444727542 |
| truth_return_distance_m | 0.5934849543080641 |
| truth_final_heading_change_deg | -37.90754356876133 |
| known_map_area_m2 | 17.921250534094874 |
| max_tilt_deg | 2.699869328381916e-06 |
| error | None |


## baseline_12m_retry

경로: `slam/results/research_20261112/baseline_12m_retry`


| 필드 | 원본 값 |
|---|---|
| completed | False |
| baseline_pass | False |
| hardware_calibrated | False |
| scan_messages | 29 |
| trajectory_samples | 57 |
| slam_ate_rmse_m | 2.5446167800905905e-05 |
| truth_return_distance_m | 0.5672111579443385 |
| known_map_area_m2 | 17.09562550948933 |
| max_tilt_deg | 2.699869328381916e-06 |
| error | Obstacle within 0.28m; stopped before collision. |


## carry_navigation_01

경로: `slam/results/research_20261112/carry_navigation_01`


| 필드 | 원본 값 |
|---|---|
| completed | True |
| test_kind | already_held_payload_waypoint_navigation |
| controller_feedback_frame | map |
| acceptance_version | 2 |
| navigation_pass | True |
| hardware_calibrated | False |
| payload_fixed_fixture | True |
| grasp_tested | False |
| placement_tested | False |
| scan_messages | 688 |
| trajectory_samples | 1375 |
| slam_ate_rmse_m | 0.007949588806204243 |
| slam_heading_rmse_deg | 4.898140951770203 |
| truth_path_length_m | 7.608693497785852 |
| truth_return_distance_m | 2.5000391727890006 |
| truth_final_heading_change_deg | 79.98805279527056 |
| known_map_area_m2 | 18.51875055190176 |
| max_tilt_deg | 2.699869328381916e-06 |
| error | None |


| stage | sim time [s] | UTC |
|---|---:|---|
| held_payload_ready | 38.103 | 2026-11-12T05:10:33.889056+00:00 |
| mapping_started | 38.103 | 2026-11-12T05:10:33.889947+00:00 |
| mapping_complete | 92.880 | 2026-11-12T05:11:40.593006+00:00 |
| navigate_pickup_standby | 92.880 | 2026-11-12T05:11:40.594270+00:00 |
| arrived_pickup_standby | 115.943 | 2026-11-12T05:12:08.337900+00:00 |
| navigate_transit | 115.943 | 2026-11-12T05:12:08.338476+00:00 |
| arrived_transit | 147.310 | 2026-11-12T05:12:46.300775+00:00 |
| navigate_delivery_standby | 147.310 | 2026-11-12T05:12:46.301571+00:00 |
| arrived_delivery_standby | 174.221 | 2026-11-12T05:13:18.814959+00:00 |
| carry_navigation_complete | 174.221 | 2026-11-12T05:13:18.816188+00:00 |


## carry_navigation_calibrated_01

경로: `slam/results/research_20261112/carry_navigation_calibrated_01`


| 필드 | 원본 값 |
|---|---|
| completed | True |
| test_kind | already_held_payload_waypoint_navigation |
| controller_feedback_frame | map |
| acceptance_version | 2 |
| navigation_pass | True |
| hardware_calibrated | False |
| payload_fixed_fixture | True |
| grasp_tested | False |
| placement_tested | False |
| scan_messages | 699 |
| trajectory_samples | 1396 |
| slam_ate_rmse_m | 0.010789746476426412 |
| slam_heading_rmse_deg | 0.43466217062935025 |
| truth_path_length_m | 7.592127162721055 |
| truth_return_distance_m | 2.497136564119116 |
| truth_final_heading_change_deg | 88.97315629978624 |
| known_map_area_m2 | 19.911875593420124 |
| max_tilt_deg | 2.699869328381916e-06 |
| error | None |


| stage | sim time [s] | UTC |
|---|---:|---|
| held_payload_ready | 14.100 | 2026-11-12T05:26:45.742758+00:00 |
| mapping_started | 14.100 | 2026-11-12T05:26:45.743617+00:00 |
| mapping_complete | 69.681 | 2026-11-12T05:27:51.975618+00:00 |
| navigate_pickup_standby | 69.681 | 2026-11-12T05:27:51.976432+00:00 |
| arrived_pickup_standby | 92.800 | 2026-11-12T05:28:19.614879+00:00 |
| navigate_transit | 92.800 | 2026-11-12T05:28:19.615477+00:00 |
| arrived_transit | 124.902 | 2026-11-12T05:28:58.064988+00:00 |
| navigate_delivery_standby | 124.902 | 2026-11-12T05:28:58.065986+00:00 |
| arrived_delivery_standby | 152.261 | 2026-11-12T05:29:30.694054+00:00 |
| carry_navigation_complete | 152.261 | 2026-11-12T05:29:30.695022+00:00 |


## initial_stationary

경로: `slam/results/research_20261112/initial_stationary`


| 필드 | 원본 값 |
|---|---|
| completed | True |
| baseline_pass | False |
| hardware_calibrated | False |
| scan_messages | 13 |
| trajectory_samples | 34 |
| slam_ate_rmse_m | 1.5675079967582508e-05 |
| truth_return_distance_m | 0.00028934042922279524 |
| known_map_area_m2 | 0.9975000297278168 |
| max_tilt_deg | 2.4148365394514667e-06 |
| error | None |


## pick_place_attempt1

경로: `slam/results/research_20261112/pick_place_attempt1`


| 필드 | 원본 값 |
|---|---|
| completed | False |
| test_kind | mobile_pick_place |
| controller_feedback_frame | map |
| acceptance_version | 2 |
| mission_pass | False |
| hardware_calibrated | False |
| scan_messages | 615 |
| trajectory_samples | 1221 |
| slam_ate_rmse_m | 0.007641149689418588 |
| slam_heading_rmse_deg | 4.4412404053127785 |
| truth_path_length_m | 4.951162404296564 |
| truth_return_distance_m | 1.0758597351356334 |
| truth_final_heading_change_deg | 88.01269395689926 |
| known_map_area_m2 | 17.483750521056358 |
| max_tilt_deg | 0.022349265870081174 |
| error | Physical grasp failed: object did not lift from the table |


물체 기록 3,614개. 최대 z=0.276510060 m. 최종 xyz=`[-1.4833436038142704, 0.3118339895407406, 0.27599998597935094]`.


| stage | sim time [s] | UTC |
|---|---:|---|
| mapping_started | 257.303 | 2026-11-12T02:21:29.214808+00:00 |
| mapping_complete | 311.810 | 2026-11-12T02:22:34.836539+00:00 |
| navigate_pickup | 311.810 | 2026-11-12T02:22:34.837223+00:00 |
| pickup_rgb_alignment | 335.946 | 2026-11-12T02:23:03.845029+00:00 |
| pregrasp | 340.919 | 2026-11-12T02:23:09.874637+00:00 |
| grasp_approach | 364.391 | 2026-11-12T02:23:38.591108+00:00 |
| gripper_closing | 367.756 | 2026-11-12T02:23:43.278067+00:00 |
| lifting | 371.986 | 2026-11-12T02:23:49.382785+00:00 |


## pick_place_attempt2

경로: `slam/results/research_20261112/pick_place_attempt2`


| 필드 | 원본 값 |
|---|---|
| completed | False |
| test_kind | mobile_pick_place |
| controller_feedback_frame | map |
| acceptance_version | 2 |
| mission_pass | False |
| hardware_calibrated | False |
| scan_messages | 740 |
| trajectory_samples | 1475 |
| slam_ate_rmse_m | 0.011984174157681028 |
| slam_heading_rmse_deg | 4.483833892939829 |
| truth_path_length_m | 4.933361717360457 |
| truth_return_distance_m | 1.0812313786325323 |
| truth_final_heading_change_deg | 94.15195490302582 |
| known_map_area_m2 | 17.505000521689656 |
| max_tilt_deg | 0.020799263234523663 |
| error | Arm cannot hold requested pose; joint errors [0.0014288225478711059, 0.0015630299521750546, 0.5777459929412392, 0.007725543169384785, 0.0015123845802835767] |


물체 기록 4,354개. 최대 z=0.362502376 m. 최종 xyz=`[-1.5539090137674643, 0.13756555156321507, 0.015999982949509092]`.


| stage | sim time [s] | UTC |
|---|---:|---|
| mapping_started | 18.118 | 2026-11-12T02:28:15.681343+00:00 |
| mapping_complete | 72.296 | 2026-11-12T02:29:22.151448+00:00 |
| navigate_pickup | 72.296 | 2026-11-12T02:29:22.152482+00:00 |
| pickup_rgb_alignment | 97.296 | 2026-11-12T02:29:52.668913+00:00 |
| pregrasp | 101.363 | 2026-11-12T02:29:57.536937+00:00 |
| grasp_approach | 134.512 | 2026-11-12T02:30:38.032435+00:00 |
| gripper_closing | 141.245 | 2026-11-12T02:30:46.881934+00:00 |
| lifting | 145.473 | 2026-11-12T02:30:52.243298+00:00 |
| lift_verified | 157.072 | 2026-11-12T02:31:06.323040+00:00 |


## pick_place_attempt3

경로: `slam/results/research_20261112/pick_place_attempt3`


| 필드 | 원본 값 |
|---|---|
| completed | False |
| test_kind | mobile_pick_place |
| controller_feedback_frame | map |
| acceptance_version | 2 |
| mission_pass | False |
| hardware_calibrated | False |
| scan_messages | 690 |
| trajectory_samples | 1372 |
| slam_ate_rmse_m | 0.0066554810951896665 |
| slam_heading_rmse_deg | 4.064714077378389 |
| truth_path_length_m | 4.914584117391285 |
| truth_return_distance_m | 1.078759062372564 |
| truth_final_heading_change_deg | 93.29036364018654 |
| known_map_area_m2 | 17.543750522844498 |
| max_tilt_deg | 0.0029535936201776428 |
| error | Physical grasp failed: object did not lift from the table |


물체 기록 4,071개. 최대 z=0.276452727 m. 최종 xyz=`[-1.5075695010864023, 0.3139702737436299, 0.2759999551629543]`.


| stage | sim time [s] | UTC |
|---|---:|---|
| mapping_started | 24.513 | 2026-11-12T02:33:39.093486+00:00 |
| mapping_complete | 78.858 | 2026-11-12T02:34:46.163558+00:00 |
| navigate_pickup | 78.858 | 2026-11-12T02:34:46.167939+00:00 |
| pickup_rgb_alignment | 102.965 | 2026-11-12T02:35:16.074434+00:00 |
| pregrasp | 107.234 | 2026-11-12T02:35:21.459708+00:00 |
| grasp_approach | 140.031 | 2026-11-12T02:36:02.028966+00:00 |
| gripper_closing | 146.760 | 2026-11-12T02:36:10.266109+00:00 |
| lifting | 150.988 | 2026-11-12T02:36:15.395321+00:00 |


## resume_grasp_bench_01

경로: `slam/results/research_20261112/resume_grasp_bench_01`


| 필드 | 원본 값 |
|---|---|
| completed | False |
| test_kind | grasp_bench |
| controller_feedback_frame | map |
| acceptance_version | 2 |
| mission_pass | False |
| functional_pass | False |
| hardware_calibrated | False |
| scan_messages | 283 |
| trajectory_samples | 561 |
| slam_ate_rmse_m | 0.0001772482473842811 |
| slam_heading_rmse_deg | 0.04465647081264404 |
| truth_path_length_m | 0.0036002342498104487 |
| truth_return_distance_m | 0.0006229741598571841 |
| truth_final_heading_change_deg | 0.06419040248995782 |
| known_map_area_m2 | 0.9631250287033619 |
| max_tilt_deg | 0.01182309566837041 |
| error | Physical grasp failed: object did not lift from the table |


물체 기록 1,662개. 최대 z=0.364184586 m. 최종 xyz=`[-1.5422350846100394, 0.13395851918521093, 0.01599997557216484]`.


| stage | sim time [s] | UTC |
|---|---:|---|
| grasp_bench_ready | 30.120 | 2026-11-12T03:15:44.672257+00:00 |
| pickup_rgb_alignment | 30.120 | 2026-11-12T03:15:44.672970+00:00 |
| pregrasp | 30.620 | 2026-11-12T03:15:45.294390+00:00 |
| grasp_approach | 63.067 | 2026-11-12T05:04:22.333672+00:00 |
| gripper_closing | 69.796 | 2026-11-12T05:04:30.498641+00:00 |
| grip_contact_verified | 75.384 | 2026-11-12T05:04:37.348024+00:00 |
| lifting | 75.384 | 2026-11-12T05:04:37.348902+00:00 |


## slam_feedback_12m

경로: `slam/results/research_20261112/slam_feedback_12m`


| 필드 | 원본 값 |
|---|---|
| completed | True |
| test_kind | square_loop |
| controller_feedback_frame | map |
| acceptance_version | 2 |
| baseline_pass | True |
| hardware_calibrated | False |
| scan_messages | 311 |
| trajectory_samples | 615 |
| slam_ate_rmse_m | 0.007921483009346541 |
| slam_heading_rmse_deg | 3.7769512953168043 |
| truth_path_length_m | 4.65968344769427 |
| truth_return_distance_m | 0.0398345201425173 |
| truth_final_heading_change_deg | -10.382610191478305 |
| known_map_area_m2 | 17.731250528432433 |
| max_tilt_deg | 2.699869328381916e-06 |
| error | None |


## smoke_025m

경로: `slam/results/research_20261112/smoke_025m`


| 필드 | 원본 값 |
|---|---|
| completed | True |
| baseline_pass | True |
| hardware_calibrated | False |
| scan_messages | 151 |
| trajectory_samples | 300 |
| slam_ate_rmse_m | 0.0037648759956901727 |
| truth_return_distance_m | 0.13659017769275109 |
| known_map_area_m2 | 15.263125454876576 |
| max_tilt_deg | 2.699869328381916e-06 |
| error | None |


# 부록 D. 공식 참고 자료와 인용 범위

아래는 작업 중 참고한 공식 자료와 원본 코드다. 이 보고서는 새롭게 수행한 포괄적 문헌조사가 아니다. 수치 결과의 1차 근거는 로컬 실험 파일이며 외부 문서는 하드웨어 기준 사양·소프트웨어 동작의 참고다. 하드웨어 사양이 곧 사용자 기체의 실측값은 아니다.

1. [ROBOTIS XL430-W250](https://emanual.robotis.com/docs/en/dxl/x/xl430-w250/) — wheel motor 기준 사양.

2. [LeRobot SO-101](https://huggingface.co/docs/lerobot/so101) — follower 구성과 전원 주의.

3. [SO-ARM100/101 official repository](https://github.com/TheRobotStudio/SO-ARM100) — 로봇 구성 참고.

4. [Waveshare ST3215 Servo](https://docs.waveshare.com/ST3215_Servo) — 7.4 V/12 V 계열 사양.

5. [ROBOTIS LDS-02](https://emanual.robotis.com/docs/en/platform/turtlebot3/appendix_lds_02/) — LiDAR baseline 사양.

6. [slam_toolbox Jazzy source](https://github.com/SteveMacenski/slam_toolbox/blob/jazzy/src/slam_toolbox_common.cpp) — shouldProcessScan의 거리/각도 gate.

7. [ROS 2 diff_drive_controller Jazzy](https://control.ros.org/jazzy/doc/ros2_controllers/diff_drive_controller/doc/userdoc.html) — radius/track 보정 개념; 현재 controller가 이 패키지라는 뜻은 아님.

8. [SDFormat lidar schema](https://raw.githubusercontent.com/gazebosim/sdformat/sdf14/sdf/1.10/lidar.sdf) — noise/type 구조.

9. [Gazebo contact system source](https://github.com/gazebosim/gz-sim/blob/gz-sim8/src/systems/contact/Contact.cc) — contact topic의 처리.

10. [RViz rendering source](https://github.com/ros2/rviz/blob/jazzy/rviz_rendering/src/rviz_rendering/render_system.cpp) — local resource overlay 경로.

11. [RViz sampler issue #1279](https://github.com/ros2/rviz/issues/1279) — 유사 sampler 오류의 upstream 이력.

12. [ROBOTIS TurtleBot3 bringup](https://emanual.robotis.com/docs/en/platform/turtlebot3/bringup/) — Jazzy cmd_vel type과 domain.

13. [ROBOTIS TurtleBot3 navigation](https://emanual.robotis.com/docs/en/platform/turtlebot3/navigation/) — Twist/TwistStamped 선택.

14. [Nav2 physical TurtleBot3 guide](https://docs.nav2.org/jazzy/tutorials/general_tutorials/navigation2_on_real_turtlebot3/navigation2_on_real_turtlebot3/) — 실물 연결 참고.

15. [MolmoAct2 SO100/101 model card](https://huggingface.co/allenai/MolmoAct2-SO100_101) — 향후 action convention 검토 대상.

16. [LeRobot MolmoAct2 documentation](https://github.com/huggingface/lerobot/blob/main/docs/source/molmoact2.mdx) — 향후 adapter 검토 대상.

17. [Stanford HomeBody project](https://tml.stanford.edu/homebody/) — 향후 참고 프로젝트; 이 환경에 재현하지 않음.

18. [MolmoB0T paper](https://arxiv.org/abs/2603.16861) — 과거 메모의 연구 참고; 현재 실험과 동등한 결과 주장 안 함.


## 로컬 증거 우선순위

최신 handoff 상태 → 원본 metrics/configuration/trajectory → 해당 trial source snapshot → current code → 과거 checkpoint의 순서로 용도를 구분해 대조한다. 현재 코드와 과거 수치가 일치하지 않을 수 있는 것은 실험 사이의 수정 때문이며, 결과를 현재 코드로 소급해서 바꾸지 않는다.
