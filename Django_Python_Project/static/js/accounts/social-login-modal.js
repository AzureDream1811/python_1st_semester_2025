/**
 * SocialLoginModal - Quản lý modal đăng nhập/đăng ký social (Google, Facebook)
 * Tích hợp với FormValidator và backend APIs
 */

class SocialLoginModal {
    constructor(provider) {
        this.provider = provider; // 'google' or 'facebook'
        this.validator = new FormValidator();
        this.isLoading = false;
        
        // Modal elements
        this.modal = null;
        this.modalBody = null;
        this.form = null;
        this.emailInput = null;
        this.registrationFields = null;
        this.submitButton = null;
        this.loadingSpinner = null;
        this.errorContainer = null;
        this.successContainer = null;
        
        // State
        this.currentStep = 'email'; // 'email' | 'registration' | 'login'
        this.userExists = false;
        
        this.init();
    }
    
    /**
     * Initialize modal elements and event listeners
     */
    init() {
        this.createModalHTML();
        this.bindEvents();
    }
    
    /**
     * Create modal HTML structure
     */
    createModalHTML() {
        const modalId = `${this.provider}Modal`;
        const existingModal = document.getElementById(modalId);
        
        if (existingModal) {
            this.modal = existingModal;
            this.updateModalContent();
        } else {
            // Create new modal if not exists
            const modalHTML = this.getModalHTML();
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            this.modal = document.getElementById(modalId);
        }
        
        // Get modal elements
        this.modalBody = this.modal.querySelector('.modal-body');
        this.form = this.modal.querySelector('#social-login-form');
        this.emailInput = this.modal.querySelector('#social-email');
        this.registrationFields = this.modal.querySelector('#registration-fields');
        this.submitButton = this.modal.querySelector('#social-submit-btn');
        this.loadingSpinner = this.modal.querySelector('#loading-spinner');
        this.errorContainer = this.modal.querySelector('#error-container');
        this.successContainer = this.modal.querySelector('#success-container');
    }
    
    /**
     * Update existing modal content
     */
    updateModalContent() {
        const modalBody = this.modal.querySelector('.modal-body');
        if (modalBody) {
            modalBody.innerHTML = this.getModalBodyHTML();
        }
    }

    
    /**
     * Get modal HTML template
     */
    getModalHTML() {
        const modalId = `${this.provider}Modal`;
        const providerName = this.provider === 'google' ? 'Google' : 'Facebook';
        const providerColor = this.provider === 'google' ? 'danger' : 'primary';
        const providerIcon = this.provider === 'google' ? 'fab fa-google' : 'fab fa-facebook-f';
        
        return `
        <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header border-0">
                        <h5 class="modal-title" id="${modalId}Label">
                            <i class="${providerIcon} me-2"></i>
                            Đăng nhập với ${providerName}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        ${this.getModalBodyHTML()}
                    </div>
                </div>
            </div>
        </div>
        `;
    }
    
    /**
     * Get modal body HTML
     */
    getModalBodyHTML() {
        const providerName = this.provider === 'google' ? 'Google' : 'Facebook';
        const providerColor = this.provider === 'google' ? 'danger' : 'primary';
        const providerIcon = this.provider === 'google' ? 'fab fa-google' : 'fab fa-facebook-f';
        
        return `
        <!-- Loading Spinner -->
        <div id="loading-spinner" class="text-center d-none">
            <div class="spinner-border text-${providerColor}" role="status">
                <span class="visually-hidden">Đang xử lý...</span>
            </div>
            <p class="mt-2 text-muted">Đang xử lý...</p>
        </div>
        
        <!-- Error Container -->
        <div id="error-container" class="alert alert-danger d-none" role="alert">
            <i class="fas fa-exclamation-triangle me-2"></i>
            <span id="error-message"></span>
            <button type="button" class="btn btn-sm btn-outline-danger ms-2 d-none" id="retry-btn">
                Thử lại
            </button>
        </div>
        
        <!-- Success Container -->
        <div id="success-container" class="alert alert-success d-none" role="alert">
            <i class="fas fa-check-circle me-2"></i>
            <span id="success-message"></span>
        </div>
        
        <!-- Main Form -->
        <form id="social-login-form">
            <!-- Email Field -->
            <div class="mb-3">
                <label for="social-email" class="form-label">Email</label>
                <input type="email" class="form-control" id="social-email" 
                       placeholder="Nhập email của bạn" required>
                <div class="invalid-feedback"></div>
            </div>
            
            <!-- Registration Fields (Hidden by default) -->
            <div id="registration-fields" class="d-none">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label for="social-first-name" class="form-label">Tên</label>
                        <input type="text" class="form-control" id="social-first-name" placeholder="Tên">
                        <div class="invalid-feedback"></div>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label for="social-last-name" class="form-label">Họ</label>
                        <input type="text" class="form-control" id="social-last-name" placeholder="Họ">
                        <div class="invalid-feedback"></div>
                    </div>
                </div>
                <div class="mb-3">
                    <label for="social-phone" class="form-label">Số điện thoại (tùy chọn)</label>
                    <input type="tel" class="form-control" id="social-phone" 
                           placeholder="0xxxxxxxxx hoặc +84xxxxxxxxx">
                    <div class="invalid-feedback"></div>
                    <div class="form-text">Định dạng: 0xxxxxxxxx hoặc +84xxxxxxxxx</div>
                </div>
            </div>
            
            <!-- Submit Button -->
            <div class="d-grid">
                <button type="submit" class="btn btn-${providerColor}" id="social-submit-btn">
                    <i class="${providerIcon} me-2"></i>
                    <span id="submit-text">Tiếp tục với ${providerName}</span>
                </button>
            </div>
        </form>
        
        <!-- Info Text -->
        <div class="text-center mt-3">
            <small class="text-muted">
                Bằng cách tiếp tục, bạn đồng ý với 
                <a href="#" class="text-decoration-none">Điều khoản sử dụng</a> và 
                <a href="#" class="text-decoration-none">Chính sách bảo mật</a>.
            </small>
        </div>
        `;
    }
    
    /**
     * Bind event listeners
     */
    bindEvents() {
        if (!this.modal) return;
        
        // Form submit
        const form = this.modal.querySelector('#social-login-form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleSubmit();
            });
        }
        
        // Email input blur - check email exists
        const emailInput = this.modal.querySelector('#social-email');
        if (emailInput) {
            emailInput.addEventListener('blur', () => {
                this.checkEmailExists();
            });
        }
        
        // Retry button
        const retryBtn = this.modal.querySelector('#retry-btn');
        if (retryBtn) {
            retryBtn.addEventListener('click', () => {
                this.hideError();
                this.handleSubmit();
            });
        }
        
        // Modal hidden - reset form
        this.modal.addEventListener('hidden.bs.modal', () => {
            this.resetForm();
        });
    }

    
    /**
     * Open modal
     */
    open() {
        if (!this.modal) return;
        
        const bsModal = new bootstrap.Modal(this.modal);
        bsModal.show();
        
        // Focus email input after modal opens
        this.modal.addEventListener('shown.bs.modal', () => {
            const emailInput = this.modal.querySelector('#social-email');
            if (emailInput) emailInput.focus();
        }, { once: true });
    }
    
    /**
     * Close modal
     */
    close() {
        if (!this.modal) return;
        
        const bsModal = bootstrap.Modal.getInstance(this.modal);
        if (bsModal) bsModal.hide();
    }
    
    /**
     * Show loading state
     */
    showLoading() {
        this.isLoading = true;
        
        const spinner = this.modal.querySelector('#loading-spinner');
        const form = this.modal.querySelector('#social-login-form');
        
        if (spinner) spinner.classList.remove('d-none');
        if (form) form.classList.add('d-none');
        
        this.hideError();
        this.hideSuccess();
    }
    
    /**
     * Hide loading state
     */
    hideLoading() {
        this.isLoading = false;
        
        const spinner = this.modal.querySelector('#loading-spinner');
        const form = this.modal.querySelector('#social-login-form');
        
        if (spinner) spinner.classList.add('d-none');
        if (form) form.classList.remove('d-none');
    }
    
    /**
     * Show error message
     * @param {string} message - Error message
     * @param {boolean} showRetry - Show retry button
     */
    showError(message, showRetry = false) {
        const container = this.modal.querySelector('#error-container');
        const messageEl = this.modal.querySelector('#error-message');
        const retryBtn = this.modal.querySelector('#retry-btn');
        
        if (container && messageEl) {
            messageEl.textContent = message;
            container.classList.remove('d-none');
            
            if (retryBtn) {
                retryBtn.classList.toggle('d-none', !showRetry);
            }
        }
    }
    
    /**
     * Hide error message
     */
    hideError() {
        const container = this.modal.querySelector('#error-container');
        if (container) container.classList.add('d-none');
    }
    
    /**
     * Show success message
     * @param {string} message - Success message
     */
    showSuccess(message) {
        const container = this.modal.querySelector('#success-container');
        const messageEl = this.modal.querySelector('#success-message');
        
        if (container && messageEl) {
            messageEl.textContent = message;
            container.classList.remove('d-none');
        }
    }
    
    /**
     * Hide success message
     */
    hideSuccess() {
        const container = this.modal.querySelector('#success-container');
        if (container) container.classList.add('d-none');
    }
    
    /**
     * Show registration fields
     */
    showRegistrationFields() {
        const fields = this.modal.querySelector('#registration-fields');
        const submitText = this.modal.querySelector('#submit-text');
        
        if (fields) fields.classList.remove('d-none');
        if (submitText) submitText.textContent = 'Đăng ký';
        
        this.currentStep = 'registration';
    }
    
    /**
     * Hide registration fields
     */
    hideRegistrationFields() {
        const fields = this.modal.querySelector('#registration-fields');
        const submitText = this.modal.querySelector('#submit-text');
        const providerName = this.provider === 'google' ? 'Google' : 'Facebook';
        
        if (fields) fields.classList.add('d-none');
        if (submitText) submitText.textContent = `Tiếp tục với ${providerName}`;
        
        this.currentStep = 'email';
    }
    
    /**
     * Reset form to initial state
     */
    resetForm() {
        const form = this.modal.querySelector('#social-login-form');
        if (form) form.reset();
        
        this.hideRegistrationFields();
        this.hideError();
        this.hideSuccess();
        this.hideLoading();
        
        // Clear validation errors
        this.validator.clearAllErrors([
            'social-email', 'social-first-name', 
            'social-last-name', 'social-phone'
        ]);
        
        this.currentStep = 'email';
        this.userExists = false;
    }

    
    /**
     * Check if email exists in database
     */
    async checkEmailExists() {
        const emailInput = this.modal.querySelector('#social-email');
        if (!emailInput) return;
        
        const email = emailInput.value.trim();
        
        // Validate email format first
        const validation = this.validator.validateEmail(email);
        if (!validation.valid) {
            this.validator.showFieldError('social-email', validation.error);
            return;
        }
        
        this.validator.clearFieldError('social-email');
        this.showLoading();
        
        try {
            const response = await fetch('/accounts/api/check-email/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email: email })
            });
            
            const data = await response.json();
            
            this.hideLoading();
            
            if (response.ok) {
                this.userExists = data.exists;
                
                if (data.exists) {
                    // User exists - show login flow
                    this.currentStep = 'login';
                    this.hideRegistrationFields();
                    
                    const submitText = this.modal.querySelector('#submit-text');
                    if (submitText) submitText.textContent = 'Đăng nhập';
                } else {
                    // New user - show registration fields
                    this.showRegistrationFields();
                }
            } else {
                this.showError(data.message || 'Có lỗi xảy ra khi kiểm tra email', true);
            }
        } catch (error) {
            this.hideLoading();
            this.showError('Không thể kết nối đến server. Vui lòng thử lại.', true);
        }
    }
    
    /**
     * Handle form submission
     */
    async handleSubmit() {
        if (this.isLoading) return;
        
        const email = this.modal.querySelector('#social-email')?.value.trim();
        
        // Validate email
        const emailValidation = this.validator.validateEmail(email);
        if (!emailValidation.valid) {
            this.validator.showFieldError('social-email', emailValidation.error);
            return;
        }
        
        // If we haven't checked email yet, check it first
        if (this.currentStep === 'email') {
            await this.checkEmailExists();
            return;
        }
        
        // Handle based on current step
        if (this.userExists || this.currentStep === 'login') {
            await this.handleLogin(email);
        } else {
            await this.handleRegistration(email);
        }
    }
    
    /**
     * Handle login for existing user
     * @param {string} email - User email
     */
    async handleLogin(email) {
        this.showLoading();
        
        try {
            const response = await fetch('/accounts/api/social-login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    provider: this.provider
                })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                this.hideLoading();
                this.showSuccess('Đăng nhập thành công! Đang chuyển hướng...');
                
                // Redirect after short delay
                setTimeout(() => {
                    window.location.href = data.redirect_url || '/';
                }, 1000);
            } else {
                this.hideLoading();
                this.showError(data.message || 'Đăng nhập thất bại', true);
            }
        } catch (error) {
            this.hideLoading();
            this.showError('Không thể kết nối đến server. Vui lòng thử lại.', true);
        }
    }
    
    /**
     * Handle registration for new user
     * @param {string} email - User email
     */
    async handleRegistration(email) {
        const firstName = this.modal.querySelector('#social-first-name')?.value.trim();
        const lastName = this.modal.querySelector('#social-last-name')?.value.trim();
        const phone = this.modal.querySelector('#social-phone')?.value.trim();
        
        // Validate registration data
        const validation = this.validator.validateSocialRegistration({
            email: email,
            first_name: firstName,
            last_name: lastName,
            phone: phone,
            provider: this.provider
        });
        
        if (!validation.valid) {
            // Show field errors
            if (validation.errors.email) {
                this.validator.showFieldError('social-email', validation.errors.email);
            }
            if (validation.errors.first_name) {
                this.validator.showFieldError('social-first-name', validation.errors.first_name);
            }
            if (validation.errors.last_name) {
                this.validator.showFieldError('social-last-name', validation.errors.last_name);
            }
            if (validation.errors.phone) {
                this.validator.showFieldError('social-phone', validation.errors.phone);
            }
            return;
        }
        
        // Clear previous errors
        this.validator.clearAllErrors([
            'social-email', 'social-first-name', 
            'social-last-name', 'social-phone'
        ]);
        
        this.showLoading();
        
        try {
            const response = await fetch('/accounts/api/social-register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    first_name: firstName,
                    last_name: lastName,
                    phone: phone,
                    provider: this.provider
                })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                this.hideLoading();
                this.showSuccess('Đăng ký thành công! Đang chuyển hướng...');
                
                // Redirect after short delay
                setTimeout(() => {
                    window.location.href = data.redirect_url || '/';
                }, 1000);
            } else {
                this.hideLoading();
                
                // Show specific field errors if available
                if (data.errors) {
                    this.validator.showFieldErrors(data.errors);
                }
                
                this.showError(data.message || 'Đăng ký thất bại', true);
            }
        } catch (error) {
            this.hideLoading();
            this.showError('Không thể kết nối đến server. Vui lòng thử lại.', true);
        }
    }
}

// Global instances for Google and Facebook modals
let googleLoginModal = null;
let facebookLoginModal = null;

/**
 * Open Google login modal
 */
function openGoogleModal() {
    if (!googleLoginModal) {
        googleLoginModal = new SocialLoginModal('google');
    }
    googleLoginModal.open();
}

/**
 * Open Facebook login modal
 */
function openFacebookModal() {
    if (!facebookLoginModal) {
        facebookLoginModal = new SocialLoginModal('facebook');
    }
    facebookLoginModal.open();
}

/**
 * Close Google login modal
 */
function closeGoogleModal() {
    if (googleLoginModal) {
        googleLoginModal.close();
    }
}

/**
 * Close Facebook login modal
 */
function closeFacebookModal() {
    if (facebookLoginModal) {
        facebookLoginModal.close();
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SocialLoginModal, openGoogleModal, openFacebookModal };
} else {
    window.SocialLoginModal = SocialLoginModal;
    window.openGoogleModal = openGoogleModal;
    window.openFacebookModal = openFacebookModal;
    window.closeGoogleModal = closeGoogleModal;
    window.closeFacebookModal = closeFacebookModal;
}
