import os
import shutil
import logging
from datetime import datetime
from src.config import AppPaths

logger = logging.getLogger("migration")

class BackupManager:
    """Manages automated backups and rollbacks of critical settings."""
    
    def __init__(self, paths: AppPaths):
        self.paths = paths
        self.backup_dir = os.path.join(paths.new_roaming, "migration_backups")
        
    def create_backup(self) -> str:
        """
        Creates a timestamped backup of settings.json, state.vscdb, and extensions.json.
        Returns the path to the backup folder.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        current_backup_path = os.path.join(self.backup_dir, timestamp)
        
        # Create backup directory
        os.makedirs(current_backup_path, exist_ok=True)
        logger.info(f"Creating backup at: {current_backup_path}")
        
        # Define files to backup
        files_to_backup = [
            (
                os.path.join(self.paths.new_roaming, "User", "settings.json"),
                "settings.json"
            ),
            (
                os.path.join(self.paths.new_roaming, "User", "globalStorage", "state.vscdb"),
                "state.vscdb"
            ),
            (
                os.path.join(self.paths.new_dot, "extensions", "extensions.json"),
                "extensions.json"
            ),
            (
                os.path.join(self.paths.new_roaming, "Local State"),
                "Local State"
            )
        ]
        
        backed_up_count = 0
        for src_file, dest_name in files_to_backup:
            if os.path.exists(src_file):
                dest_file = os.path.join(current_backup_path, dest_name)
                try:
                    # Ensure parent dir of destination backup file exists (if nested)
                    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                    shutil.copy2(src_file, dest_file)
                    logger.info(f"Backed up {os.path.basename(src_file)} to {dest_file}")
                    backed_up_count += 1
                except Exception as e:
                    logger.error(f"Failed to backup {src_file}: {e}")
                    raise e
            else:
                logger.debug(f"File not found for backup: {src_file}")
                
        if backed_up_count == 0:
            logger.info("No active files found to backup. Proceeding with clean migration.")
            
        return current_backup_path

    def restore_backup(self, backup_folder: str) -> None:
        """Restores files from a specific backup folder."""
        logger.info(f"Restoring backup from: {backup_folder}")
        
        restore_map = [
            ("settings.json", os.path.join(self.paths.new_roaming, "User", "settings.json")),
            ("state.vscdb", os.path.join(self.paths.new_roaming, "User", "globalStorage", "state.vscdb")),
            ("extensions.json", os.path.join(self.paths.new_dot, "extensions", "extensions.json")),
            ("Local State", os.path.join(self.paths.new_roaming, "Local State"))
        ]
        
        for name, dest_file in restore_map:
            src_file = os.path.join(backup_folder, name)
            if os.path.exists(src_file):
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                try:
                    shutil.copy2(src_file, dest_file)
                    logger.info(f"Restored {name} to {dest_file}")
                except Exception as e:
                    logger.error(f"Failed to restore {name} to {dest_file}: {e}")
                    raise e

    def clean_backups(self) -> None:
        """Deletes the entire migration backups directory to free up space."""
        if os.path.exists(self.backup_dir):
            logger.info(f"Deleting all backups at: {self.backup_dir}")
            shutil.rmtree(self.backup_dir)
            logger.info("Backup directory deleted successfully.")
        else:
            logger.info("No backups found to clean up.")
