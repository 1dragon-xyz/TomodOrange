from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Signal, QObject, Qt

class TrayIconManager(QObject):
    # Signals
    show_settings_requested = Signal()
    toggle_ghost_requested = Signal(bool)
    quit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create Tray Icon
        # Note: We need a valid icon path. For now we might generate a placeholder or use standard.
        # sprint 1 used a text label, here we need a pixel icon.
        self.tray_icon = QSystemTrayIcon(parent)
        
        # Try to load real icon
        import os
        icon_path = os.path.join(os.getcwd(), 'assets', 'icon.png')
        
        if os.path.exists(icon_path):
             self.tray_icon.setIcon(QIcon(icon_path))
        else:
            # Fallback to generated pixel
            from PySide6.QtGui import QPixmap, QPainter, QColor
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setBrush(QColor("#008080")) # Teal
            painter.drawEllipse(0, 0, 16, 16)
            painter.end()
            self.tray_icon.setIcon(QIcon(pixmap))
        self.tray_icon.setToolTip("Michael's Pomodoro")
        
        # Context Menu
        self.menu = QMenu()
        self.init_menu()
        self.tray_icon.setContextMenu(self.menu)
        
        self.tray_icon.show()
        
        # On click
        self.tray_icon.activated.connect(self.on_tray_activated)

    def init_menu(self):
        # Status (Disabled Action acting as label)
        # Status (Disabled Action acting as label)
        # self.status_action = QAction("25 Minutes Remaining", self.menu) # Removed per feedback
        # self.status_action.setEnabled(False)
        # self.menu.addAction(self.status_action)
        
        # self.menu.addSeparator()
        
        # Ghost Mode Toggle
        self.ghost_action = QAction("Ghost Mode", self.menu)
        self.ghost_action.setCheckable(True)
        self.ghost_action.triggered.connect(lambda c: self.toggle_ghost_requested.emit(c))
        self.menu.addAction(self.ghost_action)
        
        self.menu.addSeparator()
        
        # Settings
        self.settings_action = QAction("Settings", self.menu)
        self.settings_action.triggered.connect(self.show_settings_requested.emit)
        self.menu.addAction(self.settings_action)
        
        self.menu.addSeparator()
        
        # Exit
        self.quit_action = QAction("Exit", self.menu)
        self.quit_action.triggered.connect(self.quit_requested.emit)
        self.menu.addAction(self.quit_action)

    def update_ghost_state(self, is_ghost):
        """Update the menu check state if changed externally."""
        # Block signals to prevent feedback loop if needed
        self.ghost_action.blockSignals(True)
        self.ghost_action.setChecked(is_ghost)
        self.ghost_action.blockSignals(False)

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            # Left click -> could toggle settings or just bring widget to front
            self.show_settings_requested.emit()
