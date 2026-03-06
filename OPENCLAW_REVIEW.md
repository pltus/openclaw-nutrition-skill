# OpenClaw Nutrition Skill 최신 정합성 리뷰 (2026-03)

기준 문서:
- `SKILL.md`
- `README.md`
- `references/logging_rules.md`
- `references/privacy_security.md`
- `references/data_model.md`

## 한줄 결론
- 현재 저장소는 **문서 중심 스킬 저장소**라는 점에서 최신 OpenClaw의 스킬 운영 방식과 잘 맞습니다.
- 다만 문서 간 정책 문구가 일부 엇갈려, 실제 에이전트 적용 시 혼선이 생길 수 있습니다.

---

## 1) 잘 맞는 점 (Pass)

1. **문서 중심 구조**
   - `README.md`에서 실행용 CLI가 아닌 스킬 명세 저장소임을 명시하고 있습니다.
   - 최신 OpenClaw의 chat-first 스킬 배포/운영 방식과 일치합니다.

2. **확인 후 저장(confirmation-first) 원칙**
   - `SKILL.md` 워크플로에서 저장 전 사용자 확인을 명시합니다.
   - append-only 규칙과 함께 데이터 무결성 측면에서 적절합니다.

3. **append-only 원칙**
   - `references/logging_rules.md`에서 기존 라인 수정 금지 및 정정은 새 엔트리 추가로 정의되어 있습니다.

4. **민감정보/보안 가이드 포함**
   - `references/privacy_security.md`에서 비밀정보 저장 금지, 외부 액션의 명시적 확인 필요를 명시합니다.

---

## 2) 오류/불일치 (Fix Needed)

1. **리뷰 문서 자체가 현재 저장소 상태와 불일치 (중요)**
   - 기존 리뷰가 `oc_nutrition/*`, CLI 명령(`log-image`, `export-week`) 등 **현재 저장소에 없는 구현**을 전제로 작성되어 있습니다.
   - 이 문서는 현행 기준에서 오해를 만들 수 있어 교체/정정이 필요합니다.

2. **확인(Confirm) 기준 문구 불일치**
   - `SKILL.md`: 저장 전에는 항상 explicit confirmation 필요.
   - `references/logging_rules.md` 5번: 매크로 추정이 불확실할 때 확인.
   - 결과적으로 “항상 확인”인지 “조건부 확인”인지 해석 충돌이 있습니다.

3. **네트워크 정책 문구의 맥락 부족**
   - `SKILL.md`는 이미지 입력 시 연결된 멀티모달 모델(온라인 분석) 사용을 안내합니다.
   - `references/privacy_security.md`는 “로깅/요약에 네트워크 불필요”라고 표현합니다.
   - 예외(이미지 분석)를 문서에 명시적으로 연결하지 않으면 정책 충돌처럼 보일 수 있습니다.

---

## 3) 개선 제안 (우선순위)

### P1 (즉시 권장)
1. **정책 우선순위 단일화**
   - “저장 전 확인은 항상 필수”로 통일하거나,
   - “조건부 확인”으로 바꿀 경우 조건을 `SKILL.md`와 `references/*`에 동일하게 반영.

2. **네트워크 예외 규칙 명문화**
   - `privacy_security.md`에 “이미지 분석은 사용자 사전 동의 시에만 예외적으로 네트워크 사용”을 명시.

3. **리뷰 문서 최신화 유지**
   - 구현 코드가 없는 저장소라는 현재 상태를 기준으로 리뷰를 유지하고,
   - 과거 CLI 기반 점검 항목은 별도 아카이브로 분리.

### P2
4. **운영 체크리스트 추가**
   - OpenClaw 에이전트 적용 시 체크할 최소 항목(질문 2개 제한, 저장 전 확인, append-only, 동의 후 네트워크)을 한 페이지 체크리스트로 추가.

5. **입력/출력 계약(Contract) 명확화**
   - `SKILL.md`의 입력 예시와 `references/data_model.md` 필드를 1:1로 매핑한 표를 추가해 구현체 간 해석 차이를 줄임.

---

## 4) 권장 수정안 (문서 레벨)

- `references/logging_rules.md` 5번을 아래처럼 조정:
  - 기존: “macro estimate uncertain 시 confirm”
  - 권장: “**모든 기록 append 전 사용자 확인 필수**. 불확실 추정이 포함되면 그 사실을 함께 고지.”

- `references/privacy_security.md`에 예외 문구 추가:
  - “기본적으로 로컬 처리. 단, 이미지 기반 영양 추정은 사용자의 명시적 사전 동의가 있을 때에만 연결 모델/네트워크 사용 가능.”

---

## 5) 최종 판정
- **최신 OpenClaw 기준 적합도: 양호(Good) + 문서 정합성 보완 필요**
- 치명적 보안 결함보다는 **정책 문구 일관성**이 주요 개선 포인트입니다.


## 6) 반영 상태 (이번 커밋)
- 정책 정합성 점검을 코드로 강제하기 위해 `scripts/validate_skill_policies.py`를 추가했습니다.
- 이 스크립트는 confirmation-first 및 이미지 분석 사전 동의 규칙이 핵심 문서에 동시에 존재하는지 검사합니다.
