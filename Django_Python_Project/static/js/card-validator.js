/**
 * Card Validator Module for ElectroShop
 * Xác thực thẻ thanh toán real-time
 */

const CardValidator = {
    /**
     * Nhận diện loại thẻ từ số thẻ
     */
    detectCardType(cardNumber) {
        const number = cardNumber.replace(/[\s\-]/g, '');
        
        if (!number || !/^\d+$/.test(number)) {
            return null;
        }
        
        // Visa: bắt đầu bằng 4
        if (number.startsWith('4')) {
            return 'visa';
        }
        
        // Mastercard: 51-55 hoặc 2221-2720
        if (number.length >= 2) {
            const firstTwo = parseInt(number.substring(0, 2));
            if (firstTwo >= 51 && firstTwo <= 55) {
                return 'mastercard';
            }
        }
        
        if (number.length >= 4) {
            const firstFour = parseInt(number.substring(0, 4));
            if (firstFour >= 2221 && firstFour <= 2720) {
                return 'mastercard';
            }
            // JCB: 3528-3589
            if (firstFour >= 3528 && firstFour <= 3589) {
                return 'jcb';
            }
        }
        
        return null;
    },
    
    /**
     * Xác thực số thẻ bằng thuật toán Luhn
     */
    validateLuhn(cardNumber) {
        const number = cardNumber.replace(/[\s\-]/g, '');
        
        if (!number || !/^\d+$/.test(number)) {
            return false;
        }
        
        if (number.length < 13 || number.length > 19) {
            return false;
        }
        
        let sum = 0;
        let isEven = false;
        
        for (let i = number.length - 1; i >= 0; i--) {
            let digit = parseInt(number[i]);
            
            if (isEven) {
                digit *= 2;
                if (digit > 9) {
                    digit -= 9;
                }
            }
            
            sum += digit;
            isEven = !isEven;
        }
        
        return sum % 10 === 0;
    },
    
    /**
     * Xác thực ngày hết hạn
     */
    validateExpiry(month, year) {
        const m = parseInt(month);
        const y = parseInt(year);
        
        if (isNaN(m) || isNaN(y) || m < 1 || m > 12) {
            return false;
        }
        
        // Chuyển năm 2 chữ số thành 4 chữ số
        const fullYear = y < 100 ? 2000 + y : y;
        
        const now = new Date();
        const currentYear = now.getFullYear();
        const currentMonth = now.getMonth() + 1;
        
        if (fullYear > currentYear) {
            return true;
        } else if (fullYear === currentYear) {
            return m >= currentMonth;
        }
        
        return false;
    },
    
    /**
     * Xác thực CVV
     */
    validateCVV(cvv) {
        return /^\d{3}$/.test(cvv);
    },
    
    /**
     * Format số thẻ với khoảng trắng
     */
    formatCardNumber(cardNumber) {
        const number = cardNumber.replace(/[\s\-]/g, '');
        const groups = number.match(/.{1,4}/g) || [];
        return groups.join(' ');
    },
    
    /**
     * Che số thẻ
     */
    maskCardNumber(cardNumber) {
        const number = cardNumber.replace(/[\s\-]/g, '');
        if (number.length < 4) {
            return '*'.repeat(number.length);
        }
        
        const lastFour = number.slice(-4);
        const maskedLength = number.length - 4;
        const maskedParts = [];
        
        for (let i = 0; i < maskedLength; i += 4) {
            maskedParts.push('****');
        }
        maskedParts.push(lastFour);
        
        return maskedParts.join('-');
    },
    
    /**
     * Lấy icon cho loại thẻ
     */
    getCardIcon(cardType) {
        const icons = {
            'visa': 'bi-credit-card-2-front',
            'mastercard': 'bi-credit-card',
            'jcb': 'bi-credit-card-fill'
        };
        return icons[cardType] || 'bi-credit-card';
    },
    
    /**
     * Lấy tên hiển thị cho loại thẻ
     */
    getCardTypeName(cardType) {
        const names = {
            'visa': 'Visa',
            'mastercard': 'Mastercard',
            'jcb': 'JCB'
        };
        return names[cardType] || 'Unknown';
    },
    
    /**
     * Xác thực đầy đủ thông tin thẻ
     */
    validateCard(cardNumber, expiryMonth, expiryYear, cvv, cardholderName) {
        const errors = [];
        
        // Kiểm tra tên chủ thẻ
        if (!cardholderName || cardholderName.trim().length < 2) {
            errors.push('Vui lòng nhập tên chủ thẻ');
        }
        
        // Kiểm tra loại thẻ
        const cardType = this.detectCardType(cardNumber);
        if (!cardType) {
            errors.push('Loại thẻ không được hỗ trợ (chỉ hỗ trợ Visa, Mastercard, JCB)');
        }
        
        // Kiểm tra số thẻ bằng Luhn
        if (!this.validateLuhn(cardNumber)) {
            errors.push('Số thẻ không hợp lệ');
        }
        
        // Kiểm tra ngày hết hạn
        if (!this.validateExpiry(expiryMonth, expiryYear)) {
            errors.push('Thẻ đã hết hạn hoặc ngày hết hạn không hợp lệ');
        }
        
        // Kiểm tra CVV
        if (!this.validateCVV(cvv)) {
            errors.push('Mã CVV không hợp lệ (phải là 3 chữ số)');
        }
        
        if (errors.length > 0) {
            return { valid: false, errors };
        }
        
        return {
            valid: true,
            cardType,
            maskedNumber: this.maskCardNumber(cardNumber),
            lastFour: cardNumber.replace(/[\s\-]/g, '').slice(-4)
        };
    },
    
    /**
     * Setup real-time validation cho form thẻ
     */
    setupCardForm(options) {
        const {
            cardNumberInput,
            expiryMonthInput,
            expiryYearInput,
            cvvInput,
            cardholderNameInput,
            cardTypeIcon,
            cardTypeText,
            errorContainer,
            onValidationChange
        } = options;
        
        // Card number input handler
        if (cardNumberInput) {
            cardNumberInput.addEventListener('input', (e) => {
                // Format card number
                let value = e.target.value.replace(/[\s\-]/g, '');
                value = value.replace(/\D/g, '');
                value = value.substring(0, 16);
                e.target.value = this.formatCardNumber(value);
                
                // Detect card type
                const cardType = this.detectCardType(value);
                
                if (cardTypeIcon) {
                    cardTypeIcon.className = `bi ${this.getCardIcon(cardType)}`;
                }
                
                if (cardTypeText) {
                    cardTypeText.textContent = cardType ? this.getCardTypeName(cardType) : '';
                }
                
                // Validate
                const isValid = value.length >= 13 && this.validateLuhn(value);
                e.target.classList.toggle('is-valid', isValid);
                e.target.classList.toggle('is-invalid', value.length >= 13 && !isValid);
                
                // Show error in container if provided
                if (errorContainer) {
                    if (value.length >= 13 && !isValid) {
                        errorContainer.innerHTML = '<span class="text-danger">Số thẻ không hợp lệ</span>';
                    } else {
                        errorContainer.innerHTML = '';
                    }
                }
                
                if (onValidationChange) {
                    onValidationChange('cardNumber', isValid);
                }
            });
        }
        
        // Expiry inputs handler
        const validateExpiry = () => {
            const month = expiryMonthInput?.value;
            const year = expiryYearInput?.value;
            
            if (month && year) {
                const isValid = this.validateExpiry(month, year);
                expiryMonthInput?.classList.toggle('is-valid', isValid);
                expiryMonthInput?.classList.toggle('is-invalid', !isValid);
                expiryYearInput?.classList.toggle('is-valid', isValid);
                expiryYearInput?.classList.toggle('is-invalid', !isValid);
                
                if (onValidationChange) {
                    onValidationChange('expiry', isValid);
                }
            }
        };
        
        if (expiryMonthInput) {
            expiryMonthInput.addEventListener('change', validateExpiry);
        }
        if (expiryYearInput) {
            expiryYearInput.addEventListener('change', validateExpiry);
        }
        
        // CVV input handler
        if (cvvInput) {
            cvvInput.addEventListener('input', (e) => {
                let value = e.target.value.replace(/\D/g, '');
                value = value.substring(0, 3);
                e.target.value = value;
                
                const isValid = this.validateCVV(value);
                e.target.classList.toggle('is-valid', isValid);
                e.target.classList.toggle('is-invalid', value.length > 0 && !isValid);
                
                if (onValidationChange) {
                    onValidationChange('cvv', isValid);
                }
            });
        }
        
        // Cardholder name input handler
        if (cardholderNameInput) {
            cardholderNameInput.addEventListener('input', (e) => {
                // Convert to uppercase
                e.target.value = e.target.value.toUpperCase();
                
                const isValid = e.target.value.trim().length >= 2;
                e.target.classList.toggle('is-valid', isValid);
                e.target.classList.toggle('is-invalid', e.target.value.length > 0 && !isValid);
                
                if (onValidationChange) {
                    onValidationChange('cardholderName', isValid);
                }
            });
        }
    }
};

// Export for use in other scripts
window.CardValidator = CardValidator;
