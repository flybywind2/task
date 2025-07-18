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

# Windows 전용 알림 모듈
try:
    import win10toast
    TOAST_AVAILABLE = True
except ImportError:
    TOAST_AVAILABLE = False

# 시스템 트레이 모듈 (선택적)
try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False

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
        self.tray_icon = None
        self.running = True
        
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
        import traceback
        import io
        
        # PyInstaller 환경에서 표준 입출력 리다이렉트
        if getattr(sys, 'frozen', False):
            # 가짜 stdout/stderr 생성
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()
        
        # 로그 파일 경로 설정 (EXE와 같은 폴더에 생성)
        if getattr(sys, 'frozen', False):
            # PyInstaller로 빌드된 환경
            log_dir = Path(sys.executable).parent
        else:
            # 개발 환경
            log_dir = Path(current_dir)
        
        log_file = log_dir / "todo2_server.log"
        
        try:
            # 로그 파일에 서버 시작 정보 기록
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(f"=== Todo2 서버 시작 로그 ===\n")
                f.write(f"시간: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"호스트: {self.host}\n")
                f.write(f"포트: {self.port}\n")
                f.write(f"실행 환경: {'PyInstaller' if getattr(sys, 'frozen', False) else '개발환경'}\n")
                f.write(f"로그 파일 위치: {log_file}\n")
                f.write(f"Python 버전: {sys.version}\n\n")
            
            print(f"Todo2 애플리케이션을 시작합니다...")
            print(f"서버 주소: http://{self.host}:{self.port}")
            print(f"로그 파일: {log_file}")
            
            # 서버 시작 전 추가 로그
            with open(log_file, "a", encoding="utf-8") as f:
                f.write("uvicorn 서버 시작 시도...\n")
                f.flush()
            
            # PyInstaller 환경에서 uvicorn 서버 시작
            config = uvicorn.Config(
                app=app,
                host=self.host,
                port=self.port,
                log_level="error",  # 로그 레벨을 error로 낮춤
                access_log=False,   # 액세스 로그 비활성화
                use_colors=False,   # 색상 비활성화
                reload=False,
                log_config=None     # 기본 로그 설정 비활성화
            )
            
            server = uvicorn.Server(config)
            
            # 로그에 서버 시작 성공 기록
            with open(log_file, "a", encoding="utf-8") as f:
                f.write("서버 시작 성공!\n")
                f.flush()
            
            # 서버 실행
            server.run()
            
        except Exception as e:
            error_msg = f"서버 시작 실패: {e}"
            full_traceback = traceback.format_exc()
            
            # 에러 로그 기록
            try:
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"\n=== 에러 발생 ===\n")
                    f.write(f"시간: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"에러: {error_msg}\n")
                    f.write(f"상세 에러:\n{full_traceback}\n")
                    f.flush()
            except Exception as log_error:
                print(f"로그 기록 실패: {log_error}")
            
            # 트레이 알림으로 에러 표시
            if TRAY_AVAILABLE and self.tray_icon:
                try:
                    self.tray_icon.notify(
                        f"서버 시작 실패\n{error_msg}\n로그: {log_file}",
                        "Todo2 오류"
                    )
                except:
                    pass
            
            print(error_msg)
            if not TOAST_AVAILABLE and not TRAY_AVAILABLE:
                input("아무 키나 눌러 종료하세요...")
    
    def open_browser(self):
        """브라우저 열기"""
        url = f"http://{self.host}:{self.port}"
        
        # 서버가 실제로 응답할 때까지 대기
        import socket
        max_wait = 30  # 최대 30초 대기
        wait_time = 0
        
        while wait_time < max_wait:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex((self.host, self.port))
                    if result == 0:  # 연결 성공
                        break
            except:
                pass
            
            time.sleep(1)
            wait_time += 1
        
        # 추가로 1초 더 대기 (서버 완전 초기화)
        time.sleep(1)
        
        try:
            print(f"브라우저를 엽니다: {url}")
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
    
    def create_tray_icon(self):
        """시스템 트레이 아이콘 생성"""
        if not TRAY_AVAILABLE:
            return None
            
        # 간단한 아이콘 이미지 생성
        image = Image.new('RGB', (64, 64), color='blue')
        draw = ImageDraw.Draw(image)
        draw.rectangle([16, 16, 48, 48], fill='white')
        draw.text((20, 20), "T2", fill='blue')
        
        # 트레이 메뉴 생성
        menu = pystray.Menu(
            pystray.MenuItem("Todo2 열기", self.open_browser_action),
            pystray.MenuItem("서버 정보", self.show_server_info),
            pystray.MenuItem("로그 파일 열기", self.open_log_file),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("종료", self.quit_application)
        )
        
        return pystray.Icon("Todo2", image, "Todo2 애플리케이션", menu)
    
    def open_browser_action(self, icon=None, item=None):
        """트레이에서 브라우저 열기"""
        self.open_browser()
    
    def show_server_info(self, icon=None, item=None):
        """서버 정보 알림"""
        if TRAY_AVAILABLE and self.tray_icon:
            self.tray_icon.notify(
                f"Todo2 서버가 실행 중입니다\nURL: http://{self.host}:{self.port}",
                "Todo2 정보"
            )
    
    def open_log_file(self, icon=None, item=None):
        """로그 파일 열기"""
        try:
            if getattr(sys, 'frozen', False):
                log_file = Path(sys.executable).parent / "todo2_server.log"
            else:
                log_file = Path(current_dir) / "todo2_server.log"
            
            if log_file.exists():
                os.startfile(str(log_file))
            else:
                if TRAY_AVAILABLE and self.tray_icon:
                    self.tray_icon.notify(
                        "로그 파일이 존재하지 않습니다",
                        "Todo2"
                    )
        except Exception as e:
            if TRAY_AVAILABLE and self.tray_icon:
                self.tray_icon.notify(
                    f"로그 파일 열기 실패: {e}",
                    "Todo2 오류"
                )
    
    def quit_application(self, icon=None, item=None):
        """애플리케이션 종료"""
        self.running = False
        if self.tray_icon:
            self.tray_icon.stop()
        sys.exit(0)
    
    
    def run(self):
        """애플리케이션 실행"""
        # 종료 신호 핸들러 등록
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # 포트 찾기
        self.port = self.find_free_port()
        
        # Windows 알림 표시
        if TOAST_AVAILABLE:
            try:
                toaster = win10toast.ToastNotifier()
                toaster.show_toast(
                    "Todo2 시작됨",
                    f"Todo2 애플리케이션이 시작되었습니다\nURL: http://{self.host}:{self.port}",
                    duration=5,
                    threaded=True
                )
            except Exception as e:
                print(f"알림 표시 실패: {e}")
        
        # 시스템 트레이가 사용 가능한 경우 트레이 아이콘 시작
        if TRAY_AVAILABLE:
            try:
                # 트레이 아이콘을 먼저 생성
                self.tray_icon = self.create_tray_icon()
                if self.tray_icon:
                    # 트레이를 별도 스레드에서 실행
                    tray_thread = threading.Thread(target=self.tray_icon.run, daemon=False)
                    tray_thread.start()
            except Exception as e:
                print(f"트레이 아이콘 생성 실패: {e}")
        
        # 브라우저 열기를 별도 스레드에서 실행
        browser_thread = threading.Thread(target=self.open_browser, daemon=True)
        browser_thread.start()
        
        # 서버 시작 (메인 스레드에서 실행)
        try:
            self.start_server()
        except KeyboardInterrupt:
            if not TRAY_AVAILABLE:
                print("\n사용자에 의해 종료되었습니다.")
        except Exception as e:
            if not TRAY_AVAILABLE:
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