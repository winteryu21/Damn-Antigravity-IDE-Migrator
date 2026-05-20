# Antigravity to Antigravity IDE 마이그레이션 도구

이 도구는 VSCode Fork 기반 구버전 **Antigravity** 애플리케이션의 설정, 플러그인(익스텐션), 대화 기록 데이터를 새로운 독립형 데스크톱 앱인 **Antigravity IDE**로 안전하게 이식해 주는 자동화 명령줄 도구입니다.

GitHub 오픈소스 배포를 고려하여 고수준의 예외 처리와 안전 설계가 적용되었습니다.

## 주요 기능

1. **자동 백업 및 롤백**: 작업을 진행하기 전 대상 설정 파일들의 타임스탬프 백업을 자동으로 생성합니다. 작업 중 오류가 발생하면 즉시 자동 롤백을 수행하여 원본 상태로 복구합니다.
2. **설정 병합**: 기존 `settings.json`을 파싱하여 신규 설정과 충돌 없이 누락된 개인 설정들만 안전하게 합칩니다.
3. **익스텐션 복사 및 경로 수정**: 설치되어 있던 기존 플러그인 폴더를 새 폴더로 안전 복사하며, `extensions.json` 메타데이터에 등록된 절대 경로 내 `.antigravity`를 `.antigravity-ide`로 일괄 변환합니다.
4. **대화 히스토리 병합 (Protobuf Binary Concatenation)**: SQLite 글로벌 저장소(`state.vscdb`)의 키-값 데이터를 복사하며, 대화 목록(`trajectorySummaries`)의 경우 Protobuf 바이너리 포맷의 특성을 이용해 기존 데이터와 신규 세션 데이터를 완전하게 결합합니다.
5. **Dry-Run 시뮬레이션 지원**: `--dry-run` 옵션을 제공하여 디스크 쓰기를 수행하기 전에 어떤 파일들이 복사되고 어떤 DB 레코드가 추가될 예정인지 로그로 미리 확인할 수 있습니다.
6. **작업 영역 파일 동기화**: 대화 파일(`.pb`), 브레인 스냅샷 등 `.gemini` 폴더 아래에서 누락된 에이전트 핵심 파일들을 동기화합니다.

---

## 필수 안전 수칙

> [!CAUTION]
> **마이그레이션 실행 전, 반드시 Antigravity와 Antigravity IDE 프로그램을 모두 완전히 종료해야 합니다.**
> SQLite 데이터베이스(`state.vscdb`)는 에디터 실행 중 메모리에 로드 및 캐싱됩니다. 프로그램을 켜둔 채로 마이그레이션을 실행하면, 에디터 종료 시 메모리에 있던 내용이 데이터베이스에 덮어씌워져 이식된 데이터가 유실될 수 있습니다.

---

## 설치 및 사전 요구사항

이 도구는 **Python 3.8 이상**에서 실행 가능하며, 추가적인 외부 라이브러리 설치가 필요 없습니다 (파이썬 표준 라이브러리 `sqlite3`, `json`, `shutil`, `argparse`, `logging`만 사용).

1. 리포지토리를 개발 영역에 다운로드하거나 클론합니다.
2. 파이썬이 설치되어 있는지 확인합니다:
   ```bash
   python --version
   ```

---

## 사용 방법

터미널이나 명령 프롬프트(CMD, PowerShell)에서 다음 명령어를 실행합니다.

### 1. Dry-Run 시뮬레이션 수행 (권장)
실제 파일 수정을 하지 않고 모의 실행해 봅니다:
```bash
python -m src.main --dry-run --verbose
```

### 2. 마이그레이션 실행
실제 마이그레이션을 진행합니다 (자동으로 백업 폴더가 생성됩니다):
```bash
python -m src.main
```

### 3. 백업 파일로부터 복원 (롤백 필요 시)
문제가 발생하여 자동 생성된 백업 데이터를 수동 복원해야 할 경우 아래 명령을 실행합니다:
```bash
python -m src.main --restore "C:\Users\<사용자명>\AppData\Roaming\Antigravity IDE\migration_backups\<타임스탬프>"
```

### 4. CLI 옵션 가이드
```text
options:
  -h, --help           도움말 메시지를 출력하고 종료합니다.
  --dry-run            실제 파일이나 DB를 수정하지 않고 시뮬레이션만 수행합니다.
  --no-backup          마이그레이션 전 자동 백업 과정을 건너뜁니다 (권장하지 않음).
  --restore RESTORE    지정한 백업 폴더의 상태로 파일들을 복원합니다.
  -v, --verbose        콘솔 디버그 로그 출력을 활성화합니다.
```

---

## 프로젝트 구조

- `src/config.py`: Windows 환경 변수를 통해 마이그레이션 관련 폴더 경로들을 동적 분석 및 리졸브합니다.
- `src/backup.py`: 자동 백업 파일 관리 및 롤백 메서드를 제공합니다.
- `src/file_handler.py`: 설정 JSON 병합, 익스텐션 복사 및 메타데이터 경로 수정, `.gemini` 하위 파일 동기화를 담당합니다.
- `src/database.py`: SQLite DB 연결, 누락 키 복사 및 Protobuf 바이너리 병합 로직을 구현합니다.
- `src/main.py`: CLI 인자 파싱, 에디터 프로세스 중복 실행 여부 확인, 전체 실행 흐름 조정을 담당합니다.

---

## 단위 테스트 실행

시뮬레이션 디렉토리 구조 위에서 안정성 검증을 위한 테스트 케이스를 수행합니다:
```bash
python -m unittest tests/test_migration.py
```
