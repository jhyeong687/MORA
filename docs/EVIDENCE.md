# 검증 범위와 읽는 법

## MuJoCo 기록

`simulation/mujoco/results/scenarios.csv`가 조건별 요약, `cases.json`이 조건 정의,
`*_trace.csv`와 `*_poses.npz`가 시간 기록이다. 주요 source는 `engine.py`, `r4.xml`, `run_tests.py`다.

- 평지 주행·급정지·회전, 경사면·단차·보조 강구·토크 제한·시간 간격을 조사했다.
- `edge_80mm` 및 시간 간격 교차검증에서 전도가 관측됐다. 평지 일부 조건의 작은 기울기로 전체 안정성을 주장하지 않는다.
- `pick_100g`는 그리퍼 쪽 모델 body의 질량을 변경하고 팔 궤적을 실행한 시험이다.
  접촉으로 자유 물체를 집어 100 g 파지에 성공한 시험이 아니다.
- 기본 12 V 근사와 7.4 V/rated-cap 변형을 같은 모터 조건으로 합산하지 않는다.

## Ubuntu / ROS / Gazebo 기록

`evidence/ubuntu/metadata/experiment_registry.json`과 trial별 JSON을 우선한다.
전체 기술 설명은 [정리한 보고서](ubuntu/REPORT.md)와 [PDF](ubuntu/R4_Engineering_Handoff.pdf)에 있다.

| 확인한 항목 | 결과와 한계 |
| --- | --- |
| 팔 작은 범위 추종 | 12/12 유지 구간. 5개 팔 회전 관절 + gripper이며 전 작업공간 검증 아님 |
| 접촉 파지 | 일시 lift 뒤 낙하. 안정 hold·pick-carry-place 미해결 |
| carry 주행 | 32 mm, 10 g 물체를 fixed joint로 부착. 단일 trial의 waypoint 3/3 통과 |
| 보정 후 실제 위치 오차 | 2.151 / 3.601 / 3.150 cm. 세 지점은 독립 반복 3회가 아님 |
| 보정 후 방향 오차 | -1.565 / +0.794 / +1.027 deg |
| real robot / VLA | 실물 주행·파지와 VLA/WAM 학습은 아직 미검증 |

SLAM ATE와 실제 도착 오차를 구분한다. 보정 시 여러 설정을 함께 바꿨고 조건별 1회이므로 인과적 개선·통계적 신뢰성을 주장하지 않는다.
MuJoCo와 Gazebo/DART의 접촉·관성 근사는 동일하지 않다.
현재 raw bag, binary pose graph와 전체 길이 녹화는 원래 VM에 별도 보존되어 있으며,
기존 전달 ZIP에 포함되지 않았다. `planning_bundle_omissions.json`에 그 범위를 기록했다.

## 공개 사본의 변환

개인 홈 경로·계정 식별자·개인 문서 링크를 제거한 사본이다. 현재 실행 script의 경로는 상대 경로로 정리했다.
과거 snapshot 안의 hash는 당시 원본의 값이며, 개인정보 제거 후 파일의 hash와 같다고 주장하지 않는다.
이 저장소의 현재 byte 검증은 `metadata/manifest.json`을 사용한다.
