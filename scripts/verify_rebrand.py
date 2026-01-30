import os
import sys

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from utils.settings_manager import SettingsManager
from utils.startup_manager import StartupManager

def verify():
    print("Verifying Rebranding...")
    
    # 1. Assets
    assets = ['assets/icon.png', 'assets/icon.ico', 'assets/logo_full.png']
    for asset in assets:
        if os.path.exists(asset):
            print(f"[OK] Asset found: {asset}")
        else:
            print(f"[FAIL] Asset missing: {asset}")

    # 2. Settings Defaults
    defaults = SettingsManager.DEFAULT_SETTINGS
    if defaults['work_color'].upper() == "#FFA500":
        print("[OK] Default Work Color is Orange (#FFA500)")
    else:
        print(f"[FAIL] Default Work Color is {defaults['work_color']}")
        
    if defaults['break_color'].upper() == "#32CD32":
        print("[OK] Default Break Color is Lime Green (#32CD32)")
    else:
        print(f"[FAIL] Default Break Color is {defaults['break_color']}")

    # 3. Startup Manager Name
    if StartupManager.APP_NAME == "TomodOrange":
        print("[OK] Startup App Name is TomodOrange")
    else:
        print(f"[FAIL] Startup App Name is {StartupManager.APP_NAME}")

if __name__ == "__main__":
    verify()
