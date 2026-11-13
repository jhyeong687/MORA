# 원문 근거 · 2026-11-13

확인 범위는 targeted primary-source review이며 선행연구의 완전한 목록이나 최초성 증명이 아니다.
아래의 method/실험은 저자가 보고한 결과다. MORA에서 재현된 결과가 아니다.

- **[R01] [On Agentic Manipulation Policies / AMP1](https://arxiv.org/html/2611.09892v1)** - 2026-11-06, arXiv. §§2D.2, 4A: 직접 행동·보조 루틴·관측 인터페이스 비교. 본문 확인.

- **[R02] [TAMPAgent: Agentic Belief-Space Planning for Mobile Manipulation](https://arxiv.org/html/2611.03584v1)** - 2026-11-02, arXiv. §3, §7: 관측·행동 계획과 belief, 보정되지 않은 비용 판단의 한계. 본문 확인.

- **[R03] [DiMuRe: Diagnosis-Guided Multilevel Recovery](https://arxiv.org/html/2611.04226v1)** - 2026-11-03, arXiv. §IV, Appendix A: 단계별 진단·제한된 복구·완료 검증. 본문 확인.

- **[R04] [CheckVLA: Execution-Time Verification](https://arxiv.org/html/2607.26789v1)** - 2026-07-29, arXiv. §3: 실행 중 action-conditioned 검증·개입. 원문 method/평가 범위 확인.

- **[R05] [VeriVLA: Adaptive Test-Time Verification](https://arxiv.org/html/2610.21985v1)** - 2026-10-15, arXiv. §3: trigger와 latent world-model 후보 순위화. 본문 확인.

- **[R06] [Cracking Mobile Manipulation](https://arxiv.org/html/2610.19600v1)** - 2026-10-14, arXiv. §§5-6: fixed VLA, memory, base/EEF 조정. 본문 확인.

- **[R07] [ProbeAct: Probe-Guided Training-Free Failure Recovery](https://arxiv.org/html/2606.09740v1)** - 2026-06-08, arXiv. §3.3: 물체와 팔의 운동 동기화로 grasp/drop 검증. probe는 hidden-state 추출기.

- **[R08] [Imagine then Verify / ATAP](https://arxiv.org/abs/2609.23504)** - 2026-09-20, arXiv. task affordance를 검증하기 위한 능동 시야 선택. 초록 확인; 세부 성능 재현은 하지 않음.

- **[R09] [GraspCorrect](https://arxiv.org/html/2503.15035v1)** - 2025-03-19, arXiv. §3: VLM 파지 검출·중간 visual goal·교정. 본문 확인; 학회 채택 여부는 확정하지 않음.

- **[R10] [Grasp-MPC](https://research.nvidia.com/labs/lpr/publication/yamada2026graspmpc/)** - ICRA 2026, NVIDIA 공식 publication. visual value와 MPC를 결합한 폐루프 grasp. 프로젝트/초록 확인.

- **[R11] [Task-Oriented Grasp Planning Based on Disturbance Distribution](https://digitalcommons.usf.edu/esb_facpub/4/)** - 2016, Robotics Research chapter. 예상 작업 외란을 고려하는 grasp quality는 기존 개념. 기관 저장소 초록 확인.

- **[R12] [Statistical Stratification and Benchmarking of Robotic Grasping Performance](https://qmro.qmul.ac.uk/xmlui/bitstream/123456789/90711/2/Jamone%20Statistical%20Stratification%20and%20Benchmarking%20of%20Robotic%20Grasping%20Performance%202023%20Accepted.pdf)** - 2023 accepted manuscript. §III: lift/hold 뒤 shaking test. 동적 확인 자체의 선행 사례.

- **[R13] [Claude Fable 5.2 공식 발표](https://www.anthropic.com/claude-fable-and-mythos-5-2)** - 2026-11-09. RoboDojo Sim 64.9%는 Anthropic 내부, 최고 effort 평가. 우리 로봇 성능으로 전용하지 않음.

- **[R14] [Claude Fable 5.2 API 공식 문서](https://platform.claude.com/docs/en/models/fable-5-2/overview)** - 2026-11-13 조회. ID, image/tool 지원, effort, 가격, 지원하지 않는 sampling 설정.

- **[R15] [LeRobot v0.7.0 릴리스](https://huggingface.co/blog/lerobot/lerobot-release-v070)** - 2026-11-05. interactive/external planner, remote inference, WAM 통합.

- **[R16] [G0.5 및 SO-101 체크포인트](https://huggingface.co/docs/lerobot/v0.7.0/g05)** - LeRobot 0.7 문서. 저장 processor/6-joint 계약과 비상업용 라이선스. 초기 VLA 대안.

- **[R17] [FoundationPose 공식 demo](https://github.com/NVlabs/FoundationPose/blob/main/run_demo.py)** - register/track_one에 RGB·depth·intrinsics, 등록 시 mask 사용. 6D object pose와 grasp pose를 구분.

- **[R18] [NVIDIA GraspGenX 공식 구현](https://github.com/NVlabs/GraspGenX)** - 새 gripper에 URDF·swept-volume 설정 필요. SO-101 즉시 호환을 주장하지 않음.

- **[R19] [NVIDIA cuRobo 공식 구현](https://github.com/NVlabs/curobo)** - V2와 v1의 API 차이. motion/IK/collision을 grasp 판정과 분리.

- **[R20] [MegaPose 공식 구현](https://github.com/megapose6d/megapose6d)** - RGB+CAD 경로가 존재하는 depth 없는 구현 대안. 과제별 실제 정밀도 검증 필요.

- **[R21] [RoboJev-27B 모델 카드](https://huggingface.co/josefchen/RoboJev-27B)** - 완료 여부 심판 후보, bf16 80 GB 경로. 사진의 Jev와 동일하다고 식별하지 않음.

- **[R22] [NVIDIA Cosmos 3 / LeRobot 통합](https://huggingface.co/docs/lerobot/v0.7.0/cosmos3)** - video/action 공동 예측과 실제 recipe의 메모리. 4주 핵심 일정 뒤 확장 후보.

- **[R23] [RunPod GPU 가격](https://www.runpod.io/pricing)** - 2026-11-13 조회, 페이지 갱신 11-12. A6000 48 GB $0.69/h 표시; 실제 주문 가격/재고는 별도.

- **[R24] [IEEE Robotics and Automation Letters 공식 scope](https://www.ieee-ras.org/publications/ieee-robotics-and-automation-letters/)** - 혁신적 연구·유의미한 이론 및 응용 결과를 심사. 특정 계획의 채택을 보장하는 규칙은 아님.
