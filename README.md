# openclaw-nutrition-skill

OpenClaw 에이전트에서 사용하는 영양 관리 스킬 명세 저장소입니다.

이 저장소는 **스킬 동작 규칙/레퍼런스 문서 중심**으로 구성되며,
실행용 Python CLI 구현은 포함하지 않습니다.

## 포함 내용

- `SKILL.md`
  - 스킬 메타데이터, 워크플로, 안전 규칙, 실행 정책
- `references/`
  - 데이터 모델/로깅 규칙/개인정보·보안 참고 문서
- `data/*.example.json`
  - 예시 데이터 템플릿

## 설계 원칙

- Chat-first, confirmation-first
- 저장은 append-only 워크플로
- 이미지 분석은 연결된 모델을 통해 수행
- 로컬 Python 스크립트/CLI 실행을 기본 경로로 사용하지 않음

## 라이선스

- MIT License (`LICENSE`)
