@echo off
echo Creating executable file for CCTV Viewer
py -m PyInstaller main.py --add-data "resources/;resources"