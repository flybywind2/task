from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routers import tasks, statuses, settings, stats, categories
from app.database import engine, Base
import uvicorn

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todo Management App", version="1.0.0")

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")

# 템플릿 설정
templates = Jinja2Templates(directory="templates")

# 라우터 등록
app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(statuses.router, prefix="/api", tags=["statuses"])
app.include_router(categories.router, prefix="/api", tags=["categories"])
app.include_router(settings.router, prefix="/api", tags=["settings"])
app.include_router(stats.router, prefix="/api", tags=["stats"])

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