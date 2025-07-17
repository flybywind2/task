from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database import get_db
from app.models import Status, Task
from app.schemas import Status as StatusSchema, StatusCreate, StatusUpdate
from app.utils.logger import daily_logger

router = APIRouter()

@router.get("/statuses", response_model=List[StatusSchema])
async def get_statuses(db: Session = Depends(get_db)):
    return db.query(Status).order_by(Status.order_index).all()

@router.get("/statuses/{status_id}", response_model=StatusSchema)
async def get_status(status_id: int, db: Session = Depends(get_db)):
    status = db.query(Status).filter(Status.id == status_id).first()
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")
    return status

@router.post("/statuses", response_model=StatusSchema)
async def create_status(status: StatusCreate, db: Session = Depends(get_db)):
    try:
        # 중복 이름 확인
        existing_status = db.query(Status).filter(Status.name == status.name).first()
        if existing_status:
            raise HTTPException(status_code=400, detail="Status name already exists")
        
        # 다음 order_index 계산
        max_order = db.query(func.max(Status.order_index)).scalar() or 0
        
        status_data = status.dict()
        status_data['order_index'] = max_order + 1
        
        # status_type에 따라 is_done 값 설정
        if status_data.get('status_type') == 'done':
            status_data['is_done'] = True
        else:
            status_data['is_done'] = False
        
        db_status = Status(**status_data)
        db.add(db_status)
        db.commit()
        db.refresh(db_status)
        
        # 로깅
        try:
            status_data = {
                "id": db_status.id,
                "name": db_status.name,
                "status_type": db_status.status_type,
                "order_index": db_status.order_index
            }
            print(f"[STATUS] 새 상태 생성: {db_status.name}")
        except Exception as e:
            print(f"로깅 실패: {e}")
        
        return db_status
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"상태 생성 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/statuses/{status_id}", response_model=StatusSchema)
async def update_status(status_id: int, status: StatusUpdate, db: Session = Depends(get_db)):
    db_status = db.query(Status).filter(Status.id == status_id).first()
    if not db_status:
        raise HTTPException(status_code=404, detail="Status not found")
    
    # 이름 변경 시 중복 확인
    if status.name and status.name != db_status.name:
        existing_status = db.query(Status).filter(Status.name == status.name).first()
        if existing_status:
            raise HTTPException(status_code=400, detail="Status name already exists")
    
    # 상태 변경으로 인한 태스크 상태 변경 로깅
    old_status_name = db_status.name
    
    update_data = status.dict(exclude_unset=True)
    
    # status_type에 따라 is_done 값 자동 설정
    if 'status_type' in update_data:
        if update_data['status_type'] == 'done':
            update_data['is_done'] = True
        else:
            update_data['is_done'] = False
    
    for field, value in update_data.items():
        setattr(db_status, field, value)
    
    db.commit()
    db.refresh(db_status)
    
    # 상태 이름이 변경된 경우 해당 상태를 사용하는 모든 태스크에 대해 로깅
    if status.name and status.name != old_status_name:
        try:
            affected_tasks = db.query(Task).filter(Task.status_id == status_id).all()
            for task in affected_tasks:
                task_data = {
                    "id": task.id,
                    "title": task.title,
                    "status": db_status.name,
                    "category": task.category.name if task.category else None,
                    "priority": task.priority,
                    "is_pinned": task.is_pinned
                }
                daily_logger.log_task_status_changed(task_data, old_status_name, db_status.name)
        except Exception as e:
            print(f"상태 변경 로깅 실패: {e}")
    
    return db_status

@router.delete("/statuses/{status_id}")
async def delete_status(status_id: int, db: Session = Depends(get_db)):
    db_status = db.query(Status).filter(Status.id == status_id).first()
    if not db_status:
        raise HTTPException(status_code=404, detail="Status not found")
    
    # 해당 상태를 사용하는 태스크가 있는지 확인
    tasks_count = db.query(Task).filter(Task.status_id == status_id).count()
    if tasks_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete status with existing tasks")
    
    # 로깅
    try:
        print(f"[STATUS] 상태 삭제: {db_status.name}")
    except Exception as e:
        print(f"로깅 실패: {e}")
    
    db.delete(db_status)
    db.commit()
    return {"message": "Status deleted successfully"}