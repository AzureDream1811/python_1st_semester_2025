/**
 * Address Cascade Component
 * Quản lý cascade dropdown Tỉnh → Quận → Phường
 * Dùng API: /accounts/api/provinces/, /districts/, /wards/
 */

class AddressCascade {
    constructor(config) {
        this.provinceSelect = document.getElementById(config.provinceSelectId);
        this.districtSelect = document.getElementById(config.districtSelectId);
        this.wardSelect = document.getElementById(config.wardSelectId);
        
        this.provinceNameInput = document.getElementById(config.provinceNameId);
        this.districtNameInput = document.getElementById(config.districtNameId);
        this.wardNameInput = document.getElementById(config.wardNameId);
        
        this.apiBase = config.apiBase || '/accounts/api';
        
        // Pre-selected values for edit mode
        this.initialProvinceCode = config.initialProvinceCode || '';
        this.initialDistrictCode = config.initialDistrictCode || '';
        this.initialWardCode = config.initialWardCode || '';
        
        this.onProvinceChange = config.onProvinceChange || null;
        this.onDistrictChange = config.onDistrictChange || null;
        this.onWardChange = config.onWardChange || null;
        
        this.init();
    }
    
    async init() {
        if (!this.provinceSelect || !this.districtSelect) {
            console.warn('AddressCascade: Required elements not found');
            return;
        }
        
        this.bindEvents();
        
        // Load provinces if empty
        if (this.provinceSelect.options.length <= 1) {
            await this.loadProvinces();
        }
        
        // Pre-select for edit mode
        if (this.initialProvinceCode) {
            this.provinceSelect.value = this.initialProvinceCode;
            await this.loadDistricts(this.initialProvinceCode);
            
            if (this.initialDistrictCode) {
                this.districtSelect.value = this.initialDistrictCode;
                await this.loadWards(this.initialDistrictCode);
                
                if (this.initialWardCode && this.wardSelect) {
                    this.wardSelect.value = this.initialWardCode;
                    this.updateHiddenName(this.wardSelect, this.wardNameInput);
                }
            }
        }
        
        this.updateHiddenName(this.provinceSelect, this.provinceNameInput);
        this.updateHiddenName(this.districtSelect, this.districtNameInput);
        if (this.wardSelect) {
            this.updateHiddenName(this.wardSelect, this.wardNameInput);
        }
    }
    
    bindEvents() {
        this.provinceSelect.addEventListener('change', async (e) => {
            const selectedOption = e.target.options[e.target.selectedIndex];
            const code = selectedOption ? (selectedOption.dataset.code || e.target.value) : '';
            
            this.updateHiddenName(e.target, this.provinceNameInput);
            this.resetSelect(this.districtSelect, '-- Chọn Quận/Huyện --');
            if (this.wardSelect) {
                this.resetSelect(this.wardSelect, '-- Chọn Phường/Xã --');
            }
            
            if (code) {
                await this.loadDistricts(code);
                this.districtSelect.disabled = false;
            } else {
                this.districtSelect.disabled = true;
            }
            
            if (this.wardSelect) {
                this.wardSelect.disabled = true;
            }
            
            if (this.onProvinceChange) this.onProvinceChange(code);
        });
        
        this.districtSelect.addEventListener('change', async (e) => {
            const selectedOption = e.target.options[e.target.selectedIndex];
            const code = selectedOption ? (selectedOption.dataset.code || e.target.value) : '';
            
            this.updateHiddenName(e.target, this.districtNameInput);
            
            if (this.wardSelect) {
                this.resetSelect(this.wardSelect, '-- Chọn Phường/Xã --');
                
                if (code) {
                    await this.loadWards(code);
                    this.wardSelect.disabled = false;
                } else {
                    this.wardSelect.disabled = true;
                }
            }
            
            if (this.onDistrictChange) this.onDistrictChange(code);
        });
        
        if (this.wardSelect) {
            this.wardSelect.addEventListener('change', (e) => {
                const selectedOption = e.target.options[e.target.selectedIndex];
                const code = selectedOption ? (selectedOption.dataset.code || e.target.value) : '';
                
                this.updateHiddenName(e.target, this.wardNameInput);
                if (this.onWardChange) this.onWardChange(code);
            });
        }
    }
    
    async loadProvinces() {
        try {
            this.provinceSelect.disabled = true;
            const response = await fetch(`${this.apiBase}/provinces/`);
            const data = await response.json();
            
            this.provinceSelect.innerHTML = '<option value="">-- Chọn Tỉnh/Thành phố --</option>';
            
            data.provinces.forEach(p => {
                const option = document.createElement('option');
                option.value = p.code;
                option.textContent = p.name;
                option.dataset.name = p.name;
                this.provinceSelect.appendChild(option);
            });
            
            // Re-select initial value if exists
            if (this.initialProvinceCode) {
                this.provinceSelect.value = this.initialProvinceCode;
            }
        } catch (error) {
            console.error('Error loading provinces:', error);
            this.showError(this.provinceSelect, 'Không thể tải danh sách tỉnh/thành phố');
        } finally {
            this.provinceSelect.disabled = false;
        }
    }
    
    async loadDistricts(provinceCode) {
        try {
            this.districtSelect.disabled = true;
            const response = await fetch(`${this.apiBase}/districts/${provinceCode}/`);
            const data = await response.json();
            
            this.districtSelect.innerHTML = '<option value="">-- Chọn Quận/Huyện --</option>';
            
            data.districts.forEach(d => {
                const option = document.createElement('option');
                option.value = d.code;
                option.textContent = d.name;
                option.dataset.name = d.name;
                this.districtSelect.appendChild(option);
            });
            
            // Re-select initial value if exists
            if (this.initialDistrictCode) {
                this.districtSelect.value = this.initialDistrictCode;
                this.updateHiddenName(this.districtSelect, this.districtNameInput);
            }
        } catch (error) {
            console.error('Error loading districts:', error);
            this.showError(this.districtSelect, 'Không thể tải danh sách quận/huyện');
        } finally {
            this.districtSelect.disabled = false;
        }
    }
    
    async loadWards(districtCode) {
        if (!this.wardSelect) return;
        
        try {
            this.wardSelect.disabled = true;
            const response = await fetch(`${this.apiBase}/wards/${districtCode}/`);
            const data = await response.json();
            
            this.wardSelect.innerHTML = '<option value="">-- Chọn Phường/Xã --</option>';
            
            data.wards.forEach(w => {
                const option = document.createElement('option');
                option.value = w.code;
                option.textContent = w.name;
                option.dataset.name = w.name;
                this.wardSelect.appendChild(option);
            });
            
            // Re-select initial value if exists
            if (this.initialWardCode) {
                this.wardSelect.value = this.initialWardCode;
                this.updateHiddenName(this.wardSelect, this.wardNameInput);
            }
        } catch (error) {
            console.error('Error loading wards:', error);
        } finally {
            this.wardSelect.disabled = false;
        }
    }
    
    updateHiddenName(select, hiddenInput) {
        if (!hiddenInput) return;
        const selected = select.options[select.selectedIndex];
        hiddenInput.value = selected ? (selected.dataset.name || selected.textContent || '') : '';
    }
    
    resetSelect(select, placeholder) {
        select.innerHTML = `<option value="">${placeholder}</option>`;
    }
    
    showError(element, message) {
        element.classList.add('is-invalid');
        const feedback = element.parentElement.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.textContent = message;
        }
    }
    
    clearError(element) {
        element.classList.remove('is-invalid');
    }
}

// Address Form Validator
class AddressFormValidator {
    constructor(formId, config = {}) {
        this.form = document.getElementById(formId);
        this.config = {
            fullNameId: config.fullNameId || 'full_name',
            phoneId: config.phoneId || 'phone',
            addressId: config.addressId || 'address',
            provinceSelectId: config.provinceSelectId || 'provinceSelect',
            districtSelectId: config.districtSelectId || 'districtSelect',
            ...config
        };
        
        if (this.form) {
            this.init();
        }
    }
    
    init() {
        this.form.addEventListener('submit', (e) => {
            if (!this.validate()) {
                e.preventDefault();
            }
        });
        
        // Real-time validation
        this.form.querySelectorAll('input, select, textarea').forEach(field => {
            field.addEventListener('blur', () => this.validateField(field));
            field.addEventListener('input', () => this.clearFieldError(field));
        });
    }
    
    validate() {
        let isValid = true;
        
        // Full name validation
        const fullName = document.getElementById(this.config.fullNameId);
        if (fullName && !this.validateFullName(fullName)) {
            isValid = false;
        }
        
        // Phone validation
        const phone = document.getElementById(this.config.phoneId);
        if (phone && !this.validatePhone(phone)) {
            isValid = false;
        }
        
        // Address validation
        const address = document.getElementById(this.config.addressId);
        if (address && !this.validateAddress(address)) {
            isValid = false;
        }
        
        // Province validation
        const province = document.getElementById(this.config.provinceSelectId);
        if (province && !province.value) {
            this.showFieldError(province, 'Vui lòng chọn Tỉnh/Thành phố');
            isValid = false;
        }
        
        // District validation
        const district = document.getElementById(this.config.districtSelectId);
        if (district && !district.value) {
            this.showFieldError(district, 'Vui lòng chọn Quận/Huyện');
            isValid = false;
        }
        
        return isValid;
    }
    
    validateField(field) {
        const id = field.id;
        
        if (id === this.config.fullNameId) {
            return this.validateFullName(field);
        } else if (id === this.config.phoneId) {
            return this.validatePhone(field);
        } else if (id === this.config.addressId) {
            return this.validateAddress(field);
        } else if (field.hasAttribute('required') && !field.value) {
            this.showFieldError(field, 'Trường này là bắt buộc');
            return false;
        }
        
        return true;
    }
    
    validateFullName(field) {
        const value = field.value.trim();
        
        if (!value) {
            this.showFieldError(field, 'Vui lòng nhập họ tên');
            return false;
        }
        
        if (value.length < 4) {
            this.showFieldError(field, 'Họ tên phải có ít nhất 4 ký tự');
            return false;
        }
        
        const words = value.split(/\s+/).filter(w => w.length > 0);
        if (words.length < 2) {
            this.showFieldError(field, 'Vui lòng nhập đầy đủ họ và tên');
            return false;
        }
        
        // Vietnamese name pattern
        const namePattern = /^[a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ\s]+$/;
        if (!namePattern.test(value)) {
            this.showFieldError(field, 'Họ tên chỉ được chứa chữ cái và khoảng trắng');
            return false;
        }
        
        this.clearFieldError(field);
        return true;
    }
    
    validatePhone(field) {
        const value = field.value.trim();
        
        if (!value) {
            this.showFieldError(field, 'Vui lòng nhập số điện thoại');
            return false;
        }
        
        // Vietnamese phone pattern
        const phonePattern = /^(0|\+84)[0-9]{9,10}$/;
        if (!phonePattern.test(value.replace(/\s/g, ''))) {
            this.showFieldError(field, 'Số điện thoại không hợp lệ (VD: 0912345678)');
            return false;
        }
        
        this.clearFieldError(field);
        return true;
    }
    
    validateAddress(field) {
        const value = field.value.trim();
        
        if (!value) {
            this.showFieldError(field, 'Vui lòng nhập địa chỉ');
            return false;
        }
        
        if (value.length < 5) {
            this.showFieldError(field, 'Địa chỉ phải có ít nhất 5 ký tự');
            return false;
        }
        
        this.clearFieldError(field);
        return true;
    }
    
    showFieldError(field, message) {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');
        
        let feedback = field.parentElement.querySelector('.invalid-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            field.parentElement.appendChild(feedback);
        }
        feedback.textContent = message;
        feedback.style.display = 'block';
    }
    
    clearFieldError(field) {
        field.classList.remove('is-invalid');
        const feedback = field.parentElement.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.style.display = 'none';
        }
    }
}

// Export for use
window.AddressCascade = AddressCascade;
window.AddressFormValidator = AddressFormValidator;
