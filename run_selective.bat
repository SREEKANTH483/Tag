@echo off
REM Selective scenario runner for Windows
REM Usage examples:
REM   run_selective.bat --first 5
REM   run_selective.bat --last 3
REM   run_selective.bat --range 2-5
REM   run_selective.bat --scenarios 1,3,7

python run_scenarios_selective.py %*
pause