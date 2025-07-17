from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, date, timedelta
from app.database import get_db
from app.models import Task, Status, DailyStat
from app.schemas import DailyStat as DailyStatSchema, SummaryStats

router = APIRouter()

@router.get("/stats/daily", response_model=List[DailyStatSchema])
async def get_daily_stats(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(DailyStat)
    
    if start_date:
        query = query.filter(DailyStat.date >= start_date)
    if end_date:
        query = query.filter(DailyStat.date <= end_date)
    
    return query.order_by(DailyStat.date.desc()).all()

@router.get("/stats/summary", response_model=SummaryStats)
async def get_summary_stats(db: Session = Depends(get_db)):
    # 전체 태스크 수
    total_tasks = db.query(Task).count()
    
    # 완료된 태스크 수 (상태가 완료인 것들)
    completed_tasks = db.query(Task).join(Status).filter(Status.is_done == True).count()
    
    # 미완료 태스크 수
    incomplete_tasks = total_tasks - completed_tasks
    
    # 핀고정된 태스크 수
    pinned_tasks = db.query(Task).filter(Task.is_pinned == True).count()
    
    # 완료율 계산
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # 상태별 태스크 수
    status_breakdown = {}
    status_counts = db.query(
        Status.name, 
        func.count(Task.id).label('count')
    ).outerjoin(Task).group_by(Status.id, Status.name).all()
    
    for status_name, count in status_counts:
        status_breakdown[status_name] = count
    
    return SummaryStats(
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        incomplete_tasks=incomplete_tasks,
        pinned_tasks=pinned_tasks,
        completion_rate=round(completion_rate, 2),
        status_breakdown=status_breakdown
    )

@router.get("/stats/cumulative")
async def get_cumulative_stats(
    days: Optional[int] = Query(30),
    db: Session = Depends(get_db)
):
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # 기간별 누적 통계
    daily_stats = db.query(DailyStat).filter(
        and_(DailyStat.date >= start_date, DailyStat.date <= end_date)
    ).order_by(DailyStat.date).all()
    
    cumulative_data = []
    cumulative_added = 0
    cumulative_completed = 0
    
    # 선택된 기간의 시작점을 0으로 설정 (상대적 누적)
    for stat in daily_stats:
        cumulative_added += stat.tasks_added
        cumulative_completed += stat.tasks_completed
        
        # 완료율 계산 (누적 추가가 0이면 0%, 아니면 정상 계산하되 100% 제한)
        if cumulative_added > 0:
            completion_rate = min((cumulative_completed / cumulative_added * 100), 100.0)
        else:
            completion_rate = 0
        
        cumulative_data.append({
            "date": stat.date,
            "daily_added": stat.tasks_added,
            "daily_completed": stat.tasks_completed,
            "cumulative_added": cumulative_added,
            "cumulative_completed": cumulative_completed,
            "completion_rate": completion_rate
        })
    
    return {
        "period": f"{start_date} to {end_date}",
        "data": cumulative_data
    }

@router.post("/stats/update-daily")
async def update_daily_stats(target_date: Optional[date] = None, db: Session = Depends(get_db)):
    if not target_date:
        target_date = date.today()
    
    # 해당 날짜의 통계 계산
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = datetime.combine(target_date, datetime.max.time())
    
    # 추가된 태스크 수
    tasks_added = db.query(Task).filter(
        and_(Task.created_at >= start_datetime, Task.created_at <= end_datetime)
    ).count()
    
    # 완료된 태스크 수
    tasks_completed = db.query(Task).filter(
        and_(Task.completed_at >= start_datetime, Task.completed_at <= end_datetime)
    ).count()
    
    # 미완료 태스크 수 (전체 - 완료)
    tasks_incomplete = db.query(Task).filter(Task.completed_at.is_(None)).count()
    
    # 핀고정된 태스크 수
    tasks_pinned = db.query(Task).filter(Task.is_pinned == True).count()
    
    # 기존 통계 업데이트 또는 새로 생성
    daily_stat = db.query(DailyStat).filter(DailyStat.date == target_date).first()
    
    if not daily_stat:
        daily_stat = DailyStat(
            date=target_date,
            tasks_added=tasks_added,
            tasks_completed=tasks_completed,
            tasks_incomplete=tasks_incomplete,
            tasks_pinned=tasks_pinned
        )
        db.add(daily_stat)
    else:
        daily_stat.tasks_added = tasks_added
        daily_stat.tasks_completed = tasks_completed
        daily_stat.tasks_incomplete = tasks_incomplete
        daily_stat.tasks_pinned = tasks_pinned
    
    db.commit()
    db.refresh(daily_stat)
    
    return {"message": "Daily stats updated successfully", "stats": daily_stat}

@router.get("/stats/recent-activities")
async def get_recent_activities(
    limit: Optional[int] = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """최근 활동 내역 조회"""
    
    # 최근 생성된 태스크
    recent_tasks = db.query(Task).order_by(Task.created_at.desc()).limit(limit//2).all()
    
    # 최근 완료된 태스크
    recent_completed = db.query(Task).filter(
        Task.completed_at.isnot(None)
    ).order_by(Task.completed_at.desc()).limit(limit//2).all()
    
    activities = []
    
    # 생성된 태스크 활동
    for task in recent_tasks:
        activities.append({
            "id": f"created_{task.id}",
            "type": "created",
            "action": "생성됨",
            "task_title": task.title,
            "task_id": task.id,
            "timestamp": task.created_at,
            "icon": "fa-plus",
            "color": "text-primary"
        })
    
    # 완료된 태스크 활동
    for task in recent_completed:
        activities.append({
            "id": f"completed_{task.id}",
            "type": "completed", 
            "action": "완료됨",
            "task_title": task.title,
            "task_id": task.id,
            "timestamp": task.completed_at,
            "icon": "fa-check",
            "color": "text-success"
        })
    
    # 시간순으로 정렬
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # 최대 개수로 제한
    activities = activities[:limit]
    
    return {"activities": activities}