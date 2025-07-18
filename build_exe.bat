@echo off
chcp 65001 > nul
echo Starting Todo2 application EXE build...
echo.

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Using global Python.
)

REM Check and install required packages
echo Installing required packages...
pip install pyinstaller pystray pillow win10toast

REM Clean previous build results and cache
if exist "dist" (
    echo Cleaning previous build results...
    rmdir /s /q dist
)
if exist "build" (
    rmdir /s /q build
)
if exist "__pycache__" (
    rmdir /s /q __pycache__
)

REM Clear PyInstaller cache
echo Clearing PyInstaller cache...
pyinstaller --clean todo2.spec

REM Build EXE file
echo.
echo Building EXE file...
pyinstaller todo2.spec

REM Check build result
if exist "dist\Todo2.exe" (
    echo.
    echo ================================
    echo    Build completed successfully!
    echo ================================
    echo.
    echo Generated file: dist\Todo2.exe
    echo.
    echo Would you like to test the EXE file? (Y/N)
    set /p choice=
    if /i "%choice%"=="Y" (
        echo.
        echo Running Todo2.exe...
        cd dist
        Todo2.exe
    )
) else (
    echo.
    echo ================================
    echo        Build failed!
    echo ================================
    echo.
    echo Please check error logs and try again.
)

echo.
pause