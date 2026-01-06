/**
 * Social Login Modal - ElectroShop
 * Placeholder for social login functionality
 */

(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        initSocialLogin();
    });

    function initSocialLogin() {
        // Social login buttons
        const socialBtns = document.querySelectorAll('.social-login-btn');

        socialBtns.forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                const provider = btn.dataset.provider;

                if (provider) {
                    handleSocialLogin(provider);
                }
            });
        });
    }

    function handleSocialLogin(provider) {
        // Placeholder - implement actual social login
        console.log('Social login with:', provider);

        // Show loading state
        const btn = document.querySelector(`[data-provider="${provider}"]`);
        if (btn) {
            btn.classList.add('loading');
            btn.disabled = true;
        }

        // For now, show a message that feature is coming soon
        showMessage('Tính năng đăng nhập bằng ' + provider + ' sẽ sớm được hỗ trợ!', 'info');

        // Reset button state
        setTimeout(function() {
            if (btn) {
                btn.classList.remove('loading');
                btn.disabled = false;
            }
        }, 1000);
    }

    function showMessage(message, type) {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = 'toast-notification toast-' + type;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="bi bi-info-circle me-2"></i>
                <span>${message}</span>
            </div>
        `;

        document.body.appendChild(toast);

        // Animate in
        setTimeout(function() {
            toast.classList.add('show');
        }, 100);

        // Remove after delay
        setTimeout(function() {
            toast.classList.remove('show');
            setTimeout(function() {
                toast.remove();
            }, 300);
        }, 3000);
    }

})();

