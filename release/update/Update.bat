@echo off
setlocal enabledelayedexpansion

echo ======================================
echo VTBC UPDATE PROCESS
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
set VERSION_FILE=%SYSTEM_DIR%\VERSION.txt

set BACKUP_MAIN=%APP_DIR%\main_backup.exe
set BACKUP_CONFIG=%APP_DIR%\config_editor_backup.exe
set BACKUP_VERSION=%SYSTEM_DIR%\VERSION_backup.txt

REM ---------------------------
REM REMOTE URLS (RAW GITHUB)
REM ---------------------------
set REMOTE_MAIN=https://raw.githubusercontent.com/gah2208/VTBC/main/release/app/main.exe
set REMOTE_CONFIG=https://raw.githubusercontent.com/gah2208/VTBC/main/release/app/config_editor.exe
set REMOTE_VERSION=https://raw.githubusercontent.com/gah2208/VTBC/main/release/system/VERSION.txt

REM ---------------------------
REM STOP RUNNING PROCESSES
REM ---------------------------
echo Stopping running applications...
taskkill /f /im main.exe >nul 2>&1
taskkill /f /im config_editor.exe >nul 2>&1

REM ---------------------------
REM GET LOCAL VERSION
REM ---------------------------
if not exist %VERSION_FILE% (
    set LOCAL=0.0.0
) else (
    set /p LOCAL=<%VERSION_FILE%
)

echo Local version: %LOCAL%

REM ---------------------------
REM GET REMOTE VERSION
REM ---------------------------
echo Checking remote version...
curl -s -o remote_version.txt %REMOTE_VERSION%

if not exist remote_version.txt (
    echo ERROR: Could not retrieve remote version
    goto END
)

set /p REMOTE=<remote_version.txt
echo Remote version: %REMOTE%

if "%LOCAL%"=="%REMOTE%" (
    echo Already up to date.
    goto CLEANUP
)

echo Update available.

REM ---------------------------
REM BACKUP CURRENT
REM ---------------------------
echo Creating backup...
if exist %MAIN_EXE% copy /y %MAIN_EXE% %BACKUP_MAIN% >nul
if exist %CONFIG_EXE% copy /y %CONFIG_EXE% %BACKUP_CONFIG% >nul
if exist %VERSION_FILE% copy /y %VERSION_FILE% %BACKUP_VERSION% >nul

REM ---------------------------
REM DOWNLOAD NEW FILES
REM ---------------------------
echo Downloading new executables...

curl -L -o %MAIN_EXE% %REMOTE_MAIN%
curl -L -o %CONFIG_EXE% %REMOTE_CONFIG%

REM ---------------------------
REM VALIDATION
REM ---------------------------
if not exist %MAIN_EXE% goto ROLLBACK
if not exist %CONFIG_EXE% goto ROLLBACK

for %%A in (%MAIN_EXE%) do set S1=%%~zA
for %%A in (%CONFIG_EXE%) do set S2=%%~zA

if %S1% LSS 1000000 goto ROLLBACK
if %S2% LSS 500000 goto ROLLBACK

echo %REMOTE% > %VERSION_FILE%

echo.
echo ✅ UPDATE SUCCESSFUL
goto CLEANUP

REM ---------------------------
REM ROLLBACK
REM ---------------------------
:ROLLBACK
echo ERROR: Update failed. Restoring backup...

if exist %BACKUP_MAIN% copy /y %BACKUP_MAIN% %MAIN_EXE% >nul
if exist %BACKUP_CONFIG% copy /y %BACKUP_CONFIG% %CONFIG_EXE% >nul
if exist %BACKUP_VERSION% copy /y %BACKUP_VERSION% %VERSION_FILE% >nul

echo Rollback complete.

goto CLEANUP

REM ---------------------------
:CLEANUP
del remote_version.txt >nul 2>&1

echo.
echo ======================================
echo UPDATE COMPLETE
echo ======================================
echo.

:END
pause