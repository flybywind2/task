# Todo2 관리 애플리케이션

FastAPI와 현대적인 웹 기술을 기반으로 구축된 종합적인 Todo 관리 애플리케이션입니다. 직관적인 칸반보드와 리스트뷰를 제공하며, 풍부한 통계 및 데이터 관리 기능을 갖추고 있습니다.

## ✨ 주요 기능

### 📋 **할일 관리**
- **CRUD 작업**: 할일 생성, 조회, 수정, 삭제
- **상태 관리**: 커스터마이징 가능한 상태 시스템 (Backlog → Todo → In Progress → Done)
- **우선순위 설정**: 4단계 우선순위 (낮음, 보통, 높음, 긴급)
- **핀고정**: 중요한 할일을 목록 상단에 고정
- **Rich Text 편집**: Quill 에디터를 통한 풍부한 텍스트 편집

### 🎨 **시각화 및 뷰**
- **칸반보드**: 드래그 앤 드롭으로 상태 변경 가능한 직관적인 보드
- **리스트뷰**: 테이블 형태의 상세한 할일 관리
- **레이블 그룹핑**: 레이블별로 할일을 그룹화하여 표시
- **반응형 디자인**: 모든 디바이스에서 완벽한 사용자 경험

### 🏷️ **분류 및 태깅**
- **카테고리**: 색상별 카테고리로 할일 분류
- **레이블**: 다중 레이블을 통한 유연한 태깅 시스템
- **스마트 필터링**: 상태, 카테고리, 우선순위별 필터링

### 📊 **대시보드 및 통계**
- **전체 완료율**: 실시간 진행률 추적
- **상태별 현황**: 원형 차트로 상태별 할일 분포 시각화
- **카테고리별 통계**: 카테고리별 완료율 및 현황
- **레이블별 진행률**: 레이블별 완료 상태 추적
- **일별/누적 통계**: 시간별 생산성 분석
- **최근 활동**: 최근 할일 생성 및 완료 이력

### 📤 **데이터 관리**
- **CSV 내보내기**: 필터링된 데이터를 CSV로 내보내기
- **CSV 가져오기**: 기존 데이터를 CSV로 일괄 가져오기
- **템플릿 제공**: CSV 형식 가이드 및 예시 파일
- **데이터 백업**: 자동 백업 및 복원 기능

### ⚙️ **고급 기능**
- **일괄 작업**: 여러 할일을 한번에 수정/삭제
- **키보드 단축키**: 빠른 작업을 위한 단축키 지원
- **실시간 알림**: 작업 상태 변경 시 즉시 알림
- **로컬 스토리지**: 사용자 설정 및 뷰 상태 저장

## 🏗️ 프로젝트 구조

```
todo2/
├── app/                          # FastAPI 백엔드 애플리케이션
│   ├── __init__.py
│   ├── main.py                   # 메인 애플리케이션 파일
│   ├── database.py               # 데이터베이스 연결 설정
│   ├── models.py                 # SQLAlchemy ORM 모델
│   ├── schemas.py                # Pydantic 스키마 정의
│   ├── routers/                  # API 라우터 모듈
│   │   ├── __init__.py
│   │   ├── tasks.py              # 할일 관리 API
│   │   ├── statuses.py           # 상태 관리 API
│   │   ├── categories.py         # 카테고리 관리 API
│   │   ├── settings.py           # 설정 관리 API
│   │   ├── stats.py              # 통계 및 대시보드 API
│   │   └── csv_export.py         # CSV 내보내기/가져오기 API
│   └── utils/
│       └── logger.py             # 로깅 유틸리티
├── static/                       # 정적 파일 (CSS, JS)
│   ├── css/
│   │   └── style.css            # 메인 스타일시트
│   └── js/
│       └── app.js               # 프론트엔드 JavaScript
├── templates/                    # Jinja2 HTML 템플릿
│   ├── base.html                # 기본 레이아웃
│   ├── index.html               # 메인 페이지 (칸반보드/리스트뷰)
│   └── dashboard.html           # 대시보드 페이지
├── logs/                        # 애플리케이션 로그
├── venv/                        # Python 가상환경
├── main.py                      # 독립 실행형 메인 파일
├── reset_database.py            # 데이터베이스 초기화 스크립트
├── requirements.txt             # Python 의존성
├── todo2.spec                   # PyInstaller 설정
├── build_exe.bat               # Windows EXE 빌드 스크립트
├── quick_build.bat             # 빠른 EXE 빌드 스크립트
├── start_with_browser.bat      # 브라우저 자동 실행 스크립트
├── README.md                   # 프로젝트 문서
├── README_EXE.md              # EXE 빌드 가이드
└── todo.db                     # SQLite 데이터베이스
```

## 🚀 설치 및 실행

### **요구사항**
- Python 3.8+
- 웹 브라우저 (Chrome, Firefox, Edge 등)

### **방법 1: 간편 실행 (권장)**

#### Windows 사용자
1. **프로젝트 다운로드** 또는 클론
2. **`start_with_browser.bat` 실행** (더블클릭)
   - 자동으로 가상환경 활성화
   - 의존성 설치
   - 서버 시작
   - 브라우저 자동 실행

#### 수동 설정
```bash
# 1. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 또는
venv\Scripts\activate     # Windows

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 애플리케이션 실행
python main.py
# 또는
python -m app.main
# 또는
uvicorn app.main:app --host 0.0.0.0 --port 8501 --reload
```

### **방법 2: EXE 파일 생성**

독립 실행 가능한 EXE 파일을 만들 수 있습니다:

```bash
# 빠른 빌드 (권장)
quick_build.bat

# 또는 수동 빌드
build_exe.bat
```

자세한 내용은 [README_EXE.md](README_EXE.md)를 참조하세요.

### **접속**
- 브라우저에서 `http://localhost:8501` 또는 `http://127.0.0.1:8501` 접속
- 서버가 자동으로 사용 가능한 포트를 찾아 실행됩니다

## 🎯 사용 방법

### **기본 설정**
1. **첫 실행 시**: 기본 상태들이 자동 생성됩니다
   - Backlog (진행 전)
   - Todo (진행 전)
   - In Progress (진행 중)
   - Done (완료)

2. **할일 추가**: 
   - 상단의 빠른 추가 입력창 사용
   - "상세" 버튼으로 Rich Text 편집

3. **뷰 전환**:
   - **칸반보드**: 드래그 앤 드롭으로 직관적 관리
   - **리스트뷰**: 테이블 형태로 상세 관리

### **고급 기능**
- **레이블 그룹핑**: 칸반보드에서 레이블별 그룹화
- **CSV 관리**: 데이터 내보내기/가져오기
- **대시보드**: 통계 및 진행률 확인
- **상태/카테고리 관리**: 커스터마이징 가능한 워크플로우

## 🔧 데이터베이스 관리

### **초기화**
```bash
python reset_database.py
```

### **백업**
```bash
# 수동 백업
cp todo.db todo_backup_$(date +%Y%m%d).db
```

## 🔌 API 엔드포인트

### **할일 관리** (`/api/tasks`)
- `GET /api/tasks` - 할일 목록 조회 (필터링, 정렬 지원)
- `POST /api/tasks` - 새 할일 생성
- `GET /api/tasks/{task_id}` - 특정 할일 조회
- `PUT /api/tasks/{task_id}` - 할일 수정
- `DELETE /api/tasks/{task_id}` - 할일 삭제
- `PUT /api/tasks/{task_id}/status` - 상태 변경
- `PUT /api/tasks/{task_id}/pin` - 핀고정 토글

### **상태 관리** (`/api/statuses`)
- `GET /api/statuses` - 상태 목록 조회
- `POST /api/statuses` - 새 상태 생성
- `PUT /api/statuses/{status_id}` - 상태 수정
- `DELETE /api/statuses/{status_id}` - 상태 삭제

### **카테고리 관리** (`/api/categories`)
- `GET /api/categories` - 카테고리 목록 조회
- `POST /api/categories` - 새 카테고리 생성
- `PUT /api/categories/{category_id}` - 카테고리 수정
- `DELETE /api/categories/{category_id}` - 카테고리 삭제

### **통계 및 대시보드** (`/api/stats`)
- `GET /api/stats/summary` - 전체 요약 통계
- `GET /api/stats/daily` - 일별 통계
- `GET /api/stats/cumulative` - 누적 통계
- `GET /api/stats/labels` - 레이블별 통계
- `GET /api/stats/recent-activities` - 최근 활동

### **CSV 관리** (`/api/csv`)
- `GET /api/csv/export` - CSV 내보내기
- `POST /api/csv/import` - CSV 가져오기
- `GET /api/csv/template` - CSV 템플릿 다운로드

### **설정** (`/api/settings`)
- `GET /api/settings` - 설정 조회
- `PUT /api/settings/{key}` - 설정 업데이트

## 🛠️ 기술 스택

### **백엔드**
- **FastAPI** - 고성능 웹 프레임워크
- **SQLAlchemy** - ORM 및 데이터베이스 관리
- **SQLite** - 경량 데이터베이스
- **Pydantic** - 데이터 검증 및 설정

### **프론트엔드**
- **HTML5/CSS3** - 마크업 및 스타일링
- **JavaScript (ES6+)** - 클라이언트 사이드 로직
- **Bootstrap 5** - UI 프레임워크
- **Chart.js** - 데이터 시각화
- **Quill.js** - Rich Text 에디터
- **SortableJS** - 드래그 앤 드롭

### **배포 및 빌드**
- **PyInstaller** - EXE 파일 생성
- **Uvicorn** - ASGI 서버

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 문의

프로젝트에 대한 문의사항이나 버그 리포트는 GitHub Issues를 통해 제출해주세요.

---

**Todo2** - 효율적이고 직관적인 할일 관리의 새로운 표준 ✨
