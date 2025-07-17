# Todo2 EXE 파일 빌드 가이드

이 가이드는 Todo2 애플리케이션을 독립 실행 가능한 EXE 파일로 만드는 방법을 설명합니다.

## 🚀 빌드 방법

### Windows 사용자

1. **자동 빌드 (권장)**
   ```bash
   build_exe.bat
   ```
   - 배치 파일을 더블클릭하거나 명령프롬프트에서 실행
   - 자동으로 의존성 설치, 빌드, 테스트까지 수행

2. **수동 빌드**
   ```bash
   # 가상환경 활성화 (선택사항)
   venv\Scripts\activate
   
   # PyInstaller 설치
   pip install pyinstaller
   
   # EXE 파일 빌드
   pyinstaller todo2.spec
   ```

### Linux/macOS 사용자

1. **자동 빌드 (권장)**
   ```bash
   ./build_exe.sh
   ```

2. **수동 빌드**
   ```bash
   # 가상환경 활성화 (선택사항)
   source venv/bin/activate
   
   # PyInstaller 설치
   pip install pyinstaller
   
   # 실행 파일 빌드
   pyinstaller todo2.spec
   ```

## 📁 빌드 결과

빌드가 완료되면 다음 위치에 실행 파일이 생성됩니다:

- **Windows**: `dist/Todo2.exe`
- **Linux/macOS**: `dist/Todo2`

## 🎯 사용 방법

1. **실행 파일 실행**
   - Windows: `Todo2.exe` 더블클릭
   - Linux/macOS: `./Todo2` 실행

2. **자동 실행 과정**
   - 애플리케이션이 시작되면 자동으로 사용 가능한 포트를 찾습니다
   - 웹 서버가 시작됩니다 (기본: http://127.0.0.1:8501)
   - 자동으로 브라우저가 열립니다
   - Todo 관리 웹 애플리케이션을 사용할 수 있습니다

3. **종료 방법**
   - 콘솔 창에서 `Ctrl+C` 또는 창 닫기
   - 브라우저는 별도로 닫아야 합니다

## 🔧 문제 해결

### 빌드 오류 시

1. **의존성 설치 확인**
   ```bash
   pip install -r requirements.txt
   ```

2. **PyInstaller 재설치**
   ```bash
   pip uninstall pyinstaller
   pip install pyinstaller
   ```

3. **빌드 디렉토리 정리**
   ```bash
   # Windows
   rmdir /s /q build dist
   
   # Linux/macOS
   rm -rf build dist
   ```

### 실행 오류 시

1. **포트 충돌**
   - 다른 애플리케이션이 8501 포트를 사용 중인 경우
   - 자동으로 다른 포트를 찾아 사용합니다

2. **브라우저가 열리지 않는 경우**
   - 콘솔에 표시된 URL을 수동으로 브라우저에 입력
   - 예: http://127.0.0.1:8501

3. **데이터베이스 오류**
   - 첫 실행 시 자동으로 SQLite 데이터베이스 생성
   - `todo.db` 파일이 실행 파일과 같은 위치에 생성됩니다

## 📋 포함된 기능

- **할일 관리**: 생성, 수정, 삭제, 상태 변경
- **칸반보드**: 드래그 앤 드롭으로 상태 변경
- **리스트뷰**: 테이블 형태로 할일 관리
- **카테고리**: 색상별 카테고리 분류
- **레이블**: 태그 기반 분류 및 그룹핑
- **대시보드**: 진행률 및 통계 확인
- **핀고정**: 중요한 할일 우선 표시

## 🎨 커스터마이징

### 포트 변경
`main.py` 파일에서 `self.port = 8501` 부분을 수정

### 아이콘 추가
1. ICO 파일 준비 (32x32 또는 64x64 권장)
2. `todo2.spec` 파일에서 `icon=None` 부분을 `icon='path/to/icon.ico'`로 수정

### 추가 파일 포함
`todo2.spec` 파일의 `datas` 리스트에 필요한 파일 경로 추가

## 📦 배포

생성된 EXE 파일은 다른 컴퓨터에서도 Python 설치 없이 실행 가능합니다.

**주의사항:**
- Windows EXE는 Windows에서만 실행 가능
- Linux/macOS 실행 파일은 해당 플랫폼에서만 실행 가능
- 각 플랫폼별로 별도 빌드 필요

## 🆘 지원

문제가 발생하거나 개선 사항이 있다면 GitHub Issues를 통해 문의해주세요.