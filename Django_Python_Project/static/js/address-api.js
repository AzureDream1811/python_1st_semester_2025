/**
 * Address API Module for ElectroShop
 * Fetch địa chỉ từ API provinces.open-api.vn
 */

const AddressAPI = {
    baseUrl: '/accounts/api',
    
    /**
     * Fetch danh sách tỉnh/thành phố
     */
    async getProvinces() {
        try {
            const response = await fetch(`${this.baseUrl}/provinces/`);
            const data = await response.json();
            return data.provinces || [];
        } catch (error) {
            console.error('Error fetching provinces:', error);
            return [];
        }
    },
    
    /**
     * Fetch danh sách quận/huyện theo tỉnh
     */
    async getDistricts(provinceCode) {
        try {
            const response = await fetch(`${this.baseUrl}/districts/${provinceCode}/`);
            const data = await response.json();
            return data.districts || [];
        } catch (error) {
            console.error('Error fetching districts:', error);
            return [];
        }
    },
    
    /**
     * Fetch danh sách phường/xã theo quận/huyện
     */
    async getWards(districtCode) {
        try {
            const response = await fetch(`${this.baseUrl}/wards/${districtCode}/`);
            const data = await response.json();
            return data.wards || [];
        } catch (error) {
            console.error('Error fetching wards:', error);
            return [];
        }
    },
    
    /**
     * Populate select element với options
     */
    populateSelect(selectElement, items, placeholder = '-- Chọn --') {
        selectElement.innerHTML = `<option value="">${placeholder}</option>`;
        items.forEach(item => {
            const option = document.createElement('option');
            option.value = item.code;
            option.textContent = item.name;
            option.dataset.name = item.name;
            selectElement.appendChild(option);
        });
    },
    
    /**
     * Setup cascade dropdowns cho địa chỉ
     */
    setupCascadeDropdowns(provinceSelect, districtSelect, wardSelect, options = {}) {
        const {
            provinceCodeInput,
            districtCodeInput,
            wardCodeInput,
            provinceNameInput,
            districtNameInput,
            wardNameInput,
            onProvinceChange,
            onDistrictChange,
            onWardChange
        } = options;
        
        // Load provinces
        this.getProvinces().then(provinces => {
            this.populateSelect(provinceSelect, provinces, '-- Chọn Tỉnh/Thành phố --');
        });
        
        // Province change handler
        provinceSelect.addEventListener('change', async (e) => {
            const provinceCode = e.target.value;
            const provinceName = e.target.options[e.target.selectedIndex]?.dataset?.name || '';
            
            // Update hidden inputs
            if (provinceCodeInput) provinceCodeInput.value = provinceCode;
            if (provinceNameInput) provinceNameInput.value = provinceName;
            
            // Reset district and ward
            this.populateSelect(districtSelect, [], '-- Chọn Quận/Huyện --');
            this.populateSelect(wardSelect, [], '-- Chọn Phường/Xã --');
            if (districtCodeInput) districtCodeInput.value = '';
            if (wardCodeInput) wardCodeInput.value = '';
            if (districtNameInput) districtNameInput.value = '';
            if (wardNameInput) wardNameInput.value = '';
            
            if (provinceCode) {
                const districts = await this.getDistricts(provinceCode);
                this.populateSelect(districtSelect, districts, '-- Chọn Quận/Huyện --');
            }
            
            if (onProvinceChange) onProvinceChange(provinceCode, provinceName);
        });
        
        // District change handler
        districtSelect.addEventListener('change', async (e) => {
            const districtCode = e.target.value;
            const districtName = e.target.options[e.target.selectedIndex]?.dataset?.name || '';
            
            // Update hidden inputs
            if (districtCodeInput) districtCodeInput.value = districtCode;
            if (districtNameInput) districtNameInput.value = districtName;
            
            // Reset ward
            this.populateSelect(wardSelect, [], '-- Chọn Phường/Xã --');
            if (wardCodeInput) wardCodeInput.value = '';
            if (wardNameInput) wardNameInput.value = '';
            
            if (districtCode) {
                const wards = await this.getWards(districtCode);
                this.populateSelect(wardSelect, wards, '-- Chọn Phường/Xã --');
            }
            
            if (onDistrictChange) onDistrictChange(districtCode, districtName);
        });
        
        // Ward change handler
        wardSelect.addEventListener('change', (e) => {
            const wardCode = e.target.value;
            const wardName = e.target.options[e.target.selectedIndex]?.dataset?.name || '';
            
            // Update hidden inputs
            if (wardCodeInput) wardCodeInput.value = wardCode;
            if (wardNameInput) wardNameInput.value = wardName;
            
            if (onWardChange) onWardChange(wardCode, wardName);
        });
    },
    
    /**
     * Pre-select values (for edit mode)
     */
    async preselectValues(provinceSelect, districtSelect, wardSelect, provinceCode, districtCode, wardCode) {
        // Load and select province
        const provinces = await this.getProvinces();
        this.populateSelect(provinceSelect, provinces, '-- Chọn Tỉnh/Thành phố --');
        provinceSelect.value = provinceCode;
        
        if (provinceCode) {
            // Load and select district
            const districts = await this.getDistricts(provinceCode);
            this.populateSelect(districtSelect, districts, '-- Chọn Quận/Huyện --');
            districtSelect.value = districtCode;
            
            if (districtCode) {
                // Load and select ward
                const wards = await this.getWards(districtCode);
                this.populateSelect(wardSelect, wards, '-- Chọn Phường/Xã --');
                wardSelect.value = wardCode;
            }
        }
    }
};

// Export for use in other scripts
window.AddressAPI = AddressAPI;
