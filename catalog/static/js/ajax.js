// Получение CSRF токена
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Переменные для модального окна
let currentDeleteProductId = null;
let currentDeleteRow = null;

// Показ уведомлений
function showNotification(message, type) {
    const toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) return;

    const icon = type === 'success' ? 'check-circle' :
                 type === 'danger' ? 'exclamation-circle' :
                 type === 'warning' ? 'exclamation-triangle' : 'info-circle';

    const bgClass = type === 'success' ? 'success' :
                    type === 'danger' ? 'danger' :
                    type === 'warning' ? 'warning' : 'primary';

    const toastHTML = `
        <div class="toast align-items-center text-white bg-${bgClass} border-0 mb-2"
             role="alert"
             aria-live="assertive"
             aria-atomic="true"
             data-bs-autohide="true"
             data-bs-delay="3000">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi bi-${icon} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-${type === 'warning' ? 'black' : 'white'} me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement);
    toast.show();

    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

// Загрузка данных через AJAX
function loadProductsData(params = {}) {
    const container = document.getElementById('products-table-container');
    if (!container) return;

    container.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">Загрузка...</p></div>';

    const urlParams = new URLSearchParams(params);
    const queryString = urlParams.toString();
    const url = queryString ? `/products/?${queryString}` : '/products/';

    fetch(url, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.text())
    .then(html => {
        container.innerHTML = html;
        // После загрузки новой таблицы - инициализируем обработчики
        initEventHandlers();
        initDeleteHandlers();
    })
    .catch(error => {
        container.innerHTML = '<div class="alert alert-danger">Ошибка загрузки данных</div>';
    });
}

// Получение текущих параметров
function getCurrentParams() {
    const params = new URLSearchParams();

    const searchInput = document.getElementById('search-input');
    if (searchInput && searchInput.value) params.set('search', searchInput.value);

    const manufacturer = document.getElementById('manufacturer-filter');
    if (manufacturer && manufacturer.value) params.set('manufacturer', manufacturer.value);

    const productType = document.getElementById('type-filter');
    if (productType && productType.value) params.set('product_type', productType.value);

    const sort = localStorage.getItem('current_sort');
    const order = localStorage.getItem('current_order');
    if (sort) {
        params.set('sort', sort);
        params.set('order', order);
    }

    return params;
}

// Инициализация обработчиков удаления
function initDeleteHandlers() {
    const deleteButtons = document.querySelectorAll('.delete-product-btn');

    deleteButtons.forEach(button => {
        // Убираем старый обработчик, чтобы не дублировать
        button.removeEventListener('click', button.deleteHandler);

        // Создаем новый обработчик
        button.deleteHandler = function(e) {
            e.preventDefault();
            e.stopPropagation();

            currentDeleteProductId = this.dataset.productId;
            currentDeleteRow = this.closest('tr');
            const productName = this.dataset.productName;
            const manufacturerName = this.dataset.manufacturerName;

            // Заполняем модальное окно
            const nameElement = document.getElementById('delete-product-name');
            const manufacturerElement = document.getElementById('delete-manufacturer-name');

            if (nameElement) nameElement.textContent = productName;
            if (manufacturerElement) manufacturerElement.textContent = manufacturerName;

            // Показываем модальное окно
            const modalElement = document.getElementById('deleteConfirmModal');
            if (modalElement) {
                const modal = new bootstrap.Modal(modalElement);
                modal.show();
            } else {
                // Если модального окна нет, используем confirm
                if (confirm(`Удалить товар "${productName}"?`)) {
                    deleteProduct(currentDeleteProductId, currentDeleteRow);
                }
            }
        };

        button.addEventListener('click', button.deleteHandler);
    });
}

// Функция удаления товара
function deleteProduct(productId, row) {
    fetch(`/product/delete/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (row) row.remove();
            showNotification(data.message, 'success');
            loadProductsData(getCurrentParams());
        } else {
            showNotification(data.message, 'danger');
        }
    })
    .catch(() => showNotification('Ошибка при удалении', 'danger'));
}

// Инициализация обработчиков сортировки и пагинации
function initEventHandlers() {
    // Сортировка
    document.querySelectorAll('.sort-link').forEach(link => {
        link.onclick = function(e) {
            e.preventDefault();
            const sort = this.dataset.sort;
            let order = 'asc';

            const currentSort = localStorage.getItem('current_sort');
            const currentOrder = localStorage.getItem('current_order');

            if (currentSort === sort && currentOrder === 'asc') {
                order = 'desc';
            }

            localStorage.setItem('current_sort', sort);
            localStorage.setItem('current_order', order);

            const params = getCurrentParams();
            loadProductsData(params);
        };
    });

    // Пагинация
    document.querySelectorAll('.pagination-link').forEach(link => {
        link.onclick = function(e) {
            e.preventDefault();
            const page = this.dataset.page;
            if (page) {
                const params = getCurrentParams();
                params.set('page', page);
                loadProductsData(params);
            }
        };
    });
}

// Обработчик кнопки подтверждения удаления
document.addEventListener('DOMContentLoaded', function() {
    const confirmDeleteBtn = document.getElementById('confirm-delete-btn');
    if (confirmDeleteBtn) {
        confirmDeleteBtn.onclick = function() {
            if (currentDeleteProductId) {
                deleteProduct(currentDeleteProductId, currentDeleteRow);
            }
            // Закрываем модальное окно
            const modalElement = document.getElementById('deleteConfirmModal');
            if (modalElement) {
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) modal.hide();
            }
            // Сбрасываем переменные
            currentDeleteProductId = null;
            currentDeleteRow = null;
        };
    }

    // Форма фильтров
    const filterForm = document.getElementById('filter-form');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            loadProductsData(getCurrentParams());
        });
    }

    // Форма поиска
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            loadProductsData(getCurrentParams());
        });
    }

    // Сброс фильтров
    const resetBtn = document.getElementById('reset-filters-btn');
    if (resetBtn) {
        resetBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const manufacturerFilter = document.getElementById('manufacturer-filter');
            const typeFilter = document.getElementById('type-filter');
            const searchInput = document.getElementById('search-input');
            const clearBtn = document.getElementById('clear-search-btn');

            if (manufacturerFilter) manufacturerFilter.value = '';
            if (typeFilter) typeFilter.value = '';
            if (searchInput) searchInput.value = '';
            if (clearBtn) clearBtn.style.display = 'none';

            localStorage.removeItem('current_sort');
            localStorage.removeItem('current_order');
            loadProductsData({});
        });
    }

    // Очистка поиска
    const clearSearchBtn = document.getElementById('clear-search-btn');
    if (clearSearchBtn) {
        clearSearchBtn.addEventListener('click', function() {
            const searchInput = document.getElementById('search-input');
            if (searchInput) {
                searchInput.value = '';
                this.style.display = 'none';
                loadProductsData(getCurrentParams());
            }
        });
    }

    // Показать/скрыть кнопку очистки
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const clearBtn = document.getElementById('clear-search-btn');
            if (clearBtn) {
                clearBtn.style.display = this.value ? 'block' : 'none';
            }
        });
    }

    // Автоматическое отображение toast-уведомлений
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toastElement => {
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    });

    // Закрытие модального окна по клику на фон
    const modal = document.getElementById('imageModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) bsModal.hide();
            }
        });
    }

    // Инициализация
    initEventHandlers();
    initDeleteHandlers();
});