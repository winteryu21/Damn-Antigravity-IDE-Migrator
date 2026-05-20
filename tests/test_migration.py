import os
import json
import sqlite3
import base64
import unittest
import tempfile
import shutil
from src.config import AppPaths
from src.backup import BackupManager
from src.file_handler import FileMigrator
from src.database import DatabaseMigrator

class TestMigrationTool(unittest.TestCase):
    
    def setUp(self):
        # Create temp directory for simulating the user's home and AppData
        self.test_dir = tempfile.TemporaryDirectory()
        base_path = self.test_dir.name
        
        # Define mock paths
        self.paths = AppPaths(
            old_roaming=os.path.join(base_path, "AppData", "Roaming", "Antigravity"),
            new_roaming=os.path.join(base_path, "AppData", "Roaming", "Antigravity IDE"),
            old_dot=os.path.join(base_path, ".antigravity"),
            new_dot=os.path.join(base_path, ".antigravity-ide"),
            old_gemini=os.path.join(base_path, "Gemini", "antigravity"),
            new_gemini=os.path.join(base_path, "Gemini", "antigravity-ide")
        )
        
        # Setup basic mock directory structures
        os.makedirs(os.path.join(self.paths.old_roaming, "User", "globalStorage"), exist_ok=True)
        os.makedirs(os.path.join(self.paths.new_roaming, "User", "globalStorage"), exist_ok=True)
        os.makedirs(os.path.join(self.paths.old_dot, "extensions"), exist_ok=True)
        os.makedirs(os.path.join(self.paths.new_dot, "extensions"), exist_ok=True)
        os.makedirs(os.path.join(self.paths.old_gemini, "conversations"), exist_ok=True)
        os.makedirs(os.path.join(self.paths.new_gemini, "conversations"), exist_ok=True)
        
    def tearDown(self):
        self.test_dir.cleanup()
        
    def test_settings_merge(self):
        old_settings = {
            "editor.fontFamily": "Pretendard",
            "workbench.colorTheme": "Solarized Light"
        }
        new_settings = {
            "workbench.colorTheme": "Solarized Dark"  # different theme in new
        }
        
        old_settings_path = os.path.join(self.paths.old_roaming, "User", "settings.json")
        new_settings_path = os.path.join(self.paths.new_roaming, "User", "settings.json")
        
        with open(old_settings_path, "w", encoding="utf-8") as f:
            json.dump(old_settings, f)
        with open(new_settings_path, "w", encoding="utf-8") as f:
            json.dump(new_settings, f)
            
        migrator = FileMigrator(self.paths)
        migrator.migrate_settings()
        
        # Verify
        with open(new_settings_path, "r", encoding="utf-8") as f:
            result = json.load(f)
            
        # Missing key should be copied
        self.assertEqual(result["editor.fontFamily"], "Pretendard")
        # Existing key should be overwritten with old preference
        self.assertEqual(result["workbench.colorTheme"], "Solarized Light")

    def test_local_state_migration(self):
        old_local_state = os.path.join(self.paths.old_roaming, "Local State")
        new_local_state = os.path.join(self.paths.new_roaming, "Local State")
        
        with open(old_local_state, "w", encoding="utf-8") as f:
            json.dump({"os_crypt": {"encrypted_key": "OLD_KEY_VALUE"}}, f)
        with open(new_local_state, "w", encoding="utf-8") as f:
            json.dump({"os_crypt": {"encrypted_key": "NEW_KEY_VALUE"}}, f)
            
        migrator = FileMigrator(self.paths)
        migrator.migrate_local_state()
        
        with open(new_local_state, "r", encoding="utf-8") as f:
            result = json.load(f)
            
        self.assertEqual(result["os_crypt"]["encrypted_key"], "OLD_KEY_VALUE")

    def test_extensions_migration(self):
        # 1. Create a dummy extension folder in old extensions
        old_ext_folder = os.path.join(self.paths.old_dot, "extensions", "my.dummy-extension-1.0.0")
        os.makedirs(old_ext_folder)
        with open(os.path.join(old_ext_folder, "package.json"), "w") as f:
            f.write('{"name": "dummy"}')
            
        # 2. Mock old and new extensions.json
        old_json = [
            {
                "identifier": {"id": "my.dummy-extension"},
                "version": "1.0.0",
                "location": {
                    "path": "/c:/Users/User/.antigravity/extensions/my.dummy-extension-1.0.0"
                }
            }
        ]
        new_json = [
            {
                "identifier": {"id": "my.existing-extension"},
                "version": "2.0.0"
            }
        ]
        
        with open(os.path.join(self.paths.old_dot, "extensions", "extensions.json"), "w") as f:
            json.dump(old_json, f)
        with open(os.path.join(self.paths.new_dot, "extensions", "extensions.json"), "w") as f:
            json.dump(new_json, f)
            
        migrator = FileMigrator(self.paths)
        migrator.migrate_extensions()
        
        # Verify folder copied
        new_ext_folder = os.path.join(self.paths.new_dot, "extensions", "my.dummy-extension-1.0.0")
        self.assertTrue(os.path.exists(new_ext_folder))
        
        # Verify extensions.json merged and paths rewritten
        with open(os.path.join(self.paths.new_dot, "extensions", "extensions.json"), "r") as f:
            result = json.load(f)
            
        self.assertEqual(len(result), 2)
        
        # Find the migrated extension in result
        migrated = next(x for x in result if x["identifier"]["id"] == "my.dummy-extension")
        self.assertEqual(
            migrated["location"]["path"],
            "/c:/Users/User/.antigravity-ide/extensions/my.dummy-extension-1.0.0"
        )

    def test_gemini_data_sync(self):
        # Create a conversation file in old
        convo_file = os.path.join(self.paths.old_gemini, "conversations", "convo1.pb")
        with open(convo_file, "wb") as f:
            f.write(b"protobuf content")
            
        # Run sync
        migrator = FileMigrator(self.paths)
        migrator.migrate_gemini_data()
        
        # Verify copied
        new_convo_file = os.path.join(self.paths.new_gemini, "conversations", "convo1.pb")
        self.assertTrue(os.path.exists(new_convo_file))
        with open(new_convo_file, "rb") as f:
            self.assertEqual(f.read(), b"protobuf content")

    def test_database_migration_with_merge(self):
        old_db_path = os.path.join(self.paths.old_roaming, "User", "globalStorage", "state.vscdb")
        new_db_path = os.path.join(self.paths.new_roaming, "User", "globalStorage", "state.vscdb")
        
        # Setup old DB with trajectory summaries and a secret key
        old_conn = sqlite3.connect(old_db_path)
        old_conn.execute("CREATE TABLE ItemTable (key TEXT PRIMARY KEY, value TEXT)")
        # Trajectory base64 "A"
        old_conn.execute(
            "INSERT INTO ItemTable (key, value) VALUES (?, ?)", 
            ("antigravityUnifiedStateSync.trajectorySummaries", base64.b64encode(b"OLD_TRAJECTORY").decode())
        )
        old_conn.execute(
            "INSERT INTO ItemTable (key, value) VALUES (?, ?)", 
            ("secret://my_key", "secret_value")
        )
        old_conn.execute(
            "INSERT INTO ItemTable (key, value) VALUES (?, ?)", 
            ("antigravityUserSettings.allUserSettings", "settings_value")
        )
        old_conn.commit()
        old_conn.close()
        
        # Setup new DB with some trajectory summaries and a conflicting settings key
        new_conn = sqlite3.connect(new_db_path)
        new_conn.execute("CREATE TABLE ItemTable (key TEXT PRIMARY KEY, value TEXT)")
        new_conn.execute(
            "INSERT INTO ItemTable (key, value) VALUES (?, ?)", 
            ("antigravityUnifiedStateSync.trajectorySummaries", base64.b64encode(b"NEW_TRAJECTORY").decode())
        )
        new_conn.execute(
            "INSERT INTO ItemTable (key, value) VALUES (?, ?)", 
            ("antigravityUserSettings.allUserSettings", "settings_value_new")
        )
        new_conn.commit()
        new_conn.close()
        
        # Run migration
        migrator = DatabaseMigrator(self.paths)
        migrator.migrate()
        
        # Verify merging results
        new_conn = sqlite3.connect(new_db_path)
        cursor = new_conn.cursor()
        cursor.execute("SELECT key, value FROM ItemTable")
        results = {row[0]: row[1] for row in cursor.fetchall()}
        new_conn.close()
        
        # Secret should be copied
        self.assertEqual(results["secret://my_key"], "secret_value")
        # Settings should be copied
        self.assertEqual(results["antigravityUserSettings.allUserSettings"], "settings_value")
        # Trajectories should be binary concatenated
        merged_bytes = base64.b64decode(results["antigravityUnifiedStateSync.trajectorySummaries"])
        self.assertEqual(merged_bytes, b"OLD_TRAJECTORYNEW_TRAJECTORY")

    def test_backup_and_restore(self):
        # Create files to back up
        settings_path = os.path.join(self.paths.new_roaming, "User", "settings.json")
        with open(settings_path, "w") as f:
            f.write('{"test": "original"}')
            
        backup_mgr = BackupManager(self.paths)
        backup_path = backup_mgr.create_backup()
        
        # Verify backup folder exists and contains the backed up file
        self.assertTrue(os.path.exists(os.path.join(backup_path, "settings.json")))
        
        # Modify original file
        with open(settings_path, "w") as f:
            f.write('{"test": "modified"}')
            
        # Restore
        backup_mgr.restore_backup(backup_path)
        
        # Verify restored
        with open(settings_path, "r") as f:
            self.assertEqual(f.read(), '{"test": "original"}')

    def test_backup_cleanup(self):
        settings_path = os.path.join(self.paths.new_roaming, "User", "settings.json")
        with open(settings_path, "w") as f:
            f.write('{"test": "original"}')
            
        backup_mgr = BackupManager(self.paths)
        backup_path = backup_mgr.create_backup()
        
        self.assertTrue(os.path.exists(backup_path))
        
        # Clean backups
        backup_mgr.clean_backups()
        
        # Verify backup directory does not exist anymore
        self.assertFalse(os.path.exists(backup_mgr.backup_dir))

if __name__ == "__main__":
    unittest.main()
