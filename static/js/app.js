// 전역 유틸리티 함수들

// 날짜 포맷팅
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// 시간 포맷팅
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 상대 시간 계산
function getRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = now - date;
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
        const diffHours = Math.floor(diffTime / (1000 * 60 * 60));
        if (diffHours === 0) {
            const diffMinutes = Math.floor(diffTime / (1000 * 60));
            return diffMinutes <= 1 ? '방금 전' : `${diffMinutes}분 전`;
        }
        return `${diffHours}시간 전`;
    } else if (diffDays === 1) {
        return '어제';
    } else if (diffDays < 7) {
        return `${diffDays}일 전`;
    } else {
        return formatDate(dateString);
    }
}

// 알림 표시
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle'} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // 자동 제거
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// 로딩 상태 표시
function showLoading(container) {
    const loading = document.createElement('div');
    loading.className = 'loading';
    loading.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    
    container.innerHTML = '';
    container.appendChild(loading);
}

// 빈 상태 표시
function showEmptyState(container, message, icon = 'fa-inbox') {
    const emptyState = document.createElement('div');
    emptyState.className = 'empty-state';
    emptyState.innerHTML = `
        <i class="fas ${icon}"></i>
        <p>${message}</p>
    `;
    
    container.innerHTML = '';
    container.appendChild(emptyState);
}

// 에러 처리
function handleError(error, context = '') {
    console.error(`${context} 에러:`, error);
    showNotification(`오류가 발생했습니다: ${error.message}`, 'danger');
}

// API 호출 래퍼
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        handleError(error, `API 호출 (${url})`);
        throw error;
    }
}

// 로컬 스토리지 유틸리티
const storage = {
    set: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('로컬 스토리지 저장 실패:', error);
        }
    },
    
    get: (key, defaultValue = null) => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('로컬 스토리지 조회 실패:', error);
            return defaultValue;
        }
    },
    
    remove: (key) => {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('로컬 스토리지 삭제 실패:', error);
        }
    }
};

// 설정 관리
const settings = {
    async get(key) {
        try {
            const response = await fetch(`/api/settings/${key}`);
            if (response.ok) {
                const setting = await response.json();
                return setting.setting_value;
            }
            return null;
        } catch (error) {
            console.error('설정 조회 실패:', error);
            return null;
        }
    },
    
    async set(key, value) {
        try {
            await fetch(`/api/settings/${key}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ setting_value: value })
            });
        } catch (error) {
            console.error('설정 저장 실패:', error);
        }
    },
    
    async getMultiple(keys) {
        try {
            const response = await fetch('/api/settings');
            if (response.ok) {
                const allSettings = await response.json();
                const result = {};
                keys.forEach(key => {
                    const setting = allSettings.find(s => s.setting_key === key);
                    result[key] = setting ? setting.setting_value : null;
                });
                return result;
            }
            return {};
        } catch (error) {
            console.error('설정 조회 실패:', error);
            return {};
        }
    },
    
    async setMultiple(settingsObj) {
        try {
            await fetch('/api/settings', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settingsObj)
            });
        } catch (error) {
            console.error('설정 저장 실패:', error);
        }
    }
};

// 검색 기능
function createSearchBox(containerId, onSearch) {
    const container = document.getElementById(containerId);
    const searchBox = document.createElement('div');
    searchBox.className = 'search-box mb-3';
    searchBox.innerHTML = `
        <i class="fas fa-search search-icon"></i>
        <input type="text" class="form-control" placeholder="검색..." id="searchInput">
    `;
    
    container.appendChild(searchBox);
    
    const searchInput = document.getElementById('searchInput');
    let searchTimeout;
    
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            onSearch(this.value);
        }, 300);
    });
    
    return searchInput;
}

// 필터링 기능
function filterTasks(tasks, searchQuery) {
    if (!searchQuery) return tasks;
    
    const query = searchQuery.toLowerCase();
    return tasks.filter(task => 
        task.title.toLowerCase().includes(query) ||
        (task.description && task.description.toLowerCase().includes(query))
    );
}

// 키보드 단축키
document.addEventListener('keydown', function(event) {
    // Ctrl+N: 새 할일 추가
    if (event.ctrlKey && event.key === 'n') {
        event.preventDefault();
        const taskModal = document.getElementById('taskModal');
        if (taskModal) {
            new bootstrap.Modal(taskModal).show();
        }
    }
    
    // Esc: 모달 닫기
    if (event.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            bootstrap.Modal.getInstance(modal)?.hide();
        });
    }
});

// 페이지 이동 유틸리티
function navigateTo(path) {
    window.location.href = path;
}

// 확인 대화상자
function confirmAction(message, onConfirm, onCancel = null) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">확인</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p>${message}</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">취소</button>
                    <button type="button" class="btn btn-primary" id="confirmBtn">확인</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    const bootstrapModal = new bootstrap.Modal(modal);
    
    document.getElementById('confirmBtn').addEventListener('click', function() {
        bootstrapModal.hide();
        if (onConfirm) onConfirm();
    });
    
    modal.addEventListener('hidden.bs.modal', function() {
        document.body.removeChild(modal);
        if (onCancel) onCancel();
    });
    
    bootstrapModal.show();
}

// 데이터 검증
function validateTask(taskData) {
    const errors = [];
    
    if (!taskData.title || taskData.title.trim() === '') {
        errors.push('제목을 입력해주세요.');
    }
    
    if (taskData.title && taskData.title.length > 200) {
        errors.push('제목은 200자를 초과할 수 없습니다.');
    }
    
    if (taskData.description && taskData.description.length > 1000) {
        errors.push('설명은 1000자를 초과할 수 없습니다.');
    }
    
    if (!taskData.status_id) {
        errors.push('상태를 선택해주세요.');
    }
    
    if (taskData.priority && (taskData.priority < 1 || taskData.priority > 4)) {
        errors.push('우선순위가 올바르지 않습니다.');
    }
    
    return errors;
}

// 디바운스 유틸리티
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 스로틀 유틸리티
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// 초기화 함수
function initializeApp() {
    // 툴팁 초기화
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // 현재 페이지 네비게이션 활성화
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    console.log('앱 초기화 완료');
}

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', initializeApp);