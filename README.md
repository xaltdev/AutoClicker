# Python AutoClicker 🖱️✨

A feature-rich auto-clicker application built with Python, using **CustomTkinter** for a modern UI and **Pynput** for global input control. This repository contains the source code (`.py`) and an icon (`.ico`) for the application.

## Features

*   **Precise Click Interval:** Set hours, minutes, seconds, and milliseconds.
*   **Click Options:** Choose Left, Right, or Middle mouse button; Single or Double click.
*   **Repeat Modes:** Repeat a specific number of times or click continuously until stopped.
*   **Cursor Positioning:** Click at the current cursor location or pick a specific X,Y coordinate on screen.
*   **Customizable Hotkey:** Start/stop clicking with a global hotkey (default: F6), changeable within the app.
*   **Modern UI:** Clean, dark-themed interface.

## How to Compile (to .exe for Windows)

Follow these steps to compile the Python script into a standalone Windows executable:

**1. Prerequisites:**
    *   Ensure you have Python installed (version 3.7+ recommended).
    *   Make sure `pip` (Python package installer) is available.

**2. Install Dependencies:**
    Open your terminal or command prompt and install the required libraries:
    ```bash
    pip install customtkinter pynput pyinstaller
    ```

**3. Compile with PyInstaller:**
    Navigate to the directory containing the Python script (e.g., `main.py` or `autoclicker.py`) and the icon file (e.g., `icon.ico`) in your terminal. Then, run the following command:

    ```bash
    pyinstaller --name "AutoClicker" --onefile --windowed --icon="icon.ico" --hidden-import="pynput.keyboard._win32" --hidden-import="pynput.mouse._win32" --hidden-import="customtkinter" YOUR_PYTHON_SCRIPT_NAME.py
    ```

    **Replace:**
    *   `"icon.ico"`: If your icon file has a different name, update it here. Ensure it's in the same directory or provide the correct path.
    *   `YOUR_PYTHON_SCRIPT_NAME.py`: With the actual name of the Python source file (e.g., `main.py`).

    **Explanation of flags:**
    *   `--name "AutoClicker"`: Name of the output executable.
    *   `--onefile`: Creates a single executable file.
    *   `--windowed`: Prevents a console window from appearing when the GUI runs.
    *   `--icon="icon.ico"`: Sets the application icon.
    *   `--hidden-import="..."`: These are crucial for PyInstaller to correctly bundle `pynput` and `customtkinter` functionalities for Windows.

**4. Find Your Executable:**
    After PyInstaller finishes, you will find the `AutoClicker.exe` file inside a newly created `dist` folder.

---
