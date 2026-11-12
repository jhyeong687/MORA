# 공개 / 비공개 사본의 처리

두 저장소 모두 개인 계정·홈 경로·개인 문서 링크와 인증정보를 제외한다.
공개 저장소는 current source·선별한 결과와 검토한 media, 비공개 저장소는 추가로 전체 텍스트 trial 기록·이전 CAD를 보존한다.
기존 PDF는 개인 경로와 주소를 redaction하고 metadata를 정리한 71쪽 사본을 사용한다.
발견된 text 식별자는 치환했고 binary CAD 내부도 알려진 식별자·경로의 압축 해제 후 검사 대상으로 삼았다.
인증 파일·Codex session·브라우저 프로필·기기 credential은 수집하지 않았다.

`metadata/reviewed_binary.json`은 검토 시점의 파일 hash다. 새 이미지·영상·CAD는 내용 확인 후에만 목록을 갱신한다.
자동 text 검사는 그림 속 글씨나 CAD의 모든 독자 형식 정보를 보장하지 않는다.
공개 export는 allowlist와 검토 hash를 함께 확인하고 자동 push를 하지 않는다.

정리된 source의 경로 변경은 재현 편의를 위한 것으로 동역학 결과를 새로 실행한 것은 아니다.
원본 기록은 로컬에 남기고, 이 저장소의 hash는 공개·작업 사본의 현재 bytes를 검증한다.
