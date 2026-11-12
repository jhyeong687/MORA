# CAD와 애니메이션 열기

| 파일 | 용도 |
| --- | --- |
| `cad/R4/TurtleBot3_SO101_R4_Final.f3d` | 최종 조립 원본 |
| `cad/R4/TurtleBot3_SO101_R4_Animated.f3d` | Animation 컨테이너가 포함된 Fusion 원본 |
| `cad/R4/PRINT_R4_Mount.step` | CAD 교환용 장착 구조 |
| `cad/R4/STL/` | 12종 출력 파트 |
| `cad/R4/출력_구매_조립표.html` | 수량·체결·네이버 구매 검색 링크 |
| `cad/R4/R4_3D_Playback.html` | 브라우저 3D 재생 |
| `cad/R4/Fusion/R4Playback/` | Fusion 안에서 HTML 재생 창을 여는 스크립트 |
| `media/fusion/R4_Robot_Only.mp4` | 글씨 없는 로봇 영상 |

Fusion에서 File → Open → Open from my computer로 `.f3d`를 연다.
Animated 파일의 native Animation 작업공간과 HTML palette 재생은 서로 다른 기능이다.
두 종류를 모두 보존했으며, 조립 애니메이션은 동역학 검증 영상이 아니다.
STL/STEP와 F3D의 내부 파일 구조를 검사했고, 애니메이션 원본에 Animation segment가 있음을 확인했다.
실물 체결·카메라 외형·전압·질량을 실측한 설계 인증은 아니다.
R1/R2/R3는 이전 버전이며 R4 파트와 혼합하지 않는다. 이전 버전 전체는 비공개 작업 저장소에 보존한다.
