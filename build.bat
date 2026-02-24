@echo off
echo Building Background Color Viewer...
python -m pip install pyinstaller packaging
python -m PyInstaller --noconfirm --onefile --windowed --name "BackgroundColorViewer" --collect-all customtkinter main.py
echo Build Complete! The executable is located in the dist folder.
pause
