import os
from dataclasses import dataclass

@dataclass
class AppPaths:
    # Roaming AppData folders (contains settings.json and state.vscdb)
    old_roaming: str
    new_roaming: str
    
    # User Profile dot-folders (contains extensions and argv.json)
    old_dot: str
    new_dot: str
    
    # Gemini folders (contains conversations and brain states)
    old_gemini: str
    new_gemini: str

def resolve_paths() -> AppPaths:
    """Dynamically resolves migration paths on the user's system."""
    user_home = os.path.expanduser("~")
    app_data = os.environ.get("APPDATA")
    
    if not app_data:
        raise EnvironmentError("APPDATA environment variable is not defined.")
        
    return AppPaths(
        old_roaming=os.path.join(app_data, "Antigravity"),
        new_roaming=os.path.join(app_data, "Antigravity IDE"),
        old_dot=os.path.join(user_home, ".antigravity"),
        new_dot=os.path.join(user_home, ".antigravity-ide"),
        old_gemini=os.path.join(user_home, ".gemini", "antigravity"),
        new_gemini=os.path.join(user_home, ".gemini", "antigravity-ide")
    )
