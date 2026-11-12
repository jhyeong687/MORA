# Carry 시뮬레이션 엔코더 보정

`carry_simulation.yaml`은 `results/research_20261112/odometry_identification_01/`에서 식별한 값이다. 10 g fixed payload, tire friction 0.7, seed 42의 carry 장면에 한정한다.

직진/후진 변위로 공통 유효 반경을 추정하고, 독립된 양방향 회전의 실제 각도와 raw quantized encoder 변위로 유효 축간거리를 추정했다. 두 방향의 일관성을 확인한 뒤 별도의 waypoint 주행에서 검증했다. 식별 원본은 `raw_identification.json`, 구간별 계산은 `identification.json`이다. Simulator truth는 식별/평가에만 쓰며 SLAM 주행 feedback은 map TF다.

유효 축간거리 약 0.178 m는 슬립 등의 영향을 포함한 encoder 모델 파라미터다. 실제 축간거리 측정값으로 해석하지 않는다. physical/command geometry는 0.033 m / 0.160 m를 유지했다.

다른 마찰/하중/장면에는 다시 식별하고 검증한다. 실물에는 별도의 물리 측정 및 calibration 파일이 필요하다. 현재 물성·관성·센서 noise는 실제 로봇을 완전히 식별한 모델이 아니다.

제자리 회전 스캔 처리 설정의 근거: [slam_toolbox Jazzy shouldProcessScan 구현](https://github.com/SteveMacenski/slam_toolbox/blob/jazzy/src/slam_toolbox_common.cpp). `check_min_dist_and_heading_precisely=true`에서 거리 또는 방향 변화 기준으로 스캔을 처리한다.
