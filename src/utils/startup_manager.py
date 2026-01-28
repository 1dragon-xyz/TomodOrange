import os
import sys
import subprocess

class StartupManager:
    APP_NAME = "Michael's Pomodoro"

    @staticmethod
    def _get_shortcut_path():
        startup_folder = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
        return os.path.join(startup_folder, f"{StartupManager.APP_NAME}.lnk")

    @staticmethod
    def is_run_at_startup():
        """Check if the app shortcut exists in startup folder."""
        if getattr(sys, 'frozen', False):
            # When packaged (e.g. MSIX), startup is managed by the OS/Manifest.
            # We assume it is enabled by default or managed via Task Manager.
            return True
        return os.path.exists(StartupManager._get_shortcut_path())

    @staticmethod
    def set_run_at_startup(enabled):
        """Enable or disable warning at startup by creating/removing a shortcut."""
        if getattr(sys, 'frozen', False):
            print("Startup management is handled by Windows Store ecosystem for packaged app.")
            return True

        shortcut_path = StartupManager._get_shortcut_path()
        
        if enabled:
            # Create Shortcut using VBScript (Standard method without pywin32)
            try:
                # Target: pythonw.exe (no console)
                python_exe = sys.executable.replace("python.exe", "pythonw.exe")
                if not os.path.exists(python_exe):
                    python_exe = sys.executable # Fallback
                
                script_path = os.path.abspath(sys.argv[0])
                src_dir = os.path.dirname(script_path) # .../src
                project_root = os.path.dirname(src_dir) # .../michaels-pomodoro
                
                # Check where assets is. If main.py is run from root, logic differs?
                # Best to check existence.
                icon_path_root = os.path.join(project_root, "assets", "icon.png")
                icon_path_src = os.path.join(src_dir, "assets", "icon.png")
                
                if os.path.exists(icon_path_root):
                    icon_path = icon_path_root
                else:
                    icon_path = icon_path_src
                
                # IMPORTANT: Set working dir to project root (where assets usually are relative to)
                # If we use src_dir, os.getcwd() becomes src and assets/audio won't be found.
                working_dir = project_root
                
                # However, we must ensure project_root is valid. 
                if not os.path.exists(os.path.join(working_dir, "assets")):
                    # Fallback if structure is different
                    working_dir = src_dir
                
                # VBScript to create shortcut
                vbs_script = f"""
                Set oWS = WScript.CreateObject("WScript.Shell")
                Set oLink = oWS.CreateShortcut("{shortcut_path}")
                oLink.TargetPath = "{python_exe}"
                oLink.Arguments = "{script_path}"
                oLink.WorkingDirectory = "{working_dir}"
                oLink.IconLocation = "{icon_path}"
                oLink.Save
                """
                
                # Write temp vbs file
                vbs_path = os.path.join(working_dir, "create_shortcut.vbs")
                with open(vbs_path, "w") as f:
                    f.write(vbs_script)
                
                # Execute
                subprocess.run(["cscript", "//Nologo", vbs_path], check=True)
                
                # Cleanup
                if os.path.exists(vbs_path):
                    os.remove(vbs_path)
                    
                return True
            except Exception as e:
                print(f"Error creating shortcut: {e}")
                return False
        else:
            # Remove Shortcut
            try:
                if os.path.exists(shortcut_path):
                    os.remove(shortcut_path)
                return True
            except Exception as e:
                print(f"Error removing shortcut: {e}")
                return False
