#!/usr/bin/env python3
"""
Todo2 Application Main Entry Point
독립 실행 가능한 Todo 관리 애플리케이션
"""
import os
import sys
import threading
import time
import webbrowser
import signal
import subprocess
from pathlib import Path

# 현재 스크립트의 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

import uvicorn
from app.main import app

class TodoApp:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 8501
        self.server = None
        self.server_thread = None
        
    def find_free_port(self, start_port=8501):
        """사용 가능한 포트 찾기"""
        import socket
        port = start_port
        while port < start_port + 100:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind((self.host, port))
                    return port
            except OSError:
                port += 1
        return start_port
    
    def start_server(self):
        """서버 시작"""
        self.port = self.find_free_port()
        print(f"Todo2 애플리케이션을 시작합니다...")
        print(f"서버 주소: http://{self.host}:{self.port}")
        
        try:
            uvicorn.run(
                app, 
                host=self.host, 
                port=self.port,
                log_level="warning",  # 로그 레벨을 warning으로 설정하여 출력 줄이기
                access_log=False      # 액세스 로그 비활성화
            )
        except Exception as e:
            print(f"서버 시작 실패: {e}")
            input("아무 키나 눌러 종료하세요...")
    
    def open_browser(self):
        """브라우저 열기"""
        url = f"http://{self.host}:{self.port}"
        time.sleep(2)  # 서버가 시작될 때까지 대기
        
        try:
            print("브라우저를 엽니다...")
            webbrowser.open(url)
        except Exception as e:
            print(f"브라우저 열기 실패: {e}")
            print(f"수동으로 브라우저에서 {url}을 열어주세요.")
    
    def signal_handler(self, signum, frame):
        """종료 신호 처리"""
        print("\n애플리케이션을 종료합니다...")
        if self.server:
            self.server.should_exit = True
        sys.exit(0)
    
    def run(self):
        """애플리케이션 실행"""
        # 종료 신호 핸들러 등록
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # 브라우저 열기를 별도 스레드에서 실행
        browser_thread = threading.Thread(target=self.open_browser, daemon=True)
        browser_thread.start()
        
        # 서버 시작 (메인 스레드에서 실행)
        try:
            self.start_server()
        except KeyboardInterrupt:
            print("\n사용자에 의해 종료되었습니다.")
        except Exception as e:
            print(f"예상치 못한 오류: {e}")
            input("아무 키나 눌러 종료하세요...")

def main():
    """메인 함수"""
    print("=" * 50)
    print("           Todo2 관리 애플리케이션")
    print("=" * 50)
    print()
    
    app = TodoApp()
    app.run()

if __name__ == "__main__":
    main()