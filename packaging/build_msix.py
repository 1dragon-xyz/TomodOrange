import os
import shutil
import subprocess
import sys
from PIL import Image

def build_exe():
    print("Building EXE with PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "PyInstaller", "pomodoro.spec", "--noconfirm", "--clean"])

def create_images(source_icon, dest_dir):
    print("Generating Store Assets...")
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    img = Image.open(source_icon)
    
    # Required sizes
    sizes = {
        "StoreLogo.png": (50, 50),
        "Square150x150Logo.png": (150, 150),
        "Square44x44Logo.png": (44, 44),
    }
    
    for name, size in sizes.items():
        resized = img.resize(size, Image.Resampling.LANCZOS)
        resized.save(os.path.join(dest_dir, name))

def prepare_package():
    # Only run from project root
    if not os.path.exists("pomodoro.spec"):
        print("Error: Please run this script from the project root directory.")
        return

    # 1. Build
    build_exe()
    
    # 2. Setup Staging
    dist_dir = os.path.join("dist", "MichaelsPomodoro")
    if not os.path.exists(dist_dir):
        print("Error: Build failed, dist directory not found.")
        return
        
    # 3. Copy Manifest
    shutil.copy("packaging/AppxManifest.xml", os.path.join(dist_dir, "AppxManifest.xml"))
    
    # 4. Generate Images
    # Assets folder should exist in dist/MichaelsPomodoro/assets because of spec file
    assets_dir = os.path.join(dist_dir, "assets")
    create_images(os.path.join("assets", "icon.png"), assets_dir)
    
    print("Package preparation complete.")
    print(f"Staging directory: {os.path.abspath(dist_dir)}")
    print("\nTo create the MSIX package, you need the Windows SDK 'MakeAppx' tool.")
    print("Run the following command:")
    print(f'MakeAppx pack /d "{os.path.abspath(dist_dir)}" /p "MichaelsPomodoro.msix"')

if __name__ == "__main__":
    prepare_package()
