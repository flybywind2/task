@echo off
echo Todo App을 시작합니다...

cd /d "D:\Python\todo2"
call venv\Scripts\activate

echo 서버를 시작합니다...
start /B python -m app.main

echo 브라우저가 열릴 때까지 기다리는 중...
timeout /t 5 /nobreak > nul

echo 브라우저를 엽니다...
start http://localhost:8501

echo Todo App이 시작되었습니다!
echo 종료하려면 이 창을 닫으세요.
pause