/**
 * FormValidator - Client-side validation cho Social Login Modal
 * Validates email, phone (Vietnamese format), full name, required fields
 */

class FormValidator {
    constructor() {
        // Vietnamese phone regex từ Profile model
        this.phoneRegex = /^(0|\+84)[0-9]{9,10}$/;
        
        // Standard email regex
        this.emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    }
    
    /**
     * Validate email format
     * @param {string} email - Email to validate
     * @returns {object} {valid: boolean, error: string}
     */
    validateEmail(email) {
        if (!email || typeof email !== 'string') {
            return {
                valid: false,
                error: 'Email không được để trống'
            };
        }
        
        const trimmedEmail = email.trim();
        
        if (!trimmedEmail) {
            return {
                valid: false,
                error: 'Email không được để trống'
            };
        }
        
        if (!this.emailRegex.test(trimmedEmail)) {
            return {
                valid: false,
                error: 'Định dạng email không hợp lệ'
            };
        }
        
        return {
            valid: true,
            error: null
        };
    }
    
    /**
     * Validate Vietnamese phone number
     * Format: 0xxxxxxxxx or +84xxxxxxxxx
     * @param {string} phone - Phone number to validate
     * @returns {object} {valid: boolean, error: string}
     */
    validatePhone(phone) {
        // Phone is optional, so empty is valid
        if (!phone || typeof phone !== 'string') {
            return {
                valid: true,
                error: null
            };
        }
        
        const trimmedPhone = phone.trim();
        
        if (!trimmedPhone) {
            return {
                valid: true,
                error: null
            };
        }
        
        if (!this.phoneRegex.test(trimmedPhone)) {
            return {
                valid: false,
                error: 'Số điện thoại phải có định dạng: 0xxxxxxxxx hoặc +84xxxxxxxxx'
            };
        }
        
        return {
            valid: true,
            error: null
        };
    }

    
    /**
     * Validate full name (at least 2 words)
     * @param {string} fullName - Full name to validate
     * @returns {object} {valid: boolean, error: string}
     */
    validateFullName(fullName) {
        if (!fullName || typeof fullName !== 'string') {
            return {
                valid: false,
                error: 'Họ tên không được để trống'
            };
        }
        
        const trimmedName = fullName.trim();
        
        if (!trimmedName) {
            return {
                valid: false,
                error: 'Họ tên không được để trống'
            };
        }
        
        // Check at least 2 words
        const words = trimmedName.split(/\s+/).filter(word => word.length > 0);
        
        if (words.length < 2) {
            return {
                valid: false,
                error: 'Họ tên phải có ít nhất 2 từ'
            };
        }
        
        return {
            valid: true,
            error: null
        };
    }
    
    /**
     * Validate first name
     * @param {string} firstName - First name to validate
     * @returns {object} {valid: boolean, error: string}
     */
    validateFirstName(firstName) {
        if (!firstName || typeof firstName !== 'string') {
            return {
                valid: false,
                error: 'Tên không được để trống'
            };
        }
        
        const trimmedName = firstName.trim();
        
        if (!trimmedName) {
            return {
                valid: false,
                error: 'Tên không được để trống'
            };
        }
        
        return {
            valid: true,
            error: null
        };
    }
    
    /**
     * Validate last name
     * @param {string} lastName - Last name to validate
     * @returns {object} {valid: boolean, error: string}
     */
    validateLastName(lastName) {
        if (!lastName || typeof lastName !== 'string') {
            return {
                valid: false,
                error: 'Họ không được để trống'
            };
        }
        
        const trimmedName = lastName.trim();
        
        if (!trimmedName) {
            return {
                valid: false,
                error: 'Họ không được để trống'
            };
        }
        
        return {
            valid: true,
            error: null
        };
    }
    
    /**
     * Validate required fields
     * @param {object} fields - Object with field names as keys and values
     * @returns {object} {valid: boolean, errors: object}
     */
    validateRequired(fields) {
        const errors = {};
        let hasErrors = false;
        
        for (const [fieldName, value] of Object.entries(fields)) {
            if (!value || (typeof value === 'string' && !value.trim())) {
                errors[fieldName] = `${this.getFieldDisplayName(fieldName)} không được để trống`;
                hasErrors = true;
            }
        }
        
        return {
            valid: !hasErrors,
            errors: errors
        };
    }
    
    /**
     * Get display name for field
     * @param {string} fieldName - Field name
     * @returns {string} Display name
     */
    getFieldDisplayName(fieldName) {
        const displayNames = {
            'email': 'Email',
            'first_name': 'Tên',
            'last_name': 'Họ',
            'phone': 'Số điện thoại',
            'provider': 'Nhà cung cấp'
        };
        
        return displayNames[fieldName] || fieldName;
    }
    
    /**
     * Validate all fields for social registration
     * @param {object} data - Form data
     * @returns {object} {valid: boolean, errors: object}
     */
    validateSocialRegistration(data) {
        const errors = {};
        
        // Validate email
        const emailResult = this.validateEmail(data.email);
        if (!emailResult.valid) {
            errors.email = emailResult.error;
        }
        
        // Validate first name
        const firstNameResult = this.validateFirstName(data.first_name);
        if (!firstNameResult.valid) {
            errors.first_name = firstNameResult.error;
        }
        
        // Validate last name
        const lastNameResult = this.validateLastName(data.last_name);
        if (!lastNameResult.valid) {
            errors.last_name = lastNameResult.error;
        }
        
        // Validate phone (optional)
        const phoneResult = this.validatePhone(data.phone);
        if (!phoneResult.valid) {
            errors.phone = phoneResult.error;
        }
        
        // Validate provider
        if (!data.provider || !['google', 'facebook'].includes(data.provider)) {
            errors.provider = 'Nhà cung cấp không hợp lệ';
        }
        
        return {
            valid: Object.keys(errors).length === 0,
            errors: errors
        };
    }
    
    /**
     * Validate social login data
     * @param {object} data - Form data
     * @returns {object} {valid: boolean, errors: object}
     */
    validateSocialLogin(data) {
        const errors = {};
        
        // Validate email
        const emailResult = this.validateEmail(data.email);
        if (!emailResult.valid) {
            errors.email = emailResult.error;
        }
        
        // Validate provider
        if (!data.provider || !['google', 'facebook'].includes(data.provider)) {
            errors.provider = 'Nhà cung cấp không hợp lệ';
        }
        
        return {
            valid: Object.keys(errors).length === 0,
            errors: errors
        };
    }
    
    /**
     * Show validation error on field
     * @param {string} fieldId - Field ID
     * @param {string} error - Error message
     */
    showFieldError(fieldId, error) {
        const field = document.getElementById(fieldId);
        if (!field) return;
        
        // Remove existing error
        this.clearFieldError(fieldId);
        
        // Add error class
        field.classList.add('is-invalid');
        
        // Create error element
        const errorElement = document.createElement('div');
        errorElement.className = 'invalid-feedback';
        errorElement.textContent = error;
        errorElement.id = `${fieldId}-error`;
        
        // Insert after field
        field.parentNode.insertBefore(errorElement, field.nextSibling);
    }
    
    /**
     * Clear validation error from field
     * @param {string} fieldId - Field ID
     */
    clearFieldError(fieldId) {
        const field = document.getElementById(fieldId);
        if (!field) return;
        
        // Remove error class
        field.classList.remove('is-invalid');
        
        // Remove error element
        const errorElement = document.getElementById(`${fieldId}-error`);
        if (errorElement) {
            errorElement.remove();
        }
    }
    
    /**
     * Clear all validation errors
     * @param {string[]} fieldIds - Array of field IDs
     */
    clearAllErrors(fieldIds) {
        fieldIds.forEach(fieldId => {
            this.clearFieldError(fieldId);
        });
    }
    
    /**
     * Show multiple field errors
     * @param {object} errors - Object with fieldId as key and error as value
     */
    showFieldErrors(errors) {
        for (const [fieldId, error] of Object.entries(errors)) {
            if (error) {
                this.showFieldError(fieldId, error);
            }
        }
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FormValidator;
} else {
    window.FormValidator = FormValidator;
}
