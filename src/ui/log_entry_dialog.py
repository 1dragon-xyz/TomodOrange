from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QComboBox, QTextEdit, QPushButton, 
    QGroupBox, QWidget, QButtonGroup
)
from PySide6.QtCore import Qt, Signal
from utils.log_manager import LogManager

class LogEntryDialog(QDialog):
    def __init__(self, parent=None, mode="logging"):
        super().__init__(parent)
        self.mode = mode # "logging" or "planning"
        
        if self.mode == "planning":
            self.setWindowTitle("Plan Next Session")
        else:
            self.setWindowTitle("Work Log")
            
        self.resize(500, 600)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        self.log_manager = LogManager()
        
        # Layout
        layout = QVBoxLayout(self)
        
        # --- Task Identity ---
        task_group = QGroupBox("Context")
        task_layout = QHBoxLayout()
        
        # Task ID (Visual only)
        self.task_id_label = QLabel("#T-")
        self.task_id_label.setStyleSheet("font-weight: bold; color: #7FB069; font-size: 14px;")
        
        # Task Name (Editable + History)
        self.task_combo = QComboBox()
        self.task_combo.setEditable(True)
        self.task_combo.setPlaceholderText("Task Name...")
        self.populate_tasks()
        self.task_combo.editTextChanged.connect(self.update_task_details)
        
        # Session Count
        self.session_label = QLabel("Session: 1")
        
        task_layout.addWidget(self.task_id_label)
        task_layout.addWidget(self.task_combo, 1) # Stretch
        task_layout.addWidget(self.session_label)
        task_group.setLayout(task_layout)
        layout.addWidget(task_group)
        
        # --- Focus Rating ---
        rating_group = QGroupBox("Focus Level 👁️")
        rating_layout = QHBoxLayout()
        self.rating_group = QButtonGroup(self)
        
        self.rating_buttons = []
        for i in range(1, 6):
            btn = QPushButton(str(i))
            btn.setCheckable(True)
            btn.setFixedSize(40, 40)
            self.rating_group.addButton(btn, i)
            rating_layout.addWidget(btn)
            self.rating_buttons.append(btn)
            
        rating_group.setLayout(rating_layout)
        # Add a label for validation error message, initially hidden
        self.rating_error_label = QLabel("⚠️ Please rate your focus!")
        self.rating_error_label.setStyleSheet("color: red; font-weight: bold;")
        self.rating_error_label.hide()
        layout.addWidget(self.rating_error_label)
        layout.addWidget(rating_group)

        # Connect buttons to styling update
        self.rating_group.buttonClicked.connect(self._update_rating_styles)
        self._update_rating_styles() # Initial state
        
        # --- Reflections (Quadrants) ---
        # Grid layout of edits
        reflections_layout = QVBoxLayout()
        
        # Row 1
        row1 = QHBoxLayout()
        self.deliverables_edit = self._create_field("📦 Deliverables", row1)
        self.good_bad_edit = self._create_field("👍/👎 Good/Bad", row1)
        reflections_layout.addLayout(row1)
        
        # Row 2
        row2 = QHBoxLayout()
        self.better_way_edit = self._create_field("🧠 Better Way", row2)
        self.wishes_edit = self._create_field("🪄 I Wish", row2)
        reflections_layout.addLayout(row2)
        
        layout.addLayout(reflections_layout)
        
        # --- Actions ---
        btn_layout = QHBoxLayout()
        
        skip_btn = QPushButton("Skip Review")
        skip_btn.setFlat(True) # Minimal style
        skip_btn.clicked.connect(self.reject)
        skip_btn.setStyleSheet("color: #888; text-decoration: underline;")
        
        save_btn = QPushButton("Save Plan" if self.mode == "planning" else "Save Log")
        save_btn.clicked.connect(self.save_log)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: %s; 
                color: white; 
                padding: 10px; 
                border-radius: 5px; 
                font-weight: bold;
            }
            QPushButton:hover { background-color: %s; }
        """ % ("#4CAF50" if self.mode == "planning" else "#008080", 
               "#45a049" if self.mode == "planning" else "#006666"))
        
        btn_layout.addWidget(skip_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
        
        # Initial Update
        # If Logging mode, check for Pending Plan to pre-fill
        if self.mode == "logging":
            self._apply_pending_plan()
            
        # Ensure ID/Session are updated based on what's now in the box
        self.update_task_details(self.task_combo.currentText())

    def _apply_pending_plan(self):
        """Check LogManager for a 'planned' entry and fill fields."""
        plan = self.log_manager.get_pending_plan()
        if plan:
            if plan.get('task_name'):
                self.task_combo.setCurrentText(plan['task_name'])
            if plan.get('deliverables'):
                self.deliverables_edit.setText(plan['deliverables'])

    def _create_field(self, title, parent_layout):
        container = QGroupBox(title)
        lyt = QVBoxLayout()
        edit = QTextEdit()
        edit.setPlaceholderText("Type or press [Win + H] to dictate...")
        edit.setToolTip("💡 Pro Tip: Press [Windows Key + H] to use Voice Typing for faster logging.")
        lyt.addWidget(edit)
        container.setLayout(lyt)
        parent_layout.addWidget(container)
        return edit

    def _update_rating_styles(self, btn=None):
        """Update styles of rating buttons based on selection."""
        checked_id = self.rating_group.checkedId()
        
        # Define colors for ratings 1-5 (Low -> High)
        colors = {
            1: "#FF4D4D", # Red
            2: "#FF944D", # Orange
            3: "#FFDB4D", # Yellow
            4: "#A4DE02", # Light Green
            5: "#4CAF50"  # Green
        }
        
        for button in self.rating_buttons:
            rating = self.rating_group.id(button)
            color = colors.get(rating, "#CCCCCC")
            
            if checked_id == -1:
                # No selection: all neutral but colored on hover (handled by basic stylesheet if needed, 
                # but here we'll keep them simple gray/white until selected or simple colored text)
                # Let's give them a colored border or text to indicate what they represent
                button.setStyleSheet(f"""
                    QPushButton {{
                        border: 2px solid {color};
                        border-radius: 20px;
                        background-color: white;
                        color: {color};
                        font-weight: bold;
                        font-size: 16px;
                    }}
                    QPushButton:hover {{
                        background-color: {color};
                        color: white;
                    }}
                """)
            elif rating == checked_id:
                # Selected: Full Color
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color};
                        border: 2px solid {color};
                        border-radius: 20px;
                        color: white;
                        font-weight: bold;
                        font-size: 18px;
                    }}
                """)
            else:
                # Unselected when one is active: Dimmed/Grayed out
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #F0F0F0;
                        border: 1px solid #DDD;
                        border-radius: 20px;
                        color: #BBB;
                    }
                """)

 
    def populate_tasks(self):
        """Fill combo with historical tasks."""
        # Get tasks from log manager (need to implement a unique task getter or just iterate logs)
        # For efficiency, LogManager could support `get_unique_task_names()`
        # We'll just read all logs for now.
        logs = self.log_manager.get_all_logs()
        seen = set()
        for log in logs:
            name = log.get('task_name')
            if name and name not in seen:
                self.task_combo.addItem(name)
                seen.add(name)
        
        # Select last used
        last = self.log_manager.get_last_task_name()
        if last:
            self.task_combo.setCurrentText(last)

    def update_task_details(self, text):
        """Update ID and Session count based on text input."""
        tid = self.log_manager.get_task_id(text)
        self.task_id_label.setText(tid if tid else "#T-")
        
        # Calculate Next Session ID
        # +1 because we are about to save the next one
        session_num = self.log_manager.get_next_session_number(text)
        self.session_label.setText(f"Session: {session_num}")

    def save_log(self):
        task_name = self.task_combo.currentText()
        if not task_name:
            task_name = "Unspecified Task"
            
        rating = self.rating_group.checkedId()
        
        # VALIDATION: Enforce rating in "logging" mode
        if self.mode == "logging" and rating == -1:
            self.rating_error_label.show()
            # Shake effect or visual cue could be added here
            return

        if rating == -1: rating = 0
            
        entry = {
            "task_name": task_name,
            "task_id": self.task_id_label.text(),
            "session_num_display": self.session_label.text(), # Store the string or int? Int is better.
            "rating": rating,
            "deliverables": self.deliverables_edit.toPlainText(),
            "good_bad": self.good_bad_edit.toPlainText(),
            "better_way": self.better_way_edit.toPlainText(),
            "wishes": self.wishes_edit.toPlainText(),
            "status": "planned" if self.mode == "planning" else "completed"
        }
        
        self.log_manager.save_log(entry)
        self.accept()
