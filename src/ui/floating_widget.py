from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QApplication
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QPalette, QFont
import ctypes
from ctypes import wintypes

class FloatingWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # State
        self.ghost_mode = False
        self.drag_pos = None
        self.current_bg_opacity = 0.0 # Default 0
        self.current_text_opacity = 1.0
        self.current_text_size = 72
        self.current_text_color = "#008080"
        
        # UI Setup
        self.init_ui()
        
    def init_ui(self):
        # Window Flags
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint |
            Qt.Tool  # Hides from taskbar
        )
        
        # App Icon
        # Try to load icon if exists, otherwise it might be set via QApplication
        from utils.path_utils import get_resource_path
        icon_path = get_resource_path('assets', 'icon.png')
        import os
        if os.path.exists(icon_path):
            from PySide6.QtGui import QIcon
            self.setWindowIcon(QIcon(icon_path))
        
        # Translucent Background
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Central Widget & Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Timer Label (Placeholder "MM" display)
        self.label = QLabel("25")
        self.label.setAlignment(Qt.AlignCenter)
        
        # Font Configuration (Segoe UI Variable Display or fallback)
        font = QFont("Segoe UI Variable Display", 72) 
        font.setBold(True)
        self.label.setFont(font)
        
        # Initial Colors (Teal for Work)
        self.update_style(text_color="#008080", bg_opacity=0.0) # 0% bg default
        
        layout.addWidget(self.label)
        
        # Sizing (Compact)
        self.resize(300, 200)

    def update_style(self, text_color, bg_opacity, text_opacity=1.0, text_size=72):
        """Updates the visual style of the widget."""
        # Use Stylesheet for both text color and background to ensure consistency
        # Also applying text opacity via rgba string or stylesheet opacity
        
        # Convert hex color to rgba for opacity control if needed, 
        # but Qt stylesheet "color" supports alpha if we parse it.
        # Simpler approach: Set widget opacity? No, that affects background too.
        # We need independent opacity.
        
        # Apply Text Size
        font = self.label.font()
        font.setPixelSize(text_size)
        self.label.setFont(font)
        
        # Apply Text Color with Opacity
        # QColor can handle this cleanly
        c = QColor(text_color)
        c.setAlphaF(text_opacity)
        rgba_color = f"rgba({c.red()}, {c.green()}, {c.blue()}, {c.alpha()})"
        self.label.setStyleSheet(f"color: {rgba_color};")
        
        # Background Styling
        self.centralWidget().setStyleSheet(
            f"background-color: rgba(255, 255, 255, {int(bg_opacity * 255)});"
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.ghost_mode:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos and not self.ghost_mode:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def toggle_ghost_mode(self, enabled):
        """
        Toggles 'Ghost Mode' (Click-through) using Windows API.
        """
        self.ghost_mode = enabled
        
        # Get Window Handle (HWND)
        hwnd = self.winId()
        
        # Windows API Constants
        GWL_EXSTYLE = -20
        WS_EX_LAYERED = 0x80000
        WS_EX_TRANSPARENT = 0x20
        
        # Get current extended style
        style = ctypes.windll.user32.GetWindowLongW(wintypes.HWND(hwnd), GWL_EXSTYLE)
        
        if enabled:
            # Add Transparent flag (Click-through) and Layered (required for transparency)
            # Note: Qt usually handles WS_EX_LAYERED for translucent windows, but we force it to hold the transparent flag.
            style = style | WS_EX_TRANSPARENT | WS_EX_LAYERED
            
            # Visual Feedback: User requested NO visual change for Ghost Mode.
            # Keeping the color consistent.
            
        else:
            # Remove Transparent flag
            style = style & ~WS_EX_TRANSPARENT
            
            # Restore Visuals: No change needed as we didn't change it.
            
        # Apply new style
        ctypes.windll.user32.SetWindowLongW(wintypes.HWND(hwnd), GWL_EXSTYLE, style)



if __name__ == "__main__":
    app = QApplication([])
    window = FloatingWidget()
    window.show()
    
    # Test Ghost Mode toggle after 3 seconds
    # from PySide6.QtCore import QTimer
    # QTimer.singleShot(3000, lambda: window.toggle_ghost_mode(True))
    
    app.exec()
