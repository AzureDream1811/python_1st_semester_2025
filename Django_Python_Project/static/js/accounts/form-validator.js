/**
 * Form Validator - ElectroShop
 * Xử lý validation form đăng nhập/đăng ký
 */

(function() {
    'use strict';

    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        initFormValidation();
    });

    function initFormValidation() {
        // Get all forms with validation
        const forms = document.querySelectorAll('form[novalidate], form.needs-validation');

        forms.forEach(function(form) {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }

                form.classList.add('was-validated');
            }, false);

            // Real-time validation
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(function(input) {
                input.addEventListener('blur', function() {
                    validateInput(input);
                });

                input.addEventListener('input', function() {
                    if (form.classList.contains('was-validated')) {
                        validateInput(input);
                    }
                });
            });
        });

        // Password strength indicator
        initPasswordStrength();

        // Password match validation
        initPasswordMatch();
    }

    function validateInput(input) {
        const isValid = input.checkValidity();

        if (isValid) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
        }

        return isValid;
    }

    function initPasswordStrength() {
        const passwordInputs = document.querySelectorAll('input[type="password"][data-strength]');

        passwordInputs.forEach(function(input) {
            const strengthMeter = document.querySelector(input.dataset.strength);

            if (strengthMeter) {
                input.addEventListener('input', function() {
                    const strength = calculatePasswordStrength(input.value);
                    updateStrengthMeter(strengthMeter, strength);
                });
            }
        });
    }

    function calculatePasswordStrength(password) {
        let strength = 0;

        if (password.length >= 8) strength++;
        if (password.length >= 12) strength++;
        if (/[a-z]/.test(password)) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^a-zA-Z0-9]/.test(password)) strength++;

        return Math.min(strength, 5);
    }

    function updateStrengthMeter(meter, strength) {
        const levels = ['very-weak', 'weak', 'fair', 'good', 'strong', 'very-strong'];
        const colors = ['#dc3545', '#fd7e14', '#ffc107', '#20c997', '#198754', '#0d6efd'];

        meter.style.width = (strength * 20) + '%';
        meter.style.backgroundColor = colors[strength] || colors[0];
        meter.setAttribute('data-level', levels[strength] || levels[0]);
    }

    function initPasswordMatch() {
        const confirmInputs = document.querySelectorAll('input[data-match]');

        confirmInputs.forEach(function(confirmInput) {
            const originalInput = document.querySelector(confirmInput.dataset.match);

            if (originalInput) {
                confirmInput.addEventListener('input', function() {
                    if (confirmInput.value !== originalInput.value) {
                        confirmInput.setCustomValidity('Mật khẩu không khớp');
                    } else {
                        confirmInput.setCustomValidity('');
                    }
                });

                originalInput.addEventListener('input', function() {
                    if (confirmInput.value && confirmInput.value !== originalInput.value) {
                        confirmInput.setCustomValidity('Mật khẩu không khớp');
                    } else {
                        confirmInput.setCustomValidity('');
                    }
                });
            }
        });
    }

})();

