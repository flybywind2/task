import os
import json
from datetime import datetime, date
from typing import Dict, Any, Optional
import logging

# 로그 디렉토리 생성
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

class DailyChangeLogger:
    """일일 변경점을 로그 파일로 기록하는 클래스"""
    
    def __init__(self):
        self.log_dir = LOG_DIR
        
    def _get_log_filename(self, target_date: date = None) -> str:
        """로그 파일명 생성"""
        if target_date is None:
            target_date = date.today()
        return os.path.join(self.log_dir, f"{target_date.strftime('%Y-%m-%d')}.log")
    
    def _format_log_entry(self, action_type: str, task_data: Dict[str, Any], 
                         old_data: Optional[Dict[str, Any]] = None) -> str:
        """로그 엔트리 포맷팅"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_entry = {
            "timestamp": timestamp,
            "action": action_type,
            "task": {
                "id": task_data.get("id"),
                "title": task_data.get("title"),
                "status": task_data.get("status"),
                "category": task_data.get("category"),
                "priority": task_data.get("priority"),
                "is_pinned": task_data.get("is_pinned", False)
            }
        }
        
        # 변경 전 데이터가 있는 경우 추가
        if old_data:
            log_entry["changes"] = self._get_changes(old_data, task_data)
        
        return json.dumps(log_entry, ensure_ascii=False, indent=2)
    
    def _get_changes(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
        """변경사항 추출"""
        changes = {}
        
        # 추적할 필드들
        fields_to_track = ["title", "description", "priority", "status", "category", "is_pinned"]
        
        for field in fields_to_track:
            old_value = old_data.get(field)
            new_value = new_data.get(field)
            
            if old_value != new_value:
                changes[field] = {
                    "from": old_value,
                    "to": new_value
                }
        
        return changes
    
    def log_task_created(self, task_data: Dict[str, Any]):
        """할일 생성 로그"""
        self._write_log("TASK_CREATED", task_data)
    
    def log_task_updated(self, task_data: Dict[str, Any], old_data: Dict[str, Any]):
        """할일 수정 로그"""
        self._write_log("TASK_UPDATED", task_data, old_data)
    
    def log_task_deleted(self, task_data: Dict[str, Any]):
        """할일 삭제 로그"""
        self._write_log("TASK_DELETED", task_data)
    
    def log_task_completed(self, task_data: Dict[str, Any]):
        """할일 완료 로그"""
        self._write_log("TASK_COMPLETED", task_data)
    
    def log_task_status_changed(self, task_data: Dict[str, Any], old_status: str, new_status: str):
        """할일 상태 변경 로그"""
        old_data = task_data.copy()
        old_data["status"] = old_status
        task_data["status"] = new_status
        self._write_log("TASK_STATUS_CHANGED", task_data, old_data)
    
    def log_task_pinned(self, task_data: Dict[str, Any], is_pinned: bool):
        """할일 핀고정 로그"""
        old_data = task_data.copy()
        old_data["is_pinned"] = not is_pinned
        task_data["is_pinned"] = is_pinned
        action = "TASK_PINNED" if is_pinned else "TASK_UNPINNED"
        self._write_log(action, task_data, old_data)
    
    def _write_log(self, action_type: str, task_data: Dict[str, Any], 
                   old_data: Optional[Dict[str, Any]] = None):
        """로그 파일에 기록"""
        try:
            log_filename = self._get_log_filename()
            log_entry = self._format_log_entry(action_type, task_data, old_data)
            
            # 로그 파일에 추가
            with open(log_filename, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n' + '-' * 50 + '\n')
            
            print(f"[LOG] {action_type}: {task_data.get('title', 'Unknown')} -> {log_filename}")
            
        except Exception as e:
            print(f"로그 기록 실패: {e}")
    
    def get_daily_summary(self, target_date: date = None) -> Dict[str, Any]:
        """일일 요약 생성"""
        if target_date is None:
            target_date = date.today()
        
        log_filename = self._get_log_filename(target_date)
        
        if not os.path.exists(log_filename):
            return {
                "date": target_date.strftime('%Y-%m-%d'),
                "total_changes": 0,
                "summary": "변경사항 없음"
            }
        
        try:
            with open(log_filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 로그 엔트리 개수 계산
            entries = content.split('-' * 50)
            total_changes = len([e for e in entries if e.strip()])
            
            return {
                "date": target_date.strftime('%Y-%m-%d'),
                "total_changes": total_changes,
                "file_size": os.path.getsize(log_filename),
                "summary": f"{total_changes}개의 변경사항이 기록됨"
            }
            
        except Exception as e:
            return {
                "date": target_date.strftime('%Y-%m-%d'),
                "total_changes": 0,
                "error": str(e)
            }
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """오래된 로그 파일 정리"""
        try:
            current_date = date.today()
            
            for filename in os.listdir(self.log_dir):
                if filename.endswith('.log'):
                    file_path = os.path.join(self.log_dir, filename)
                    
                    # 파일 생성일 확인
                    file_date = datetime.fromtimestamp(os.path.getctime(file_path)).date()
                    days_old = (current_date - file_date).days
                    
                    if days_old > days_to_keep:
                        os.remove(file_path)
                        print(f"[CLEANUP] 오래된 로그 파일 삭제: {filename}")
                        
        except Exception as e:
            print(f"로그 정리 실패: {e}")

# 싱글톤 인스턴스
daily_logger = DailyChangeLogger()