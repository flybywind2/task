@echo off
echo Todo2 애플리케이션 EXE 파일 빌드를 시작합니다...
echo.

REM 가상환경 활성화
if exist "venv\Scripts\activate.bat" (
    echo 가상환경을 활성화합니다...
    call venv\Scripts\activate.bat
) else (
    echo 가상환경을 찾을 수 없습니다. 전역 Python을 사용합니다.
)

REM PyInstaller 설치 확인
echo PyInstaller를 확인/설치합니다...
pip install pyinstaller

REM 이전 빌드 결과 정리
if exist "dist" (
    echo 이전 빌드 결과를 정리합니다...
    rmdir /s /q dist
)
if exist "build" (
    rmdir /s /q build
)

REM EXE 파일 빌드
echo.
echo EXE 파일을 빌드합니다...
pyinstaller todo2.spec

REM 빌드 결과 확인
if exist "dist\Todo2.exe" (
    echo.
    echo ================================
    echo    빌드가 성공적으로 완료되었습니다!
    echo ================================
    echo.
    echo 생성된 파일: dist\Todo2.exe
    echo.
    echo EXE 파일을 테스트하시겠습니까? (Y/N)
    set /p choice=
    if /i "%choice%"=="Y" (
        echo.
        echo Todo2.exe를 실행합니다...
        cd dist
        Todo2.exe
    )
) else (
    echo.
    echo ================================
    echo       빌드에 실패했습니다!
    echo ================================
    echo.
    echo 오류 로그를 확인하고 다시 시도해주세요.
)

echo.
pause