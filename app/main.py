import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routers import tasks, statuses, settings, stats, categories, csv_export
from app.database import engine, Base
import uvicorn

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todo Management App", version="1.0.0")

# 실행 환경에 따른 경로 설정
def get_resource_path(relative_path):
    """PyInstaller 환경에서 리소스 파일의 절대 경로를 반환"""
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 환경
        base_path = Path(sys._MEIPASS)
    else:
        # 개발 환경
        base_path = Path(__file__).parent.parent
    
    return str(base_path / relative_path)

# 정적 파일 및 템플릿 디렉토리 경로
static_dir = get_resource_path("static")
templates_dir = get_resource_path("templates")

# 디렉토리 존재 확인
if not os.path.exists(static_dir):
    print(f"Warning: Static directory not found: {static_dir}")
if not os.path.exists(templates_dir):
    print(f"Warning: Templates directory not found: {templates_dir}")

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 템플릿 설정
templates = Jinja2Templates(directory=templates_dir)

# 라우터 등록
app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(statuses.router, prefix="/api", tags=["statuses"])
app.include_router(categories.router, prefix="/api", tags=["categories"])
app.include_router(settings.router, prefix="/api", tags=["settings"])
app.include_router(stats.router, prefix="/api", tags=["stats"])
app.include_router(csv_export.router, prefix="/api", tags=["csv"])

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

if __name__ == "__main__":
    import os
    import sys
    
    # Windows 환경에서 reload 시 발생하는 문제 해결
    if os.name == 'nt':  # Windows
        # test_env 디렉토리가 있다면 reload_dirs에서 제외
        reload_dirs = ["."]
        if os.path.exists("test_env"):
            reload_dirs = ["app", "static", "templates"]
        
        uvicorn.run(
            "app.main:app", 
            host="0.0.0.0", 
            port=8501, 
            reload=True,
            reload_dirs=reload_dirs
        )
    else:
        uvicorn.run("app.main:app", host="0.0.0.0", port=8501, reload=True)