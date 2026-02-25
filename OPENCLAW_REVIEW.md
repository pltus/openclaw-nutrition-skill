# OpenClaw Nutrition Skill 코드 전체 리뷰

기준: `SKILL.md`, `references/logging_rules.md`, `references/privacy_security.md`의 요구사항 대비 현재 구현(`oc_nutrition/*`) 정합성 점검.

## 결론 요약
- **핵심 저장/집계/리포트 기능은 대체로 요구사항에 부합**합니다.
- 다만 **채팅형 스킬 워크플로 요구사항(질문 수 제한, 기록 전 확인, 목표 업데이트/정정 UX)**은 CLI 구현과 완전히 1:1 매핑되어 있지 않습니다.
- 특히 “네트워크 액션은 명시적 확인 후” 규칙은 현재 `log-image` 실행 시점에 온라인 분석을 즉시 수행하므로, OpenClaw 에이전트 통합 시 추가 가드가 필요합니다.

---

## 1) 요구사항 충족 항목 (Pass)

### 1-1. Append-only 저장 규칙
- `append_log_entry()`는 NDJSON 파일에 라인 append만 수행하고 기존 라인을 수정하지 않습니다.
- `read_log_entries()`는 파일을 읽어 검증만 수행합니다.

판정: **충족**

### 1-2. 타임존 포함 타임스탬프 검증
- `MealLogEntry`의 `timestamp` validator가 timezone offset 필수 조건을 강제합니다.

판정: **충족**

### 1-3. 이미지 분석 후 저장 전 확인
- `log-image` 명령은 먼저 분석 결과를 출력하고, `--confirm` 옵션이 있을 때만 append 저장합니다.

판정: **부분 충족** (저장 전 확인은 충족, 하지만 네트워크 호출 전 확인은 별도 필요)

### 1-4. 주간 리포트 경로/형식
- `export_weekly_markdown()`은 `data/exports/weekly_YYYY-MM-DD.md` 형식으로 출력합니다.

판정: **충족**

---

## 2) 요구사항 대비 갭/리스크 (Action Needed)

### 2-1. `SKILL.md`의 입력 범위 대비 CLI 기능 공백
`SKILL.md`는 아래 입력을 지원한다고 명시합니다.
- goals updates
- correction entries
- meal planning / grocery list

하지만 현재 CLI 커맨드는 `init-profile/log/log-image/today/week/export-week`만 제공됩니다.

영향:
- 스킬 설명과 실제 실행 표면(API/CLI) 간 기대 불일치
- OpenClaw에서 “목표 업데이트/장보기 제안” 요청 시 일관된 처리 경로 부족

권고:
1) 기능을 실제로 추가하거나,
2) `SKILL.md` 설명 범위를 현재 제공 기능에 맞게 축소

### 2-2. 기록 전 명시적 확인(일반 log 경로) 미흡
`SKILL.md` 워크플로는 “최종 해석 결과 확인 후 쓰기”를 요구하지만, `log` 명령은 즉시 append합니다.

영향:
- 채팅형 오케스트레이션 없이 CLI 직접 사용 시, 확인 단계가 강제되지 않음

권고:
- `log`에도 `--confirm` 옵션을 두고 미확인 상태에서는 preview만 출력
- 혹은 OpenClaw adapter 레이어에서 반드시 2단계(confirm) 플로우 강제

### 2-3. 네트워크 호출 전 명시적 확인 부재 (`log-image`)
안전 규칙에는 “네트워크 액션은 명시적 확인 후”가 포함되어 있으나, 현재 `log-image`는 실행 즉시 `analyze_food_image_online()` 호출을 수행합니다.

영향:
- 정책 해석에 따라 비준수로 볼 수 있음

권고:
- `--analyze` 같은 별도 명시 플래그를 요구하거나,
- OpenClaw 상위 레이어에서 “온라인 분석 실행해도 되는지” 1차 확인 후 명령 호출

### 2-4. “최대 2개 확인 질문” 규칙의 실행 계층 불명확
해당 규칙은 `SKILL.md`/reference 문서에 있으나, 코드에는 질문 카운트/제어 로직이 없습니다.

영향:
- 현재 구조상 이 규칙은 모델 프롬프트/에이전트 오케스트레이션 레이어 의존

권고:
- 규칙이 코드 레벨 보장 대상이 아니면 문서에 “에이전트 레이어 책임”을 명시
- 코드 보장을 원하면 대화 상태/질문 횟수 상태 저장 로직 추가

---

## 3) 우선순위 제안

### P1 (반드시 권장)
1. `SKILL.md` 기능 범위와 실제 기능을 일치시키기(확장 또는 문구 축소)
2. 네트워크 호출/쓰기 호출의 confirm 게이트를 정책과 동일하게 정의하기

### P2
3. `log` 명령 preview-confirm 2단계 도입
4. correction/goals 업데이트용 명시 커맨드 추가

### P3
5. meal planning/grocery list 보조 기능(최근 로그 기반 추천) 구현 또는 범위 조정

---

## 4) 이번 수정 사항
- 이전 변경(스킬 문구 정합성만 검사하는 테스트 파일)은 사용자 요청 범위와 맞지 않아 제거했습니다.
