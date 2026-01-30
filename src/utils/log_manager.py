import json
import os
from datetime import datetime

class LogManager:
    """
    Manages reading and writing work logs to a JSON file.
    """
    def __init__(self, data_dir="user_data", filename="work_logs.json"):
        self.data_dir = os.path.join(os.getcwd(), data_dir)
        self.filepath = os.path.join(self.data_dir, filename)
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Creates the data directory and empty logs file if they don't exist."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=4)

    def get_all_logs(self):
        """Returns a list of all log entries."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_log(self, entry):
        """
        Saves a single log entry.
        entry: dict containing log details.
        """
        logs = self.get_all_logs()
        
        # Add timestamp if not present
        if 'timestamp' not in entry:
            entry['timestamp'] = datetime.now().isoformat()
            
        # Check status
        status = entry.get('status', 'completed')
        
        if status == 'completed':
            # Check if previous log was 'planned'
            if logs and logs[-1].get('status') == 'planned':
                # Update the existing planned log instead of appending
                # We overwrite keys with new data
                logs[-1].update(entry)
            else:
                logs.append(entry)
        else:
            # For 'planned' or other statuses, always append
            logs.append(entry)
        
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=4, ensure_ascii=False)

    def get_pending_plan(self):
        """
        Returns the last log ONLY IF its status is 'planned'.
        Otherwise returns None.
        """
        logs = self.get_all_logs()
        if logs and logs[-1].get('status') == 'planned':
            return logs[-1]
        return None

    def get_next_session_number(self, task_name):
        """
        Returns the next session number for a given task name.
        Counts how many entries have the exact same 'task_name'.
        """
        logs = self.get_all_logs()
        count = 0
        for log in logs:
            if log.get('task_name') == task_name:
                count += 1
        return count + 1

    def get_last_task_name(self):
        """Returns the task name of the most recent log, or empty string."""
        logs = self.get_all_logs()
        if not logs:
            return ""
        return logs[-1].get('task_name', "")

    def get_task_id(self, task_name):
        """
        Generates or retrieves a Task ID (e.g., #T1) for a given task name.
        This simple implementation assigns ID based on order of appearance of unique task names.
        """
        if not task_name:
            return ""
            
        logs = self.get_all_logs()
        unique_tasks = []
        for log in logs:
            name = log.get('task_name')
            if name and name not in unique_tasks:
                unique_tasks.append(name)
        
        # If this is a new task not in history yet, append it to calculation
        if task_name not in unique_tasks:
             unique_tasks.append(task_name)
             
        index = unique_tasks.index(task_name) + 1
        return f"#T{index}"
