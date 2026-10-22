@echo off
rem SaiLang launcher for Windows 10 and 11.
rem Usage:  sai.bat                  (starts the prompt)
rem         sai.bat examples\hello.sai
setlocal
set "SAI_HOME=%~dp0"
set "PYTHONPATH=%SAI_HOME%src"

call :find_python
if errorlevel 1 goto :no_python

%PY% -m sailang %*
exit /b %errorlevel%

:find_python
where py >nul 2>nul
if not errorlevel 1 (
    set "PY=py -3"
    exit /b 0
)
where python >nul 2>nul
if not errorlevel 1 (
    set "PY=python"
    exit /b 0
)
exit /b 1

:no_python
echo.
echo SaiLang needs Python 3.9 or newer, which was not found on this computer.
echo.
echo To fix this without administrator rights:
echo   1. Go to https://www.python.org/downloads/ and download the Windows installer.
echo   2. Run it and choose "Install Now" or "Customize installation".
echo   3. Tick "tcl/tk and IDLE" (needed for windows and games).
echo   4. Choose "Install for me only" if you are asked, then finish the install.
echo   5. Close this window, open a new one, and run sai.bat again.
echo.
exit /b 1
