# openclaw-nutrition-skill

로컬 환경에서 동작하는 OpenClaw 영양 관리 스킬이자 Python CLI 툴킷입니다.  
채팅 기반 식사 기록, 매크로(칼로리/탄단지) 집계, 주간 리포트 내보내기를 **로컬 파일 중심(append-only)** 으로 처리합니다.

## 1) 핵심 기능

- **식사 로그 누적 기록 (Append-only NDJSON)**
  - 식사 데이터는 `data/meal_log.ndjson`에 한 줄(JSON)씩 추가됩니다.
  - 기존 기록 수정/삭제 대신, 정정 내용도 새로운 엔트리로 추가하는 워크플로를 권장합니다.

- **Pydantic 기반 데이터 검증**
  - 프로필/식사 항목/로그 엔트리를 스키마로 검증해 잘못된 입력을 조기에 차단합니다.
  - 타임스탬프 타임존 포함 여부, 매크로 음수 값 여부 등 기본 무결성 검사가 포함됩니다.

- **오늘 / 최근 7일 매크로 집계**
  - `today` 명령으로 당일 합계, `week` 명령으로 최근 7일(오늘 포함) 합계를 확인할 수 있습니다.
  - 칼로리, 단백질, 탄수화물, 지방 합계를 빠르게 계산합니다.

- **주간 마크다운 리포트 생성**
  - `export-week` 명령으로 `data/exports/weekly_YYYY-MM-DD.md` 파일을 생성합니다.
  - 기간, 총합, 최근 식사 목록을 보고서 형태로 저장합니다.

- **사진 기반 음식 분석 + 확인 후 기록**
  - 음식 사진 입력 시 온라인 비전 모델로 음식 여부와 영양(칼로리/탄단지)을 추정할 수 있습니다.
  - 분석 결과를 먼저 보여주고, 사용자가 확인(`--confirm`)한 경우에만 로그에 append 합니다.

- **안전한 로컬 우선 설계**
  - 로그 저장은 로컬 append-only 파일을 사용하며, 파괴적 재작성 동작을 피하도록 설계되어 있습니다.

## 2) 프로젝트 구조와 파일 상세 설명

아래는 저장소의 주요 파일/디렉터리와 역할입니다.

### 루트 파일

- `README.md`
  - 현재 문서입니다. 설치/사용법, 기능, 파일 구조를 설명합니다.

- `SKILL.md`
  - OpenClaw 스킬 메타데이터(이름, 설명, 지원 기능)와 대화형 워크플로(질문 제한, 확인 절차, append-only 규칙)를 정의합니다.

- `pyproject.toml`
  - 패키지 메타데이터, 의존성(`typer`, `pydantic` 등), 개발 의존성(`pytest`), CLI 엔트리포인트(`oc-nutrition`)를 정의합니다.

- `LICENSE`
  - MIT 라이선스 전문입니다.

### `oc_nutrition/` (핵심 Python 패키지)

- `oc_nutrition/__init__.py`
  - 패키지 초기화 파일입니다.

- `oc_nutrition/models.py`
  - 데이터 모델 정의:
    - `UserProfile`: 사용자 이름, 타임존, 일일 목표치, 선호 정보
    - `MealItem`: 음식명/수량/칼로리/탄단지/옵션 필드(식이섬유, 나트륨, 입력 출처, 신뢰도)
    - `MealLogEntry`: 시각, 식사 타입, 아이템 목록, 메모
  - 타임스탬프에 타임존 정보가 포함되었는지 검증합니다.

- `oc_nutrition/storage.py`
  - 로컬 파일 저장소 계층:
    - 데이터 디렉터리 결정(`OC_NUTRITION_DATA_DIR` 환경변수 지원)
    - `data/exports` 레이아웃 보장
    - 예시 프로필로부터 `profile.json` 초기화
    - 식사 로그 append 기록
    - NDJSON 로그 읽기/파싱/검증
  - 저장 관련 예외(`StorageError`)를 일관되게 처리합니다.

- `oc_nutrition/summaries.py`
  - 집계 로직:
    - `today_summary()`
    - `last_7_days_summary()`
  - 기간 내 엔트리 필터링 후 칼로리/탄단지 누적 합계를 계산합니다.

- `oc_nutrition/export.py`
  - 주간 리포트 렌더링/저장:
    - `render_weekly_markdown()`
    - `export_weekly_markdown()`
  - 최근 식사(최대 10개)를 포함한 Markdown 보고서를 생성합니다.

- `oc_nutrition/cli.py`
  - Typer 기반 CLI 명령 정의:
    - `init-profile`
    - `log`
    - `log-image`
    - `today`
    - `week`
    - `export-week`
  - 사용자 입력을 모델로 검증하고 저장/집계/내보내기 함수를 호출합니다.

### `scripts/`

- `scripts/oc_nutrition_cli.py`
  - 로컬 실행 편의를 위한 스크립트 진입점 파일입니다.

### `tests/` (테스트)

- `tests/conftest.py`
  - pytest 공용 fixture/테스트 설정을 제공합니다.

- `tests/test_storage.py`
  - 저장소 계층(초기화, append, 읽기, 예외 처리)을 검증합니다.

- `tests/test_summaries.py`
  - 오늘/주간 합계 계산 로직의 정확성을 검증합니다.

- `tests/test_export.py`
  - 마크다운 리포트 생성 내용 및 파일 출력 동작을 검증합니다.

### `references/` (설계 참고 문서)

- `references/data_model.md`
  - 데이터 스키마 및 필드 의미를 설명합니다.

- `references/logging_rules.md`
  - 식사 로깅 규칙, 정정 방식, 운영 원칙을 정리합니다.

- `references/privacy_security.md`
  - 개인정보/보안 관점의 기본 정책을 설명합니다.

### `data/` (로컬 데이터 경로)

- `data/profile.example.json`
  - 초기 프로필 생성을 위한 예시 템플릿입니다.

- `data/food_aliases.example.json`
  - 음식 별칭 매핑 예시 파일입니다.

- `data/exports/.gitkeep`
  - 빈 디렉터리 유지를 위한 파일입니다.

> 실행 중 실제 생성/사용 파일
> - `data/profile.json`
> - `data/meal_log.ndjson`
> - `data/food_aliases.json` (선택)
> - `data/exports/weekly_YYYY-MM-DD.md`

### 기타

- `pydantic/__init__.py`
  - 로컬 모듈 경로 호환/테스트 환경용 패키지 파일입니다.

## 3) 설치 방법

```bash
git clone <your-fork-or-repo-url>
cd openclaw-nutrition-skill
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## 4) CLI 사용법

기본 데이터 경로는 `./data` 입니다.  
다른 경로를 사용하려면 환경변수 `OC_NUTRITION_DATA_DIR=/path/to/data`를 설정하세요.

```bash
oc-nutrition init-profile
oc-nutrition log --meal-type lunch --item "chicken salad" --qty "1 bowl" --calories 450 --protein 35 --carbs 20 --fat 18
oc-nutrition log --meal-type lunch --item "chicken salad" --qty "1 bowl" --calories 450 --protein 35 --carbs 20 --fat 18 --confirm
oc-nutrition today
oc-nutrition week
oc-nutrition export-week
oc-nutrition log-image --image ./meal.jpg --meal-type dinner
oc-nutrition log-image --image ./meal.jpg --meal-type dinner --analyze
oc-nutrition log-image --image ./meal.jpg --meal-type dinner --analyze --confirm
```

### 명령별 설명

- `oc-nutrition init-profile`
  - `data/profile.example.json`을 검증한 뒤 `data/profile.json`을 생성합니다.
  - 기존 `profile.json`이 있으면 덮어쓰지 않고 오류를 반환합니다.

- `oc-nutrition log ... [--confirm]`
  - 식사 1건을 먼저 preview 출력합니다.
  - `--confirm`을 지정하면 NDJSON 로그에 append합니다.
  - `meal-type`은 `breakfast/lunch/dinner/snack` 중 하나여야 합니다.

- `oc-nutrition log-image --image ... --meal-type ... [--analyze] [--confirm]`
  - `--analyze`가 있어야 온라인 분석을 수행합니다.
  - 분석 결과를 먼저 보여주며, `--confirm` 없이는 저장하지 않습니다.
  - `--analyze --confirm`을 함께 지정한 경우에만 `source=estimate`로 append 저장합니다.

- `oc-nutrition today`
  - 당일 00:00~23:59:59 범위의 누적 매크로를 출력합니다.

- `oc-nutrition week`
  - 실행 시점을 기준으로 최근 7일 범위 누적 매크로를 출력합니다.

- `oc-nutrition export-week`
  - 최근 7일 요약을 Markdown 파일로 내보냅니다.

## 5) 운영 가이드

- 과거 로그를 직접 수정하지 말고, **정정 엔트리를 추가**하세요.
- 추정치 입력 시 `source=estimate`, `confidence` 값을 활용해 품질을 표시하세요.
- 리포트는 기록 정확도에 의존하므로, 가능하면 각 식사마다 탄단지 수치를 함께 기록하세요.

## 6) 테스트

```bash
pytest
```

## 7) 라이선스

- MIT License (`LICENSE` 참고)
