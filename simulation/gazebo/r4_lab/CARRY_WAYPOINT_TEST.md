# 물체를 든 상태의 waypoint 이동 시험

사용자 최신 요청에 따라 **이미 물체를 들고 있는 상태에서 목표 지점까지 이동하는 기본 기능만** 확인한다. 집기·내려놓기·VLA 정책은 시험하지 않는다.

## 실행

```bash
~/r4_lab/start_carry
```

다른 터미널에서:

```bash
~/r4_lab/test_carry
```

장면을 중복 실행하지 않는다. 시험별 새 월드를 시작한다.

## 조건

- 32 mm, 10 g 빨간 물체를 `held_payload_fixture` fixed joint로 그리퍼에 연결한 초기 상태다. 질량과 관성·충돌을 Gazebo 물리에 포함한다. 총 모델 질량은 약 2.733 kg이다.
- 이 고정 결합은 이동 시험용 fixture다. 실제 파지에 성공했거나 물리적 파지가 검증됐다는 뜻이 아니다.
- LiDAR/odom으로 지도 작성 후 SLAM map TF로 제어한다. 실제 `/map` 점유 격자에 A*와 장애물 팽창을 적용한다. 작업대 footprint는 명시적으로 제공한 keep-out prior다.
- 베이스 명령 20 Hz, 최대 속도 0.08 m/s. 팔은 기본 자세를 유지하며 그리퍼 목표는 0.06 rad이다.
- RGB 카메라를 유지하지만 이번 이동 제어에는 물체 인식이나 RGB-D가 필요하지 않다.
- 기본 목표는 `slam/carry.yaml`에 지정한다. RViz에 목표 화살표·이름, 계획 경로, 실제 SLAM 궤적을 표시한다.

| 지점 | World x [m] | World y [m] | 방향 |
|---|---:|---:|---:|
| pickup_standby | -1.50 | -0.12 | 90° |
| transit | 0.00 | -0.70 | 0° |
| delivery_standby | 1.30 | -0.70 | 90° |

## 판정과 기록

각 지점에서 정지 후 map 좌표 도착 오차, simulator truth 기준 실제 위치·방향 오차, 기울기와 모터 토크를 저장한다. Truth는 평가에만 쓰며 주행 명령을 생성하지 않는다.

사전 설정한 판정: map 위치 오차 <3 cm, 실제 위치 오차 <10 cm, 실제 방향 오차 <15°. 결과 수치는 시험 폴더의 `waypoint_results.json`, `metrics.json`을 기준으로 한다. 시험 한 번의 통과가 반복 신뢰성이나 실물 성능 입증은 아니다.

## 완료 결과와 기본 보정

`carry_navigation_01`과 보정 후 `carry_navigation_calibrated_01` 모두 3개 지점에 도착했다. 아래는 simulator truth로 평가한 값이다.

| 지점 | 이전 위치 [cm] | 보정 후 위치 [cm] | 이전 방향 [°] | 보정 후 방향 [°] |
|---|---:|---:|---:|---:|
| pickup_standby | 2.245 | 2.151 | -3.936 | -1.565 |
| transit | 2.485 | 3.601 | +3.142 | +0.794 |
| delivery_standby | 2.207 | 3.150 | +10.012 | +1.027 |

별도의 직진/후진/CW/CCW 시험 `odometry_identification_01`에서 유효 encoder radius/track을 식별한 뒤 waypoint 경로에 고정 적용했다. `slam/calibration/carry_simulation.yaml`에 조건과 원본 경로를 기록했다. 물리 바퀴 geometry와 명령용 geometry를 바꾸지 않았다. 이 값은 실물에 적용하지 않는다.

`start_carry`는 이제 해당 carry 전용 보정과 회전 스캔을 처리하는 SLAM 설정을 기본 사용한다. 위치 오차는 일부 늘었고 방향 오차는 줄었다. SLAM gating, encoder geometry, 도착 제어 설정을 함께 바꿨으므로 개별 변경의 효과를 분리한 실험은 아니다. 각 조건 1회로 반복 신뢰성을 주장하지 않는다.

보정 후 map 위치 오차는 2.348 / 2.363 / 2.967 cm, SLAM ATE RMSE는 1.079 cm다. LiDAR 5 Hz, odom 50 Hz, scan 획득 시각 TF 연결과 sim time 일치를 별도 점검했다. 지도·pose graph·소스/설정·사진·MP4는 각 시험 폴더에 저장했다.

핵심 선별본: `slam/results/research_20261112/carry_calibration_selected/README.md`. 실물 이행 범위와 미확인 사항은 `REAL_TURTLEBOT_READINESS.md`에 정리했다. 실험 중 자동 카메라 follow나 시점 변경을 하지 않으며, 녹화는 현재 창을 읽기만 한다.
