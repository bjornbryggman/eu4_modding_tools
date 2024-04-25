@echo off

REM Get the directory where the .bat file resides
SET "basePath=%~dp0"

REM Define the relative paths
SET "sourceDir=%basePath%\gui_files"

REM Change directory to the source directory
cd "%sourceDir%"

echo Processing...

REM Loop through all .dds files in the source directory and convert them
python scaling_script.py

echo Success! You can now close this window.

pause