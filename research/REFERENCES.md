# 참고문헌 / References

확인일 2026-11-12. 우리 실험에서 재현한 결과가 아닌 원문 근거다.

- **[1] [LeRobot v0.7.0: From Terabytes to Prompting Robots](https://huggingface.co/blog/lerobot/lerobot-release-v070)** — 2026-11-05. 릴리스의 지원 범위와 방향.
- **[2] [LeRobot Remote Inference](https://huggingface.co/docs/lerobot/v0.7.0/en/remote_inference)** — stable 0.7 문서. 로컬 제어와 원격 정책 분리, 하드웨어 제약.
- **[3] [RoboJev: An Open Vision-Language Judge for Robot Success Detection](https://arxiv.org/abs/2610.33718)** — 2026-10-24. 원 논문 및 프로젝트.
- **[4] [RoboJev-27B model card](https://huggingface.co/josefchen/RoboJev-27B)** — 80 GB GPU·입력 프로토콜·한계. 프로젝트: https://robo-jev.com/
- **[5] [CheckVLA: Execution-Time Verification with Action-Conditioned World Model for Long-Horizon Mobile Manipulation](https://arxiv.org/abs/2607.26789)** — 2026-07-29. 가장 가까운 action-conditioned mobile verification 연구.
- **[6] [DreamTrajectory: Trajectory-Guided Action Generation with World Model Alignment for Mobile Manipulation](https://arxiv.org/abs/2608.01381)** — 2026-08, v2 08-25. 궤적 조건의 base-arm 행동과 미래 예측.
- **[7] [VeriVLA: Adaptive Test-Time Verification for Flow-Based VLAs with Latent World Models](https://arxiv.org/abs/2610.21985)** — 2026-10-15. 불확실성 trigger와 latent 행동 평가.
- **[8] [Robot Planning and Situation Handling with Active Perception (VAP-TAMP)](https://arxiv.org/abs/2604.26988)** — 2026-04-28. 능동 관찰·실패 대응·이동 조작.
- **[9] [Visibility-Aware Mobile Grasping in Dynamic Environments](https://visibility-aware-mobile-grasping.github.io/)** — 프로젝트 원문. 시야·base-arm·환경 관측을 함께 다룸.
- **[10] [Keep it Upright: Model Predictive Control for Nonprehensile Object Transportation with Obstacle Avoidance on a Mobile Manipulator](https://arxiv.org/abs/2305.17484)** — 2023. 이동 운반·물리 제약의 선행연구.
- **[11] [Robust Nonprehensile Object Transportation with Uncertain Inertial Parameters](https://arxiv.org/abs/2411.07079)** — 2025, RA-L. 미지 관성·물성 아래 강건 운반.
- **[12] [FLUX 3 Action SO-101 model card](https://huggingface.co/black-forest-labs/flux-3-action-so101)** — 가중치·action contract·보정·access 조건.
- **[13] [LeRobot FLUX 3 Action integration](https://huggingface.co/docs/lerobot/main/flux3)** — main 문서. SO-101 데이터·LoRA·history 설정. stable과 구분.
- **[14] [Black Forest Labs: Run FLUX 3 Action](https://docs.bfl.ai/flux_3/flux3_action_inference)** — 공식 실행 환경·메모리 사례. 학습 사양으로 읽지 않음.
- **[15] [LaWAM: Latent World Action Models for Efficient Dynamics-Aware Robot Policies](https://arxiv.org/abs/2606.15768)** — 2026-06, v2 10-25. latent 미래 조건 정책.
- **[16] [LeRobot LaWAM integration](https://huggingface.co/docs/lerobot/main/en/lawam)** — main 문서. action/state·camera·LIBERO recipe.
- **[17] [NVIDIA DreamZero official repository](https://github.com/dreamzero0/dreamzero)** — 공식 quick start·최소 2 GPU distributed 추론·embodiment 적응.
- **[18] [FoundationPose official project and demonstration](https://nvlabs.github.io/FoundationPose/)** — CVPR 2024. 6D object pose. demo: github.com/NVlabs/FoundationPose/blob/main/run_demo.py
- **[19] [cuRobo official repository](https://github.com/NVlabs/curobo)** — 현재 V2 rewrite 및 v1 API 구분, CUDA 기반 motion generation.
- **[20] [Ai2 MolmoAct2-SO100_101 model card](https://huggingface.co/allenai/MolmoAct2-SO100_101)** — SO용 공개 checkpoint·absolute joint-pose·normalization.
- **[21] [Ai2 MolmoAct2 official repository](https://github.com/allenai/molmoact2)** — 배포·LeRobot branch·카메라·관절 보정의 구현 근거.
- **[22] [LeRobot asynchronous inference implementation reference](https://github.com/huggingface/lerobot/blob/main/src/lerobot/remote_inference/README.md)** — main 소스의 policy support table. MolmoAct2/FLUX 원격 지원 상태 구분.
- **[23] [How Visible Are Silent Manipulation Failures? An Observability Study of False-Success Detection in Simulated Robot Episodes](https://arxiv.org/abs/2606.03134)** — 2026-06-02. noiseless proprioception과 평가 누출 주의의 근거.
- **[24] [RunPod GPU Cloud Pricing](https://www.runpod.io/pricing)** — 2026-11-09 갱신 표시. 2026-11-12 조회 가격으로 예산 산출.
- **[25] [HomeBody: A Humanoid That Explores, Remembers, and Acts on Its Own](https://tml.stanford.edu/homebody/)** — 2026-09. 공간 기억과 VLM의 skill 호출 참고. 우리 플랫폼 재현 아님.
- **[26] [Gazebo Sim 8: Headless Rendering](https://gazebosim.org/api/sim/8/headless_rendering.html)** — 공식 Harmonic API 문서. OGRE2·EGL의 서버 측 RGB 렌더.
- **[27] [Gazebo Harmonic installation and supported platforms](https://gazebosim.org/docs/harmonic/install/)** — Ubuntu 24.04 amd64와 Harmonic 라이브러리 구성.
- **[28] [RunPod storage options](https://docs.runpod.io/pods/storage/types)** — container disk와 지속 volume의 생존 범위 차이.
- **[29] [RunPod: Connect to a Pod with SSH](https://docs.runpod.io/pods/configuration/use-ssh)** — 접속·file transfer 방식의 차이.
