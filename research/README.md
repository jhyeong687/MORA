# 다음 연구: 터틀봇 주행에 따른 운반 준비 판단

**가설:** 같은 파지라도 터틀봇의 다음 직진·회전·감속에 따라 운반 유지 가능성이 다를 수 있다.
영상의 grasp complete 점수와 예정된 주행의 carry readiness를 분리해서 측정한다.

[20쪽 연구 계획 PDF](R4_Research_Plan_20261112.pdf)에 가설·선행연구·변수·비교군·예산·8주 계획·sim-to-real 단계를 정리했다.

## 최소 실험

1. cloud에서 기존 모델·RGB 2대·관절·LiDAR를 확인하고 자유 물체 1회 집기를 재현한다.
2. 정지 lift/hold를 fresh reset 20회 점검한다.
3. 동일 reset recipe 20개 × 주행 profile 4개로 베이스 효과를 조사한다.
4. 관측만 / 주행 계획 추가 / 고정 확인 / 선택 확인을 비교한다.
5. 항상 느린 주행, 같은 시간·동작을 쓰고 새 관측을 버리는 sham 기준을 포함한다.
6. 성공률·낙하율·승인 비율·완료시간·질의 비용을 함께 보고한다.

모든 n과 통과 기준은 제안이며 실험 결과가 아니다. Pilot 분산으로 본 실험 n을 사전 결정한다.
현재 조건에서 베이스 효과가 없으면 비현실적인 힘으로 효과를 만들지 않고 시야/베이스 배치 주제로 범위를 조정한다.

## 모델의 역할

- MolmoAct2 SO100_101: 공개 SO용 정책을 먼저 호환성 점검. 입력 보정 후에도 부족할 때만 추가 학습.
- RoboJev: 완료 판정 비교군. 미래 주행에서 떨어질지를 이미 해결했다고 가정하지 않음.
- FLUX 3 Action SO-101: WAM 확장 후보. 48/80 GB cloud에서 메모리·processor·history 지원을 먼저 검증.
- LaWAM: latent 미래 예측 참고. LIBERO action을 우리 팔에 직접 넣지 않음.
- LLM: navigate/observe/grasp/verify/carry/recover의 상위 선택. 저수준 모터 제어는 실행측 controller.

CheckVLA, DreamTrajectory, VeriVLA, 능동 시야·운반 MPC가 이미 가까운 문제를 다룬다.
차별점은 최초 조합이라는 주장보다, 주행별 결과와 확인 행동의 정보 가치를 통제해 입증하는 데 둔다.

## cloud-only 및 sim-to-real

시뮬레이션 대량 실행·학습·GPU 추론은 RunPod. Mac/Ubuntu는 작업·접속·기록·Git 동기화 환경이다.
실물에서는 같은 관측/action 계약을 유지하고 simulator adapter를 실제 driver로 바꾼다.
모터 전압·관절 zero/sign·카메라/TCP·질량·접촉·지연을 계측하고 zero-shot, calibration-only, 추가 학습을 분리한다.
1차 예산 상한은 $150-250 제안이며 실행시간·저장 비용은 실측 후 확정한다. Pod를 새로 대여한 기록은 없다.
