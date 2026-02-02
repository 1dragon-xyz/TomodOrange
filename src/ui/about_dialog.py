from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame
from PySide6.QtGui import QDesktopServices, QFont, QIcon
from PySide6.QtCore import Qt, QUrl
import os
from utils.constants import APP_NAME, APP_VERSION, DEVELOPER_NAME, WEBSITE_URL, SUPPORT_EMAIL

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setFixedSize(300, 350)
        
        # Set Window Icon (same as app icon)
        icon_path = os.path.join(os.getcwd(), 'assets', 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 30, 20, 30)
        
        # --- App Logo/Icon display ---
        # We can reuse the visual logic or just simply draw the icon if available
        # For simplicity, let's just use the text first, but if we had the logo image we'd show it.
        # Let's try to show the icon if it exists via a Pixmap Label
        if os.path.exists(icon_path):
            from PySide6.QtGui import QPixmap 
            logo_label = QLabel()
            pixmap = QPixmap(icon_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
        
        # --- App Name ---
        name_label = QLabel(APP_NAME)
        name_font = QFont()
        name_font.setPointSize(16)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)
        
        # --- Version ---
        version_label = QLabel(f"Version {APP_VERSION}")
        version_label.setStyleSheet("color: #888888;")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # --- Developer Info ---
        dev_label = QLabel(f"Created by {DEVELOPER_NAME}")
        dev_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(dev_label)
        
        # --- Links ---
        
        # Website Link
        website_label = QLabel(f'<a href="{WEBSITE_URL}" style="color: #008080; text-decoration: none;">{WEBSITE_URL}</a>')
        website_label.setAlignment(Qt.AlignCenter)
        website_label.setOpenExternalLinks(True)
        website_label.setCursor(Qt.PointingHandCursor)
        layout.addWidget(website_label)
        
        # Support Email Link
        email_label = QLabel(f'<a href="mailto:{SUPPORT_EMAIL}" style="color: #008080; text-decoration: none;">{SUPPORT_EMAIL}</a>')
        email_label.setAlignment(Qt.AlignCenter)
        email_label.setOpenExternalLinks(True)
        email_label.setCursor(Qt.PointingHandCursor)
        layout.addWidget(email_label)
        
        layout.addStretch()
