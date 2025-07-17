# Todo 관리 애플리케이션

FastAPI를 기반으로 구축된 간단한 Todo 관리 애플리케이션입니다. 프론트엔드는 HTML, CSS, JavaScript를 사용합니다.

## 주요 기능

- **작업 관리:** 작업 생성, 조회, 수정, 삭제 기능
- **상태 관리:** 작업에 "대기", "진행 중", "완료" 등 다양한 상태를 지정할 수 있습니다.
- **카테고리 관리:** 작업을 여러 카테고리로 분류할 수 있습니다.
- **작업 고정:** 중요한 작업을 목록 상단에 고정할 수 있습니다.
- **일일 통계:** 일별로 추가된 작업, 완료된 작업, 미완료된 작업 등의 통계를 추적합니다.
- **일일 로그:** 특정 날짜의 모든 작업 관련 활동을 기록합니다.
- **설정:** 애플리케이션 설정을 구성할 수 있습니다.

## 프로젝트 구조

```
/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── categories.py
│   │   ├── settings.py
│   │   ├── stats.py
│   │   ├── statuses.py
│   │   └── tasks.py
│   └── utils/
│       └── logger.py
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   └── index.html
├── .gitignore
├── install_service.py
├── PRD.md
├── requirements.txt
├── start_todo_app.bat
├── start_with_browser.bat
└── todo.db
```

### `app` 디렉토리

- `main.py`: FastAPI 애플리케이션의 메인 파일입니다. 앱을 초기화하고, 정적 파일을 마운트하며, 템플릿을 설정하고, API 라우터를 포함합니다.
- `database.py`: SQLAlchemy를 사용한 데이터베이스 연결 설정을 포함합니다.
- `models.py`: 데이터베이스 테이블(Status, Category, Task, DailyStat, UserSetting, DailyLog)에 대한 SQLAlchemy ORM 모델을 정의합니다.
- `schemas.py`: 데이터 유효성 검사 및 직렬화를 위한 Pydantic 모델을 정의합니다.
- `routers/`: 다양한 리소스(작업, 상태, 카테고리, 설정, 통계)에 대한 API 라우터를 포함합니다.
- `utils/`: 로거와 같은 유틸리티 모듈을 포함합니다.

### `static` 디렉토리

- CSS 및 JavaScript와 같은 프론트엔드용 정적 파일을 포함합니다.

### `templates` 디렉토리

- HTML 페이지를 위한 Jinja2 템플릿을 포함합니다.

## 실행 방법

1.  **의존성 설치:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **애플리케이션 실행:**
    - Windows에서는 `start_todo_app.bat` 파일을 실행할 수 있습니다.
    - 또는 터미널에서 다음 명령을 실행할 수 있습니다.
      ```bash
      uvicorn app.main:app --reload --port 8501
      ```
    - 다른 명령어
      ```bash
      python -m app.main
      ```

3.  **애플리케이션 접속:**
    - 웹 브라우저를 열고 `http://localhost:8501`로 이동합니다.

## API 엔드포인트

API 엔드포인트는 `app/routers/` 디렉토리에 정의되어 있습니다. 주요 엔드포인트는 다음과 같습니다.

- `GET /api/tasks`: 작업 목록을 가져옵니다.
- `POST /api/tasks`: 새 작업을 생성합니다.
- `GET /api/tasks/{task_id}`: 특정 작업을 가져옵니다.
- `PUT /api/tasks/{task_id}`: 작업을 수정합니다.
- `DELETE /api/tasks/{task_id}`: 작업을 삭제합니다.
- `PUT /api/tasks/{task_id}/status`: 작업의 상태를 업데이트합니다.
- `PUT /api/tasks/{task_id}/pin`: 작업을 고정하거나 고정 해제합니다.

전체 API 엔드포인트 목록은 `app/routers/` 디렉토리의 코드를 참조하십시오.
