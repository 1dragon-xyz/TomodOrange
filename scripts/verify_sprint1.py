import sys
import os
import shutil

# Ensure we can import from src
sys.path.append(os.path.join(os.getcwd(), 'src'))

from utils.log_manager import LogManager

def test_log_manager():
    print("Testing LogManager...")
    
    # Setup clean environment
    test_dir = "test_user_data"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
        
    # Initialize
    manager = LogManager(data_dir=test_dir, filename="test_logs.json")
    
    # Test 1: File Creation
    if not os.path.exists(os.path.join(test_dir, "test_logs.json")):
        print("FAIL: File not created")
        return
    print("PASS: File created")
    
    # Test 2: Task ID Generation (New Task)
    task_name = "Feature A"
    tid = manager.get_task_id(task_name)
    if tid != "#T1":
        print(f"FAIL: Expected #T1, got {tid}")
        return
    print(f"PASS: Task ID for '{task_name}' is {tid}")
    
    # Test 3: Save Log
    entry = {
        "task_name": task_name,
        "task_id": tid,
        "session_num": manager.get_next_session_number(task_name),
        "rating": 5
    }
    manager.save_log(entry)
    print("PASS: Log saved")
    
    # Test 4: Session Count
    next_session = manager.get_next_session_number(task_name)
    if next_session != 2:
        print(f"FAIL: Expected Session 2, got {next_session}")
        return
    print(f"PASS: Next session is {next_session}")
    
    # Test 5: Task ID Persistence (Old Task)
    tid_again = manager.get_task_id(task_name)
    if tid_again != "#T1":
        print(f"FAIL: Expected #T1 again, got {tid_again}")
        return
    print(f"PASS: Task ID persisted as {tid_again}")
    
    # Test 6: New Task ID
    other_task = "Feature B"
    tid_other = manager.get_task_id(other_task)
    if tid_other != "#T2":
        print(f"FAIL: Expected #T2 for new task, got {tid_other}")
        return
    print(f"PASS: New Task ID is {tid_other}")
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("All Tests Passed!")

if __name__ == "__main__":
    test_log_manager()
