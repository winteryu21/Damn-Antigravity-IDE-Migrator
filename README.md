# Damn Antigravity IDE Migrator

A safe, robust, and automated utility to migrate configurations, settings, extensions, and conversation history from the legacy VSCode-fork based **Antigravity** (Antigravity 1.23.2 and below) application to the new **Antigravity IDE**.

> [!NOTE]
> **Product Naming Rebranding**
> - **Legacy Antigravity (1.23.2 and below)**: The old VSCode Fork-based editor with IDE features has been split into a separate product called **Antigravity IDE**. The legacy Antigravity 1.23.2 version is transitioned to **Antigravity IDE**.
> - **New Antigravity**: A completely new standalone desktop application has taken over the name **Antigravity**.

## Key Features

1. **Automated Backup & Rollback**: Automatically creates a timestamped backup of target configuration files before modification. If any part of the migration fails, it performs a complete automatic rollback to restore settings to their original state.
2. **Settings Merge**: Parses and safely merges `settings.json` without overwriting existing settings specific to the new IDE version.
3. **Extensions Migration & Path Rewriting**: Copies all installed VSCode extensions physically, and merges/rewrites the `extensions.json` file to update absolute paths from `.antigravity` to `.antigravity-ide`.
4. **Protobuf Database Merging**: Merges SQLite global storage (`state.vscdb`) keys, utilizing Protobuf binary wire format concatenation to safely combine historical conversation lists without needing a schema file.
5. **Dry-Run Simulation**: Supports a `--dry-run` flag to preview copy operations and database mutations before writing them to disk.
6. **Workspace Sync**: Syncs all Gemini agent state files (conversations, brain snapshots, prompting configs) that are present in the old app but missing in the new one.

---

## Safety Requirements

> [!CAUTION]
> **Before running the migration, you MUST close both Antigravity and Antigravity IDE.**
> SQLite databases (`state.vscdb`) are loaded and cached in memory when the editor is active. Running this tool while the editor is running may lead to the editor overwriting your migrated database on exit, resulting in data loss.

---

## Installation & Prerequisites

This tool requires **Python 3.8+** with no external dependencies (uses standard library modules like `sqlite3`, `json`, `shutil`, `argparse`, and `logging`).

1. Clone or download the repository to your workspace.
2. Ensure you have python installed:
   ```bash
   python --version
   ```

---

## Usage

On Windows, you can use the provided batch files for convenient, one-click execution via double-click.

### 1. Perform a Dry-Run Simulation (Optional)
Simulate the migration process safely without modifying any files or databases, allowing you to preview which files will copy and which settings will merge. Since no actual data is altered, this is useful to run before starting the real migration.
- **How to Run**: Double-click the `00_migrate-dry-run.bat` file in the root directory.

### 2. Run the Standard Migration (Required)
Run the actual migration process. (This automatically creates a safe backup of the target folders.)
- **How to Run**: Double-click the `01_migrate.bat` file in the root directory.

> [!TIP]
> **Post-Migration Startup Recommendation**
> After the migration completes, **launch the Antigravity IDE for the first time**, wait a moment for all newly copied extensions to fully load, and then **completely close and restart the editor**. This ensures that all extensions and file icon themes are properly indexed and loaded by the VSCode engine cache.

### 3. Restore from a Backup (Recovery on Issues)
If an error occurs or you need to revert to a previous configuration backup:
- **How to Run**: Run `02_restore.bat` followed by the backup folder path as an argument.
  ```cmd
  02_restore.bat "C:\Users\<Username>\AppData\Roaming\Antigravity IDE\migration_backups\<timestamp>"
  ```

### 4. Delete All Backups (Optional)
If you no longer need the backup files after a successful migration and want to free up disk space:
- **How to Run**: Double-click the `03_clean-backups.bat` file in the root directory.

---

## CLI Options & Usage Examples

Available command-line flags and execution examples when running the migration script directly via terminal or Command Prompt (CMD):

### 1. Usage Examples
- **Show Help Message**:
  ```bash
  python -m src.main --help
  ```
- **Run Dry-run Simulation (with verbose logging)**:
  ```bash
  python -m src.main --dry-run --verbose
  ```
- **Restore from Backup Directory**:
  ```bash
  python -m src.main --restore "C:\Users\<Username>\AppData\Roaming\Antigravity IDE\migration_backups\<timestamp>"
  ```
- **Delete All Backups (Cleanup)**:
  ```bash
  python -m src.main --cleanup
  ```

### 2. Command-Line Options
```text
options:
  -h, --help           show this help message and exit
  --dry-run            Simulate the migration without making any modifications to files or database.
  --no-backup          Skip automatic configuration backups before migration (not recommended).
  --restore RESTORE    Path to a backup directory to restore configurations from.
  --cleanup            Delete all migration backups to free up space.
  -v, --verbose        Enable verbose debug logging in console.
```

---

## Project Architecture

- `src/config.py`: Resolves environment paths dynamically (handles Windows APPDATA and profile folders).
- `src/backup.py`: Handles automatic ZIP/directory backups and rollback routines.
- `src/file_handler.py`: Merges `settings.json`, copies extensions, rewrites paths in `extensions.json`, and synchronizes `.gemini` folder structures.
- `src/database.py`: Performs SQLite key insertion and Protobuf concatenation merges.
- `src/main.py`: Coordinates the migration CLI process, process checks, and error boundaries.

---

## Testing

Run unit tests to verify the migration logic under simulated directory structures:
```bash
python -m unittest tests/test_migration.py
```

---

## License

This project is licensed under the [MIT License](file:///d:/Dev/Damn-Antigravity-Converstation-Restore/LICENSE) - see the [LICENSE](file:///d:/Dev/Damn-Antigravity-Converstation-Restore/LICENSE) file for details.
