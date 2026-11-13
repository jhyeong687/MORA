# MORA 최종 연구계획 · 2026-11-13

**회전하기 전에 확인하기: 주행 조건에 따른 능동 파지 검증**

[12쪽 최종 계획 PDF](MORA_Final_Research_Plan_20261113.pdf) · [전체 본문](FINAL_PLAN_20261113.md) · [현재 protocol](protocol.yaml) · [신규성 대조표](novelty_audit_20261113.json) · [확인한 원문](REFERENCES.md)

사진의 모듈식 구조인 물체 pose 추정 → grasp 후보 → cuRobo 경로 → LLM/VLM 확인·복구를 기반으로 한다.
**연구 기여 후보는 예정된 터틀봇 주행에 맞춘 확인 행동 선택과, 새 관측 정보의 효과를 분리하는 평가다.**
단순 모듈 조합이나 최신 모델 사용만으로 논문 신규성이 확보됐다고 주장하지 않는다.

## 사용자 조건과 일정

- 실물은 약 2주 뒤 준비 가능. 먼저 cloud simulation으로 연구한다.
- 2026-12-13 전후 제출용 원고 완성을 목표로 한 4주 계획이다. 게재·채택 일정이 아니다.
- RunPod에서 simulation·render·risk 학습을, Anthropic cloud API에서 Fable 5.2를 실행하는 구성이 후보다.
- 현재 새 GPU 대여·유료 API 호출·본문의 신규 실험을 수행한 상태는 아니다.

## 핵심 실험

1. 자유 접촉 grasp와 실제 두 RGB·관절·주행 기록을 cloud에서 확인한다.
2. 같은 post-grasp recipe에 네 route를 적용해 주행 효과를 pilot 80회로 조사한다.
3. 같은 Fable·grasp·주행 실행기에서 completion / route passive / Fable full-context active / route-aware selector를 비교한다.
4. 새 관측을 숨긴 sham, 고정 확인, 항상 저속을 추가해 정보·물리 동작·대기 효과를 분리한다.
5. 본 비교 120 block × 4방법은 제안 규모이며, pilot 분산·cluster·비용을 보고 test 전에 동결한다.
6. 실물이 준비되면 별도 calibration 뒤 탐색 60회를 제안한다. 실물 결과가 없으면 sim-to-real 성공을 주장하지 않는다.

## 신규성과 투고 판단

AMP1, TAMPAgent, DiMuRe, CheckVLA, VeriVLA, ProbeAct, ATAP와 대조했다.
작업 외란을 고려한 grasp quality와 shaking test도 기존 개념이다.
차별성은 유효한 가설이며 아직 구현·실험으로 입증되지 않았다.
첫 한 달에는 재현 가능한 좁은 결과와 원고를 목표로 하고, 국제 본논문/RA-L 수준은 새로운 방법과 강한 비교·일반화 증거가 확보된 뒤 판단한다.

## 이전 계획 이력

- [2026-11-12 원래 20쪽 PDF](R4_Research_Plan_20261112.pdf) · [원래 protocol](protocol_20261112.yaml)
- [초기 8주 실행 개정안](EXECUTION_PLAN_20261113.md) · [protocol v2](protocol_v2.yaml)

위 이력의 일정·모델 우선순위보다 **현재 4주 최종 계획과 protocol v3**를 우선한다.
원본 CAD·Fusion·MuJoCo·ROS 증거는 플랫폼 자료이며 이번 신규 연구의 반복 실험 결과가 아니다.
