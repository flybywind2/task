@echo off
title Todo2 EXE Builder
color 0A

echo.
echo  ████████╗ ██████╗ ██████╗  ██████╗ ██████╗ 
echo  ╚══██╔══╝██╔═══██╗██╔══██╗██╔═══██╗╚════██╗
echo     ██║   ██║   ██║██║  ██║██║   ██║ █████╔╝
echo     ██║   ██║   ██║██║  ██║██║   ██║██╔═══╝ 
echo     ██║   ╚██████╔╝██████╔╝╚██████╔╝███████╗
echo     ╚═╝    ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝
echo.
echo     빠른 EXE 빌드 도구
echo     ================
echo.

REM 현재 디렉토리로 이동
cd /d "%~dp0"

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo Python을 설치한 후 다시 시도해주세요.
    pause
    exit /b 1
)

REM 가상환경 확인/생성
if not exist "venv" (
    echo [1/5] 가상환경을 생성합니다...
    python -m venv venv
    if errorlevel 1 (
        echo [오류] 가상환경 생성에 실패했습니다.
        pause
        exit /b 1
    )
    echo      ✓ 가상환경 생성 완료
) else (
    echo [1/5] 기존 가상환경을 사용합니다...
    echo      ✓ 가상환경 확인 완료
)

REM 가상환경 활성화
echo [2/5] 가상환경을 활성화합니다...
call venv\Scripts\activate
if errorlevel 1 (
    echo [오류] 가상환경 활성화에 실패했습니다.
    pause
    exit /b 1
)
echo      ✓ 가상환경 활성화 완료

REM 의존성 설치
echo [3/5] 필요한 패키지를 설치합니다...
pip install -r requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 (
    echo [오류] 패키지 설치에 실패했습니다.
    pause
    exit /b 1
)
echo      ✓ 패키지 설치 완료

REM 이전 빌드 정리
echo [4/5] 이전 빌드 결과를 정리합니다...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
echo      ✓ 빌드 정리 완료

REM EXE 빌드
echo [5/5] EXE 파일을 빌드합니다...
echo      (이 과정은 몇 분 소요될 수 있습니다)
pyinstaller todo2.spec --noconfirm --clean
if errorlevel 1 (
    echo [오류] EXE 빌드에 실패했습니다.
    echo 오류 로그를 확인하고 다시 시도해주세요.
    pause
    exit /b 1
)
echo      ✓ EXE 빌드 완료

REM 결과 확인
echo.
if exist "dist\Todo2.exe" (
    echo ┌─────────────────────────────────────────────┐
    echo │            빌드 성공! 🎉                    │
    echo └─────────────────────────────────────────────┘
    echo.
    echo 📁 생성된 파일: dist\Todo2.exe
    echo 📊 파일 크기: 
    for %%F in (dist\Todo2.exe) do echo    %%~zF bytes
    echo.
    echo 🚀 지금 실행해보시겠습니까? (Y/N)
    set /p choice="> "
    if /i "%choice%"=="Y" (
        echo.
        echo Todo2.exe를 실행합니다...
        start "" "dist\Todo2.exe"
        echo.
        echo 브라우저가 자동으로 열리면 Todo 애플리케이션을 사용할 수 있습니다.
        echo 종료하려면 콘솔 창을 닫으세요.
    )
) else (
    echo ┌─────────────────────────────────────────────┐
    echo │            빌드 실패! ❌                    │
    echo └─────────────────────────────────────────────┘
    echo.
    echo 오류가 발생했습니다. 다음을 확인해주세요:
    echo 1. Python이 올바르게 설치되어 있는지
    echo 2. 모든 파일이 존재하는지
    echo 3. 인터넷 연결이 정상인지
)

echo.
pause