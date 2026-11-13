# MORA · 영상 갤러리

SLAM 지도와 주행, **macOS에서 진행한 설계·전복 안정성 시험**, CAD 애니메이션을 바로 재생한다.

[Ubuntu SLAM](#slam) · [엔코더 비교](#encoder) · [고정 물체 운반](#carry) · **[Mac 설계·전복 시험](#stability)** · [CAD·전체 모음](#cad)

현재 공유 자료의 영상 **16개**를 모았다. 각 플레이어의 ▶ 버튼으로 재생하고 원본 MP4도 받을 수 있다. 큰 영상 4개는 H.264 재생본을 사용하며 새 자막이나 배속은 추가하지 않았다.

## Ubuntu · ROS 2 / Gazebo / RViz

선별 녹화의 중간 생략과 시험 조건은 각 영상 설명을 따른다.

<a id="slam"></a>

### SLAM 지도 작성과 피드백 주행

36.1초 · Gazebo와 RViz의 지도·궤적을 함께 본다. 약 36초 선별본으로 중간 구간이 생략되어 있다.

https://github.com/user-attachments/assets/9e905b3d-3407-4002-bb9c-686936f740d7

[원본 MP4](ubuntu/R4_SLAM_Feedback_36s.mp4)

<a id="encoder"></a>

### 엔코더 기반 주행과 누적 오차

36.1초 · SLAM 피드백 시험과 구분한 엔코더 기반 주행 기록. 약 36초 선별본이며 중간 생략이 있다.

https://github.com/user-attachments/assets/2fc91472-7413-4553-b0c3-a413543a7740

[원본 MP4](ubuntu/R4_Encoder_Drift_36s.mp4)

<a id="carry"></a>

### SLAM waypoint 이동과 고정 물체 운반

50.1초 · 32 mm·10 g 물체를 그리퍼에 fixed joint로 연결한 조건. 시작과 마지막 접근·도착을 선별했다. 접촉 파지 성공을 뜻하지 않는다.

https://github.com/user-attachments/assets/cc5a4715-9705-4967-aacf-9fbe3a0dd602

[원본 MP4](ubuntu/R4_Carry_Fixed_Fixture_50s.mp4)

<a id="arm"></a>

### 팔 관절의 작은 범위 동작

24.0초 · 작은 관절 범위의 동작 확인. 전 작업공간·충돌·실물 부하 검증과 구분한다.

https://github.com/user-attachments/assets/312566cd-1f22-4424-a610-22ef66189f6b

[원본 MP4](ubuntu/R4_Arm_Small_Motion_24s.mp4)

<a id="grasp"></a>

### 부분 상승 뒤 실패한 파지 시도

23.4초 · 일시적으로 물체를 들어 올린 선별 장면. 이후 물체가 낙하했으며 완전한 pick-and-place 성공이 아니다.

https://github.com/user-attachments/assets/9f32ac26-2215-4e06-b8b9-ce71ade58952

[원본 MP4](ubuntu/R4_Partial_Lift_Subsequent_Failure_23s.mp4)

<a id="stability"></a>

## macOS · MuJoCo 설계·전복 안정성 테스트

“터틀봇에 팔을 올린 상태로 주행·제동하면 넘어지는가?”를 확인했던 기존 시험이다. 급정지·회전·경사·단차·보조 지지·라이다·모터 근사를 구분해 본다.

**[57행 시험 결과와 무게중심·출력 검토 보기 →](../docs/STABILITY.md)**

<details open>
<summary>설계·물리 시험 영상 7개</summary>

<a id="drive"></a>

### 평지 주행·급정지·회전

15.0초 · 가정한 물성·모터 근사에서 수행한 주행 시험. 실물 운용 한계로 일반화하지 않는다.

https://github.com/user-attachments/assets/636ecd89-ff41-4040-94a9-424342eaef85

[원본 MP4](mujoco/presentation/03_평지_주행_급정지_회전.mp4)

<a id="payload"></a>

### 100 g 팔 동작과 경사면 제동

21.8초 · 100 g payload는 그리퍼 body에 부착한 조건이다. 자유 접촉 파지 시험이 아니다.

https://github.com/user-attachments/assets/24ee1e07-c61e-444a-b8b7-eda69b182a66

[원본 MP4](mujoco/presentation/04_100g_팔작업과_경사면_제동.mp4)

<a id="steps"></a>

### 오르는 턱과 내려가는 단차

19.0초 · 단차 조건에 따른 정지·전도 가능성을 관찰한 시뮬레이션.

https://github.com/user-attachments/assets/26352c2f-a8b0-4174-8f21-9d62c5ba5202

[원본 MP4](mujoco/presentation/05_오르는_턱과_내려가는_단차.mp4)

<a id="support"></a>

### 보조 강구 접촉 조건 비교

9.0초 · 왼쪽은 정상 접촉, 오른쪽은 접촉 해제 조건. 두 조건을 구분해 본다.

https://github.com/user-attachments/assets/a11f809b-dec7-43c9-b98f-817f401eb122

[원본 MP4](mujoco/presentation/07_보조강구_왼쪽_정상_오른쪽_접촉해제.mp4)

<a id="lidar"></a>

### 라이다 시야와 가림

13.0초 · 라이다와 구조물의 배치를 검토하는 시각화. 이 장면 자체는 SLAM 성능 검증이 아니다.

https://github.com/user-attachments/assets/88f0e9aa-1f8d-4020-b737-e4e19397861f

[원본 MP4](mujoco/presentation/06_라이다_시야와_가림.mp4)

<a id="motor"></a>

### 모터 토크 제한과 시간 간격 교차검증

12.6초 · 모터 토크의 근사 제한과 수치 시간 간격 조건을 비교한 기록.

https://github.com/user-attachments/assets/7766af5d-58a6-40d2-a822-72dca3d8a7d4

[원본 MP4](mujoco/presentation/08_모터_토크제한과_시간간격_교차검증.mp4)

<a id="tip"></a>

### 80 mm 하강 단차의 전도

8.0초 · 8 cm 하강 단차에서 전도가 관측된 시뮬레이션. 물리 모델의 가정과 시간 간격 검증 범위는 검증 문서에 기록했다.

https://github.com/user-attachments/assets/a3e8268b-6383-4e0e-ad34-fb09c7dd1501

[원본 MP4](mujoco/edge_80mm_tip.mp4)

</details>

<a id="cad"></a>

## CAD 애니메이션과 전체 모음

<details>
<summary>로봇 전용·조립·체결부·발표 모음 4개 펼치기</summary>

<a id="fusion"></a>

### 로봇만 보이는 CAD 애니메이션

27.0초 · 설계 형상과 조립 동작을 보여주는 시각화. 물리 검증 영상과 구분한다.

https://github.com/user-attachments/assets/f1a39649-3adb-438b-8176-429ac38505c2

[원본 MP4](fusion/R4_Robot_Only.mp4)

<a id="assembly"></a>

### 설계 조립과 전체 동작

27.0초 · 조립 형상과 동작 시각화 구간. 물리적 안정성을 입증하는 시험과 구분한다.

https://github.com/user-attachments/assets/8f76428a-4609-4059-a661-8d43e5cb1c40

[원본 MP4](mujoco/presentation/01_설계_조립과_전체동작.mp4)

<a id="mount"></a>

### 체결부·카메라·보조 강구

23.0초 · 장착부와 카메라, 보조 지지 구조를 살펴보는 설계 시각화.

https://github.com/user-attachments/assets/d9fc3aad-55f3-4f26-99cf-d83d06cd3105

[원본 MP4](mujoco/presentation/02_체결부_카메라와_보조강구.mp4)

<a id="overview"></a>

### 전체 발표용 영상

140.4초 · 설계 애니메이션과 물리 시험을 이어 놓은 기존 발표용 모음. 개별 시험 조건은 아래 원본과 검증 문서를 따른다.

https://github.com/user-attachments/assets/8c2bbf45-e404-47fa-b072-9ff24f0fe9c7

[원본 MP4](mujoco/presentation/00_발표_전체.mp4)

</details>

## 기록과 해석

[설계·안정성 기록](../docs/STABILITY.md) · [실험 검증 범위](../docs/EVIDENCE.md) · [Ubuntu 보고서](../docs/ubuntu/R4_Engineering_Handoff.pdf) · [원본·재생본 SHA-256](../metadata/video_gallery.json)

16개는 현재 공유용으로 정리한 영상 전체다. Ubuntu의 수분 길이 녹화 원본·ROS bag 전체는 이 선별 MP4와 별개로 원래 VM에 보관한다. fixed-joint 운반과 접촉 파지, CAD 애니메이션과 물리 시뮬레이션을 같은 성공 결과로 합치지 않는다.
