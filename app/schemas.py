from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List
from enum import Enum

class StatusType(str, Enum):
    PENDING = "pending"
    PROGRESS = "progress" 
    DONE = "done"

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class SortBy(str, Enum):
    NAME = "name"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    PRIORITY = "priority"
    PINNED = "pinned"

# Status schemas
class StatusBase(BaseModel):
    name: str
    order_index: Optional[int] = 0
    status_type: Optional[StatusType] = StatusType.PROGRESS
    is_done: Optional[bool] = False

class StatusCreate(StatusBase):
    pass

class StatusUpdate(BaseModel):
    name: Optional[str] = None
    order_index: Optional[int] = None
    status_type: Optional[StatusType] = None
    is_done: Optional[bool] = None

class Status(StatusBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Task schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[int] = 1
    status_id: int
    category_id: Optional[int] = None
    labels: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    status_id: Optional[int] = None
    category_id: Optional[int] = None
    labels: Optional[str] = None

class TaskPin(BaseModel):
    is_pinned: bool

# Category schemas
class CategoryBase(BaseModel):
    name: str
    color: Optional[str] = "#007bff"

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None

class Category(CategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Task(TaskBase):
    id: int
    is_pinned: bool
    pinned_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    status: Status
    category: Optional[Category] = None
    
    class Config:
        from_attributes = True

# Setting schemas
class SettingBase(BaseModel):
    setting_key: str
    setting_value: str

class SettingCreate(SettingBase):
    pass

class SettingUpdate(BaseModel):
    setting_value: str

class Setting(SettingBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Stats schemas
class DailyStatBase(BaseModel):
    date: date
    tasks_added: int = 0
    tasks_completed: int = 0
    tasks_incomplete: int = 0
    tasks_pinned: int = 0

class DailyStat(DailyStatBase):
    id: int
    
    class Config:
        from_attributes = True

class SummaryStats(BaseModel):
    total_tasks: int
    completed_tasks: int
    incomplete_tasks: int
    pinned_tasks: int
    completion_rate: float
    status_breakdown: dict

class TaskQuery(BaseModel):
    status_id: Optional[int] = None
    sort_by: Optional[SortBy] = SortBy.PINNED
    sort_order: Optional[SortOrder] = SortOrder.DESC
    days_filter: Optional[int] = None