# MORA 최종 연구계획 · 2026-11-13

상태: 계획 확정안 / 신규성·효과는 실험 전 가설. 유료 실행 없음.
사용자 조건: 실물 약 2주 뒤, 1개월 내 제출 목표, local GPU 없음.

이 문서는 기존 8주 실행안의 우선순위와 일정을 대체한다. 기존 문서는 이력으로 보존한다.

## 신규성 판정과 최종 연구 방향

2026-11-13 기준 원문 조사 · 기존 8주안의 범위를 4주로 재설정

현재 사진의 모듈 조합만으로 국제 본논문에 충분한 신규성이 있다고 보기 어렵다. 연구 기여를 “운반 직전, 예정된 주행에 맞춰 어떤 확인 행동을 할 것인가”로 좁히고 실험으로 입증한다.

**가제:** Before the Turn: Route-Conditioned Active Grasp Verification for Mobile Manipulation
**한국어:** 회전하기 전에 확인하기 - 주행 조건에 따른 능동 파지 검증

지각·파지 → Fable 피드백 → route-aware 확인 → 실제 재관측 → 운반·재파지·중단

### 4주 안에 만들 논문 기여 후보

① 같은 파지를 다른 route로 운반하는 통제된 평가셋. ② 두 RGB 시점·관절·예정 주행으로 짧은 확인 행동을 선택하는 모듈. ③ 낙하 감소가 새 정보의 활용 때문인지, 대기·저속·물리적 재안착 때문인지 분리하는 실험.

### 목표 수준을 구분한다

이번 한 달의 현실적인 목표는 **재현 코드·결과·한계를 갖춘 투고용 원고**다. 예비 결과 수준이면 워크숍/국내 학술대회 범위로 정리하고, 새로운 방법과 강한 비교·일반화 결과가 확보되면 국제 본논문/RA-L 투고 수준을 검토한다. 채택·게재를 보장하거나 확률로 제시할 근거는 없다. [R24]

사용자 확정 조건: 로컬 GPU 없음, cloud 사용. 실물은 약 2주 뒤 세팅 가능. 제출 목표 약 한 달. 제안 일정 2026-11-13~12-13. 이 문서의 수치·방법·일정은 계획이며 실험 결과가 아니다.

## 가까운 최신 연구와 겹치는 부분

최근 논문의 명시된 기여와 우리 계획의 차이를 비교했다. “찾지 못했다”는 것이 최초성의 증명은 아니다. 아래 arXiv 원고는 별도 확인한 경우 외에는 동료심사를 통과한 논문이라고 표현하지 않는다.

| 선행연구 | 이미 해결하려는 내용 | 우리 주장에 주는 제약 |
| --- | --- | --- |
| AMP1 [R01] | 직접 조작·재관측·재시도, 여러 robot의 agentic harness | 일반 agent 조합이 신규하다는 주장은 포기. 같은 Fable와 도구로 passive/active를 비교. |
| TAMPAgent [R02] | belief 아래 관측·조작 행동을 교차 계획 | 한 단계의 운반 전 확인 선택과 비용을 좁혀 평가. 범용 belief planning 최초 주장 금지. |
| DiMuRe [R03] | 증거·전제조건으로 재사용/복구/재계획 결정 | 실패 후 복구 자체 대신 출발 전 route-specific 증거 획득을 분리. |
| CheckVLA [R04] | 현재 실행 중 action-conditioned mismatch와 suffix repair | 예정된 base route에 대해 사전 진단 행동을 고르는 문제로 제한. 전체 CheckVLA 재현이라고 부르지 않음. |
| VeriVLA [R05] | 선택적 검증과 latent world-model 행동 후보 평가 | VLA noise 후보 대신 현실에서 수행할 확인 행동의 결과·비용을 다룸. adaptive verification 자체는 기존. |
| Cracking Mobile Manipulation [R06] | fixed VLA 위 memory·base 조정·EEF 교정 | base가 있다는 것과 재시도만으로는 차별화 불가. 운반 중 잔여 낙하 문제에 초점. |

### 심사자가 제기할 가장 강한 반론

“이미 좋은 agent와 verifier가 있는데, robot을 TurtleBot으로 바꾼 시스템 구현 아닌가?”가 핵심 반론이다. 같은 Fable·perception·grasp·주행 controller에서 **확인 행동 선택 규칙만 바꾼 효과**가 필요하다. 최신 모델로 기존 결과를 재현한 것과 새 알고리즘의 효과를 구분한다.

AMP1의 basic/assistive 비교와 TAMPAgent의 belief 계획 때문에, “LLM이 도구를 호출한다”를 주요 기여로 내세우지 않는다. [R01, R02]

## 신규성을 주장할 수 있는 정확한 단위

| 선행 범주 | 중복 요소 | 남길 실험 질문 |
| --- | --- | --- |
| ProbeAct [R07] | grasp/transport/place의 운동 동기화 검증과 복구 | probe는 hidden-state 추출. 물리적 정보 수집 행동과 동일시하지 않되 운동 동기화 baseline은 포함. |
| ATAP [R08] | task affordance 중심 능동 시야 확인 | grasp 전 형상/손잡이 찾기와, grasp 뒤 운반 유지 판단의 차이를 검증. active view 최초 주장 금지. |
| GraspCorrect / Grasp-MPC [R09/R10] | VLM 교정 / visual value를 이용한 폐루프 grasp | 폐루프 grasp 자체는 구현 기반. controller와 판단 모듈을 고정한 비교 필요. |
| Task-wrench / shaking 평가 [R11/R12] | 작업 외란을 고려한 grasp와 동적 안정성 시험 | route 입력이나 흔들기 자체를 발명으로 주장할 수 없음. 정보 활용 효과를 따로 시험. |

### 차별화할 세 가지 가설

**H1:** 같은 post-grasp 조건에서도 다음 route가 다르면 유지 결과와 필요한 증거가 달라진다.
**H2:** 같은 최대 시간·호출 예산에서 route-aware 확인 선택이 route-blind active 확인보다 낫다.
**H3:** 같은 확인 동작 뒤 새 관측을 쓰는 조건이 관측을 숨긴 sham보다 낫다.

### 이번 논문의 범위

첫 과제는 작은 단단한 물체의 정지 집기 → 짧은 실내 운반 → 정지 놓기다. 가변 무게중심 큰 짐, 계단, 사람과의 협업, 주행 중 동시 집기, 범용 집안일은 제외한다. robot 전복은 독립 결과·실행 제약으로 기록한다. 파지 검증이 차체 전복까지 보장하지 않는다.

### 주장이 성립하지 않는 경우

H1의 효과가 없거나 저속 기준이 모든 조건에서 우세하면 route-aware 알고리즘 우월성을 쓰지 않는다. 충분한 도구·route를 받은 Fable보다 낫지 않으면 선택기 효과를 주장하지 않는다. H3가 성립하지 않으면 정보 효과 대신 물리적 안정화로 설명한다. 효과가 약하면 관측 한계·실패 분석 원고로 전환한다.

## 사진의 모듈 구조와 센서 조건

사진의 추천 구조는 유지한다. 단, FoundationPose는 **물체의 6D 위치·자세**를 추정하는 모듈이며 파지 후보 생성기는 별도다. [R17]

| 단계 | 실행안 | 준비되지 않은 조건 |
| --- | --- | --- |
| 물체 pose | RGB+CAD 경로를 먼저 점검. depth가 있으면 FoundationPose 비교. | 지금 카메라 2대는 RGB로 취급. stereo 보정·depth를 자동 가정하지 않음. |
| grasp 후보 | 알려진 소형 물체의 제한된 후보로 시작. GraspGenX가 SO gripper에 맞으면 확장. | GraspGenX에는 URDF·sweep 설정이 필요. 새 gripper의 성공을 보장하지 않음. [R18] |
| 팔 경로 | cuRobo의 IK·collision·trajectory를 SO-101에 맞춤. 첫 성공 버전/revision 동결. | 팔 5축+gripper로 임의 6D pose를 모두 달성할 수 없음. [R19] |
| 피드백 | Fable 5.2가 RGB 이력·측정 state를 보고 구조화된 판정/다음 skill 선택. | 사진의 Jev 제품은 미식별. RoboJev-27B는 별도 completion 비교 후보. [R21] |
| 우리 추가 | route-conditioned 확인 선택, actual observation 재평가, 제한된 재파지. | GT 물체 pose·접촉·질량·마찰을 온라인 판정에 공급하지 않음. |

### RGB와 sim-to-real을 맞추는 방법

실물 depth 구매를 필수로 두지 않는다. 알려진 CAD와 RGB를 쓰는 MegaPose 등의 경로를 검증하거나, RGB 기반 SO VLA를 executor로 사용할 수 있다. [R20] 기하 모듈이 simulator depth를 썼으면 RGB-D 조건으로 명시하고 RGB-only 결과와 섞지 않는다. GT pose를 쓰는 oracle은 진단군으로만 표시한다.

GraspGenX/새 cuRobo 통합에 이틀 이상 막히면 알려진 물체 후보와 이미 동작하는 경로 생성기로 핵심 검증을 진행한다. 이 교체는 비교군 전체에 동일하게 적용하고 방법명이 아니라 실제 구현을 보고한다.

## 제안 방법: 주행에 맞는 확인 행동 선택

**입력 x:** 현재까지의 wrist/belly RGB, 센서로 추정한 object-gripper 상대 운동·가림, gripper 위치, 팔/odom/IMU, 시간.
**입력 r:** 앞으로의 base 속도·가속·회전 방향/곡률과 고정 운반 자세. 정확한 물체 질량/마찰은 입력하지 않는다.

| 확인 후보 q | 실제로 수행하는 동작 | 얻을 수 있는 관측 |
| --- | --- | --- |
| hold | 기준 자세에서 정해진 시간 유지 | 중력 하 미끄러짐, 가림이 해소되는지 |
| view | 차체를 멈춘 채 팔을 작게 재배치하고 운반 자세로 복귀 | belly에서 gripper-object 경계를 더 잘 보도록 함 |
| load | 작은 wrist tilt 또는 제한된 짧은 pulse 뒤 복귀 | 접촉 유지가 약한 경우 상대 운동이 드러나는지 |

wrist 카메라는 집게와 같이 움직이므로, 안정 파지에서 wrist 회전만으로 물체의 새 시야가 생긴다고 가정하지 않는다. view는 belly 시야 개선 여부로 검증한다. 각 동작은 관절/충돌·차체 조건을 확인한 뒤 test 전에 고정한다.

### 작은 모델로 시작할 수 있는 선택 규칙

score(q | x,r) = 예상 확인 후 결정 손실 + 시간 비용 + 모델 호출 비용
carry / 내려놓고 재파지 / 중단도 같은 비용 기준으로 비교한다.

확인 없이 결정할 때의 예상 손실보다 score가 낮은 후보만 수행하고, 확인은 1회로 제한한다. 작은 분류기/회귀기로 risk와 후보 비용을 추정한다. 학습용 recipe에서 q를 무작위 배정하고 실제 후속 관측·운반 결과를 모아 cross-fit으로 선택 점수를 만든다. 대형 world model이나 새 VLA 학습은 필요조건이 아니다.

### LLM과 학습 모듈의 책임

Fable은 관측의 설명·실패/불명 판단과 허용 skill을 제안한다. risk 확률은 별도 calibration에서 보정하며 LLM이 쓴 숫자를 확률 보증으로 쓰지 않는다. 이 선택식은 기존 순차 의사결정 원리를 활용한 **제안 방법**이다. 수식 자체의 최초성 대신 route-specific 이득과 통제 실험으로 기여를 평가한다.

## 데이터와 실험 규모: pilot와 test 분리

| 단계 | 사전 제안 규모 | 해석 |
| --- | --- | --- |
| 초기 smoke | 자유 큐브 20 fresh resets | 물체 attachment 없는 lift/hold, 센서·action 의미 점검. |
| route pilot | 20 독립 grasp 상태 × 4 route = 80 | 초기에는 확인 없이 직진/좌회전/우회전/감속의 효과를 조사. |
| 선택기 개발 | train 60 recipe × 4 route = 240<br/>calibration 24 recipe × 4 route = 96 | q 3종을 무작위 균형 배정. 성공·실패·probe 중 낙하 모두 보관. 작은 데이터의 충분성은 learning curve로 판단. |
| 주 비교 | 새 120 block × 4방법 = 480 | block = 하나의 독립 grasp recipe와 한 route. 4 route를 균형 배정. |
| 필수 진단 | 주 비교 중 40 block × 추가 4조건 = 160 | 고정 확인·새 관측 숨김·항상 저속·선택기 route 제거. ours 결과 재사용. |
| end-to-end | 새 20 recipe × 2방법 = 40 | 초기 grasp 실패까지 분모에 포함. 좁은 운반 benchmark와 구분. |

위 설계의 합은 **1,116 sim 실행**이다. 모델 warmup·snapshot 검증·regrasp 계측은 별도다. throughput·API 사용량을 pilot에서 측정한 뒤, 본 실험 n과 비용을 test 전에 동결한다. 1,116이 검정력 계산으로 확정된 수는 아니다.

### 물체와 상태 분리

train 6 / calibration 3 / test 6개의 별도 object instance를 후보로 둔다. 최소 cuboid·cylinder·비대칭 형상, 그리퍼 폭과 팔 범위 안의 소형 물체를 사용한다. 같은 family의 새 instance와 완전히 새로운 family를 구분한다. 실물 중량/마찰은 나중에 측정한다.

검증된 post-grasp snapshot으로 분기할 수 있으면 contact·velocity·controller 상태까지 복구한다. 재현이 안 되면 같은 recipe의 fresh reset과 post-grasp 차이를 기록한다. 객체를 고정하거나 매 step pose를 덮어써서 성공시키지 않는다.

core benchmark는 유효한 자유 접촉 grasp 이후의 운반 판단을 연구한다. 이를 전체 pick 성공률로 부르지 않는다. main test recipe·물체·인접 frame·분기 결과가 학습/보정으로 새지 않게 분리한다.

## 비교군·통계·논문의 핵심 그림

| 방법 | 판단과 확인 | 왜 필요한가 |
| --- | --- | --- |
| B0 · completion | Fable의 grasp-complete 판단, 수동 RGB 이력. route 입력 없음. | 사진의 기본 피드백 구조. |
| B1 · route passive | B0와 같은 실행기 + route risk, 새 확인 행동 없음. | route 입력만의 효과. |
| B2 · Fable full-context active | Fable에 route·모든 확인 후보·비용·동일 예산을 주고 직접 선택. | 강한 LLM으로 충분하지 않은지. |
| B3 · ours | route-aware 후보 선택 후 실제 관측으로 결정 갱신. | 제안 전체. |

모든 방법은 동일 Fable 설정·perception·grasp·주행 controller, 최대 확인 1회, 재파지 1회, 동일 task deadline을 사용한다. B2/B3는 같은 tool·frame 상한을 갖는다. B2에는 개발 데이터에서 얻은 비용표와 제한된 few-shot 사례도 제공하고 prompt tuning 예산을 기록한다. 원 논문 전체를 이식하지 않은 baseline을 AMP1/CheckVLA의 재현이라고 표기하지 않는다.

### 지표와 효과 크기

주 지표: deadline 안에 **probe 중 낙하까지 포함해** 물체를 유지하고 목표에 놓은 비율. abort/timeout은 완료 실패다. 낙하율, 승인 coverage, 재파지, 실제 시간·호출·비용, body tip을 함께 보고한다. 들기 성공만으로 운반 성공을 판정하지 않는다.

B3-B2를 주 비교로 사전 지정하고 paired difference CI/정확 McNemar를 사용한다. 진단 비교는 탐색 또는 다중 비교 보정을 표시한다. 독립 block 기준 n을 세고 family별 결과도 공개한다. test 물체 6개로 모든 물체에 일반화한다고 주장하지 않는다.

계획용 근사: discordance q=0.35, 검출 차이 15 pp, 양측 α=0.05/power 0.8 가정이면 n ≈ (1.96+0.84)^2×0.35/0.15^2 ≈ 122 paired blocks. 실제 q·cluster와 정확 검정으로 재설계해야 하며 120이 충분하다는 보장은 아니다.

**그림:** 같은 grasp의 route별 결과 / 완료율-시간·호출 Pareto / ours·Fable active·route 제거·sham 비교 / unseen instance와 real의 실패 유형. full 결과표와 성공·실패 대표 영상 원본을 함께 남긴다.

## Fable 5.2·cloud 비용·실행 계약

공식 11월 9일 발표에서 Fable 5.2는 RoboDojo Sim 64.9%를 보고했다. **Anthropic 내부·최고 effort·시뮬레이터 양팔 평가**이며 SO-101/TurtleBot 성능이나 독립 재현 결과가 아니다. [R13]

API ID는 **claude-fable-5-2**. 첫 30개 고정 입력으로 가시성·구조화 출력·tool 선택·지연·실제 token 사용량을 점검한 뒤 effort와 최대 출력/입력 budget을 동결한다. 공식 문서상 adaptive thinking은 항상 켜져 있고 temperature/top_p/top_k 및 강제 tool_choice의 일부 설정을 사용할 수 없다. [R14]

### 공정한 사용과 재현

초기 비교는 같은 Fable로 수행한다. Qwen 등 다른 모델은 자원이 남으면 별도 소규모 모델 의존성 검사로 추가한다. API 호출 시점·반환 model ID·요청/응답·usage를 저장하고, immutable snapshot이 제공되지 않으면 그 한계를 명시한다. frame/control/evaluator 도구를 분리하며 future outcome·mass/friction truth를 요청에 넣지 않는다.

RunPod x86에서 Gazebo/ROS·렌더·cuRobo·가벼운 risk 학습을 실행한다. Fable은 Anthropic cloud API다. Mac/UTM에는 GPU 모델을 올리지 않는다. 큰 WAM 학습과 multi-GPU DreamZero는 이번 4주 핵심 작업에서 제외하고 후속 계획으로 남긴다. LeRobot 0.7의 SO 정책은 대체 executor로 시험 가능하다. [R15, R16, R22]

개발 데이터는 기록한 RGB·측정 feature로 먼저 학습해 모든 frame마다 Fable을 호출하지 않는다. API closed-loop 평가는 wall-paced physics를 계속 진행하고 대기 동안 고정 hold를 유지한다. physics를 멈춘 진단은 별도 모드로 분리한다. 반환이 늦으면 새 요청 ID와 관측 age로 stale 응답을 폐기한다.

| 항목 | 예시 계산 / 제안 | 한계 |
| --- | --- | --- |
| GPU | A6000 48 GB 60 h × $0.69 = $41.40 [R23] | CPU·EGL graphics 접근·성능/재고를 실제 인스턴스에서 확인. |
| Fable API | 1,500 calls, 평균 input 4k/output 500이면 $78<br/>8k/1k이면 $156 [R14] | 출력은 billed thinking까지 포함. 이미지 token과 history가 늘면 초과. |
| 저장·여유 | 약 $20 저장/전송 + $30 작업 여유 가정 | 세금·실물 부품 제외. 제안 총상한 $250. |

가격은 2026-11-13 조회의 예시이며 지출 승인/발생 기록이 아니다. 실측 비용이 상한을 넘으면 test 전 규모/원고 범위를 재설정한다. 이 계획 수립에서는 GPU 대여·유료 API 호출을 실행하지 않았다.

## 4주 일정과 중간 의사결정

| 기간 | 수행할 일 | 완료 증거와 중단/변경 기준 |
| --- | --- | --- |
| 11/13-19 | 기존 cloud x86·RGB·관절 이식. 사진식 grasp pipeline 1회와 feedback 연결. 20 smoke/80 route pilot. | D3: 센서/action 정상, D7: 자유 접촉 grasp와 replay 검증. 막히면 새 프레임워크 이식을 멈추고 기존 실행기를 고정. |
| 11/20-26 | train/calibration 데이터, risk/선택기, B0-B3 구현. sham·slow control. 문서/논문 초안 병행. | D10: 현실적인 route 효과/확인 관측의 추가 정보 여부 판단. D14: model·prompt·n·threshold·split 동결. |
| 11/27-12/03 | 동결한 held-out sim 본 비교. 실물은 조립·보정·정지 grasp부터 병행. | 실험 중 test를 보고 prompt나 threshold 수정 금지. 수정하면 새 split/version으로 구분. |
| 12/04-10 | 필수 진단, E2E 40회, 준비되면 real 60회. 결과·CI·실패 영상·재현 패키지. | D21 실물 core 미완료면 sim 원고의 future work로 정리. D24부터 기능 추가 중단. |
| 12/11-13 | 원고/인용/수치/개인정보/재현 점검. 실제 열려 있는 venue의 규정에 맞춰 제출. | 제출 목표일이지 채택일이 아님. 맞는 공고가 없으면 preprint-ready 원고를 먼저 완성. |

### 우선 구현할 세 산출물

① 공통 observation/action schema와 단일 episode 기록기. ② 고정 grasp/주행 skill에 Fable feedback을 연결한 기본형. ③ 같은 post-grasp 상태를 네 route에 적용한 결과표. 이 셋이 연구 가능성을 판단하는 첫 주 결과다.

### Go / no-go의 원칙

route 효과가 없으면 비현실적인 힘·마찰을 넣어 효과를 만들지 않는다. 확인이 불필요하면 “언제 단순 모델로 충분한가”라는 관측 연구로 좁힌다. 효과가 있어도 baseline보다 낫지 않으면 원인을 보고하고 긍정 결과만 골라내지 않는다.

위 날짜는 사용자 제공 2주/1개월 조건을 현재 날짜에 적용한 제안이다. 특정 학회/워크숍의 접수 기간이 열렸다는 확인을 뜻하지 않는다.

## 실물 전이·투고 판단·주장 한계

### 약 2주 뒤 실물이 준비되면

질량/무게중심·모터 전압/제한, 관절 zero/sign/단위, camera intrinsic/extrinsic/TCP를 측정한다. 정지 grasp → 빈 base 주행 → 가벼운 물체의 짧은 carry 순서로 확인한다. RGB-only와 RGB-D 계약을 유지하며 simulator truth를 driver 입력으로 대체하지 않는다. 로봇의 local controller/통신 timeout 정지는 계속 로봇 측에 둔다.

**real 탐색 제안:** 3개 물체 × 2개 route × 5 reset × 2방법(B2/B3) = 60 episodes. 사전 보정용 episode와 test를 분리한다. 카메라/좌표 보정만 한 경우와 실제 데이터로 risk 모델을 재보정한 경우를 따로 보고한다. 실물 조건은 calibrated hardware 범위 안에서 확정한다.

### 한 달 뒤 결과에 따른 제출 수준 판단

| 확보한 증거 | 주장 가능한 범위 | 현실적인 다음 단계 |
| --- | --- | --- |
| 데모 + 수십 pilot | 구현과 예비 관찰. 알고리즘 우월성/안전성 주장은 약함. | 국내/워크숍용 예비 결과 또는 개발 보고. |
| 통제 sim + 유의미한 paired 효과 + sham/비용/일반화 | route-aware 확인 선택과 평가셋의 기여 후보. | 워크숍/짧은 연구 원고 우선, 국제 본논문은 방법 차별성과 규모를 추가 검토. |
| 위 증거 + 작은 real에서도 방향 일치 + 강한 최신 baseline | 우리 플랫폼에서 전이 가능성을 보여주는 제한된 실증. | ICRA/IROS/RA-L 등 scope 검토 가능. 채택을 보장하지 않음. |

### 논문에서 쓰지 않을 주장

“최초 LLM 이동 조작”, “최초 능동 파지 검증”, “전복/낙하 안전 보장”, “Fable의 benchmark 점수가 우리 성공률”, “생성 영상이 실제 예측 검증”, “고정 부착 운반이 자유 파지 성공”은 쓰지 않는다.

실물이 늦어져도 simulation 연구 자체는 제출할 수 있다. 다만 sim-to-real 성공을 쓰지 않고 대상 venue의 심사 기준에 맞는 새 방법·충분한 통제 결과가 있는지 별도로 판단한다. arXiv 공개와 peer-reviewed 게재는 구분한다.

기존 CAD/Fusion·MuJoCo 안정성·ROS/SLAM 기록은 플랫폼/보충 자료다. 이번 알고리즘의 독립 반복 실험이나 실물 근거로 재계산하지 않는다.

## 원문 근거와 확인 범위 1

제목을 누르면 원문으로 이동 · arXiv 원고와 심사된 출판물을 구분

확인일 2026-11-13. 원 논문·저자 프로젝트·공식 모델/문서를 사용했다. 제안 방법·실험 규모·게재 가능성 평가는 이 자료에 대한 우리의 해석이다.

- [R01] [On Agentic Manipulation Policies / AMP1](https://arxiv.org/html/2611.09892v1) - 2026-11-06, arXiv. §§2D.2, 4A: 직접 행동·보조 루틴·관측 인터페이스 비교. 본문 확인.

- [R02] [TAMPAgent: Agentic Belief-Space Planning for Mobile Manipulation](https://arxiv.org/html/2611.03584v1) - 2026-11-02, arXiv. §3, §7: 관측·행동 계획과 belief, 보정되지 않은 비용 판단의 한계. 본문 확인.

- [R03] [DiMuRe: Diagnosis-Guided Multilevel Recovery](https://arxiv.org/html/2611.04226v1) - 2026-11-03, arXiv. §IV, Appendix A: 단계별 진단·제한된 복구·완료 검증. 본문 확인.

- [R04] [CheckVLA: Execution-Time Verification](https://arxiv.org/html/2607.26789v1) - 2026-07-29, arXiv. §3: 실행 중 action-conditioned 검증·개입. 원문 method/평가 범위 확인.

- [R05] [VeriVLA: Adaptive Test-Time Verification](https://arxiv.org/html/2610.21985v1) - 2026-10-15, arXiv. §3: trigger와 latent world-model 후보 순위화. 본문 확인.

- [R06] [Cracking Mobile Manipulation](https://arxiv.org/html/2610.19600v1) - 2026-10-14, arXiv. §§5-6: fixed VLA, memory, base/EEF 조정. 본문 확인.

- [R07] [ProbeAct: Probe-Guided Training-Free Failure Recovery](https://arxiv.org/html/2606.09740v1) - 2026-06-08, arXiv. §3.3: 물체와 팔의 운동 동기화로 grasp/drop 검증. probe는 hidden-state 추출기.

- [R08] [Imagine then Verify / ATAP](https://arxiv.org/abs/2609.23504) - 2026-09-20, arXiv. task affordance를 검증하기 위한 능동 시야 선택. 초록 확인; 세부 성능 재현은 하지 않음.

- [R09] [GraspCorrect](https://arxiv.org/html/2503.15035v1) - 2025-03-19, arXiv. §3: VLM 파지 검출·중간 visual goal·교정. 본문 확인; 학회 채택 여부는 확정하지 않음.

- [R10] [Grasp-MPC](https://research.nvidia.com/labs/lpr/publication/yamada2026graspmpc/) - ICRA 2026, NVIDIA 공식 publication. visual value와 MPC를 결합한 폐루프 grasp. 프로젝트/초록 확인.

- [R11] [Task-Oriented Grasp Planning Based on Disturbance Distribution](https://digitalcommons.usf.edu/esb_facpub/4/) - 2016, Robotics Research chapter. 예상 작업 외란을 고려하는 grasp quality는 기존 개념. 기관 저장소 초록 확인.

- [R12] [Statistical Stratification and Benchmarking of Robotic Grasping Performance](https://qmro.qmul.ac.uk/xmlui/bitstream/123456789/90711/2/Jamone%20Statistical%20Stratification%20and%20Benchmarking%20of%20Robotic%20Grasping%20Performance%202023%20Accepted.pdf) - 2023 accepted manuscript. §III: lift/hold 뒤 shaking test. 동적 확인 자체의 선행 사례.

## 원문 근거와 확인 범위 2

제목을 누르면 원문으로 이동 · arXiv 원고와 심사된 출판물을 구분

확인일 2026-11-13. 원 논문·저자 프로젝트·공식 모델/문서를 사용했다. 제안 방법·실험 규모·게재 가능성 평가는 이 자료에 대한 우리의 해석이다.

- [R13] [Claude Fable 5.2 공식 발표](https://www.anthropic.com/claude-fable-and-mythos-5-2) - 2026-11-09. RoboDojo Sim 64.9%는 Anthropic 내부, 최고 effort 평가. 우리 로봇 성능으로 전용하지 않음.

- [R14] [Claude Fable 5.2 API 공식 문서](https://platform.claude.com/docs/en/models/fable-5-2/overview) - 2026-11-13 조회. ID, image/tool 지원, effort, 가격, 지원하지 않는 sampling 설정.

- [R15] [LeRobot v0.7.0 릴리스](https://huggingface.co/blog/lerobot/lerobot-release-v070) - 2026-11-05. interactive/external planner, remote inference, WAM 통합.

- [R16] [G0.5 및 SO-101 체크포인트](https://huggingface.co/docs/lerobot/v0.7.0/g05) - LeRobot 0.7 문서. 저장 processor/6-joint 계약과 비상업용 라이선스. 초기 VLA 대안.

- [R17] [FoundationPose 공식 demo](https://github.com/NVlabs/FoundationPose/blob/main/run_demo.py) - register/track_one에 RGB·depth·intrinsics, 등록 시 mask 사용. 6D object pose와 grasp pose를 구분.

- [R18] [NVIDIA GraspGenX 공식 구현](https://github.com/NVlabs/GraspGenX) - 새 gripper에 URDF·swept-volume 설정 필요. SO-101 즉시 호환을 주장하지 않음.

- [R19] [NVIDIA cuRobo 공식 구현](https://github.com/NVlabs/curobo) - V2와 v1의 API 차이. motion/IK/collision을 grasp 판정과 분리.

- [R20] [MegaPose 공식 구현](https://github.com/megapose6d/megapose6d) - RGB+CAD 경로가 존재하는 depth 없는 구현 대안. 과제별 실제 정밀도 검증 필요.

- [R21] [RoboJev-27B 모델 카드](https://huggingface.co/josefchen/RoboJev-27B) - 완료 여부 심판 후보, bf16 80 GB 경로. 사진의 Jev와 동일하다고 식별하지 않음.

- [R22] [NVIDIA Cosmos 3 / LeRobot 통합](https://huggingface.co/docs/lerobot/v0.7.0/cosmos3) - video/action 공동 예측과 실제 recipe의 메모리. 4주 핵심 일정 뒤 확장 후보.

- [R23] [RunPod GPU 가격](https://www.runpod.io/pricing) - 2026-11-13 조회, 페이지 갱신 11-12. A6000 48 GB $0.69/h 표시; 실제 주문 가격/재고는 별도.

- [R24] [IEEE Robotics and Automation Letters 공식 scope](https://www.ieee-ras.org/publications/ieee-robotics-and-automation-letters/) - 혁신적 연구·유의미한 이론 및 응용 결과를 심사. 특정 계획의 채택을 보장하는 규칙은 아님.
