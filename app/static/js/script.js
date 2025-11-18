document.addEventListener('DOMContentLoaded', function() {
    // Переключение статуса задачи
    const taskToggles = document.querySelectorAll('.task-toggle');
    taskToggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            const taskId = this.dataset.taskId;
            const taskItem = this.closest('.list-group-item');
            const label = this.nextElementSibling;
            
            console.log('Toggling task:', taskId);
            
            fetch(`/tasks/${taskId}/toggle`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Toggle response:', data);
                if (data.completed) {
                    taskItem.classList.add('task-completed');
                    label.classList.add('text-decoration-line-through');
                } else {
                    taskItem.classList.remove('task-completed');
                    label.classList.remove('text-decoration-line-through');
                }
                
                showNotification(data.completed ? 'Задача выполнена!' : 'Задача активирована!', 'success');
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Ошибка при обновлении задачи', 'danger');
                this.checked = !this.checked;
            });
        });
    });

    // Подтверждение удаления
    const deleteForms = document.querySelectorAll('form[action*="delete"]');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Вы уверены, что хотите удалить эту задачу?')) {
                e.preventDefault();
            }
        });
    });

    // Автосабмит форм фильтрации
    const filterSelects = document.querySelectorAll('select[onchange]');
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            this.form.submit();
        });
    });

    // Подсветка приоритетов
    const taskItems = document.querySelectorAll('.list-group-item');
    taskItems.forEach(item => {
        const priorityBadge = item.querySelector('.badge.bg-danger, .badge.bg-warning, .badge.bg-success');
        if (priorityBadge) {
            if (priorityBadge.classList.contains('bg-danger')) {
                item.classList.add('priority-high');
            } else if (priorityBadge.classList.contains('bg-warning')) {
                item.classList.add('priority-medium');
            } else if (priorityBadge.classList.contains('bg-success')) {
                item.classList.add('priority-low');
            }
        }
    });
});

function getCSRFToken() {
    // Ищем CSRF токен в meta тегах
    const metaToken = document.querySelector('meta[name="csrf-token"]');
    if (metaToken) {
        return metaToken.getAttribute('content');
    }
    
    // Ищем в input fields
    const inputToken = document.querySelector('input[name="csrf_token"]');
    if (inputToken) {
        return inputToken.value;
    }
    
    console.error('CSRF token not found');
    return '';
}

function showNotification(message, type = 'info') {
    // Создаем элемент уведомления
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Автоматически скрываем через 3 секунды
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}