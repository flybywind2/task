from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.models import UserSetting
from app.schemas import Setting as SettingSchema, SettingCreate, SettingUpdate

router = APIRouter()

@router.get("/settings", response_model=List[SettingSchema])
async def get_settings(db: Session = Depends(get_db)):
    return db.query(UserSetting).all()

@router.get("/settings/{setting_key}", response_model=SettingSchema)
async def get_setting(setting_key: str, db: Session = Depends(get_db)):
    setting = db.query(UserSetting).filter(UserSetting.setting_key == setting_key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting

@router.put("/settings/{setting_key}", response_model=SettingSchema)
async def update_setting(setting_key: str, setting: SettingUpdate, db: Session = Depends(get_db)):
    db_setting = db.query(UserSetting).filter(UserSetting.setting_key == setting_key).first()
    
    if not db_setting:
        # 새로운 설정 생성
        db_setting = UserSetting(setting_key=setting_key, setting_value=setting.setting_value)
        db.add(db_setting)
    else:
        # 기존 설정 업데이트
        db_setting.setting_value = setting.setting_value
    
    db.commit()
    db.refresh(db_setting)
    return db_setting

@router.post("/settings", response_model=SettingSchema)
async def create_setting(setting: SettingCreate, db: Session = Depends(get_db)):
    # 중복 키 확인
    existing_setting = db.query(UserSetting).filter(UserSetting.setting_key == setting.setting_key).first()
    if existing_setting:
        raise HTTPException(status_code=400, detail="Setting key already exists")
    
    db_setting = UserSetting(**setting.dict())
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return db_setting

@router.put("/settings")
async def update_settings(settings: Dict[str, Any], db: Session = Depends(get_db)):
    updated_settings = []
    
    for key, value in settings.items():
        db_setting = db.query(UserSetting).filter(UserSetting.setting_key == key).first()
        
        if not db_setting:
            db_setting = UserSetting(setting_key=key, setting_value=str(value))
            db.add(db_setting)
        else:
            db_setting.setting_value = str(value)
        
        updated_settings.append(db_setting)
    
    db.commit()
    return {"message": f"Updated {len(updated_settings)} settings"}

@router.delete("/settings/{setting_key}")
async def delete_setting(setting_key: str, db: Session = Depends(get_db)):
    db_setting = db.query(UserSetting).filter(UserSetting.setting_key == setting_key).first()
    if not db_setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    db.delete(db_setting)
    db.commit()
    return {"message": "Setting deleted successfully"}