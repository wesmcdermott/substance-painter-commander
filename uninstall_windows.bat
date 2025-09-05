@echo off
REM Substance Painter Commander - Windows Uninstaller
REM Author: Wes McDermott

echo.
echo 🗑️  Substance Painter Commander - Windows Uninstaller
echo ===================================================
echo.

REM Define paths
set "PLUGINS_DIR=%USERPROFILE%\Documents\Adobe\Adobe Substance 3D Painter\python\plugins"
set "COMMANDER_DIR=%PLUGINS_DIR%\commander"
set "MACROS_DIR=%USERPROFILE%\AppData\Local\Commander"

echo 🔍 Checking for Commander installation...

REM Check if Commander is installed
if not exist "%COMMANDER_DIR%" (
    echo ℹ️  Commander is not currently installed
    echo    Directory not found: %COMMANDER_DIR%
    pause
    exit /b 0
)

echo 📍 Found Commander installation at:
echo    %COMMANDER_DIR%

if exist "%MACROS_DIR%" (
    echo 📍 Found macro storage at:
    echo    %MACROS_DIR%
)

echo.
echo ⚠️  This will completely remove Commander and all associated files
set /p "REPLY=   Are you sure you want to uninstall Commander? (y/N): "

if /i not "%REPLY%"=="y" (
    echo ❌ Uninstallation cancelled
    pause
    exit /b 0
)

REM Ask about macros
set "REMOVE_MACROS=false"
if exist "%MACROS_DIR%" (
    echo.
    set /p "MACRO_REPLY=🔄 Do you also want to remove saved macros ^& hotkeys? (y/N): "
    
    if /i "%MACRO_REPLY%"=="y" (
        set "REMOVE_MACROS=true"
        echo 🗑️  Will remove macros and settings
    ) else (
        echo 💾 Will preserve macros and settings
    )
)

echo.
echo 🗑️  Removing Commander plugin...

REM Remove the commander directory
rmdir /s /q "%COMMANDER_DIR%" >nul 2>&1

if errorlevel 1 (
    echo ❌ Error: Failed to remove Commander directory
    echo    Please close Substance Painter and try again
    echo    Manual removal may be required: %COMMANDER_DIR%
    pause
    exit /b 1
)

REM Remove macros if requested
if "%REMOVE_MACROS%"=="true" (
    if exist "%MACROS_DIR%" (
        echo 🗑️  Removing macros and settings...
        rmdir /s /q "%MACROS_DIR%" >nul 2>&1
        
        if errorlevel 1 (
            echo ⚠️  Warning: Failed to remove macro directory
            echo    You may need to manually remove: %MACROS_DIR%
        )
    )
)

REM Verify removal
if not exist "%COMMANDER_DIR%" (
    echo.
    echo ✅ Commander has been successfully uninstalled!
    echo.
    echo 🔄 Next steps:
    echo    1. Restart Substance Painter
    echo    2. Commander shortcuts and hotkeys will be removed
    
    if not "%REMOVE_MACROS%"=="true" (
        if exist "%MACROS_DIR%" (
            echo.
            echo 💾 Your macros are preserved in:
            echo    %MACROS_DIR%
            echo    You can restore them if you reinstall Commander
        )
    )
    
    echo.
    echo Thank you for using Commander! 🎨
) else (
    echo ❌ Uninstallation may not have completed successfully
    echo    Please check: %COMMANDER_DIR%
    pause
    exit /b 1
)

echo.
echo Press any key to continue...
pause >nul
