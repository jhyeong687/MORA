# 실물 TurtleBot으로 이어가기 위한 준비

현재 검증 대상은 Gazebo의 TurtleBot3 Burger + SO-ARM101 결합 모델이다. 실물은 아직 연결하지 않았으며, 실물 주행·정지 거리·하중 안정성을 검증했다는 뜻이 아니다.

## 이번에 분리한 경계

- 공통 입력: `/scan`, `/odom`, `odom → base_footprint → 실제 LiDAR frame` TF. SLAM을 쓸 때 `map → odom`도 필요하다.
- 시뮬레이션: `use_sim_time=true`, Gazebo `/clock`, ROS domain 46, localhost discovery. `/ground_truth/odom`은 실험 평가 및 별도 파라미터 식별에만 사용한다.
- 실물: `use_sim_time=false`, 실제 TurtleBot과 같은 ROS domain 및 네트워크 discovery. Gazebo clock, generated robot_state_publisher, simulator truth, 시뮬레이션용 엔코더 보정값을 함께 실행하지 않는다.
- `calibration/carry_simulation.yaml`의 유효 반경·축간거리는 현재 시뮬레이션의 10 g fixture/마찰 조건에서 식별했다. 실물 치수나 실물 보정값이 아니다. 물리 바퀴와 명령 geometry는 변경하지 않았다.
- 현재 `test_carry`는 시뮬레이터 평가·fixture를 요구하는 시험 도구다. 그대로 실물에 실행하는 런처가 아니다. 실물 제어 연결 시에는 truth 구독을 제거한 실행 경로와 실제 팔 드라이버가 필요하다.

## 연결 후 이동 없이 점검

실제 TurtleBot의 드라이버를 실행한 뒤, 같은 domain으로 맞춘 PC에서:

```bash
export ROS_DOMAIN_ID=<TurtleBot과_같은_숫자>
~/r4_lab/check_real_base --output ~/r4_lab/real_base_preflight.json
```

`check_real_base`는 조회·구독만 하며 이동 명령을 보내지 않는다. ROS 2 Jazzy를 source하고, 이 프로세스에 남아 있는 시뮬레이션용 LOCALHOST discovery 설정을 SUBNET으로 바꾼다. 출력에는 다음이 포함된다.

- scan/odom 수신률, acquisition timestamp 단조 증가 여부, 데이터 나이
- scan의 실제 frame, odom parent/child frame
- scan 획득 시각의 LiDAR/base/odom TF 연결
- 노드별 `use_sim_time`, scan/odom publisher QoS
- 실제 드라이버의 `/cmd_vel` 입력형: `Twist` 또는 `TwistStamped`

센서마다 다른 실제 주기에 맞춰 판정 기준을 검토해야 한다. 현재 최소 기준은 scan 3 Hz, odom 10 Hz이며, discovery와 TF history가 준비된 뒤의 스캔을 검사한다. 통과는 인터페이스 준비 판정이며 물리 안전성·보정 완료 판정이 아니다. 네임스페이스를 쓰는 경우 ROS remapping으로 실제 topic과 연결한다.

## Jazzy에서 확인할 메시지형

ROBOTIS 공식 문서상 Jazzy TurtleBot3는 `cmd_vel`에 `TwistStamped`를 사용하며, `enable_stamped_cmd_vel=false`로 `Twist`를 선택할 수 있다. 현재 Gazebo bridge는 `Twist`를 쓴다. 실물 연결 때 실제 타입을 확인하고 컨트롤러 또는 adapter를 일치시켜야 한다. 시뮬레이션의 타입을 실물에도 무조건 가정하지 않는다.

출처: [ROBOTIS TurtleBot3 bringup](https://emanual.robotis.com/docs/en/platform/turtlebot3/bringup/), [ROBOTIS navigation](https://emanual.robotis.com/docs/en/platform/turtlebot3/navigation/), [Nav2 physical TurtleBot3 guide](https://docs.nav2.org/jazzy/tutorials/general_tutorials/navigation2_on_real_turtlebot3/navigation2_on_real_turtlebot3/).

## 실물에서 남은 확인

실제 기체와 팔 장착 위치·전압·하중, LiDAR extrinsic, 바퀴 반경과 유효 축간거리를 측정한다. 낮은 속도의 직진/후진/양방향 회전으로 식별하고, 별도의 waypoint 경로에서 재검증한다. 보정에 쓴 동작과 검증 경로를 구분해 원본 로그를 저장한다.

시뮬레이션의 0.08 m/s 운반 속도를 곧바로 실물 기본값으로 쓰지 않는다. `slam/hardware_interface.yaml`은 처음 확인할 목표 인터페이스와 낮은 시험 속도/명령 주기/watchdog 기준을 기록한 계약 파일이며, 아직 이 제한을 적용하는 실물 드라이버 설정은 아니다. 실물 접속 후 stop/watchdog 동작과 장애물 여유를 먼저 측정해야 한다.

카메라 자동 추적은 사용하지 않는다. 사진·영상은 사용자가 잡아 둔 화면을 그대로 기록한다.
