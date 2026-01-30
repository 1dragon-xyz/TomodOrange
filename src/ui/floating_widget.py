from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QApplication
from utils.settings_manager import SettingsManager
from PySide6.QtGui import QColor, QPalette, QFont, QPainter, QBrush, QPen, QScreen, QAction
from PySide6.QtCore import Qt, QPoint, QRectF, QLineF, QTimer
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
        
        # ANH-63: Orange Style Support
        self.timer_style = "orange" # "classic" or "orange"
        self.orange_opacity = 1.0
        self.current_mode = "work" # "work" or "break"
        self.progress = 0.0 # 0.0 to 1.0
        self.current_size_val = 72 # Store size value
        
        # Constants
        # Refined Colors (Less Carrot, more Citrus)
        self.ORANGE_PEEL = "#F57C00" # Material Orange 700
        self.ORANGE_SEGMENT = "#FFB74D" # Material Orange 200
        self.ORANGE_EMPTY = "#5D4037" # Material Brown 700 (Dark contrast)
        
        self.GREEN_PEEL = "#388E3C" # Material Green 700
        self.GREEN_SEGMENT = "#AED581" # Material Light Green 300
        self.GREEN_EMPTY = "#263238" # Material Blue Grey 900 (Dark contrast)
        
        # UI Setup
        self.init_ui()
        
        # ANH-68 & ANH-69: Restore Position or Default to Top-Middle
        self.restore_position()

    def restore_position(self):
        """
        Restores the last saved position or defaults to Top-Middle of the primary screen.
        """
        settings = SettingsManager.load_settings()
        saved_x = settings.get('widget_x')
        saved_y = settings.get('widget_y')
        
        screen = QApplication.primaryScreen()
        screen_geo = screen.availableGeometry()
        
        if saved_x is not None and saved_y is not None:
            # Validate if position is within bounds (roughly)
            # Simple check: is top-left corner within some screen?
            # For multi-monitor, this is complex. Let's just check if it's within the 'virtual desktop'.
            # A simple robust check: Is it visible on ANY screen?
            
            # For now, simplistic check:
            # If coordinates are 0,0 they might be valid.
            self.move(saved_x, saved_y)
            
            # Check if we ended up off-screen (e.g. monitor disconnected)
            # If the widget is largely offscreen, reset.
            # (TODO: Add robust off-screen detection if needed. For now, trust saved.)
        else:
            # Default: Top Middle
            # Center X, Top Y (no padding per user request)
            target_x = screen_geo.x() + (screen_geo.width() - self.width()) // 2
            target_y = screen_geo.y()
            self.move(target_x, target_y)

    def save_position(self):
        """Saves the current position to settings."""
        pos = self.pos()
        settings = SettingsManager.load_settings()
        settings['widget_x'] = pos.x()
        settings['widget_y'] = pos.y()
        SettingsManager.save_settings(settings)
        
    def init_ui(self):
        # Window Flags
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint |
            Qt.Tool  # Hides from taskbar
        )
        
        # App Icon
        # Try to load icon if exists, otherwise it might be set via QApplication
        import os
        icon_path = os.path.join(os.getcwd(), 'assets', 'icon.png')
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

    def set_timer_style(self, style):
        self.timer_style = style
        if style == "orange":
            self.label.hide()
            # Ensure background is transparent for nice circle
            self.centralWidget().setStyleSheet("background-color: transparent;")
            # Force resize to square based on current size
            s = int(self.current_size_val * 2.5) # Scale factor for visibility
            self.resize(s, s)
        else:
            self.label.show()
            # Restore background opacity logic handled by update_style
            self.update_style(self.current_text_color, self.current_bg_opacity, self.current_text_opacity, self.current_size_val)
            
        self.update()

    def set_progress(self, progress):
        self.progress = progress
        if self.timer_style == "orange":
            self.update()

    def set_mode(self, mode):
        self.current_mode = mode
        if self.timer_style == "orange":
            self.update()

    def set_orange_opacity(self, opacity):
        self.orange_opacity = opacity
        if self.timer_style == "orange":
            self.update()

    def update_style(self, text_color, bg_opacity, text_opacity=1.0, text_size=72):
        """Updates the visual style of the widget."""
        self.current_text_color = text_color
        self.current_bg_opacity = bg_opacity
        self.current_text_opacity = text_opacity
        self.current_size_val = text_size
        
        if self.timer_style == "classic":
            # Apply Text Size
            font = self.label.font()
            font.setPixelSize(text_size)
            self.label.setFont(font)
            
            # Apply Text Color with Opacity
            c = QColor(text_color)
            c.setAlphaF(text_opacity)
            rgba_color = f"rgba({c.red()}, {c.green()}, {c.blue()}, {c.alpha()})"
            self.label.setStyleSheet(f"color: {rgba_color};")
            
            # Background Styling
            self.centralWidget().setStyleSheet(
                f"background-color: rgba(255, 255, 255, {int(bg_opacity * 255)});"
            )
            
            # Resize logic for text mode (approximate)
            self.resize(int(text_size * 4), int(text_size * 2.5))
            
        else:
            # Orange Mode: Only resize, colors are hardcoded/mode based
            s = int(text_size * 2.5)
            self.resize(s, s)
            self.update()

    def paintEvent(self, event):
        if self.timer_style == "orange":
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setOpacity(self.orange_opacity)
            
            rect = self.rect()
            min_dim = min(rect.width(), rect.height())
            center = rect.center()
            radius = (min_dim / 2) * 0.9 # 10% padding
            
            peel_color = self.ORANGE_PEEL if self.current_mode == "work" else self.GREEN_PEEL
            seg_color = self.ORANGE_SEGMENT if self.current_mode == "work" else self.GREEN_SEGMENT
            empty_seg_color = self.ORANGE_EMPTY if self.current_mode == "work" else self.GREEN_EMPTY
            
            # 1. Draw Peel Frame (Ring + Connectors)
            # This frame persists even as segments disappear.
            # This meets the "separate segment using peel color" requirement.
            
            peel_thickness = radius * 0.12 # Slightly thicker
            
            # Draw Ring
            painter.setPen(QPen(QColor(peel_color), peel_thickness))
            painter.setBrush(Qt.NoBrush)
            
            # Adjust ellipse for pen width
            peel_rect = QRectF(center.x() - radius + peel_thickness/2, 
                               center.y() - radius + peel_thickness/2, 
                               (radius - peel_thickness/2) * 2, 
                               (radius - peel_thickness/2) * 2)
            
            painter.drawEllipse(peel_rect)
            
            # Draw Spokes (Separators)
            # 6 spokes.
            painter.setPen(QPen(QColor(peel_color), peel_thickness/1.5)) # Slightly thinner spokes
            
            # Inner radius for spokes (connect to center, extend to ring)
            # Start from center? Or small hub? Let's do small hub.
            # Hub radius
            hub_radius = radius * 0.05
            
            # Draw Hub
            painter.setBrush(QBrush(QColor(peel_color)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(center, hub_radius, hub_radius)
            
            # Draw Lines
            painter.setPen(QPen(QColor(peel_color), peel_thickness/2))
            
            import math
            for i in range(6):
                angle_deg = 30 + i * 60 # Centers of the gaps (30, 90, 150...)
                # No, segments are 60 deg slices. Spokes should be at boundaries.
                # Segment 0 is 12-2 (90 to 30 deg). Boundary at 90, 30.
                # Let's verify angles.
                # 0, 60, 120, 180, 240, 300.
                angle_rad = math.radians(angle_deg)
                
                # Start: Center (or hub edge)
                # End: Ring inner edge
                # Ring inner edge is radius - peel_thickness
                end_r = radius - peel_thickness/2
                
                # Calculate coords
                # Qt Coords: Y down. 0 deg is right (3 o'clock).
                # 90 deg is Down (6 o'clock)?
                # Standard Math: 0 Right. 90 Up.
                # Qt Trig (math.cos/sin) uses standard radians. Y is inverted visually only.
                # Let's just use (cos, sin) and map to center.
                
                x_end = center.x() + end_r * math.cos(angle_rad)
                y_end = center.y() + end_r * math.sin(angle_rad) # Y down for +sin? 
                # Actually let's assume standard trig logic, visuals will just be rotated.
                # Symmetry means rotation doesn't matter much for 6 spokes.
                
                painter.drawLine(center, QPoint(int(x_end), int(y_end)))
            
            # 2. Draw Segments
            # Segments fill the space between spokes.
            # We draw them "under" the spokes? Or carefully sized gaps?
            # Easier to draw segments FIRST, then draw the Frame (Peel+Spokes) on TOP.
            # This ensures clean separation.
            # Let's Reorder.
            
            # --- REORDERED PAINTING ---
            
            # A. Calculate Segments Logic
            # Loop over ALL 6 segments
            visible_count = int(6.0 * (1.0 - self.progress) + 0.99)
            if visible_count > 6: visible_count = 6
            if visible_count < 0: visible_count = 0
            
            seg_radius = radius - peel_thickness/2 # Go slightly under the ring to avoid hairline gaps
            
            painter.setPen(Qt.NoPen)
            
            for i in range(6):
                # Start Angle (CCW)
                # i=0: 90 (12h) -> 12-10
                # i=1: 150 (10h) -> 10-8
                
                # Determine Color: Is this segment visible or empty?
                # Visible segments are 0 to visible_count - 1
                if i < visible_count:
                    painter.setBrush(QBrush(QColor(seg_color)))
                else:
                    painter.setBrush(QBrush(QColor(empty_seg_color)))
                
                a_start_deg = 90 + i * 60
                
                # Full 60 deg span (Spokes will cover edges)
                final_start = a_start_deg * 16
                final_span = 60 * 16
                
                rect_seg = QRectF(center.x() - seg_radius, 
                                  center.y() - seg_radius, 
                                  seg_radius * 2, 
                                  seg_radius * 2)
                                  
                painter.drawPie(rect_seg, int(final_start), int(final_span))
            
            # B. Draw Frame (Peel Ring + Spokes) ON TOP
            
            # Draw Spokes
            painter.setPen(QPen(QColor(peel_color), peel_thickness/2))
            for i in range(6):
                # Spokes at 30, 90, 150... (Boundaries of segments centered at 0, 60...)
                # Wait, my segment i starts at 90. Ends at 150.
                # So boundaries are 90, 150, 210...
                angle_deg = 90 + i * 60 
                # Note: math functions take radians
                # Angle in Qt paint (degrees): 0 is 3 o'clock. 90 is 12 o'clock (CCW).
                # Math functions: 0 is 3 o'clock. positive CCW.
                # But Y is inverted on screen. 
                # (0,1) is Down.
                # degrees: 90 -> -90 in math logic if Y inverted?
                # Let's not overthink. The Segments align to 90, 150...
                # So we put spokes at 90, 150...
                
                # To convert "Qt Degrees" (90=Top) to "Math Radians for Screen Coordinates":
                # Top is -90 math (if Y down)? Or 270?
                # Top (0, -1). 
                # Right (1, 0).
                # 0 deg = Right.
                # 90 deg (Qt) = Top.
                # So Qt 90 corresponds to Math 270 (-90).
                # Formula: rad = -degrees * PI / 180 ? 
                # Or just use `QLineF` with polar?
                
                spoke_line = QLineF.fromPolar(radius - peel_thickness/2, angle_deg)
                # Translate to center
                spoke_line.translate(center)
                # That places start at center?
                # QLineF.fromPolar(length, angle) -> creates line starting at (0,0).
                # So we translate it.
                
                painter.drawLine(spoke_line)
                
            # Draw Hub (Center Cap)
            painter.setBrush(QBrush(QColor(peel_color)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(center, hub_radius, hub_radius)
            
            # Draw Outer Ring
            painter.setPen(QPen(QColor(peel_color), peel_thickness))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(peel_rect)
                
        else:
            # Classic: Paint nothing special, QLabel handles it.
            super().paintEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.ghost_mode:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drag_pos:
            self.drag_pos = None
            # Save position on drop
            self.save_position()
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
            
        else:
            # Remove Transparent flag
            style = style & ~WS_EX_TRANSPARENT
            
        # Apply new style
        ctypes.windll.user32.SetWindowLongW(wintypes.HWND(hwnd), GWL_EXSTYLE, style)
        
        # Re-enforce Topmost Status
        # Changing styles can sometimes reset the Z-order, so we ensure it's topmost again.
        self.enforce_topmost()

    def enforce_topmost(self):
        """
        Uses Windows API (SetWindowPos) to strictly enforce HWND_TOPMOST.
        This often works better than Qt.WindowStaysOnTopHint alone when interacting
        with other Windows API attributes like WS_EX_TRANSPARENT.
        """
        hwnd = self.winId()
        
        # Constants
        HWND_TOPMOST = -1
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_NOACTIVATE = 0x0010
        
        ctypes.windll.user32.SetWindowPos(
            wintypes.HWND(hwnd), 
            wintypes.HWND(HWND_TOPMOST), 
            0, 0, 0, 0, 
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
        )

    def showEvent(self, event):
        """
        Ensure we enforce topmost whenever the window is shown.
        """
        super().showEvent(event)
        self.enforce_topmost()




if __name__ == "__main__":
    app = QApplication([])
    window = FloatingWidget()
    window.show()
    
    # Test Ghost Mode toggle after 3 seconds
    # from PySide6.QtCore import QTimer
    # QTimer.singleShot(3000, lambda: window.toggle_ghost_mode(True))
    
    app.exec()
