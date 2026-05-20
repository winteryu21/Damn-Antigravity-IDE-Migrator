import os
import sqlite3
import base64
import logging
from src.config import AppPaths

logger = logging.getLogger("migration")

class DatabaseMigrator:
    """Handles migration and merging of the SQLite global storage state.vscdb."""
    
    def __init__(self, paths: AppPaths, dry_run: bool = False):
        self.paths = paths
        self.dry_run = dry_run
        self.old_db = os.path.join(paths.old_roaming, "User", "globalStorage", "state.vscdb")
        self.new_db = os.path.join(paths.new_roaming, "User", "globalStorage", "state.vscdb")

    def migrate(self) -> None:
        """Runs the database migration process."""
        if not os.path.exists(self.old_db):
            logger.warning(f"Old database not found at {self.old_db}. Skipping database migration.")
            return
            
        if not os.path.exists(self.new_db):
            logger.info("New database does not exist yet. Creating parent directories.")
            if not self.dry_run:
                os.makedirs(os.path.dirname(self.new_db), exist_ok=True)
                
        logger.info(f"Migrating database from {self.old_db} to {self.new_db}")
        
        try:
            # Read all key-values from the old database
            old_conn = sqlite3.connect(self.old_db)
            old_cursor = old_conn.cursor()
            
            # Check if ItemTable exists in old DB
            old_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ItemTable'")
            if not old_cursor.fetchone():
                logger.warning("ItemTable not found in old database. Skipping.")
                old_conn.close()
                return
                
            old_cursor.execute("SELECT key, value FROM ItemTable")
            old_data = {row[0]: row[1] for row in old_cursor.fetchall()}
            old_conn.close()
            
            # Connect to new database (create if not exists)
            if self.dry_run:
                logger.info("[Dry-Run] Connecting to new database and simulating merge.")
                new_data = {}
                # If new DB exists, read it for simulation
                if os.path.exists(self.new_db):
                    new_conn = sqlite3.connect(self.new_db)
                    new_cursor = new_conn.cursor()
                    new_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ItemTable'")
                    if new_cursor.fetchone():
                        new_cursor.execute("SELECT key, value FROM ItemTable")
                        new_data = {row[0]: row[1] for row in new_cursor.fetchall()}
                    new_conn.close()
            else:
                new_conn = sqlite3.connect(self.new_db)
                new_cursor = new_conn.cursor()
                # Create ItemTable if it doesn't exist
                new_cursor.execute("CREATE TABLE IF NOT EXISTS ItemTable (key TEXT PRIMARY KEY, value TEXT)")
                new_cursor.execute("SELECT key, value FROM ItemTable")
                new_data = {row[0]: row[1] for row in new_cursor.fetchall()}
                
            keys_inserted = 0
            keys_updated = 0
            
            for key, old_val in old_data.items():
                # Special Merge for Trajectory/Conversation History
                if key == "antigravityUnifiedStateSync.trajectorySummaries":
                    new_val = new_data.get(key)
                    if new_val and new_val.strip():
                        # Both have history: merge by concatenating binary protobuf payload
                        try:
                            old_bytes = base64.b64decode(old_val)
                            new_bytes = base64.b64decode(new_val)
                            
                            # Protobuf binary format concatenation merges repeated fields
                            merged_bytes = old_bytes + new_bytes
                            merged_val = base64.b64encode(merged_bytes).decode("utf-8")
                            
                            if new_val != merged_val:
                                logger.info("Merging old and new conversation histories.")
                                if not self.dry_run:
                                    new_cursor.execute("INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)", (key, merged_val))
                                keys_updated += 1
                        except Exception as e:
                            logger.error(f"Failed to merge trajectory summaries: {e}. Falling back to old value.")
                            if not self.dry_run:
                                new_cursor.execute("INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)", (key, old_val))
                            keys_updated += 1
                    else:
                        # New history is empty, write old history directly
                        logger.info("Writing old conversation history to new database.")
                        if not self.dry_run:
                            new_cursor.execute("INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)", (key, old_val))
                        keys_inserted += 1
                
                # Check for secrets and essential Antigravity state keys
                elif (
                    key.startswith("secret://") or 
                    "antigravity" in key.lower() or 
                    key in ["colorThemeData", "editorFontInfo", "iconThemeData"]
                ):
                    if key not in new_data:
                        # Key is missing in new DB, copy it
                        logger.info(f"Copying key: {key}")
                        if not self.dry_run:
                            new_cursor.execute("INSERT INTO ItemTable (key, value) VALUES (?, ?)", (key, old_val))
                        keys_inserted += 1
                    elif new_data[key] != old_val and key == "antigravityUserSettings.allUserSettings":
                        # Overwrite specific config if different and empty/default
                        logger.info(f"Updating user settings key: {key}")
                        if not self.dry_run:
                            new_cursor.execute("INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)", (key, old_val))
                        keys_updated += 1
                        
            if not self.dry_run:
                new_conn.commit()
                new_conn.close()
                
            logger.info(f"Database migration completed. Inserted {keys_inserted} keys, updated {keys_updated} keys.")
            
        except Exception as e:
            logger.error(f"Database migration failed: {e}")
            raise e
