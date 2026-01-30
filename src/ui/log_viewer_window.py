from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QTextBrowser, 
    QSplitter, QGroupBox
)
from PySide6.QtCore import Qt
from utils.log_manager import LogManager
from datetime import datetime

class LogViewerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Work Log History")
        self.resize(800, 600)
        
        self.log_manager = LogManager()
        
        layout = QVBoxLayout(self)
        
        # Splitter to resize Table vs Details
        splitter = QSplitter(Qt.Vertical)
        
        # --- Table View (Master) ---
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Task ID", "Task Name", "Session", "Rating"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch) # Stretch Task Name
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.load_details)
        
        splitter.addWidget(self.table)
        
        # --- Details View (Detail) ---
        details_group = QGroupBox("Entry Details")
        details_layout = QVBoxLayout()
        self.details_browser = QTextBrowser()
        details_layout.addWidget(self.details_browser)
        details_group.setLayout(details_layout)
        
        splitter.addWidget(details_group)
        
        # Set initial splitter sizes (60% table, 40% details)
        splitter.setSizes([360, 240])
        
        layout.addWidget(splitter)
        
        # Load Data
        self.refresh_data()

    def refresh_data(self):
        """Reloads data from LogManager."""
        self.logs = self.log_manager.get_all_logs()
        # Sort by timestamp desc (newest first)
        self.logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        self.table.setRowCount(0)
        
        for row_idx, entry in enumerate(self.logs):
            self.table.insertRow(row_idx)
            
            # Format Date
            ts_str = entry.get('timestamp', '')
            date_str = ts_str
            try:
                dt = datetime.fromisoformat(ts_str)
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                pass
                
            self.table.setItem(row_idx, 0, QTableWidgetItem(date_str))
            self.table.setItem(row_idx, 1, QTableWidgetItem(entry.get('task_id', '')))
            self.table.setItem(row_idx, 2, QTableWidgetItem(entry.get('task_name', '')))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(entry.get('session_num_display', ''))))
            
            # Rating as Stars
            rating = entry.get('rating', 0)
            stars = "⭐" * rating if rating > 0 else "-"
            self.table.setItem(row_idx, 4, QTableWidgetItem(stars))
            
            # Store original index if needed, but we rely on self.logs order matching table
            
    def load_details(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            self.details_browser.clear()
            return
            
        row = selected_items[0].row()
        if row < len(self.logs):
            entry = self.logs[row]
            
            html = f"""
            <h3>{entry.get('task_name', 'Unknown Task')} <span style="color:#777">({entry.get('task_id','')})</span></h3>
            <p><b>Focus:</b> {entry.get('rating',0)}/5 &nbsp;|&nbsp; <b>Session:</b> {entry.get('session_num_display', '?')}</p>
            <hr>
            <h4>📦 Deliverables</h4>
            <p>{self._fmt(entry.get('deliverables'))}</p>
            
            <h4>👍/👎 Good & Bad</h4>
            <p>{self._fmt(entry.get('good_bad'))}</p>
            
            <h4>🧠 Better Way</h4>
            <p>{self._fmt(entry.get('better_way'))}</p>
            
            <h4>🪄 I Wish</h4>
            <p>{self._fmt(entry.get('wishes'))}</p>
            """
            self.details_browser.setHtml(html)

    def _fmt(self, text):
        if not text: return "<i>(Empty)</i>"
        return text.replace("\n", "<br>")

    def showEvent(self, event):
        """Refresh when shown."""
        self.refresh_data()
        super().showEvent(event)
