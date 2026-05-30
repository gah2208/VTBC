@echo off
echo ======================================
echo RESTORE PREVIOUS VERSION
echo ======================================

cd /d %~dp0
cd ..

REM ---------------------------
REM PATHS
REM ---------------------------
set APP_DIR=app
set SYSTEM_DIR=system

set MAIN_EXE=%APP_DIR%\main.exe
set CONFIG_EXE=%APP_DIR%\config_editor.exe

set BACKUP_MAIN=%APP_DIR%\main_backup.exe
set BACKUP_CONFIG=%APP_DIR%\config_editor_backup.exe
set BACKUP_VERSION=%SYSTEM_DIR%\VERSION_backup.txt
set VERSION_FILE=%SYSTEM_DIR%\VERSION.txt

REM ---------------------------
REM STOP RUNNING PROCESSES
REM ---------------------------
echo Stopping running applications...
taskkill /f /im main.exe >nul 2>&1
taskkill /f /im config_editor.exe >nul 2>&1

REM ---------------------------
REM VALIDATE BACKUP FILES
REM ---------------------------
if not exist %BACKUP_MAIN% (
    echo ❌ ERROR: Backup main.exe not found
    goto END
)

if not exist %BACKUP_CONFIG% (
    echo ❌ ERROR: Backup config_editor.exe not found
    goto END
)

if not exist %BACKUP_VERSION% (
    echo ❌ ERROR: Backup VERSION.txt not found
    goto END
)

REM ---------------------------
REM OPTIONAL: SAVE CURRENT AS FAILED VERSION
REM ---------------------------
echo Preserving current version as failed copy...
copy /y %MAIN_EXE% %APP_DIR%\main_failed.exe >nul 2>&1

REM ---------------------------
REM RESTORE BACKUP
REM ---------------------------
echo Restoring previous version...

copy /y %BACKUP_MAIN% %MAIN_EXE% >nul
copy /y %BACKUP_CONFIG% %CONFIG_EXE% >nul
copy /y %BACKUP_VERSION% %VERSION_FILE% >nul

echo ✅ Restore complete.

echo.
echo You may now run "Start Trading"

:END
echo.
pause
exit /b