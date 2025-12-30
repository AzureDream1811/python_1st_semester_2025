"""
Address Service for ElectroShop
Fetch địa chỉ từ API provinces.open-api.vn
"""
import requests
from typing import List, Dict, Optional
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class AddressService:
    """Service để fetch địa chỉ từ API provinces.open-api.vn"""

    BASE_URL = "https://provinces.open-api.vn/api"
    TIMEOUT = 5  # seconds
    CACHE_TIMEOUT = 86400  # 24 hours

    @classmethod
    def get_provinces(cls) -> List[Dict]:
        """
        Lấy danh sách tỉnh/thành phố
        
        Returns:
            List các dict với keys: code, name
        """
        cache_key = 'vietnam_provinces'
        cached = cache.get(cache_key)

        if cached:
            return cached

        try:
            response = requests.get(
                f"{cls.BASE_URL}/p/",
                timeout=cls.TIMEOUT
            )
            response.raise_for_status()

            provinces = response.json()
            # Chuẩn hóa dữ liệu
            result = [
                {'code': str(p['code']), 'name': p['name']}
                for p in provinces
            ]

            # Cache kết quả
            cache.set(cache_key, result, cls.CACHE_TIMEOUT)

            return result

        except requests.Timeout:
            logger.error("Timeout khi fetch provinces từ API")
            return []
        except requests.RequestException as e:
            logger.error(f"Lỗi khi fetch provinces: {e}")
            return []
        except (KeyError, ValueError) as e:
            logger.error(f"Lỗi parse dữ liệu provinces: {e}")
            return []

    @classmethod
    def get_districts(cls, province_code: str) -> List[Dict]:
        """
        Lấy danh sách quận/huyện theo tỉnh
        
        Args:
            province_code: Mã tỉnh/thành phố
            
        Returns:
            List các dict với keys: code, name, province_code
        """
        cache_key = f'vietnam_districts_{province_code}'
        cached = cache.get(cache_key)

        if cached:
            return cached

        try:
            response = requests.get(
                f"{cls.BASE_URL}/p/{province_code}",
                params={'depth': 2},
                timeout=cls.TIMEOUT
            )
            response.raise_for_status()

            data = response.json()
            districts = data.get('districts', [])

            # Chuẩn hóa dữ liệu
            result = [
                {
                    'code': str(d['code']),
                    'name': d['name'],
                    'province_code': str(province_code)
                }
                for d in districts
            ]

            # Cache kết quả
            cache.set(cache_key, result, cls.CACHE_TIMEOUT)

            return result

        except requests.Timeout:
            logger.error(f"Timeout khi fetch districts cho province {province_code}")
            return []
        except requests.RequestException as e:
            logger.error(f"Lỗi khi fetch districts: {e}")
            return []
        except (KeyError, ValueError) as e:
            logger.error(f"Lỗi parse dữ liệu districts: {e}")
            return []

    @classmethod
    def get_wards(cls, district_code: str) -> List[Dict]:
        """
        Lấy danh sách phường/xã theo quận/huyện
        
        Args:
            district_code: Mã quận/huyện
            
        Returns:
            List các dict với keys: code, name, district_code
        """
        cache_key = f'vietnam_wards_{district_code}'
        cached = cache.get(cache_key)

        if cached:
            return cached

        try:
            response = requests.get(
                f"{cls.BASE_URL}/d/{district_code}",
                params={'depth': 2},
                timeout=cls.TIMEOUT
            )
            response.raise_for_status()

            data = response.json()
            wards = data.get('wards', [])

            # Chuẩn hóa dữ liệu
            result = [
                {
                    'code': str(w['code']),
                    'name': w['name'],
                    'district_code': str(district_code)
                }
                for w in wards
            ]

            # Cache kết quả
            cache.set(cache_key, result, cls.CACHE_TIMEOUT)

            return result

        except requests.Timeout:
            logger.error(f"Timeout khi fetch wards cho district {district_code}")
            return []
        except requests.RequestException as e:
            logger.error(f"Lỗi khi fetch wards: {e}")
            return []
        except (KeyError, ValueError) as e:
            logger.error(f"Lỗi parse dữ liệu wards: {e}")
            return []

    @classmethod
    def get_province_by_code(cls, code: str) -> Optional[Dict]:
        """Lấy thông tin tỉnh theo mã"""
        provinces = cls.get_provinces()
        for p in provinces:
            if p['code'] == str(code):
                return p
        return None

    @classmethod
    def get_district_by_code(cls, province_code: str, district_code: str) -> Optional[Dict]:
        """Lấy thông tin quận/huyện theo mã"""
        districts = cls.get_districts(province_code)
        for d in districts:
            if d['code'] == str(district_code):
                return d
        return None

    @classmethod
    def get_ward_by_code(cls, district_code: str, ward_code: str) -> Optional[Dict]:
        """Lấy thông tin phường/xã theo mã"""
        wards = cls.get_wards(district_code)
        for w in wards:
            if w['code'] == str(ward_code):
                return w
        return None

    @classmethod
    def search_provinces(cls, query: str) -> List[Dict]:
        """Tìm kiếm tỉnh/thành phố theo tên"""
        provinces = cls.get_provinces()
        query_lower = query.lower()
        return [p for p in provinces if query_lower in p['name'].lower()]

    @classmethod
    def clear_cache(cls):
        """Xóa cache địa chỉ"""
        cache.delete('vietnam_provinces')
        # Không thể xóa tất cả districts/wards cache vì không biết hết keys
        # Cần implement cache với prefix pattern nếu cần
