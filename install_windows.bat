@echo off
REM Substance Painter Commander - Windows Installer
REM Author: Wes McDermott

echo.
echo 🎨 Substance Painter Commander - Windows Installer
echo =================================================
echo.

REM Define paths
set "PLUGINS_DIR=%USERPROFILE%\Documents\Adobe\Adobe Substance 3D Painter\python\plugins"
set "COMMANDER_DIR=%PLUGINS_DIR%\commander"
set "SCRIPT_DIR=%~dp0"

REM Remove trailing backslash from SCRIPT_DIR
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Check if we're running from the commander directory
if not exist "%SCRIPT_DIR%\__init__.py" (
    echo ❌ Error: This installer must be run from the commander plugin directory
    echo    Make sure you're running it from the folder containing __init__.py and plugin.json
    pause
    exit /b 1
)

if not exist "%SCRIPT_DIR%\plugin.json" (
    echo ❌ Error: This installer must be run from the commander plugin directory
    echo    Make sure you're running it from the folder containing __init__.py and plugin.json
    pause
    exit /b 1
)

echo 📁 Checking Substance Painter installation...

REM Check if Adobe directory exists
if not exist "%USERPROFILE%\Documents\Adobe" (
    echo ❌ Error: Adobe documents folder not found
    echo    Please ensure Substance Painter is installed
    echo    Expected: %USERPROFILE%\Documents\Adobe
    pause
    exit /b 1
)

REM Create plugins directory if it doesn't exist
echo 📂 Creating plugins directory...
if not exist "%PLUGINS_DIR%" (
    mkdir "%PLUGINS_DIR%" 2>nul
    if errorlevel 1 (
        echo ❌ Error: Failed to create plugins directory
        echo    Check permissions for: %PLUGINS_DIR%
        pause
        exit /b 1
    )
)

REM Check if commander is already installed
if exist "%COMMANDER_DIR%" (
    echo ⚠️  Commander is already installed
    set /p "REPLY=   Do you want to overwrite the existing installation? (y/N): "
    if /i not "%REPLY%"=="y" (
        echo ❌ Installation cancelled
        pause
        exit /b 0
    )
    
    echo 🗑️  Removing existing installation...
    rmdir /s /q "%COMMANDER_DIR%" 2>nul
    if errorlevel 1 (
        echo ❌ Error: Failed to remove existing installation
        echo    Please close Substance Painter and try again
        pause
        exit /b 1
    )
)

REM Copy commander directory
echo 📦 Installing Commander plugin...
xcopy "%SCRIPT_DIR%" "%COMMANDER_DIR%\" /E /I /Q /Y >nul 2>&1

if errorlevel 1 (
    echo ❌ Error: Failed to copy plugin files
    echo    Source: %SCRIPT_DIR%
    echo    Target: %COMMANDER_DIR%
    pause
    exit /b 1
)

REM Remove installer files from the installed copy
if exist "%COMMANDER_DIR%\install_macos.sh" del "%COMMANDER_DIR%\install_macos.sh" >nul 2>&1
if exist "%COMMANDER_DIR%\install_windows.bat" del "%COMMANDER_DIR%\install_windows.bat" >nul 2>&1
if exist "%COMMANDER_DIR%\uninstall_macos.sh" del "%COMMANDER_DIR%\uninstall_macos.sh" >nul 2>&1
if exist "%COMMANDER_DIR%\uninstall_windows.bat" del "%COMMANDER_DIR%\uninstall_windows.bat" >nul 2>&1

REM Verify installation
if exist "%COMMANDER_DIR%\__init__.py" (
    if exist "%COMMANDER_DIR%\plugin.json" (
        echo.
        echo ✅ Installation completed successfully!
        echo.
        echo 🚀 Next steps:
        echo    1. Restart Substance Painter
        echo    2. Use Ctrl+; or Ctrl+` to open Commander
        echo    3. Look for the 'C' button in the right toolbar
        echo.
        echo 📍 Installation location:
        echo    %COMMANDER_DIR%
        echo.
        echo 📖 Macros will be stored in:
        echo    %USERPROFILE%\.substance_painter_commander\macros.json
        echo.
        echo 🎯 For help and documentation, see README.md
    ) else (
        goto :installation_error
    )
) else (
    :installation_error
    echo ❌ Installation verification failed
    echo    Plugin files may not have been copied correctly
    pause
    exit /b 1
)

echo.
echo Press any key to continue...
pause >nul
