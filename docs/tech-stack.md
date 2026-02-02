# Technology Stack

This document outlines the technologies and frameworks used in the **TomodOrange** (Michael's Pomodoro) project.

## Core Technology
*   **Language**: [Python 3.10+](https://www.python.org/)
*   **GUI Framework**: [PySide6](https://pypi.org/project/PySide6/) (Qt for Python).
    *   Used for creating the floating widget, system tray integration, and settings windows.

## Testing Frameworks
*   **Unit & Integration Testing**: `unittest` (Standard Python Library).
    *   Located in `tests/`.
*   **Behavior-Driven Development (BDD)**: [behave](https://behave.readthedocs.io/en/latest/).
    *   Located in `features/` (Gherkin feature files and Python step definitions).

## Tools & Utilities
*   **Version Control**: Git.
*   **Dependency Management**: `pip` (requirements listed in `requirements.txt`).
*   **Asset Management**: Custom logic in `src/utils` for handling paths and resources.

## Project Structure
*   `src/`: Main source code.
*   `tests/`: Unit and integration tests.
*   `features/`: BDD feature files and steps.
*   `docs/`: Documentation and screenshots.
*   `user_data/`: Local storage for user logs (JSON).
