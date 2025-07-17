from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, asc, and_
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Task, Status, Category
from app.schemas import Task as TaskSchema, TaskCreate, TaskUpdate, TaskPin, TaskQuery, SortBy, SortOrder
from app.utils.logger import daily_logger

router = APIRouter()

@router.get("/tasks", response_model=List[TaskSchema])
async def get_tasks(
    status_id: Optional[int] = Query(None),
    sort_by: Optional[SortBy] = Query(SortBy.PINNED),
    sort_order: Optional[SortOrder] = Query(SortOrder.DESC),
    days_filter: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Task).options(joinedload(Task.status), joinedload(Task.category))
    
    # 상태별 필터링
    if status_id:
        query = query.filter(Task.status_id == status_id)
    
    # 완료 단계 필터링
    if days_filter and status_id:
        status = db.query(Status).filter(Status.id == status_id).first()
        if status and status.is_done:
            cutoff_date = datetime.now() - timedelta(days=days_filter)
            query = query.filter(Task.completed_at >= cutoff_date)
    
    # 정렬
    if sort_by == SortBy.PINNED:
        if sort_order == SortOrder.DESC:
            query = query.order_by(desc(Task.is_pinned), desc(Task.pinned_at), desc(Task.created_at))
        else:
            query = query.order_by(asc(Task.is_pinned), asc(Task.pinned_at), asc(Task.created_at))
    elif sort_by == SortBy.NAME:
        if sort_order == SortOrder.DESC:
            query = query.order_by(desc(Task.is_pinned), desc(Task.pinned_at), desc(Task.title))
        else:
            query = query.order_by(desc(Task.is_pinned), desc(Task.pinned_at), asc(Task.title))
    elif sort_by == SortBy.CREATED_AT:
        if sort_order == SortOrder.DESC:
            query = query.order_by(desc(Task.is_pinned), desc(Task.pinned_at), desc(Task.created_at))
        else:
            query = query.order_by(desc(Task.is_pinned), desc(Task.pinned_at), asc(Task.created_at))
    elif sort_by == SortBy.UPDATED_AT:
        if sort_order == SortOrder.DESC:
            query = query.order_by(desc(Task.is_pinned), desc(Task.pinned_at), desc(Task.updated_at))
        else:
            query = query.order_by(desc(Task.is_pinned), desc(Task.pinned_at), asc(Task.updated_at))
    elif sort_by == SortBy.PRIORITY:
        if sort_order == SortOrder.DESC:
            query = query.order_by(desc(Task.is_pinned), desc(Task.pinned_at), desc(Task.priority))
        else:
            query = query.order_by(desc(Task.is_pinned), desc(Task.pinned_at), asc(Task.priority))
    
    return query.all()

@router.get("/tasks/{task_id}", response_model=TaskSchema)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).options(joinedload(Task.status), joinedload(Task.category)).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/tasks", response_model=TaskSchema)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    # 상태 확인
    status = db.query(Status).filter(Status.id == task.status_id).first()
    if not status:
        raise HTTPException(status_code=400, detail="Status not found")
    
    # 카테고리 확인 (선택사항)
    category = None
    if task.category_id:
        category = db.query(Category).filter(Category.id == task.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")
    
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # 로깅
    try:
        task_data = {
            "id": db_task.id,
            "title": db_task.title,
            "status": status.name,
            "category": category.name if category else None,
            "priority": db_task.priority,
            "is_pinned": db_task.is_pinned
        }
        daily_logger.log_task_created(task_data)
    except Exception as e:
        print(f"로깅 실패: {e}")
    
    return db_task

@router.put("/tasks/{task_id}", response_model=TaskSchema)
async def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # 로깅을 위한 변경 전 데이터 저장
    old_data = {
        "id": db_task.id,
        "title": db_task.title,
        "status": db_task.status.name if db_task.status else None,
        "category": db_task.category.name if db_task.category else None,
        "priority": db_task.priority,
        "is_pinned": db_task.is_pinned
    }
    
    # 상태 변경 시 완료 시간 업데이트
    if task.status_id and task.status_id != db_task.status_id:
        new_status = db.query(Status).filter(Status.id == task.status_id).first()
        if new_status and new_status.is_done:
            db_task.completed_at = datetime.now()
        else:
            db_task.completed_at = None
    
    update_data = task.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    
    # 로깅
    try:
        new_data = {
            "id": db_task.id,
            "title": db_task.title,
            "status": db_task.status.name if db_task.status else None,
            "category": db_task.category.name if db_task.category else None,
            "priority": db_task.priority,
            "is_pinned": db_task.is_pinned
        }
        daily_logger.log_task_updated(new_data, old_data)
    except Exception as e:
        print(f"로깅 실패: {e}")
    
    return db_task

@router.put("/tasks/{task_id}/status")
async def update_task_status(task_id: int, status_id: int, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    status = db.query(Status).filter(Status.id == status_id).first()
    if not status:
        raise HTTPException(status_code=400, detail="Status not found")
    
    # 로깅을 위한 이전 상태 저장
    old_status = db_task.status.name if db_task.status else None
    
    # 완료 상태로 변경 시 완료 시간 설정
    if status.is_done:
        db_task.completed_at = datetime.now()
    else:
        db_task.completed_at = None
    
    db_task.status_id = status_id
    db.commit()
    db.refresh(db_task)
    
    # 로깅
    try:
        task_data = {
            "id": db_task.id,
            "title": db_task.title,
            "status": status.name,
            "category": db_task.category.name if db_task.category else None,
            "priority": db_task.priority,
            "is_pinned": db_task.is_pinned
        }
        daily_logger.log_task_status_changed(task_data, old_status, status.name)
        
        # 완료 상태인 경우 완료 로그도 추가
        if status.is_done:
            daily_logger.log_task_completed(task_data)
    except Exception as e:
        print(f"로깅 실패: {e}")
    
    return {"message": "Status updated successfully"}

@router.put("/tasks/{task_id}/pin")
async def toggle_task_pin(task_id: int, pin_data: TaskPin, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_task.is_pinned = pin_data.is_pinned
    if pin_data.is_pinned:
        db_task.pinned_at = datetime.now()
    else:
        db_task.pinned_at = None
    
    db.commit()
    db.refresh(db_task)
    
    # 로깅
    try:
        task_data = {
            "id": db_task.id,
            "title": db_task.title,
            "status": db_task.status.name if db_task.status else None,
            "category": db_task.category.name if db_task.category else None,
            "priority": db_task.priority,
            "is_pinned": db_task.is_pinned
        }
        daily_logger.log_task_pinned(task_data, pin_data.is_pinned)
    except Exception as e:
        print(f"로깅 실패: {e}")
    
    return {"message": "Pin status updated successfully"}

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # 로깅을 위한 삭제 전 데이터 저장
    task_data = {
        "id": db_task.id,
        "title": db_task.title,
        "status": db_task.status.name if db_task.status else None,
        "category": db_task.category.name if db_task.category else None,
        "priority": db_task.priority,
        "is_pinned": db_task.is_pinned
    }
    
    db.delete(db_task)
    db.commit()
    
    # 로깅
    try:
        daily_logger.log_task_deleted(task_data)
    except Exception as e:
        print(f"로깅 실패: {e}")
    
    return {"message": "Task deleted successfully"}