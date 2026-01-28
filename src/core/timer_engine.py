from PySide6.QtCore import QObject, QTimer, Signal

class TimerEngine(QObject):
    # Signals
    tick = Signal(str) # Emits current time string "MM" or "MM:SS" (conceptually we only show MM but engine knows all)
    state_changed = Signal(str) # "work" or "break"
    completed = Signal() # Timer finished a cycle

    def __init__(self, work_minutes=25, break_minutes=5):
        super().__init__()
        
        self.work_seconds = work_minutes * 60
        self.break_seconds = break_minutes * 60
        
        self.current_state = "work" # or "break"
        self.remaining_seconds = self.work_seconds
        
        self.timer = QTimer()
        self.timer.setInterval(1000) # 1 second
        self.timer.timeout.connect(self._on_tick)
        
        self.is_running = False

    def start(self):
        self.is_running = True
        self.timer.start()

    def stop(self):
        self.is_running = False
        self.timer.stop()
        
    def toggle_pause(self):
        if self.is_running:
            self.stop()
        else:
            self.start()

    def update_durations(self, work_mins, break_mins):
        """Update durations and restart current current state with new time."""
        self.work_seconds = work_mins * 60
        self.break_seconds = break_mins * 60
        
        # Reset current state to new duration immediately
        if self.current_state == "work":
            self.remaining_seconds = self.work_seconds
        else:
            self.remaining_seconds = self.break_seconds
            
        self._emit_tick()
        
    def reset_timer(self):
        self.stop()
        self.current_state = "work"
        self.remaining_seconds = self.work_seconds
        self._emit_tick()
        self.state_changed.emit(self.current_state)

    def _on_tick(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self._emit_tick()
        else:
            self._switch_state()

    def _switch_state(self):
        trigger_auto_start = True # Requirements imply continuous flow ("looping waves" etc)
        
        if self.current_state == "work":
            self.current_state = "break"
            self.remaining_seconds = self.break_seconds
        else:
            self.current_state = "work"
            self.remaining_seconds = self.work_seconds
            
        self.state_changed.emit(self.current_state)
        self._emit_tick()
        
        if not trigger_auto_start:
            self.stop()

    def _emit_tick(self):
        """Format logic: Minutes only.
        Rounded UP (Ceiling). 
        23:44 -> 24
        11:50 -> 12
        00:12 -> 01
        00:00 -> 00 (handled by check)
        """
        import math
        if self.remaining_seconds == 0:
            minutes = 0
        else:
            minutes = math.ceil(self.remaining_seconds / 60)
        
        display_text = str(minutes)
        if len(display_text) == 1:
            display_text = f"0{display_text}"
            
        self.tick.emit(display_text)
