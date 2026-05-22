# Damn Antigravity IDE Migrator

이 도구는 VSCode Fork 기반 구버전 **Antigravity** (Antigravity 1.23.2 이하) 애플리케이션의 설정, 익스텐션, 대화 기록 데이터를 새로운 **Antigravity IDE**로 안전하게 이식해 주는 자동화 도구입니다.

> [!NOTE]
> **제품명 변경 관련 안내**
> - **기존 Antigravity (1.23.2 이하)**: IDE 기능이 포함되어 있던 기존의 Antigravity 에디터는 **Antigravity IDE**라는 별도의 제품으로 분리되었습니다. 기존 Antigravity 1.23.2 버전이 **Antigravity IDE**로 전환됩니다.
> - **새로운 Antigravity**: 완전히 새로 출시된 독립형 데스크톱 애플리케이션이 **Antigravity**라는 이름을 사용하게 되었습니다.

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

Windows 환경에서는 배치 파일을 사용하여 더블 클릭(원클릭)만으로 마이그레이션을 안전하게 실행하고 제어할 수 있습니다.

### macOS 컴패니언 포트

커뮤니티에서 만든 macOS용 버전은 아래 저장소에서 확인할 수 있습니다:

```text
https://github.com/cpu-coin/antigravity-ide-migrator-macos
```

이 버전은 Antigravity에서 Antigravity IDE로 마이그레이션한다는 동일한 목적을 유지하면서, `~/Library/Application Support/Antigravity`, `~/Library/Application Support/Antigravity IDE`, `~/.antigravity`, `~/.antigravity-ide` 같은 macOS 경로를 사용합니다. macOS `.command` 실행 파일, dry-run 지원, 복원 지원, 테스트도 포함되어 있습니다.

macOS 포트는 이 원본 Windows 마이그레이터에 크레딧을 두고 만든 컴패니언 프로젝트입니다. 원하신다면 별도 링크된 컴패니언 저장소로 유지하거나, 이 프로젝트 안의 플랫폼별 구현으로 통합할 수 있습니다.

### 1. Dry-Run 시뮬레이션 수행 (선택 사항)
실제 파일이나 데이터베이스를 수정하지 않고, 어떤 파일이 복사되고 어떤 설정이 병합되는지 안전하게 모의 시뮬레이션을 수행합니다. 실제 데이터가 변경되지 않으므로, 작업 진행 전에 미리 확인하고 싶을 때 유용합니다.
- **실행 방법**: 루트 폴더에 있는 `00_migrate-dry-run.bat` 파일을 더블 클릭하여 실행합니다.

### 2. 마이그레이션 실행 (필수)
실제 마이그레이션을 실행합니다. (실행 시 대상 폴더의 안전 백업이 자동으로 생성됩니다.)
- **실행 방법**: 루트 폴더에 있는 `01_migrate.bat` 파일을 더블 클릭하여 실행합니다.

> [!TIP]
> **성공적인 이식을 위한 첫 실행 권장 수칙**
> 마이그레이션이 완료되면 Antigravity IDE를 **최초로 한 번 실행**하여 모든 익스텐션이 완전히 로드될 때까지 기다린 후, **에디터를 완전히 종료했다가 재시작**해 주세요. 새로 추가된 일부 익스텐션 및 파일 아이콘 테마 등이 정상 인식되는 데 필요합니다.

### 3. 백업 파일로부터 복원 (문제 발생 시 복구용)
마이그레이션 도중 오류가 발생하거나 수동으로 백업된 특정 설정을 되돌려야 하는 경우:
- **실행 방법**: 복원하고자 하는 백업 폴더 경로를 `02_restore.bat` 뒤에 인자로 지정하여 실행합니다.
  ```cmd
  02_restore.bat "C:\Users\<사용자명>\AppData\Roaming\Antigravity IDE\migration_backups\<타임스탬프>"
  ```

### 4. 백업 파일 전체 정리 (선택 사항)
마이그레이션 완료 후, 보관 중인 백업 파일을 모두 일괄 삭제하고 저장공간을 정리하고자 할 때 사용합니다.
- **실행 방법**: 루트 폴더에 있는 `03_clean-backups.bat` 파일을 더블 클릭하여 실행합니다.

---

## CLI 옵션 및 사용 예시

터미널이나 명령 프롬프트(CMD)에서 마이그레이션 스크립트를 직접 실행할 때 사용할 수 있는 옵션 및 예시입니다.

### 1. 사용 예시
- **도움말 출력**:
  ```bash
  python -m src.main --help
  ```
- **Dry-run 시뮬레이션 직접 수행 (상세 로그 포함)**:
  ```bash
  python -m src.main --dry-run --verbose
  ```
- **백업 파일로부터 복원 수행**:
  ```bash
  python -m src.main --restore "C:\Users\<사용자명>\AppData\Roaming\Antigravity IDE\migration_backups\<타임스탬프>"
  ```
- **백업 파일 전체 삭제 (정리)**:
  ```bash
  python -m src.main --cleanup
  ```

### 2. CLI 옵션 목록
```text
options:
  -h, --help           도움말 메시지를 출력하고 종료합니다.
  --dry-run            실제 파일이나 DB를 수정하지 않고 시뮬레이션만 수행합니다.
  --no-backup          마이그레이션 전 자동 백업 과정을 건너뜁니다 (권장하지 않음).
  --restore RESTORE    지정한 백업 폴더의 상태로 파일들을 복원합니다.
  --cleanup            마이그레이션 백업 파일을 모두 삭제하여 공간을 확보합니다.
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

---

## 라이선스

이 프로젝트는 [MIT License](file:///d:/Dev/Damn-Antigravity-Converstation-Restore/LICENSE) 라이선스 하에 배포 및 사용이 가능합니다. 자세한 사항은 [LICENSE](file:///d:/Dev/Damn-Antigravity-Converstation-Restore/LICENSE) 파일을 참조하세요.
