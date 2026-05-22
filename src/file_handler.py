import os
import json
import shutil
import logging
from src.config import AppPaths

logger = logging.getLogger("migration")

class FileMigrator:
    """Handles migration of settings.json, extensions directories, and .gemini folder data."""
    
    def __init__(self, paths: AppPaths, dry_run: bool = False):
        self.paths = paths
        self.dry_run = dry_run
        
    def migrate_settings(self) -> None:
        """Merges settings.json from old AppData to new AppData."""
        old_settings_path = os.path.join(self.paths.old_roaming, "User", "settings.json")
        new_settings_path = os.path.join(self.paths.new_roaming, "User", "settings.json")
        
        if not os.path.exists(old_settings_path):
            logger.warning(f"Old settings.json not found at {old_settings_path}. Skipping settings migration.")
            return
            
        logger.info(f"Migrating settings from {old_settings_path} to {new_settings_path}")
        
        try:
            with open(old_settings_path, "r", encoding="utf-8") as f:
                old_settings = json.load(f)
        except Exception as e:
            logger.error(f"Failed to read old settings.json: {e}")
            return
            
        new_settings = {}
        if os.path.exists(new_settings_path):
            try:
                with open(new_settings_path, "r", encoding="utf-8") as f:
                    new_settings = json.load(f)
            except Exception as e:
                logger.error(f"Failed to read existing new settings.json: {e}")
                
        # Merge settings (old settings overwrite new settings)
        merged = False
        for key, value in old_settings.items():
            if key not in new_settings or new_settings[key] != value:
                logger.info(f"Updating setting: {key} -> {value}")
                new_settings[key] = value
                merged = True
                
        if merged:
            if self.dry_run:
                logger.info(f"[Dry-Run] Would write merged settings to {new_settings_path}")
            else:
                try:
                    os.makedirs(os.path.dirname(new_settings_path), exist_ok=True)
                    with open(new_settings_path, "w", encoding="utf-8") as f:
                        json.dump(new_settings, f, indent=4, ensure_ascii=False)
                    logger.info("Successfully merged settings.json")
                except Exception as e:
                    logger.error(f"Failed to write merged settings.json: {e}")
                    raise e
        else:
            logger.info("No new settings to merge.")

    def migrate_local_state(self) -> None:
        """Copies or merges Local State containing safeStorage encryption master keys."""
        old_local_state = os.path.join(self.paths.old_roaming, "Local State")
        new_local_state = os.path.join(self.paths.new_roaming, "Local State")
        
        if not os.path.exists(old_local_state):
            logger.warning(f"Old Local State not found at {old_local_state}. Skipping Local State migration.")
            return
            
        logger.info(f"Migrating Local State from {old_local_state} to {new_local_state}")
        
        try:
            with open(old_local_state, "r", encoding="utf-8") as f:
                old_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to read old Local State: {e}")
            return
            
        new_data = {}
        if os.path.exists(new_local_state):
            try:
                with open(new_local_state, "r", encoding="utf-8") as f:
                    new_data = json.load(f)
            except Exception as e:
                logger.error(f"Failed to read existing new Local State: {e}")
                
        # Overwrite new Local State's encryption key with the old one
        old_os_crypt = old_data.get("os_crypt", {})
        if old_os_crypt:
            new_data["os_crypt"] = old_os_crypt
            
            if self.dry_run:
                logger.info(f"[Dry-Run] Would write master encryption key to {new_local_state}")
            else:
                try:
                    os.makedirs(os.path.dirname(new_local_state), exist_ok=True)
                    with open(new_local_state, "w", encoding="utf-8") as f:
                        json.dump(new_data, f, indent=4, ensure_ascii=False)
                    logger.info("Successfully migrated Local State (safeStorage encryption key)")
                except Exception as e:
                    logger.error(f"Failed to write merged Local State: {e}")
                    raise e


    def migrate_extensions(self) -> None:
        """Copies physical extensions and merges/rewrites paths in extensions.json."""
        old_ext_dir = os.path.join(self.paths.old_dot, "extensions")
        new_ext_dir = os.path.join(self.paths.new_dot, "extensions")
        
        if not os.path.exists(old_ext_dir):
            logger.warning(f"Old extensions directory not found at {old_ext_dir}. Skipping extensions migration.")
            return
            
        logger.info(f"Migrating extensions from {old_ext_dir} to {new_ext_dir}")
        
        if not self.dry_run:
            os.makedirs(new_ext_dir, exist_ok=True)
            
        # 1. Copy physical extension directories
        try:
            for item in os.listdir(old_ext_dir):
                if item in [".obsolete", "extensions.json"]:
                    continue
                old_item_path = os.path.join(old_ext_dir, item)
                new_item_path = os.path.join(new_ext_dir, item)
                
                if os.path.isdir(old_item_path):
                    if not os.path.exists(new_item_path):
                        logger.info(f"Copying extension directory: {item}")
                        if not self.dry_run:
                            shutil.copytree(old_item_path, new_item_path)
                    else:
                        logger.debug(f"Extension directory already exists: {item}")
        except Exception as e:
            logger.error(f"Failed to copy extension directories: {e}")
            raise e
            
        # 2. Merge and rewrite extensions.json
        old_json_path = os.path.join(old_ext_dir, "extensions.json")
        new_json_path = os.path.join(new_ext_dir, "extensions.json")
        
        if os.path.exists(old_json_path):
            try:
                with open(old_json_path, "r", encoding="utf-8") as f:
                    old_exts = json.load(f)
            except Exception as e:
                logger.error(f"Failed to read old extensions.json: {e}")
                return
                
            new_exts = []
            if os.path.exists(new_json_path):
                try:
                    with open(new_json_path, "r", encoding="utf-8") as f:
                        new_exts = json.load(f)
                except Exception as e:
                    logger.error(f"Failed to read existing new extensions.json: {e}")
                    
            # Map existing extensions by ID
            existing_ids = {ext["identifier"]["id"].lower() for ext in new_exts}
            
            merged_count = 0
            for ext in old_exts:
                ext_id = ext["identifier"]["id"].lower()
                if ext_id not in existing_ids:
                    # Convert paths in this extension metadata dict
                    ext_str = json.dumps(ext)
                    # Replace paths from .antigravity to .antigravity-ide (Windows desktop)
                    ext_str = ext_str.replace("/.antigravity/extensions", "/.antigravity-ide/extensions")
                    ext_str = ext_str.replace("\\.antigravity\\extensions", "\\.antigravity-ide\\extensions")
                    ext_str = ext_str.replace(".antigravity/extensions", ".antigravity-ide/extensions")
                    ext_str = ext_str.replace(".antigravity\\\\extensions", ".antigravity-ide\\\\extensions")
                    # Replace paths from .antigravity-server to .antigravity-ide-server (WSL2)
                    ext_str = ext_str.replace(".antigravity-server/extensions", ".antigravity-ide-server/extensions")
                    
                    merged_ext = json.loads(ext_str)
                    new_exts.append(merged_ext)
                    logger.info(f"Adding extension metadata for: {ext['identifier']['id']}")
                    merged_count += 1
                    
            if merged_count > 0:
                if self.dry_run:
                    logger.info(f"[Dry-Run] Would write merged extensions.json to {new_json_path}")
                else:
                    try:
                        with open(new_json_path, "w", encoding="utf-8") as f:
                            json.dump(new_exts, f, indent=4, ensure_ascii=False)
                        logger.info(f"Merged extensions.json successfully. Added {merged_count} items.")
                    except Exception as e:
                        logger.error(f"Failed to write merged extensions.json: {e}")
                        raise e
            else:
                logger.info("No new extensions to merge in extensions.json.")

    def migrate_gemini_data(self) -> None:
        """Synchronizes conversations and other data under the .gemini directory."""
        if not os.path.exists(self.paths.old_gemini):
            logger.warning(f"Old Gemini directory not found at {self.paths.old_gemini}. Skipping Gemini data sync.")
            return
            
        logger.info(f"Synchronizing Gemini data from {self.paths.old_gemini} to {self.paths.new_gemini}")
        
        # Folder list to check and copy
        data_dirs = [
            "conversations", "brain", "prompting", "scratch", "context_state",
            "annotations", "browser_recordings", "html_artifacts", "implicit", "knowledge",
            "code_tracker"
        ]
        
        for sub_dir in data_dirs:
            old_sub_path = os.path.join(self.paths.old_gemini, sub_dir)
            new_sub_path = os.path.join(self.paths.new_gemini, sub_dir)
            
            if os.path.exists(old_sub_path):
                if not os.path.exists(new_sub_path):
                    logger.info(f"Creating new Gemini sub-directory: {sub_dir}")
                    if not self.dry_run:
                        os.makedirs(new_sub_path, exist_ok=True)
                        
                # Copy items inside
                for item in os.listdir(old_sub_path):
                    old_item_path = os.path.join(old_sub_path, item)
                    new_item_path = os.path.join(new_sub_path, item)
                    
                    if os.path.isdir(old_item_path):
                        if not os.path.exists(new_item_path):
                            logger.info(f"Copying folder: {os.path.join(sub_dir, item)}")
                            if not self.dry_run:
                                shutil.copytree(old_item_path, new_item_path)
                    else:
                        if not os.path.exists(new_item_path):
                            logger.info(f"Copying file: {os.path.join(sub_dir, item)}")
                            if not self.dry_run:
                                shutil.copy2(old_item_path, new_item_path)
