from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime
import csv
import io
import codecs
from app.database import get_db
from app.models import Task, Status, Category
from app.schemas import TaskCreate

router = APIRouter()

@router.get("/csv/export")
async def export_tasks_csv(
    status_id: Optional[int] = None,
    category_id: Optional[int] = None,
    include_completed: bool = True,
    db: Session = Depends(get_db)
):
    """할일 목록을 CSV 파일로 내보내기"""
    
    # 쿼리 작성
    query = db.query(Task)
    
    # 필터 적용
    if status_id:
        query = query.filter(Task.status_id == status_id)
    
    if category_id:
        query = query.filter(Task.category_id == category_id)
    
    if not include_completed:
        query = query.join(Status).filter(Status.is_done == False)
    
    tasks = query.all()
    
    # CSV 생성
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 헤더 작성
    headers = [
        'ID',
        '제목',
        '설명',
        '우선순위',
        '상태',
        '카테고리',
        '레이블',
        '핀고정',
        '생성일',
        '수정일',
        '완료일'
    ]
    writer.writerow(headers)
    
    # 데이터 작성
    for task in tasks:
        priority_map = {1: '낮음', 2: '보통', 3: '높음', 4: '긴급'}
        
        row = [
            task.id,
            task.title,
            task.description or '',
            priority_map.get(task.priority, '보통'),
            task.status.name if task.status else '',
            task.category.name if task.category else '',
            task.labels or '',
            '예' if task.is_pinned else '아니오',
            task.created_at.strftime('%Y-%m-%d %H:%M:%S') if task.created_at else '',
            task.updated_at.strftime('%Y-%m-%d %H:%M:%S') if task.updated_at else '',
            task.completed_at.strftime('%Y-%m-%d %H:%M:%S') if task.completed_at else ''
        ]
        writer.writerow(row)
    
    # 파일명 생성
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"todo_export_{timestamp}.csv"
    
    # StringIO를 BytesIO로 변환 (UTF-8 BOM 포함)
    output.seek(0)
    csv_content = output.getvalue()
    output_bytes = io.BytesIO()
    output_bytes.write(codecs.BOM_UTF8)  # UTF-8 BOM 추가 (엑셀 호환성)
    output_bytes.write(csv_content.encode('utf-8'))
    output_bytes.seek(0)
    
    # 스트리밍 응답 반환
    def iter_file():
        yield from output_bytes
    
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"',
        'Content-Type': 'text/csv; charset=utf-8'
    }
    
    return StreamingResponse(
        iter_file(),
        media_type='text/csv',
        headers=headers
    )

@router.post("/csv/import")
async def import_tasks_csv(
    file: UploadFile = File(...),
    overwrite_existing: bool = False,
    db: Session = Depends(get_db)
):
    """CSV 파일에서 할일 목록 가져오기"""
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="CSV 파일만 업로드 가능합니다.")
    
    try:
        # 파일 내용 읽기
        content = await file.read()
        
        # UTF-8 BOM 제거
        if content.startswith(codecs.BOM_UTF8):
            content = content[len(codecs.BOM_UTF8):]
        
        # CSV 파싱
        csv_text = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        
        imported_count = 0
        updated_count = 0
        errors = []
        
        # 상태 및 카테고리 매핑 생성
        statuses = {status.name: status for status in db.query(Status).all()}
        categories = {category.name: category for category in db.query(Category).all()}
        
        # 우선순위 매핑
        priority_map = {'낮음': 1, '보통': 2, '높음': 3, '긴급': 4}
        
        for row_num, row in enumerate(csv_reader, start=2):  # 헤더 다음부터 시작
            try:
                # 필수 필드 검증
                if not row.get('제목'):
                    errors.append(f"행 {row_num}: 제목이 필요합니다.")
                    continue
                
                # 상태 확인/생성
                status_name = row.get('상태', 'Todo')
                if status_name not in statuses:
                    # 기본 상태 사용
                    status = db.query(Status).filter(Status.is_done == False).first()
                    if not status:
                        errors.append(f"행 {row_num}: 유효한 상태를 찾을 수 없습니다.")
                        continue
                else:
                    status = statuses[status_name]
                
                # 카테고리 처리
                category = None
                if row.get('카테고리'):
                    category = categories.get(row['카테고리'])
                
                # 우선순위 처리
                priority = priority_map.get(row.get('우선순위', '보통'), 2)
                
                # 기존 항목 확인 (ID 기준)
                existing_task = None
                if row.get('ID') and row['ID'].isdigit():
                    existing_task = db.query(Task).filter(Task.id == int(row['ID'])).first()
                
                if existing_task and overwrite_existing:
                    # 기존 항목 업데이트
                    existing_task.title = row['제목']
                    existing_task.description = row.get('설명', '')
                    existing_task.priority = priority
                    existing_task.status_id = status.id
                    existing_task.category_id = category.id if category else None
                    existing_task.labels = row.get('레이블')
                    existing_task.is_pinned = row.get('핀고정', '').lower() in ['예', 'true', '1']
                    existing_task.updated_at = datetime.now()
                    
                    updated_count += 1
                    
                elif not existing_task:
                    # 새 항목 생성
                    new_task = Task(
                        title=row['제목'],
                        description=row.get('설명', ''),
                        priority=priority,
                        status_id=status.id,
                        category_id=category.id if category else None,
                        labels=row.get('레이블'),
                        is_pinned=row.get('핀고정', '').lower() in ['예', 'true', '1'],
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    
                    db.add(new_task)
                    imported_count += 1
                
            except Exception as e:
                errors.append(f"행 {row_num}: {str(e)}")
                continue
        
        # 변경사항 저장
        db.commit()
        
        return {
            "message": "CSV 파일 가져오기 완료",
            "imported_count": imported_count,
            "updated_count": updated_count,
            "total_processed": imported_count + updated_count,
            "errors": errors
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"CSV 파일 처리 중 오류 발생: {str(e)}")

@router.get("/csv/template")
async def download_csv_template():
    """CSV 템플릿 파일 다운로드"""
    
    # 템플릿 CSV 생성
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 헤더
    headers = [
        'ID',
        '제목',
        '설명',
        '우선순위',
        '상태',
        '카테고리',
        '레이블',
        '핀고정',
        '생성일',
        '수정일',
        '완료일'
    ]
    writer.writerow(headers)
    
    # 예시 데이터
    example_rows = [
        ['', '할일 예시 1', '할일에 대한 설명', '높음', 'Todo', '업무', '긴급,중요', '아니오', '', '', ''],
        ['', '할일 예시 2', '또 다른 할일', '보통', 'In Progress', '개인', '학습', '예', '', '', ''],
    ]
    
    for row in example_rows:
        writer.writerow(row)
    
    # BytesIO로 변환
    output.seek(0)
    csv_content = output.getvalue()
    output_bytes = io.BytesIO()
    output_bytes.write(codecs.BOM_UTF8)  # UTF-8 BOM 추가
    output_bytes.write(csv_content.encode('utf-8'))
    output_bytes.seek(0)
    
    def iter_file():
        yield from output_bytes
    
    headers = {
        'Content-Disposition': 'attachment; filename="todo_template.csv"',
        'Content-Type': 'text/csv; charset=utf-8'
    }
    
    return StreamingResponse(
        iter_file(),
        media_type='text/csv',
        headers=headers
    )