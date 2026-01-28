import sys
import os

def get_resource_path(*relative_segments):
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    Args:
        *relative_segments: path segments (e.g. 'assets', 'icon.png')
    """
    if getattr(sys, 'frozen', False):
        # We are running in a bundle (PyInstaller)
        # For onedir mode, the executable directory is the base
        base_path = os.path.dirname(sys.executable)
    else:
        # We are running in normal python environment
        # Assuming run from root of the project
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    return os.path.join(base_path, *relative_segments)
