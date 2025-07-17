#!/usr/bin/env python3
"""
데이터베이스 초기화 스크립트
기존 데이터베이스를 백업하고 새로 생성합니다.
"""

import os
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

def reset_database():
    db_path = Path("todo.db")
    
    # 기존 데이터베이스 백업
    if db_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"todo_backup_{timestamp}.db"
        
        try:
            shutil.copy2(db_path, backup_path)
            print(f"✅ 기존 데이터베이스 백업 완료: {backup_path}")
        except Exception as e:
            print(f"⚠️ 백업 실패: {e}")
    
    # 기존 데이터베이스 삭제
    try:
        if db_path.exists():
            os.remove(db_path)
            print("✅ 기존 데이터베이스 삭제 완료")
    except Exception as e:
        print(f"❌ 데이터베이스 삭제 실패: {e}")
        print("서버가 실행 중인 경우 먼저 종료해주세요.")
        return False
    
    print("✅ 데이터베이스 초기화 완료")
    print("이제 서버를 시작하면 새로운 데이터베이스가 생성됩니다.")
    print("기본 상태들이 올바른 status_type으로 생성될 것입니다:")
    print("  - Backlog: pending (진행 전)")
    print("  - Todo: pending (진행 전)")  
    print("  - In Progress: progress (진행 중)")
    print("  - Done: done (완료)")
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("          데이터베이스 초기화")
    print("=" * 50)
    print()
    
    confirm = input("기존 데이터베이스를 초기화하시겠습니까? (y/N): ")
    if confirm.lower() == 'y':
        reset_database()
    else:
        print("초기화를 취소했습니다.")