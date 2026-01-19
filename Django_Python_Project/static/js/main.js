// ElectroShop - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Quantity input controls
    const quantityInputs = document.querySelectorAll('input[type="number"][name="quantity"]');
    quantityInputs.forEach(function(input) {
        const min = parseInt(input.getAttribute('min')) || 1;
        const max = parseInt(input.getAttribute('max')) || 999;
        
        input.addEventListener('change', function() {
            let value = parseInt(this.value);
            if (isNaN(value) || value < min) {
                this.value = min;
            } else if (value > max) {
                this.value = max;
            }
        });
    });

    // Add to cart AJAX (optional enhancement)
    const addToCartForms = document.querySelectorAll('form[action*="cart/add"]');
    addToCartForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const button = form.querySelector('button[type="submit"]');
            if (button) {
                button.innerHTML = '<span class="loading"></span>';
                button.disabled = true;
            }
        });
    });

    // Image gallery (for product detail)
    const thumbnails = document.querySelectorAll('.product-thumbnail');
    const mainImage = document.querySelector('.product-main-image');
    
    if (thumbnails.length && mainImage) {
        thumbnails.forEach(function(thumb) {
            thumb.addEventListener('click', function() {
                mainImage.src = this.src;
                thumbnails.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }

    // Rating stars interaction
    const ratingSelect = document.querySelector('select[name="rating"]');
    const ratingStars = document.querySelector('.rating-stars-display');
    
    if (ratingSelect && ratingStars) {
        ratingSelect.addEventListener('change', function() {
            const value = parseInt(this.value);
            let stars = '';
            for (let i = 1; i <= 5; i++) {
                if (i <= value) {
                    stars += '<i class="bi bi-star-fill text-warning"></i>';
                } else {
                    stars += '<i class="bi bi-star text-warning"></i>';
                }
            }
            ratingStars.innerHTML = stars;
        });
    }

    // Confirm delete/cancel actions
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Bạn có chắc chắn?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Format currency inputs
    const currencyInputs = document.querySelectorAll('input[data-currency]');
    currencyInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            let value = this.value.replace(/[^\d]/g, '');
            if (value) {
                this.value = parseInt(value).toLocaleString('vi-VN');
            }
        });
        
        input.addEventListener('focus', function() {
            this.value = this.value.replace(/[^\d]/g, '');
        });
    });

    // Smooth scroll to top
    const scrollTopBtn = document.querySelector('.scroll-to-top');
    if (scrollTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                scrollTopBtn.classList.add('show');
            } else {
                scrollTopBtn.classList.remove('show');
            }
        });
        
        scrollTopBtn.addEventListener('click', function() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
});

// Helper function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}

// Helper function to show toast notification
function showToast(message, type = 'success') {
    const toastContainer = document.querySelector('.toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}


// ============================================
// Product Card Functions
// ============================================

// Toggle Wishlist
function toggleWishlist(productId) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                      document.querySelector('meta[name="csrf-token"]')?.content || '';
    
    fetch(`/wishlist/toggle/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.status === 401) {
            return response.json().then(data => {
                showNotification(data.message || 'Vui lòng đăng nhập để sử dụng tính năng yêu thích', 'warning');
                setTimeout(() => {
                    window.location.href = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
                }, 1500);
                throw new Error('require_login');
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Update product card wishlist buttons
            const buttons = document.querySelectorAll(`.wishlist-btn[data-product-id="${productId}"] i`);
            buttons.forEach(btn => {
                if (data.action === 'added') {
                    btn.classList.remove('bi-heart');
                    btn.classList.add('bi-heart-fill');
                } else {
                    btn.classList.remove('bi-heart-fill');
                    btn.classList.add('bi-heart');
                }
            });
            
            // Update product detail page wishlist button
            const pdWishlistBtn = document.getElementById('wishlistBtn');
            if (pdWishlistBtn) {
                const icon = pdWishlistBtn.querySelector('i');
                if (data.action === 'added') {
                    pdWishlistBtn.classList.add('active');
                    if (icon) {
                        icon.classList.remove('bi-heart');
                        icon.classList.add('bi-heart-fill');
                    }
                } else {
                    pdWishlistBtn.classList.remove('active');
                    if (icon) {
                        icon.classList.remove('bi-heart-fill');
                        icon.classList.add('bi-heart');
                    }
                }
            }
            
            showNotification(data.message, 'success');
        } else {
            showNotification(data.message || 'Có lỗi xảy ra', 'error');
        }
    })
    .catch(error => {
        if (error.message !== 'require_login') {
            console.error('Wishlist error:', error);
            showNotification('Có lỗi xảy ra', 'error');
        }
    });
}

// Quick View - navigate to product detail page
function quickView(productSlug) {
    window.location.href = `/product/${productSlug}/`;
}

// Add to Cart
function addToCart(productId, quantity = 1) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                      document.querySelector('meta[name="csrf-token"]')?.content || '';
    
    // Find and update button state
    const button = document.querySelector(`[onclick="addToCart(${productId})"]`);
    const originalContent = button?.innerHTML;
    
    if (button) {
        button.innerHTML = '<i class="bi bi-arrow-repeat spin"></i> <span>Đang thêm...</span>';
        button.disabled = true;
    }
    
    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ quantity: quantity })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Đã thêm vào giỏ hàng', 'success');
            
            // Update cart badge
            updateCartBadge(data.cart_count);
        } else {
            showNotification(data.message || 'Không thể thêm vào giỏ hàng', 'error');
        }
    })
    .catch(error => {
        console.error('Add to cart error:', error);
        showNotification('Có lỗi xảy ra', 'error');
    })
    .finally(() => {
        if (button) {
            button.innerHTML = originalContent;
            button.disabled = false;
        }
    });
}

// Update Cart Badge with animation
function updateCartBadge(count) {
    const badges = document.querySelectorAll('.cart-badge');
    const mobileBadges = document.querySelectorAll('.mobile-badge');
    
    // Update all cart badges
    [...badges, ...mobileBadges].forEach(badge => {
        if (count > 0) {
            const oldCount = parseInt(badge.textContent) || 0;
            badge.textContent = count > 99 ? '99+' : count;
            badge.style.display = 'flex';
            
            // Add bounce animation when count increases
            if (count > oldCount) {
                badge.classList.add('cart-badge--bounce');
                setTimeout(() => {
                    badge.classList.remove('cart-badge--bounce');
                }, 400);
            }
        } else {
            badge.style.display = 'none';
        }
    });
    
    // Also update cart icon with pulse effect
    const cartLinks = document.querySelectorAll('.nav-link--cart, .mobile-nav-link[href*="cart"]');
    cartLinks.forEach(link => {
        link.classList.add('cart-added-pulse');
        setTimeout(() => {
            link.classList.remove('cart-added-pulse');
        }, 600);
    });
}

// Show Notification (using SweetAlert2 if available, fallback to custom toast)
function showNotification(message, type = 'success') {
    if (typeof Swal !== 'undefined') {
        const iconMap = {
            'success': 'success',
            'error': 'error',
            'warning': 'warning',
            'info': 'info'
        };
        
        Swal.fire({
            toast: true,
            position: 'top-end',
            icon: iconMap[type] || 'info',
            title: message,
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true,
            customClass: {
                popup: 'notification-toast'
            }
        });
    } else {
        // Fallback to custom toast
        showCustomToast(message, type);
    }
}

// Custom Toast (fallback)
function showCustomToast(message, type = 'success') {
    let container = document.querySelector('.toast-container-custom');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container-custom';
        document.body.appendChild(container);
    }
    
    const toast = document.createElement('div');
    toast.className = `custom-toast custom-toast--${type}`;
    toast.innerHTML = `
        <div class="custom-toast__icon">
            <i class="bi bi-${type === 'success' ? 'check-circle-fill' : type === 'error' ? 'x-circle-fill' : type === 'warning' ? 'exclamation-triangle-fill' : 'info-circle-fill'}"></i>
        </div>
        <div class="custom-toast__message">${message}</div>
        <button class="custom-toast__close" onclick="this.parentElement.remove()">
            <i class="bi bi-x"></i>
        </button>
        <div class="custom-toast__progress"></div>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.classList.add('custom-toast--hiding');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Spin animation for loading
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .spin {
        animation: spin 1s linear infinite;
    }
    
    .toast-container-custom {
        position: fixed;
        top: 80px;
        right: 20px;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    
    .custom-toast {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 16px 20px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        min-width: 300px;
        max-width: 400px;
        position: relative;
        overflow: hidden;
        animation: slideIn 0.3s ease-out;
    }
    
    .custom-toast--hiding {
        animation: slideOut 0.3s ease-out forwards;
    }
    
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .custom-toast--success { border-left: 4px solid #22C55E; }
    .custom-toast--error { border-left: 4px solid #EF4444; }
    .custom-toast--warning { border-left: 4px solid #F59E0B; }
    .custom-toast--info { border-left: 4px solid #3B82F6; }
    
    .custom-toast__icon {
        font-size: 1.25rem;
    }
    
    .custom-toast--success .custom-toast__icon { color: #22C55E; }
    .custom-toast--error .custom-toast__icon { color: #EF4444; }
    .custom-toast--warning .custom-toast__icon { color: #F59E0B; }
    .custom-toast--info .custom-toast__icon { color: #3B82F6; }
    
    .custom-toast__message {
        flex: 1;
        font-size: 0.9375rem;
        color: #1E293B;
    }
    
    .custom-toast__close {
        background: none;
        border: none;
        color: #94A3B8;
        cursor: pointer;
        padding: 4px;
        font-size: 1.125rem;
    }
    
    .custom-toast__close:hover {
        color: #64748B;
    }
    
    .custom-toast__progress {
        position: absolute;
        bottom: 0;
        left: 0;
        height: 3px;
        background: currentColor;
        animation: progress 5s linear forwards;
        opacity: 0.3;
    }
    
    @keyframes progress {
        from { width: 100%; }
        to { width: 0%; }
    }
`;
document.head.appendChild(style);

// ============================================
// Dark Mode Toggle
// ============================================
function initDarkMode() {
    const toggle = document.getElementById('darkModeToggle');
    if (!toggle) return;
    
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
        document.documentElement.setAttribute('data-theme', 'dark');
        updateDarkModeIcon(true);
    }
    
    toggle.addEventListener('click', function() {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        
        if (isDark) {
            document.documentElement.removeAttribute('data-theme');
            localStorage.setItem('theme', 'light');
            updateDarkModeIcon(false);
        } else {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
            updateDarkModeIcon(true);
        }
    });
}

function updateDarkModeIcon(isDark) {
    const toggle = document.getElementById('darkModeToggle');
    if (!toggle) return;
    
    const icon = toggle.querySelector('i');
    if (icon) {
        if (isDark) {
            icon.classList.remove('bi-moon-stars');
            icon.classList.add('bi-sun-fill');
        } else {
            icon.classList.remove('bi-sun-fill');
            icon.classList.add('bi-moon-stars');
        }
    }
}

document.addEventListener('DOMContentLoaded', initDarkMode);
