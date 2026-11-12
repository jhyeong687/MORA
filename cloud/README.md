# RunPod에서 실행

## MuJoCo 재현

GPU가 있는 cloud Linux node의 CPU가 MuJoCo 물리를 수행한다. 카메라 렌더·학습·추론은 GPU를 쓸 수 있지만
GPU 종류만으로 물리 계산이 빨라진다고 가정하지 않는다.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-mujoco.txt
.venv/bin/python scripts/run_mujoco.py --list
R4_CLOUD=1 .venv/bin/python scripts/run_mujoco.py --case flat_drive --out runs/cloud-flat-001
```

run 폴더는 새 폴더여야 한다. 기존 결과를 덮어쓰지 않는다.
이 wrapper는 모터·물리 시험이며 자유 물체 VLA 파지 성공 benchmark가 아니다.

## Gazebo / ROS

Ubuntu 24.04 amd64 + ROS 2 Jazzy + Gazebo Harmonic/DART를 고정하고 필요한 ROS/SLAM package를 설치한다.
`simulation/gazebo/r4_lab/start_slam --headless`는 기존 launch와 plugin 빌드 경로다.
현재 VM에서 가져온 소스이며 cloud 컨테이너에서의 빌드·EGL·RGB 검증은 후속 실행 gate다.
`nvidia-smi` 성공만으로 카메라를 검증하지 않는다. headless OGRE2/EGL과 실제 RGB 두 topic을 확인한다.
ARM plugin binary는 사용하지 않고 재빌드한다. current generated 파일은 실행 시 다시 생성한다.

물리·ROS 성능은 sim clock, end-to-end inference는 client monotonic wall clock으로 측정한다.
cloud 내부 통신을 실제 로봇 WAN 지연으로 보고하지 않는다.

## 결과 회수

RunPod의 public-IP/full SSH는 SCP/SFTP가 가능하고 basic SSH proxy는 해당 전송을 지원하지 않는다.
사용할 target과 port는 Pod Connect 화면에서 확인한다. 계정·주소·key는 `.r4-local/` 같은 ignored 설정에 둔다.
결과를 지속 volume에 저장하고 내려받은 hash를 확인한 뒤 Pod를 중지한다.

공식 근거: https://gazebosim.org/api/sim/8/headless_rendering.html 와 https://docs.runpod.io/pods/configuration/use-ssh
