from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, 
    QSpinBox, QCheckBox, QColorDialog, QPushButton, QGroupBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from utils.settings_manager import SettingsManager

class SettingsWindow(QWidget):
    # Signals to update the main widget/logic
    settings_changed = Signal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings - Michael's Pomodoro")
        self.resize(350, 500)
        
        # App Icon
        import os
        icon_path = os.path.join(os.getcwd(), 'assets', 'icon.png')
        if os.path.exists(icon_path):
            from PySide6.QtGui import QIcon
            self.setWindowIcon(QIcon(icon_path))
        
        # Load persisted settings
        self.current_settings = SettingsManager.load_settings()
        
        # Main Layout
        layout = QVBoxLayout(self)
        
        # --- Timer Section ---
        timer_group = QGroupBox("Timer Durations (Minutes)")
        timer_layout = QHBoxLayout()
        
        self.work_input = QSpinBox()
        self.work_input.setRange(1, 120)
        self.work_input.setValue(self.current_settings['work_minutes'])
        self.work_input.setPrefix("Work: ")
        
        self.break_input = QSpinBox()
        self.break_input.setRange(1, 60)
        self.break_input.setValue(self.current_settings['break_minutes'])
        self.break_input.setPrefix("Break: ")
        
        timer_layout.addWidget(self.work_input)
        timer_layout.addWidget(self.break_input)
        timer_group.setLayout(timer_layout)
        layout.addWidget(timer_group)
        
        # --- Visuals Section ---
        visuals_group = QGroupBox("Visual Appearance")
        visuals_layout = QVBoxLayout()
        
        # Color Pickers
        colors_layout = QHBoxLayout()
        self.work_color_btn = QPushButton("Work Color")
        self.work_color = self.current_settings['work_color']
        self.work_color_btn.clicked.connect(lambda: self.open_color_picker("work"))
        
        self.break_color_btn = QPushButton("Break Color")
        self.break_color = self.current_settings['break_color']
        self.break_color_btn.clicked.connect(lambda: self.open_color_picker("break"))
        
        colors_layout.addWidget(self.work_color_btn)
        colors_layout.addWidget(self.break_color_btn)
        
        # Text Size
        self.size_slider = self._create_slider("Text Size", 12, 150, self.current_settings['text_size'])
        
        # Opacity Sliders (Default 0% for BG per feedback)
        self.text_opacity_slider = self._create_slider("Text Opacity", 10, 100, int(self.current_settings['text_opacity']*100))
        self.bg_opacity_slider = self._create_slider("Background Opacity", 0, 100, int(self.current_settings['bg_opacity']*100))
        
        visuals_layout.addLayout(colors_layout)
        visuals_layout.addLayout(self.size_slider['layout'])
        visuals_layout.addLayout(self.text_opacity_slider['layout'])
        visuals_layout.addLayout(self.bg_opacity_slider['layout'])
        visuals_group.setLayout(visuals_layout)
        layout.addWidget(visuals_group)
        
        # --- Audio Section ---
        audio_group = QGroupBox("Audio Levels")
        audio_layout = QVBoxLayout()
        audio_group = QGroupBox("Audio Levels")
        audio_layout = QVBoxLayout()
        self.work_vol_slider = self._create_slider("Work Volume (Tic)", 0, 100, self.current_settings['work_volume'])
        self.break_vol_slider = self._create_slider("Break Volume (Waves)", 0, 100, self.current_settings['break_volume'])
        
        audio_layout.addLayout(self.work_vol_slider['layout'])
        audio_layout.addLayout(self.break_vol_slider['layout'])
        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)
        
        # --- System Section ---
        system_group = QGroupBox("System")
        system_layout = QVBoxLayout()
        
        # self.ghost_mode_check = QCheckBox("Ghost Mode (Click-Through)") # Removed per feedback
        self.startup_check = QCheckBox("Run at Startup")
        # self.ghost_mode_check = QCheckBox("Ghost Mode (Click-Through)") # Removed per feedback
        self.startup_check = QCheckBox("Run at Startup")
        self.startup_check.setChecked(self.current_settings['run_at_startup'])
        
        # system_layout.addWidget(self.ghost_mode_check)
        system_layout.addWidget(self.startup_check)
        system_group.setLayout(system_layout)
        layout.addWidget(system_group)
        
        # Connect Signals
        self._connect_signals()
        
    def _create_slider(self, label_text, min_val, max_val, default):
        layout = QVBoxLayout()
        label = QLabel(f"{label_text}: {default}")
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        
        # Add widgets to layout
        layout.addWidget(label)
        layout.addWidget(slider)
        
        # Update label on change
        slider.valueChanged.connect(lambda v: label.setText(f"{label_text}: {v}"))
        
        return {'layout': layout, 'slider': slider, 'label': label}

    def _connect_signals(self):
        # We'll emit a consolidated signal for simplicity or individual ones
        # For now, let's wire up the critical visual ones to emit immediately
        self.size_slider['slider'].valueChanged.connect(self.emit_settings)
        self.text_opacity_slider['slider'].valueChanged.connect(self.emit_settings)
        self.bg_opacity_slider['slider'].valueChanged.connect(self.emit_settings)
        # self.ghost_mode_check.toggled.connect(self.emit_settings)
        self.startup_check.toggled.connect(self.emit_settings)
        
        # Inputs that might need 'editingFinished' or valueChanged
        self.work_input.valueChanged.connect(self.emit_settings)
        self.break_input.valueChanged.connect(self.emit_settings)
        self.work_vol_slider['slider'].valueChanged.connect(self.emit_settings)
        self.break_vol_slider['slider'].valueChanged.connect(self.emit_settings)

    def open_color_picker(self, mode):
        default = self.work_color if mode == "work" else self.break_color
        color = QColorDialog.getColor(QColor(default), self, f"Select {mode.capitalize()} Color")
        
        if color.isValid():
            if mode == "work":
                self.work_color = color.name()
            else:
                self.break_color = color.name()
            self.emit_settings()

    def get_current_settings(self):
        return {
            "work_minutes": self.work_input.value(),
            "break_minutes": self.break_input.value(),
            "work_color": self.work_color,
            "break_color": self.break_color,
            "text_size": self.size_slider['slider'].value(),
            "text_opacity": self.text_opacity_slider['slider'].value() / 100.0,
            "bg_opacity": self.bg_opacity_slider['slider'].value() / 100.0,
            "work_volume": self.work_vol_slider['slider'].value(),
            "break_volume": self.break_vol_slider['slider'].value(),
            # "ghost_mode": self.ghost_mode_check.isChecked(),
            "run_at_startup": self.startup_check.isChecked()
        }

    def emit_settings(self):
        settings = self.get_current_settings()
        SettingsManager.save_settings(settings)
        self.settings_changed.emit(settings)

    def closeEvent(self, event):
        # Minimize instead of close if this was a separate window, 
        # but since we hide it, 'close' just hides it usually. 
        # We ensure it just hides.
        event.ignore()
        self.hide()
