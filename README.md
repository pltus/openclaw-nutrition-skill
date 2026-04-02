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


## 검증 스크립트

정책 문서 정합성을 코드로 점검하려면 아래 명령을 실행하세요.

```bash
python scripts/validate_skill_policies.py
```

이 스크립트는 다음을 확인합니다.
- 저장 전 사용자 확인(confirmation-first) 정책이 `SKILL.md`와 `references/logging_rules.md`에 일관되게 반영되었는지
- 네트워크 사용 정책(로컬 기본 + 이미지 분석 시 사전 동의)이 `SKILL.md`와 `references/privacy_security.md`에 반영되었는지

## 라이선스

- MIT License (`LICENSE`)
