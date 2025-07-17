from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Category, Task
from app.schemas import Category as CategorySchema, CategoryCreate, CategoryUpdate

router = APIRouter()

@router.get("/categories", response_model=List[CategorySchema])
async def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

@router.get("/categories/{category_id}", response_model=CategorySchema)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/categories", response_model=CategorySchema)
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    # 중복 이름 확인
    existing_category = db.query(Category).filter(Category.name == category.name).first()
    if existing_category:
        raise HTTPException(status_code=400, detail="Category name already exists")
    
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    # 로깅
    try:
        print(f"[CATEGORY] 새 카테고리 생성: {db_category.name}")
    except Exception as e:
        print(f"로깅 실패: {e}")
    
    return db_category

@router.put("/categories/{category_id}", response_model=CategorySchema)
async def update_category(category_id: int, category: CategoryUpdate, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # 이름 변경 시 중복 확인
    if category.name and category.name != db_category.name:
        existing_category = db.query(Category).filter(Category.name == category.name).first()
        if existing_category:
            raise HTTPException(status_code=400, detail="Category name already exists")
    
    update_data = category.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    
    # 로깅
    try:
        print(f"[CATEGORY] 카테고리 수정: {db_category.name}")
    except Exception as e:
        print(f"로깅 실패: {e}")
    
    return db_category

@router.delete("/categories/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # 해당 카테고리를 사용하는 태스크가 있는지 확인
    tasks_count = db.query(Task).filter(Task.category_id == category_id).count()
    if tasks_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete category with existing tasks")
    
    # 로깅
    try:
        print(f"[CATEGORY] 카테고리 삭제: {db_category.name}")
    except Exception as e:
        print(f"로깅 실패: {e}")
    
    db.delete(db_category)
    db.commit()
    return {"message": "Category deleted successfully"}