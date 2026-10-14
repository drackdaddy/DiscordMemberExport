@echo off
setlocal
cd /d "%~dp0"

rem ---- 1. Find Python (install it if missing) ----
call :findpython
if not defined PY (
    echo Python not found. Installing Python 3.13 with winget...
    where winget >nul 2>&1 || (
        echo winget is not available. Install Python from https://www.python.org/downloads/
        echo and tick "Add python.exe to PATH", then run this again.
        pause & exit /b 2
    )
    winget install -e --id Python.Python.3.13 --scope user --silent --accept-package-agreements --accept-source-agreements
    call :findpython
)
if not defined PY (
    echo Python was installed but could not be found. Close this window and run it again.
    pause & exit /b 2
)
echo Using Python: %PY%

rem ---- 2. Make sure discord.py is installed ----
%PY% -c "import discord" >nul 2>&1
if errorlevel 1 (
    echo Installing discord.py...
    %PY% -m pip install --user --upgrade discord.py || (echo Could not install discord.py. & pause & exit /b 2)
)

rem ---- 3. Export members and post them to Discord ----
echo.
echo Exporting Discord members...
%PY% export_members.py
if errorlevel 1 (
    echo.
    echo Export failed - nothing was posted.
    pause & exit /b 2
)
echo.
pause
exit /b

:findpython
set "PY="
rem "py" launcher first, then python on PATH (skips the Microsoft Store stub), then the default install folder
py -3 -c "import sys" >nul 2>&1 && (set "PY=py -3" & exit /b)
python -c "import sys" >nul 2>&1 && (set "PY=python" & exit /b)
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do if exist "%%D\python.exe" set "PY="%%D\python.exe""
exit /b
