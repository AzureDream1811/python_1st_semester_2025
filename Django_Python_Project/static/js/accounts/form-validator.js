/**
 * Form Validator - ElectroShop (Real-time Edition)
 * Xử lý validation form đăng nhập/đăng ký theo thời gian thực
 */

(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        initFormValidation();
    });

    function initFormValidation() {
        const forms = document.querySelectorAll('form[novalidate], form.needs-validation');

        forms.forEach(function(form) {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();

                    // Validate tất cả fields khi submit
                    const inputs = form.querySelectorAll('input, textarea, select');
                    inputs.forEach(validateInput);
                }

                form.classList.add('was-validated');

                // Add loading state
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn && form.checkValidity()) {
                    submitBtn.classList.add('btn-loading');
                    submitBtn.disabled = true;
                }
            }, false);

            // Real-time validation cho tất cả inputs
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(function(input) {
                // Validate ngay khi đang gõ (realtime)
                input.addEventListener('input', function() {
                    // Đợi một chút để người dùng gõ xong từ
                    clearTimeout(input.validationTimeout);
                    input.validationTimeout = setTimeout(function() {
                        validateInput(input);
                    }, 300); // Delay 300ms
                });

                // Validate khi rời khỏi field
                input.addEventListener('blur', function() {
                    clearTimeout(input.validationTimeout);
                    validateInput(input);
                });

                // Validate khi focus vào field có lỗi
                input.addEventListener('focus', function() {
                    if (input.classList.contains('is-invalid')) {
                        // Giữ lỗi hiển thị nhưng cho phép sửa
                        input.classList.add('is-editing');
                    }
                });
            });
        });

        // Initialize các validator đặc biệt
        initPasswordStrength();
        initPasswordMatch();
        initEmailValidation();
        initPhoneValidation();
    }

    function validateInput(input) {
        // Bỏ qua nếu field rỗng và không required
        if (!input.required && !input.value.trim()) {
            input.classList.remove('is-invalid', 'is-valid', 'is-editing');
            hideError(input);
            return true;
        }

        let isValid = input.checkValidity();
        const value = input.value.trim();

        // Custom validation rules
        if (input.type === 'email' && value) {
            isValid = isValidEmail(value);
            if (!isValid) {
                input.setCustomValidity('Email không hợp lệ');
            } else {
                input.setCustomValidity('');
            }
        }

        if (input.type === 'tel' || input.name === 'phone') {
            if (value && !isValidPhone(value)) {
                isValid = false;
                input.setCustomValidity('Số điện thoại không hợp lệ');
            } else {
                input.setCustomValidity('');
            }
        }

        // Username validation
        if (input.name === 'username' && value) {
            if (value.length < 3) {
                isValid = false;
                input.setCustomValidity('Tên đăng nhập phải có ít nhất 3 ký tự');
            } else if (!/^[a-zA-Z0-9_@.+-]+$/.test(value)) {
                isValid = false;
                input.setCustomValidity('Tên đăng nhập chỉ được chứa chữ, số và các ký tự @.+-_');
            } else {
                input.setCustomValidity('');
            }
        }

        // Password strength validation
        if ((input.name === 'password1' || input.name === 'password') && value) {
            const strength = calculatePasswordStrength(value);
            if (strength < 2) {
                isValid = false;
                input.setCustomValidity('Mật khẩu quá yếu. Cần ít nhất 8 ký tự với chữ và số');
            } else {
                input.setCustomValidity('');
            }
        }

        // Update UI
        input.classList.remove('is-editing');
        if (isValid) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            hideError(input);
            showSuccess(input);
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
            showError(input, input.validationMessage);
            hideSuccess(input);
        }

        return isValid;
    }

    function showError(input, message) {
        const errorId = input.id + '-error';
        let errorElement = document.getElementById(errorId);

        if (!errorElement) {
            // Tạo error element mới nếu chưa có
            errorElement = document.createElement('span');
            errorElement.id = errorId;
            errorElement.className = 'form-field__error';
            errorElement.setAttribute('role', 'alert');
            errorElement.innerHTML = '<i aria-hidden="true" class="bi bi-exclamation-circle"></i> <span class="error-text"></span>';

            const wrapper = input.closest('.auth-input-group');
            if (wrapper) {
                wrapper.appendChild(errorElement);
            }
        }

        const errorText = errorElement.querySelector('.error-text');
        if (errorText) {
            errorText.textContent = message || input.validationMessage;
        }

        errorElement.style.display = 'flex';
        input.setAttribute('aria-describedby', errorId);
        input.setAttribute('aria-invalid', 'true');
    }

    function hideError(input) {
        const errorId = input.id + '-error';
        const errorElement = document.getElementById(errorId);

        if (errorElement) {
            errorElement.style.display = 'none';
        }

        input.removeAttribute('aria-invalid');
    }

    function showSuccess(input) {
        // Chỉ show success icon cho các field đã điền và valid
        if (input.value.trim() && input.checkValidity()) {
            const successId = input.id + '-success';
            let successElement = document.getElementById(successId);

            if (!successElement) {
                successElement = document.createElement('span');
                successElement.id = successId;
                successElement.className = 'form-field__success';
                successElement.innerHTML = '<i aria-hidden="true" class="bi bi-check-circle"></i>';

                const wrapper = input.closest('.auth-input-wrapper');
                if (wrapper) {
                    // Add success icon bên trong input wrapper
                    const existingSuccess = wrapper.querySelector('.input-success-icon');
                    if (!existingSuccess) {
                        const icon = document.createElement('i');
                        icon.className = 'bi bi-check-circle input-success-icon';
                        wrapper.appendChild(icon);
                    }
                }
            }
        }
    }

    function hideSuccess(input) {
        const wrapper = input.closest('.auth-input-wrapper');
        if (wrapper) {
            const icon = wrapper.querySelector('.input-success-icon');
            if (icon) {
                icon.remove();
            }
        }
    }

    function initPasswordStrength() {
        const passwordInputs = document.querySelectorAll('input[type="password"][data-strength]');

        passwordInputs.forEach(function(input) {
            const strengthMeterId = input.dataset.strength;
            const strengthMeter = document.getElementById(strengthMeterId);

            if (strengthMeter) {
                let strengthBar = strengthMeter.querySelector('.password-strength__bar');
                if (!strengthBar) {
                    strengthBar = document.createElement('div');
                    strengthBar.className = 'password-strength__bar';
                    strengthMeter.appendChild(strengthBar);
                }

                let strengthText = strengthMeter.nextElementSibling;
                if (!strengthText || !strengthText.classList.contains('password-strength__text')) {
                    strengthText = document.createElement('div');
                    strengthText.className = 'password-strength__text';
                    strengthMeter.after(strengthText);
                }

                input.addEventListener('input', function() {
                    const strength = calculatePasswordStrength(input.value);
                    updateStrengthMeter(strengthBar, strengthText, strength, input.value.length);
                });
            }
        });
    }

    function calculatePasswordStrength(password) {
        if (!password) return 0;

        let strength = 0;

        if (password.length >= 8) strength++;
        if (password.length >= 12) strength++;
        if (/[a-z]/.test(password)) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^a-zA-Z0-9]/.test(password)) strength++;

        return Math.min(strength, 5);
    }

    function updateStrengthMeter(bar, textElement, strength, passwordLength) {
        const levels = [
            { name: 'Rất yếu', class: 'very-weak', hint: 'Thêm chữ hoa, số và ký tự đặc biệt' },
            { name: 'Yếu', class: 'weak', hint: 'Cần thêm độ dài và ký tự đặc biệt' },
            { name: 'Trung bình', class: 'fair', hint: 'Khá tốt, thêm ký tự đặc biệt' },
            { name: 'Tốt', class: 'good', hint: 'Mật khẩu tốt' },
            { name: 'Mạnh', class: 'strong', hint: 'Mật khẩu mạnh' },
            { name: 'Rất mạnh', class: 'very-strong', hint: 'Mật khẩu rất mạnh' }
        ];

        const colors = ['#dc3545', '#fd7e14', '#ffc107', '#20c997', '#198754', '#22c55e'];

        const percentage = passwordLength ? (strength / 5) * 100 : 0;
        bar.style.width = percentage + '%';
        bar.style.backgroundColor = colors[strength] || colors[0];
        bar.setAttribute('data-level', levels[strength]?.class || levels[0].class);

        if (textElement && passwordLength) {
            const level = levels[strength] || levels[0];
            textElement.textContent = 'Độ mạnh: ' + level.name + ' - ' + level.hint;
            textElement.style.color = colors[strength] || colors[0];
            textElement.style.display = 'block';
        } else if (textElement) {
            textElement.style.display = 'none';
        }
    }

    function initPasswordMatch() {
        const confirmInputs = document.querySelectorAll('input[data-match]');

        confirmInputs.forEach(function(confirmInput) {
            const originalInputId = confirmInput.dataset.match;
            const originalInput = document.getElementById(originalInputId);

            if (originalInput) {
                // Real-time matching khi gõ
                confirmInput.addEventListener('input', function() {
                    clearTimeout(confirmInput.matchTimeout);
                    confirmInput.matchTimeout = setTimeout(function() {
                        checkPasswordMatch(originalInput, confirmInput);
                    }, 300);
                });

                originalInput.addEventListener('input', function() {
                    if (confirmInput.value) {
                        clearTimeout(confirmInput.matchTimeout);
                        confirmInput.matchTimeout = setTimeout(function() {
                            checkPasswordMatch(originalInput, confirmInput);
                        }, 300);
                    }
                });
            }
        });
    }

    function checkPasswordMatch(originalInput, confirmInput) {
        if (!confirmInput.value) {
            confirmInput.setCustomValidity('');
            confirmInput.classList.remove('is-invalid', 'is-valid');
            hideError(confirmInput);
            return;
        }

        if (confirmInput.value !== originalInput.value) {
            confirmInput.setCustomValidity('Mật khẩu không khớp');
            confirmInput.classList.add('is-invalid');
            confirmInput.classList.remove('is-valid');
            showError(confirmInput, 'Mật khẩu không khớp');
        } else {
            confirmInput.setCustomValidity('');
            confirmInput.classList.remove('is-invalid');
            confirmInput.classList.add('is-valid');
            hideError(confirmInput);
            showSuccess(confirmInput);
        }
    }

    function initEmailValidation() {
        const emailInputs = document.querySelectorAll('input[type="email"]');

        emailInputs.forEach(function(input) {
            input.addEventListener('input', function() {
                clearTimeout(input.emailTimeout);
                input.emailTimeout = setTimeout(function() {
                    const email = input.value.trim();
                    if (email && !isValidEmail(email)) {
                        input.setCustomValidity('Email không hợp lệ (ví dụ: user@example.com)');
                        showError(input, 'Email không hợp lệ (ví dụ: user@example.com)');
                    } else {
                        input.setCustomValidity('');
                    }
                    validateInput(input);
                }, 500);
            });
        });
    }

    function initPhoneValidation() {
        const phoneInputs = document.querySelectorAll('input[type="tel"], input[name="phone"]');

        phoneInputs.forEach(function(input) {
            input.addEventListener('input', function() {
                // Auto-format phone number
                let value = input.value.replace(/\D/g, ''); // Remove non-digits

                // Format: 0123 456 789
                if (value.length > 4 && value.length <= 7) {
                    value = value.slice(0, 4) + ' ' + value.slice(4);
                } else if (value.length > 7) {
                    value = value.slice(0, 4) + ' ' + value.slice(4, 7) + ' ' + value.slice(7, 10);
                }

                input.value = value;

                clearTimeout(input.phoneTimeout);
                input.phoneTimeout = setTimeout(function() {
                    validateInput(input);
                }, 300);
            });
        });
    }

    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email.toLowerCase());
    }

    function isValidPhone(phone) {
        const cleaned = phone.replace(/\D/g, '');
        // Vietnamese phone: 10 digits, starts with 0
        return /^0\d{9}$/.test(cleaned);
    }

})();

