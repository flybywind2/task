from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Date, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Status(Base):
    __tablename__ = "statuses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    order_index = Column(Integer, default=0)
    status_type = Column(String, default="progress")  # pending, progress, done
    is_done = Column(Boolean, default=False)  # 하위 호환성을 위해 유지
    created_at = Column(DateTime, default=func.now())
    
    tasks = relationship("Task", back_populates="status")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    color = Column(String, default="#007bff")  # 기본 파란색
    created_at = Column(DateTime, default=func.now())
    
    tasks = relationship("Task", back_populates="category")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    priority = Column(Integer, default=1)
    status_id = Column(Integer, ForeignKey("statuses.id"))
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    labels = Column(Text)  # 쉼표로 구분된 레이블들
    is_pinned = Column(Boolean, default=False)
    pinned_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime)
    
    status = relationship("Status", back_populates="tasks")
    category = relationship("Category", back_populates="tasks")

class DailyStat(Base):
    __tablename__ = "daily_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False)
    tasks_added = Column(Integer, default=0)
    tasks_completed = Column(Integer, default=0)
    tasks_incomplete = Column(Integer, default=0)
    tasks_pinned = Column(Integer, default=0)

class UserSetting(Base):
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String, unique=True, nullable=False)
    setting_value = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class DailyLog(Base):
    __tablename__ = "daily_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    action_type = Column(String, nullable=False)  # created, updated, deleted, completed, status_changed
    task_id = Column(Integer, nullable=True)
    task_title = Column(String, nullable=False)
    old_data = Column(JSON, nullable=True)  # 변경 전 데이터
    new_data = Column(JSON, nullable=True)  # 변경 후 데이터
    timestamp = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<DailyLog(date={self.date}, action={self.action_type}, task='{self.task_title}')>"