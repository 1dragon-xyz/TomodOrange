from PySide6.QtWidgets import QApplication
import sys

def before_all(context):
    # Ensure One QApplication per test run
    context.app = QApplication.instance()
    if not context.app:
        context.app = QApplication(sys.argv)
