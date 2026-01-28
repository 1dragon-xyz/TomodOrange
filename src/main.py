import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QAction
from ui.floating_widget import FloatingWidget
from ui.settings_window import SettingsWindow
from ui.tray_manager import TrayIconManager
from utils.startup_manager import StartupManager
from core.timer_engine import TimerEngine
from core.audio_manager import AudioManager

def main():
    app = QApplication(sys.argv)
    
    # Prevent the app from quitting when the last window (Settings) is closed
    settings = SettingsWindow() # Init early to get defaults
    app.setQuitOnLastWindowClosed(False)
    
    # Components
    widget = FloatingWidget()
    # settings = SettingsWindow() # Already inited
    tray_manager = TrayIconManager()
    timer_engine = TimerEngine(work_minutes=settings.current_settings['work_minutes'], break_minutes=settings.current_settings['break_minutes'])
    audio_manager = AudioManager()
    
    # --- Logic connection ---
    
    # 0. Timer -> Widget (Update Time)
    timer_engine.tick.connect(widget.label.setText)
    
    # 1. Timer -> Widget (Update Visual State Work/Break)
    def handle_state_change(state):
        # Retrieve latest settings to ensure we use current colors
        current_settings = settings.get_current_settings()
        
        if state == "work":
            # Use configured Work Color
            widget.current_text_color = current_settings['work_color']
            widget.update_style(
                text_color=widget.current_text_color, 
                bg_opacity=widget.current_bg_opacity, 
                text_opacity=widget.current_text_opacity, 
                text_size=widget.current_text_size
            )
            audio_manager.stop_break_sound()
            
        elif state == "break":
            # Use configured Break Color
            widget.current_text_color = current_settings['break_color']
            widget.update_style(
                text_color=widget.current_text_color, 
                bg_opacity=widget.current_bg_opacity, 
                text_opacity=widget.current_text_opacity, 
                text_size=widget.current_text_size
            )
            audio_manager.start_break_sound()
            
    timer_engine.state_changed.connect(handle_state_change)
    
    # 2. Timer -> Audio (Ticks)
    def handle_tick_sound(time_str):
        # Play tick only during Work phase
        if timer_engine.current_state == "work":
            audio_manager.play_tick()
            
    timer_engine.tick.connect(handle_tick_sound)
    
    # 3. Settings -> Timer & Audio
    def handle_settings_change(settings_dict):
        # Visuals
        # Store current visuals for state retention
        widget.current_bg_opacity = settings_dict['bg_opacity']
        widget.current_text_opacity = settings_dict['text_opacity']
        widget.current_text_size = settings_dict['text_size']
        
        # Determine which color to apply based on CURRENT state
        if timer_engine.current_state == "work":
             widget.current_text_color = settings_dict['work_color']
        else:
             widget.current_text_color = settings_dict['break_color']

        widget.update_style(
            text_color=widget.current_text_color, 
            bg_opacity=settings_dict['bg_opacity'],
            text_opacity=settings_dict['text_opacity'],
            text_size=settings_dict['text_size']
        )
        
        # Timer Durations - Fix: Only update if changed to avoid reset
        # Check if values differ from current engine values (converted to minutes)
        current_work_min = int(timer_engine.work_seconds / 60)
        current_break_min = int(timer_engine.break_seconds / 60)
        
        if (settings_dict['work_minutes'] != current_work_min or 
            settings_dict['break_minutes'] != current_break_min):
            timer_engine.update_durations(settings_dict['work_minutes'], settings_dict['break_minutes'])
        
        # Audio Volume
        audio_manager.set_work_volume(settings_dict['work_volume'])
        audio_manager.set_break_volume(settings_dict['break_volume'])
        
        # Startup
        if settings_dict['run_at_startup'] != StartupManager.is_run_at_startup():
            StartupManager.set_run_at_startup(settings_dict['run_at_startup'])

    settings.settings_changed.connect(handle_settings_change)
    
    # Tray -> Settings / Exit
    def show_settings():
        settings.showNormal()
        settings.activateWindow()
        settings.raise_()
        
    tray_manager.show_settings_requested.connect(show_settings)
    tray_manager.quit_requested.connect(app.quit)
    
    # Tray -> Ghost Mode
    def handle_tray_ghost_toggle(enabled):
        widget.toggle_ghost_mode(enabled)
        
    tray_manager.toggle_ghost_requested.connect(handle_tray_ghost_toggle)

    # Initialize
    # Sync visual defaults from Settings (which loaded from JSON)
    current_settings = settings.get_current_settings()
    widget.current_bg_opacity = current_settings['bg_opacity']
    widget.current_text_opacity = current_settings['text_opacity']
    widget.current_text_size = current_settings['text_size']
    
    # Determine initial color based on state (likely 'work' on startup)
    # We can rely on settings defaults or logic.
    widget.current_text_color = current_settings['work_color']
    
    # Start Timer
    # Ensure UI matches init state (Work)
    widget.update_style(
        text_color=widget.current_text_color, 
        bg_opacity=widget.current_bg_opacity,
        text_opacity=widget.current_text_opacity,
        text_size=widget.current_text_size
    )
    timer_engine.start()
    
    # Apply initial Audio volumes
    audio_manager.set_work_volume(current_settings['work_volume'])
    audio_manager.set_break_volume(current_settings['break_volume'])
    
    # Initial Sync (Settings -> Widget)
    # Ensure startup registry matches our default (True) if not already set
    current_settings = settings.get_current_settings()
    if current_settings['run_at_startup'] and not StartupManager.is_run_at_startup():
        StartupManager.set_run_at_startup(True)

    widget.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
