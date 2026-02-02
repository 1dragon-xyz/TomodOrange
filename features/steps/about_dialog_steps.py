from behave import given, when, then
from PySide6.QtWidgets import QLabel
import sys
import os

# Ensure src importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from ui.about_dialog import AboutDialog

@given('the About Dialog is initialized')
def step_impl(context):
    context.dialog = AboutDialog()

@when('I show the dialog')
def step_impl(context):
    context.dialog.show()

@then('the title should be "{title}"')
def step_impl(context, title):
    assert context.dialog.windowTitle() == title

@then('it should display the app name "{app_name}"')
def step_impl(context, app_name):
    labels = context.dialog.findChildren(QLabel)
    texts = [l.text() for l in labels]
    assert any(app_name in t for t in texts), f"App name '{app_name}' not found in {texts}"

@then('it should display the developer name "{dev_name}"')
def step_impl(context, dev_name):
    labels = context.dialog.findChildren(QLabel)
    texts = [l.text() for l in labels]
    assert any(dev_name in t for t in texts), f"Developer name '{dev_name}' not found"

@then('it should display a link to "{url}"')
def step_impl(context, url):
    labels = context.dialog.findChildren(QLabel)
    texts = [l.text() for l in labels]
    # Check for the url inside the text (HTML or plain)
    assert any(url in t for t in texts), f"URL '{url}' not found in {texts}"
