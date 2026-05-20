import os
import sys
import argparse
import logging
import subprocess
from src.config import resolve_paths
from src.backup import BackupManager
from src.file_handler import FileMigrator
from src.database import DatabaseMigrator

def setup_logging(verbose: bool) -> None:
    """Configures logging for console and file output."""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Formatter
    formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)s [%(module)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # File Handler
    file_handler = logging.FileHandler("migration.log", mode="w", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Root Logger Configuration
    root_logger = logging.getLogger("migration")
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

def is_process_running(process_name: str) -> bool:
    """Checks if a process is running on Windows using tasklist."""
    try:
        output = subprocess.check_output("tasklist", shell=True).decode("utf-8", errors="ignore")
        return process_name.lower() in output.lower()
    except Exception:
        return False

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Migrates configurations, extensions, and conversations from old Antigravity to new Antigravity IDE."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the migration without making any modifications to files or database."
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip automatic configuration backups before migration (not recommended)."
    )
    parser.add_argument(
        "--restore",
        type=str,
        help="Path to a backup directory to restore configurations from."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose debug logging in console."
    )
    
    args = parser.parse_args()
    setup_logging(args.verbose)
    
    logger = logging.getLogger("migration")
    logger.info("=== Antigravity IDE Migration Tool ===")
    
    try:
        paths = resolve_paths()
    except Exception as e:
        logger.error(f"Failed to resolve environment paths: {e}")
        sys.exit(1)
        
    backup_mgr = BackupManager(paths)
    
    # If restoring a backup
    if args.restore:
        if not os.path.exists(args.restore):
            logger.error(f"Restore path does not exist: {args.restore}")
            sys.exit(1)
        try:
            backup_mgr.restore_backup(args.restore)
            logger.info("Restore completed successfully.")
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            sys.exit(1)
        sys.exit(0)
        
    # Standard migration flow
    # Check if target programs are running
    is_old_running = is_process_running("Antigravity.exe")
    is_new_running = is_process_running("Antigravity IDE.exe")
    
    if is_old_running or is_new_running:
        running_apps = []
        if is_old_running: running_apps.append("Antigravity")
        if is_new_running: running_apps.append("Antigravity IDE")
        
        msg = f"The following processes are currently running: {', '.join(running_apps)}. Please CLOSE them before migrating to prevent data overwrite and corruption."
        
        if args.dry_run:
            logger.warning(f"[Dry-Run] {msg} Proceeding with simulation.")
        else:
            logger.error(msg)
            sys.exit(1)
            
    # Perform Backup
    backup_path = None
    if not args.no_backup:
        try:
            backup_path = backup_mgr.create_backup()
        except Exception as e:
            logger.error(f"Backup failed. Aborting migration for safety. Error: {e}")
            sys.exit(1)
            
    # Perform Migration
    try:
        file_migrator = FileMigrator(paths, dry_run=args.dry_run)
        db_migrator = DatabaseMigrator(paths, dry_run=args.dry_run)
        
        logger.info("1. Starting settings.json migration...")
        file_migrator.migrate_settings()
        
        logger.info("1.5. Starting Local State (safeStorage master key) migration...")
        file_migrator.migrate_local_state()
        
        logger.info("2. Starting extensions (plugins) migration...")
        file_migrator.migrate_extensions()
        
        logger.info("3. Starting Gemini conversations and brain data synchronization...")
        file_migrator.migrate_gemini_data()
        
        logger.info("4. Starting SQLite database merging...")
        db_migrator.migrate()
        
        if args.dry_run:
            logger.info("=== Dry-Run Simulation Finished Successfully ===")
        else:
            logger.info("=== Migration Completed Successfully ===")
            if backup_path:
                logger.info(f"Backup created at: {backup_path}")
                
    except Exception as e:
        logger.error(f"Migration encountered an error: {e}")
        if backup_path and not args.dry_run:
            logger.warning("Attempting automatic rollback to restore settings to original states...")
            try:
                backup_mgr.restore_backup(backup_path)
                logger.info("Rollback completed successfully. Critical settings restored.")
            except Exception as re:
                logger.error(f"Automatic rollback failed: {re}. Manual recovery may be needed using backup at {backup_path}")
        sys.exit(1)

if __name__ == "__main__":
    main()
