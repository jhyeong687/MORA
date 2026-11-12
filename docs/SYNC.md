# Mac과 Ubuntu 사이의 작업 다리

두 환경이 **비공개 작업 저장소**를 origin으로 사용한다. 실험 코드와 정리한 결과를 GitHub에서 교환한다.
공개 소개 저장소는 작업 저장소의 검토된 파일만 내보낸 별도의 history를 가진다.
비공개 origin을 공개 origin으로 바꾸거나 두 repo의 history를 무조건 합치지 않는다.

## 최초 1회

GitHub CLI의 `gh auth login --web --git-protocol https`로 각 환경에서 로그인한다.
인증 파일·비밀번호·token은 다른 OS에 복사하거나 commit하지 않는다.

```bash
gh repo clone OWNER/r4-mobile-manipulation-lab
cd r4-mobile-manipulation-lab
python3 scripts/r4.py doctor
python3 scripts/r4.py verify
```

`OWNER`는 자신의 GitHub 계정으로 바꾼다. 경로는 어느 폴더라도 된다.

## 매번 작업

```bash
python3 scripts/r4.py update
python3 scripts/r4.py new --name turn-pilot --engine gazebo --seed 42
# RunPod에서 실험하고 해당 run 폴더로 결과를 회수
python3 scripts/r4.py verify
python3 scripts/r4.py sync --message "Record turn pilot"
```

`runs/`는 기본적으로 git에 넣지 않는다. 검토한 run만 `evidence/new/`로 옮긴 뒤 sync한다.
sync는 개인정보 검사, manifest 갱신, commit, 현재 branch의 origin push를 수행한다.
다른 OS가 앞서 있으면 push가 거절되며 강제 덮어쓰지 않는다. 작업을 정리하고 update 후 충돌을 직접 검토한다.

## 공개 반영

비공개에서 `python3 scripts/export_public.py --target ../r4-mobile-manipulation`을 실행한다.
허용된 경로만 복사하고 새 binary/media는 검토 목록과 hash가 맞아야 한다.
공개 사본에서 diff·개인정보 검사를 마친 뒤 별도 commit/push한다.
공개용과 비공개용에는 인증정보·개인정보를 모두 넣지 않는다.

새 영상·이미지·CAD를 직접 확인한 뒤 `python3 scripts/r4.py review-media --file evidence/new/FILE --confirm-reviewed`로 hash를 등록한다. 이 명령은 자동으로 개인정보를 지우지 않으며 실제 확인을 대신하지 않는다.
