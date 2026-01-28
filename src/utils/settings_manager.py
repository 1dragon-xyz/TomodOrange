import json
import os
from PySide6.QtCore import QObject

class SettingsManager:
    SETTINGS_FILE = os.path.join(os.getcwd(), 'settings.json')
    
    DEFAULT_SETTINGS = {
        "work_minutes": 25,
        "break_minutes": 5,
        "work_color": "#008080",
        "break_color": "#7FB069",
        "text_size": 72,
        "text_opacity": 1.0,
        "bg_opacity": 0.0,
        "work_volume": 50,
        "break_volume": 50,
        "run_at_startup": True
    }

    @staticmethod
    def load_settings():
        """Load settings from JSON file, merge with defaults."""
        if not os.path.exists(SettingsManager.SETTINGS_FILE):
            return SettingsManager.DEFAULT_SETTINGS.copy()
        
        try:
            with open(SettingsManager.SETTINGS_FILE, 'r') as f:
                saved_settings = json.load(f)
                
            # Merge with defaults to ensure all keys exist
            settings = SettingsManager.DEFAULT_SETTINGS.copy()
            settings.update(saved_settings)
            return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            return SettingsManager.DEFAULT_SETTINGS.copy()

    @staticmethod
    def save_settings(settings_dict):
        """Save settings dict to JSON file."""
        try:
            with open(SettingsManager.SETTINGS_FILE, 'w') as f:
                json.dump(settings_dict, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
