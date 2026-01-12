@echo off
echo Creating executable file for CCTV Viewer
py -m PyInstaller main.py --add-data "resources/;resources"
@REM For single file, use the command below. Otherwise, default command is above
@REM py -m PyInstaller main.py -F --add-data "resources/;resources" 