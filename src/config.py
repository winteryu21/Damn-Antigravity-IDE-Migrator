import os
from dataclasses import dataclass

@dataclass
class AppPaths:
    # Roaming config folder (settings.json, state.vscdb, Local State)
    # - Windows:  %APPDATA%/Antigravity
    # - WSL2:     ~/.antigravity-server/data (no settings/db on WSL2 side)
    old_roaming: str
    new_roaming: str
    
    # Dot-folder (extensions directory and extensions.json)
    # - Windows:  ~/.antigravity
    # - WSL2:     ~/.antigravity-server
    old_dot: str
    new_dot: str
    
    # Gemini data (conversations, brain, annotations, etc.)
    # Same on both: ~/.gemini/antigravity
    old_gemini: str
    new_gemini: str

def resolve_paths(wsl2: bool = False) -> AppPaths:
    """Dynamically resolves migration paths on the user's system.
    
    Args:
        wsl2: If True, resolves paths for the WSL2 server-side layout.
              Must be run from inside WSL2 when enabled.
    """
    user_home = os.path.expanduser("~")
    
    if wsl2:
        # WSL2: server component layout with -server suffix
        return AppPaths(
            old_roaming=os.path.join(user_home, ".antigravity-server", "data"),
            new_roaming=os.path.join(user_home, ".antigravity-ide-server", "data"),
            old_dot=os.path.join(user_home, ".antigravity-server"),
            new_dot=os.path.join(user_home, ".antigravity-ide-server"),
            old_gemini=os.path.join(user_home, ".gemini", "antigravity"),
            new_gemini=os.path.join(user_home, ".gemini", "antigravity-ide")
        )
    else:
        # Windows desktop: standard AppData layout
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

