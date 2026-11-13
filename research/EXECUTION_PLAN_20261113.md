# MORA 실행 계획 개정안 · 2026-11-13

> 이 문서는 초기 8주안 이력이다. 현재는 [4주 최종 계획](FINAL_PLAN_20261113.md)과 [protocol v3](protocol_v3.yaml)를 따른다.

상태: 제안. 아래 회수·자원·일정은 앞으로의 실험 설계이며 완료한 결과가 아니다.
이 문서는 2026-11-12 PDF의 실행 순서를 수정한다. 원본 PDF와 과거 증거는 보존한다.

## 연구 목표

**공개 SO-101 VLA로 자유 물체를 집고, 예정된 터틀봇 주행에 맞춰 재관측·재파지·운반 시작을 선택하는 이동 조작 시스템.**

핵심 질문은 “같은 파지를 다음 직진에서는 유지할 수 있지만 회전·감속에서는 유지하지 못할 때, 출발 전 어떤 확인 행동에 시간을 써야 하는가?”다.
최신 정책을 실제 executor로 사용하고, 주행 조건·관측의 유용성·원격 추론 비용을 통제해서 효과를 측정한다.
주행 중 동시 집기는 후속 확장으로 두고, 첫 과제는 `도착 → 정지 → 집기 → 확인 → 이동 → 정지 → 놓기`로 한정한다.

## 기존 계획에서 바꾸는 부분

- 첫 과학 실험부터 VLA가 자유 물체를 잡는다. 수작업 grasp controller를 먼저 완성하는 일을 장기 선행 조건으로 두지 않는다.
- 관절 좌표·카메라·접촉의 짧은 점검은 VLA 연결 과정에 포함한다. 이 점검과 수동 파지 알고리즘 개발을 구분한다.
- 최신 모델을 한꺼번에 학습하지 않는다. SO-101 정책 하나를 고정한 뒤 상위 판단 방식들을 비교한다.
- LLM/VLM의 완료 판단과 물리적 운반 유지 가능성을 별도 출력으로 기록한다.
- WAM은 별도 비교 실험으로 편성한다. 미래 영상의 그럴듯함을 낙하 확률이나 전복 안전성으로 해석하지 않는다.

## 2026-11-13에 확인한 기술 선택

| 역할 | 우선 선택 | 실행 조건과 한계 |
|---|---|---|
| 최신 SO-101 executor | `lerobot/g05_so101` | LeRobot 0.7의 G0.5 통합. 6개 실제 관절을 모델의 그룹 action으로 변환하는 저장 processor를 보존한다. 먼저 System 1을 사용하고 System 2는 별도 비교한다. 비상업용 Community License. |
| SO-101 비교·대체 executor | `allenai/MolmoAct2-SO100_101` | 공개 SO 전용 absolute joint-pose 정책. 관절 순서·단위·zero/sign·통계와 RGB 시점 호환성 검증. 사전학습 정책의 우리 장면 zero-shot 성공은 미확인이다. |
| LLM/VLM 상위 판단 | LeRobot external planner 패턴, `Qwen/Qwen3-VL-8B-Instruct`를 초기 후보로 사용 | instruction과 RGB 이력으로 제한된 skill 중 선택. 원격 planner와 custom mobile adapter의 결합은 별도 검증한다. 최종 모델·정밀도는 실제 메모리/지연 측정 후 동결한다. |
| 카톡에서 추천한 성공 심판 | RoboJev-27B | 현재 과제 완료 판정 비교군. 공식 bf16 경로는 80 GB GPU를 요구한다. 처음에는 저장한 영상으로 오프라인 판정을 수행한다. 미래 운반·미끄러짐 위험을 이미 예측한다고 가정하지 않는다. |
| NVIDIA WAM | Cosmos 3 Edge | LeRobot 변환 base를 우리 데이터에 적응시키는 후보. 공식 LIBERO recipe의 Edge LoRA 21 GB / bf16 평가 15 GB는 그 설정의 측정치다. 우리 카메라와 동시 서비스 메모리는 재측정한다. |
| SO-101 WAM 대안 | FLUX 3 Action SO-101 | 전용 체크포인트가 있지만 history·past action·저장 processor가 필요하다. latest-frame만 보내는 일반 원격 경로로 대체하지 않는다. Cosmos와 둘 다 대규모 학습하는 계획은 세우지 않는다. |
| 장기 문맥 참고 | NVIDIA Long-WAM | 공개 LIBERO action/state와 시점 계약을 SO-101에 그대로 넣지 않는다. history 기반 검증의 참고와 후속 적응 후보. |
| 대규모 후속 후보 | DreamZero / GR00T 2 | DreamZero 공식 quick start는 분산 추론 최소 2 GPU. GR00T 2 공식 페이지는 코드 12월 공개 예정. 현재 핵심 실험의 필수 의존성으로 두지 않는다. |

근거: [LeRobot 0.7 릴리스](https://huggingface.co/blog/lerobot/lerobot-release-v070), [G0.5](https://huggingface.co/docs/lerobot/v0.7.0/g05), [MolmoAct2 SO](https://huggingface.co/allenai/MolmoAct2-SO100_101), [external planner](https://huggingface.co/docs/lerobot/v0.7.0/inference#external-planner), [RoboJev](https://huggingface.co/josefchen/RoboJev-27B), [Cosmos3](https://huggingface.co/docs/lerobot/v0.7.0/cosmos3), [FLUX 3](https://huggingface.co/docs/lerobot/v0.7.0/flux3), [Long-WAM](https://huggingface.co/docs/lerobot/v0.7.0/longwam), [DreamZero](https://github.com/dreamzero0/dreamzero), [GR00T 2](https://research.nvidia.com/labs/gear/gr00t-2/).

### NVIDIA 기하 기반 파지 경로도 고려한다

추천받은 구성을 정확히 나누면 `물체 위치 추정 → 파지 후보 생성/선택 → 실행 가능한 팔 경로 → 결과 확인 → 복구`다.

- **FoundationPose는 물체의 6D pose 추정·추적 모델이다.** 기본 demo는 RGB, depth, mask, intrinsics와 mesh를 사용한다. 파지 pose 생성기와 동일하지 않다.
- 파지 후보는 알려진 작은 물체의 후보 집합 또는 GraspGen 계열로 만든다. 원래 GraspGen의 공개 gripper 3종에 SO-101은 포함되지 않으므로 모델을 바로 꽂을 수 있다고 가정하지 않는다.
- cuRobo에는 SO-101의 URDF, collision geometry, 관절 제한을 정의하고 실제 5개 팔 관절로 도달 가능한 목표만 사용한다. 임의 6D pose를 모두 달성한다고 가정하지 않는다. 현재 V2는 v1과 API가 다르므로 선택 버전을 동결한다.
- wrist/belly RGB 2대는 자동으로 보정된 stereo가 되지 않는다. FoundationPose의 공식 RGB-D 경로를 실물 비교군으로 쓰려면 유효한 depth 획득 경로가 필요하다.
- 센서 구매가 없는 첫 주는 RGB 기반 VLA를 사용한다. 기하 비교군에 simulator depth를 쓰면 `sim-only depth baseline`으로 명시하고 RGB-only와 입력 조건을 구분한다. GT object pose는 별도의 oracle 진단군에만 허용한다.

근거: [FoundationPose demo](https://github.com/NVlabs/FoundationPose/blob/main/run_demo.py), [GraspGen 지원 gripper](https://github.com/NVlabs/GraspGen), [cuRobo](https://github.com/NVlabs/curobo), [SO-101 actuator 설명](https://docs.nvidia.com/learning/physical-ai/getting-started-with-isaac-lab/latest/train-a-robot-arm/02-so101-robot.html).

## 최신 선행연구와 구분할 가설

VLM으로 파지를 수정하는 접근은 [GraspCorrect, 2025-03](https://arxiv.org/abs/2503.15035)에 있다.
[CheckVLA, 2026-07](https://arxiv.org/abs/2607.26789)는 mobile manipulation의 action-conditioned world-model 검증과 latency-aware 개입을 다룬다.
[VeriVLA, 2026-10-15](https://arxiv.org/abs/2610.21985)는 필요한 결정 시점에 latent world model로 행동 후보를 검증한다.
[Cracking Mobile Manipulation, 2026-10-14](https://arxiv.org/abs/2610.19600)는 fixed VLA 위의 planning·visual memory·base adjustment·local correction을 다룬다.
[World Pilot, 2026-06](https://arxiv.org/abs/2606.12403)도 VLA에 WAM prior를 결합한다.

따라서 “LLM + VLA + 터틀봇”, “실패 확인 후 재시도”, “WAM으로 미래를 본다” 자체를 신규성으로 주장하지 않는다.
아래는 차별화를 검토할 **가설**이며, 최초성이나 우월성이 입증된 상태가 아니다.

1. **주행 조건 가설:** 동일한 물체·파지 recipe에서도 예정된 속도·가속·회전 조건을 주면 관측만 쓴 판단보다 운반 실패 예측이 좋아지는가?
2. **확인 행동 가설:** 제한된 시간/질의 예산에서 필요한 경우에만 시점을 바꾸어 관찰하면, 고정 확인이나 항상 보수적인 이동보다 완료율과 시간의 절충이 좋아지는가?
3. **정보 효과 가설:** 개선은 더 기다리거나 파지를 물리적으로 안정화한 효과를 넘어 새 관측을 활용한 덕분인가?

작은 플랫폼, 두 RGB 시점, 운반 경로, cloud 지연을 포함한 재현 가능한 평가가 1차 산출물이다.
기존 방법 대비 새로운 선택 원리와 효과가 충분하지 않으면 “새 알고리즘”보다 평가·실증 연구로 범위를 정직하게 정리한다.

## 시스템 역할과 정보 경계

| 모듈 | 입력 | 출력 |
|---|---|---|
| navigation skill | LiDAR, odometry, 현재 지도/목표 | 검증된 base controller를 통한 도착·정지 |
| VLA executor | wrist/belly RGB, 보정한 팔 state, 짧은 instruction | 저장 processor를 거친 6개 관절 목표 chunk |
| VLM feedback | 현재까지의 RGB 이력, 실행한 skill, instruction | 잡힘/미끄러짐 의심/가림/불명 판단과 제한된 다음 skill 제안 |
| route risk module | 현재 관측 특징, proprioception, 예정 속도·가속·곡률, 관측 age | 보정된 carry failure 점수와 확인 필요 여부 |
| skill selector | feedback, risk, 남은 시간/질의 예산 | `observe`, `regrasp`, `carry`, `abort` |
| 실행측 controller | 승인된 skill/chunk | 제한 범위의 모터 명령, stale 응답 폐기, timeout hold/stop |

LLM의 문장형 “확신”을 보정된 확률로 쓰지 않는다. risk module은 간단한 분류기부터 시작하고 별도 calibration split에서 threshold를 정한다.
LLM은 허용된 skill과 짧은 instruction을 고른다. base 이동을 팔 전용 VLA의 6개 출력에 임의로 덧붙이지 않는다.
초기 `observe`는 base 정지 상태에서 작은 wrist 시점 변경 후 다시 촬영하는 행동이다. 물체를 놓기 전 base를 움직여 관찰하는 확장은 별도 실험으로 분리한다.
`regrasp`는 단순히 더 세게 닫는 명령이 아니라, 지정된 받침 위에 내려놓고 다시 집는 검증된 skill이어야 한다.

GT pose/contact/mass/friction은 평가와 supervised label 생성에만 사용한다. 정답 label로 학습하는 것과 정답 state를 정책 입력에 넣는 것을 구분한다.
온라인 판정에는 그 시점 이후의 영상이나 route outcome을 넣지 않는다.

## 실행 단계와 중단 기준

### S0 · 첫 cloud 세션: 최신 정책을 연결한다

**성공 산출물:** 현재 R4 모델에서 RGB 2대와 관절 state를 보내고, 공개 SO 정책의 action을 실제 simulator에 적용한 1회 기록.

1. Gazebo/ROS 기존 소스를 cloud x86 환경에서 빌드하고 RGB timestamp, joint, odometry, LiDAR 토픽을 확인한다. cloud 빌드·headless RGB는 아직 완료된 상태가 아니다.
2. 모델을 GPU에 올려 공개 sample 입력의 추론을 확인한 다음 우리 관측을 연결한다. 첫 후보는 G0.5 SO-101이다.
3. stored processor와 관절 zero/sign/단위/범위/주기를 맞춘다. 한 관절 소동작과 reset으로 action 의미를 확인한다.
4. base를 멈춘 채 32 mm, 10 g 자유 큐브를 대상으로 집기→들기→놓기 1회를 시도한다. 물체에 fixed joint나 pose 강제 추종을 사용하지 않는다.
5. 모델 load, sample inference, own-frame inference, actuation, contact, task 결과를 각각 기록한다. 하나의 실패를 모두 “VLA 실패”로 묶지 않는다.

G0.5의 새 processor/환경 문제에 이틀 이상 막히면 MolmoAct2 SO로 같은 계약을 점검하고 원인을 분리한다. 모델 이름 교체를 성능 개선으로 해석하지 않는다.
VLA가 못 잡으면 먼저 시점·좌표·접촉을 진단한다. 그 뒤 우리 scene의 20–50개 성공 demonstration을 확보하는 작은 적응 pilot을 제안한다.
데이터 수는 충분성이 입증된 값이 아니다. 시뮬레이션 teleop 또는 기하 teacher로 만들 수 있지만 성공 trajectory가 실제 접촉으로 생성됐는지 검사하고 실패 기록도 보관한다.
teacher에 특권 정보를 썼으면 출처를 기록한다. VLA 평가에서는 해당 입력을 제거한다.

### S1 · 정지 VLA baseline

- 동일 executor/checkpoint로 새로운 reset 20회를 시행한다. 첫 물체는 기존 32 mm/10 g 큐브다.
- lift/hold와 place를 따로 평가한다. 기존 제안인 물체 바닥 20 mm 이상 상승·2초 유지를 scale 확인 후 사전 동결한다.
- 14/20 lift/hold는 다음 pilot으로 진행할 후보 기준이며 안전 기준이나 검정력 근거가 아니다. 실패하면 원인을 고친 뒤 별도 새 batch로 재평가한다.
- 색·질감·조명·위치 분포는 기록한다. 먼저 좁은 조건의 동작을 확인하고 이후 일반화 조건을 늘린다.
- 이 단계 영상은 VLA가 자유 물체를 실제로 잡은 근거가 된다. 학습 loss나 모델이 생성한 영상은 이를 대체하지 않는다.

### S2 · 터틀봇이 왜 필요한지 확인하는 route pilot

- 독립 recipe 20개 × 직진/좌회전/우회전/감속 4개 = **80개 continuation**을 제안한다.
- 네 profile은 같은 출발/도착 구간과 명시한 속도·가속 범위로 정의한다. 목적이 다른 scene을 무작정 섞지 않는다.
- grasp 이후 시뮬레이터 full-state 복구의 재현성을 먼저 검사한다. pose만 같고 contact/velocity/controller 상태가 다르면 같은 grasp라고 주장하지 않는다.
- full-state 분기를 신뢰할 수 없으면 같은 recipe로 새로 집는 matched reset 설계로 바꾸고 실제 post-grasp state 차이를 기록한다.
- route순서를 섞고 grasp 실패를 제외한 조건부 carry 성공률과 시작부터의 전체 성공률을 모두 낸다.
- 주행에 따른 차이가 없으면 그 결과를 보고한다. 비현실적 마찰·질량·급가속으로 차이를 만들어내지 않는다. 그 경우 base 도착 오차/시야가 grasp에 미치는 영향으로 연구 범위를 재검토한다.

### S3 · LLM/VLM feedback와 route-aware 확인 비교

모든 방법에서 executor checkpoint, 허용된 regrasp skill, 기본 route/controller, 최대 재시도·시간을 동일하게 둔다.
간단한 risk classifier를 위한 별도 개발 데이터 초안은 train recipe 50개 × 4 route = 200 continuation, calibration recipe 15개 × 4 route = 60 continuation이다.
이 수가 충분하다고 가정하지 않고 learning curve와 calibration 오차로 판단한다. 성공만 모으지 않고 자연적으로 발생한 미끄러짐·가림·실패와 불확실한 경우를 포함한다.
시점 변경이 유용한지 학습하려면 학습용 recipe에서 probe/no-probe를 무작위 배정한 소규모 자료를 추가한다. 첫 selector는 명시한 규칙으로 구현하고, 정보 가치 학습은 해당 자료가 확보된 뒤 비교한다.

| 방법 | 판단 입력 | 확인/복구 방식 |
|---|---|---|
| M0 | 고정 phase 규칙 | VLA 집기 뒤 고정 hold하고 운반 |
| M1 | VLM 관측·실행 이력 | 성공/불명/실패에 따라 정해진 복구, route 입력 없음 |
| M2 | M1 + 예정 route | 수동 관측으로 risk 판단, 추가 시점 변경 없음 |
| M3 | M2 + 확인 행동 선택 | risk와 비용을 보고 재관측 후 운반 또는 동일한 regrasp skill 선택 |

필수 진단군: (a) 항상 느린 운반, (b) 같은 확인 동작·대기 후 새 관측을 selector에 전달하지 않는 sham, (c) 같은 횟수의 고정 확인.
필요하면 (d) route 입력 제거/셔플, (e) feedback용 wrist/belly view 제거를 추가한다. executor 카메라 계약은 이 ablation에서 유지한다.
M3가 더 많은 모델 호출만 해서 이기지 않도록 질의·추가시간 budget을 맞춘 결과와 실제 사용량을 함께 보고한다.

본 실험은 예를 들어 새 reset block 30개 × 4방법 = **120 episodes**로 시작할 수 있다. 기존 PDF의 60×4=240도 후보지만, pilot의 분산·처리량·검출할 효과 크기를 보고 본 실험 전에 n을 동결한다.
여기서 block은 독립 reset recipe와 특정 route의 조합이다. 120은 4 route 각각에서 120회라는 뜻이 아니다. route를 균형 배정하고 전체 효과와 route별 탐색 결과의 불확실성을 구분한다.
pilot을 본 실험의 held-out test로 재사용하지 않는다. block을 분석 단위로 짝지은 차이와 신뢰구간을 낸다.

### S4 · WAM 확장 하나를 실행한다

우선 후보는 NVIDIA Cosmos 3 Edge다. 먼저 작은 데이터 batch로 load→forward/backward→video/action 출력→rollout을 확인한다.
가능하면 S1에서 확보한 동일 task demonstration으로 LoRA/새 action module을 적응시키고 동일 held-out scene에서 평가한다.
SO-101 전용 WAM 적응이 더 현실적이면 FLUX 3 Action으로 이 슬롯을 교체한다. 두 경로의 대규모 학습을 동시에 벌이지 않는다.

- 비교 질문: WAM을 executor로 바꾸었을 때 초기 grasp·carry와 추가 확인 필요 횟수가 달라지는가?
- WAM 교체 효과를 볼 때 M0/M3를 각각 적용하는 2×2 비교를 수행한다. executor와 selector를 동시에 바꾸고 원인을 한쪽에 돌리지 않는다.
- 생성된 미래 영상은 실제 미래 영상과 따로 보관한다. 영상 유사도와 물체 유지/낙하 같은 실제 task outcome을 별도로 평가한다.
- route-conditioned counterfactual world model을 학습하려면 base action까지 포함한 별도 데이터/contract가 필요하다. 기존 tabletop WAM이 이를 이미 지원한다고 쓰지 않는다.

시간이 부족하면 S0–S3를 완결한다. WAM 미실행을 실제 수행 결과로 채우지 않는다.

## 평가와 데이터

주 지표는 출발부터의 pick-carry-place 완료율이다. 함께 보고할 값은 초기 grasp 성공률, 성공 grasp 중 운반 유지율, 승인 후 낙하율, 승인 coverage, 전체 낙하율, robot tip 수, 재파지 횟수, 완료시간, 질의 수, GPU 시간이다.
거절만 하는 시스템이 안전해 보이지 않도록 정해진 task deadline/최대 재시도 안의 완료율을 반드시 포함한다.
낙하·robot tip·관측 가림·정책 오류·인프라 timeout을 각각 기록한다. 첫 원인과 최종 outcome을 같이 남긴다.
train/calibration/test는 recipe·물체 family·branch family 단위로 분리한다. 인접 프레임을 나눠 test로 만들지 않는다.
각 비율의 분모와 CI를 제시한다. 20회 pilot을 일반화 성능의 확정 근거로 사용하지 않는다.

필수 로그: run/trial/parent-reset ID, commit/asset/config/checkpoint revision, seed, engine와 physics 설정, camera calibration, unit map, simulator time, client monotonic timestamps, request/task generation, 실제 실행 action, 예정 route, 판정 입력 frame ID, 점수/skill, 실제 outcome, 모델 호출 비용.
contact/mass/friction 등 특권 label 필드는 정책 observation과 물리적으로 분리해 저장한다.

## cloud-only 구성과 sim-to-real

RunPod의 x86 Linux에서 시뮬레이터·GPU 정책·학습을 실행한다. Mac/UTM은 편집, 원격 접속, 모니터링, 기록 회수와 Git 동기화에 사용한다.
첫 cloud 설정은 **48 GB급 GPU 1대가 후보**이며 구매·대여가 실행된 상태가 아니다. G0.5+VLM+렌더의 동시 메모리/지연을 먼저 측정하고 필요한 경우 서비스를 시간 분리한다.
RoboJev 오프라인 평가는 별도 80 GB 세션 후보로 분리한다. DreamZero multi-GPU는 핵심 일정 밖이다.
처음에는 simulator와 policy를 같은 cloud host에서 연결해 기능을 확인한다. 그 지연을 실제 실물–cloud WAN 지연이라고 부르지 않는다.
추후 기록한 WAN trace 또는 선언한 지연/손실 조건을 넣어 관측 age, tail latency, stale action, timeouts와 성공률을 측정한다.
모델 버전마다 원격 contract가 다르므로 모든 정책에 `lerobot-policy-server` 한 옵션만 붙이면 된다고 가정하지 않는다. 기능 검증은 같은 cloud host의 synchronous 실행으로도 가능하다.
공식 [remote inference](https://huggingface.co/docs/lerobot/v0.7.0/remote_inference)와 [지원 상태 표](https://github.com/huggingface/lerobot/blob/main/src/lerobot/remote_inference/README.md)를 배포 revision에 맞춰 다시 확인한다.
Gazebo의 [headless EGL/OGRE2](https://gazebosim.org/api/sim/8/headless_rendering.html)는 실제 RGB frame 수신으로 확인한다.

1차 sim-to-real은 정지 집기, 다음은 빈 base 주행, 그 뒤 가벼운 물체의 느린 carry다.
joint zero/sign/units, 실물 모터 전압·제한, 카메라/TCP, 질량/무게중심, 접촉과 통신 지연을 계측한다.
미지 물체 질량을 정책에 알려주는 편법 대신 허용 물체 범위/보수적 제한을 선언한다.
zero-shot, calibration-only, 실제 추가 데이터 적응 결과를 별도 보고한다. 실물 성공은 실제 촬영·로그가 생긴 뒤에만 주장한다.
저수준 모터 루프와 통신두절 정지는 실물 실행측에서 유지한다.

## 8주 목표와 첫 작업

| 기간 | 목표 | 다음 단계 판단 자료 |
|---|---|---|
| 1주 | G0.5 SO-101 연결, 자유 물체 시도, reset 20회 | 입력/action 검증표, 성공·실패 원본 영상과 CSV |
| 2주 | 80 continuation route pilot | 주행별 낙하/유지와 분기 재현성, 연구 질문 유지/수정 |
| 3주 | VLM feedback, 간단한 risk 분류기, split/calibration 동결 | 혼동행렬·coverage와 실행시간 |
| 4주 | M0–M3와 sham/보수 baseline 소규모 dry run | 시간/질의 예산 매칭, 본 실험 n 사전 결정 |
| 5주 | 새 held-out main evaluation | paired 효과와 CI, 실패 분류 |
| 6주 | Cosmos Edge 또는 FLUX 한 종류의 WAM pilot | 실제 메모리/처리량과 task 결과; 불가 시 main 분석 보강 |
| 7주 | latency·물성·시야 일반화, 가능한 경우 실물 calibration | 현실 차이와 소규모 sim-to-real 탐색 |
| 8주 | 재현 패키지·깔끔한 영상·발표 정리 | 수행/미수행/실패/한계를 구분한 결과표 |

**가장 먼저 할 일은 최신 SO-101 VLA의 공개 입력 추론을 cloud에서 확인하고, 우리 Gazebo의 두 RGB 영상과 관절을 연결하는 것이다.**
첫 milestone은 모델 설치 완료가 아니라, 자유 큐브를 대상으로 실제 action을 실행한 원본 영상·설정·로그 한 묶음이다.
S0의 접촉/렌더 환경이 막히면 원인을 분리하고 NVIDIA의 stock SO-101 환경을 진단용으로 비교할 수 있다. 이때 stock tabletop 결과를 MORA 이동 실험으로 섞지 않는다.

## 산출물 관리

- `runs/` 원본에는 설정, 원본 영상, 관측/실행 로그, 결과 CSV, 모델 호출 원문을 보관한다. 생성 영상은 별도 필드/폴더로 표시한다.
- public에는 검토한 대표 영상, 집계표, config, 재현 명령과 source revision을 공개한다. 계정·토큰·개인 경로·타인 얼굴/화면은 포함하지 않는다.
- 관측 snapshot과 recipe의 해시를 기록해 Mac/Ubuntu/cloud의 작업이 같은 실험을 가리키게 한다.
- GPU 비용은 실제 세션 시간과 서비스별 사용량으로 계산한다. 원래 예산 범위는 제안이며 새 지출이 승인·발생했다는 뜻이 아니다.

실행 파라미터 초안: [protocol_v2.yaml](protocol_v2.yaml). 원래 계획: [2026-11-12 PDF](R4_Research_Plan_20261112.pdf).
