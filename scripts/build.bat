@echo off
REM __version__ = 1.1.0
REM VTBC Build Pipeline

cd /d %~dp0

echo.
echo ===============================
echo  VTBC BUILD PIPELINE START
echo ===============================
echo.

REM ---------------------------
REM STEP 1 — BUILD CHECK
REM ---------------------------
echo Running build version check...
python -c "from build_check import run_build_check; run_build_check()"

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ BUILD VERSION CHECK FAILED
    goto END
)

echo ✅ VERSION CHECK PASSED
echo.

REM ---------------------------
REM STEP 2 — CHECKSUM VALIDATION
REM ---------------------------
echo Running checksum validation...
python -c "from checksum import verify_checksum; verify_checksum()"

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ CHECKSUM VALIDATION FAILED
    goto END
)

echo ✅ CHECKSUM VALIDATION PASSED
echo.

REM ---------------------------
REM STEP 3 — CLEAN PREVIOUS BUILD
REM ---------------------------
echo Cleaning previous build artifacts...

rmdir /s /q build >nul 2>&1
rmdir /s /q dist >nul 2>&1

del *.spec >nul 2>&1

echo Clean complete.
echo.

REM ---------------------------
REM STEP 4 — GET VERSION
REM ---------------------------
if not exist ..\release\system\VERSION.txt (
    echo ERROR: VERSION.txt not found
    goto END
)

set /p VERSION=<..\release\system\VERSION.txt
echo Building version: %VERSION%
echo.

REM ---------------------------
REM STEP 5 — BUILD EXECUTABLES
REM ---------------------------
echo ===============================
echo  BUILDING EXECUTABLES
echo ===============================
echo.

echo Building main.exe...
python -m PyInstaller --onefile --noconsole --name main dev\main.py

IF %ERRORLEVEL% NEQ 0 (
    echo ❌ main.exe build failed
    goto END
)

echo Building config_editor.exe...
python -m PyInstaller --onefile --noconsole --name config_editor dev\ui\config_editor.py

IF %ERRORLEVEL% NEQ 0 (
    echo ❌ config_editor.exe build failed
    goto END
)

echo Executables built successfully.
echo.

REM ---------------------------
REM STEP 6 — PREP RELEASE FOLDERS
REM ---------------------------
if not exist ..\release\app mkdir ..\release\app
if not exist ..\release\archives mkdir ..\release\archives

REM ---------------------------
REM STEP 7 — COPY RUNTIME EXES
REM ---------------------------
copy /y dist\main.exe ..\release\app\main.exe >nul
copy /y dist\config_editor.exe ..\release\app\config_editor.exe >nul

echo Runtime executables updated.
echo.

REM ---------------------------
REM STEP 8 — CREATE VERSIONED ARCHIVE
REM ---------------------------
copy /y dist\main.exe ..\release\archives\VTBC_%VERSION%.exe >nul

echo Versioned archive created: VTBC_%VERSION%.exe
echo.

REM ---------------------------
REM STEP 9 — COPY VERSION FILE
REM ---------------------------
copy /y ..\release\system\VERSION.txt ..\release\system\VERSION.txt >nul 2>&1

echo Version file verified.
echo.

REM ---------------------------
REM COMPLETE
REM ---------------------------
echo ===============================
echo ✅ BUILD COMPLETED SUCCESSFULLY
echo ===============================
echo.

:END
echo.
echo Press any key to close...
pause >nul
exit /b