@echo off
:: Interview Copilot Launcher
:: Adds C:\pylibs to PYTHONPATH and starts the app
set PYTHONPATH=C:\pylibs;%PYTHONPATH%
cd /d "%~dp0"
python main.py
exit
