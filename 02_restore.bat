@echo off
if "%~1"=="" (
    echo [Error] Backup directory path is required.
    echo.
    echo Usage: 02_restore.bat [backup_directory_path]
    echo Example: 02_restore.bat "C:\Users\%USERNAME%\AppData\Roaming\Antigravity IDE\migration_backups\20260520_094630"
    echo.
    pause
    exit /b 1
)

echo Restoring backup from: %~1
python -m src.main --restore "%~1"
pause
