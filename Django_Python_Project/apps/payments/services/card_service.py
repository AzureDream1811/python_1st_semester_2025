"""
Card Validator Service for ElectroShop
Xác thực và xử lý thông tin thẻ thanh toán
"""
import re
from typing import Optional
from datetime import datetime


class CardValidator:
    """Service xác thực thẻ thanh toán"""

    # BIN patterns cho các loại thẻ
    # Visa: bắt đầu bằng 4
    # Mastercard: 51-55 hoặc 2221-2720
    # JCB: 3528-3589

    @staticmethod
    def detect_card_type(card_number: str) -> Optional[str]:
        """
        Nhận diện loại thẻ từ số thẻ (BIN - Bank Identification Number)
        
        Args:
            card_number: Số thẻ (có thể có khoảng trắng hoặc dấu gạch)
            
        Returns:
            'visa', 'mastercard', 'jcb' hoặc None nếu không nhận diện được
        """
        # Loại bỏ khoảng trắng và dấu gạch
        number = re.sub(r'[\s\-]', '', card_number)

        if not number or not number.isdigit():
            return None

        # Visa: bắt đầu bằng 4
        if number.startswith('4'):
            return 'visa'

        # Mastercard: 51-55 hoặc 2221-2720
        if len(number) >= 2:
            first_two = int(number[:2])
            if 51 <= first_two <= 55:
                return 'mastercard'

        if len(number) >= 4:
            first_four = int(number[:4])
            if 2221 <= first_four <= 2720:
                return 'mastercard'

        # JCB: 3528-3589
        if len(number) >= 4:
            first_four = int(number[:4])
            if 3528 <= first_four <= 3589:
                return 'jcb'

        return None

    @staticmethod
    def validate_luhn(card_number: str) -> bool:
        """
        Kiểm tra số thẻ bằng thuật toán Luhn
        
        Args:
            card_number: Số thẻ
            
        Returns:
            True nếu số thẻ hợp lệ theo Luhn algorithm
        """
        # Loại bỏ khoảng trắng và dấu gạch
        number = re.sub(r'[\s\-]', '', card_number)

        if not number or not number.isdigit():
            return False

        if len(number) < 13 or len(number) > 19:
            return False

        # Luhn algorithm
        digits = [int(d) for d in number]
        checksum = 0

        # Đảo ngược và xử lý từng số
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:  # Vị trí chẵn (từ phải sang)
                digit *= 2
                if digit > 9:
                    digit -= 9
            checksum += digit

        return checksum % 10 == 0

    @staticmethod
    def validate_expiry(month: int, year: int) -> bool:
        """
        Kiểm tra thẻ còn hạn không
        
        Args:
            month: Tháng hết hạn (1-12)
            year: Năm hết hạn (2 hoặc 4 chữ số)
            
        Returns:
            True nếu thẻ chưa hết hạn
        """
        if not (1 <= month <= 12):
            return False

        # Chuyển năm 2 chữ số thành 4 chữ số
        if year < 100:
            year += 2000

        now = datetime.now()
        current_year = now.year
        current_month = now.month

        # Thẻ hết hạn vào cuối tháng được ghi
        if year > current_year:
            return True
        elif year == current_year:
            return month >= current_month
        else:
            return False

    @staticmethod
    def mask_card_number(card_number: str) -> str:
        """
        Che số thẻ, chỉ hiện 4 số cuối
        
        Args:
            card_number: Số thẻ đầy đủ
            
        Returns:
            Số thẻ đã che dạng ****-****-****-1234
        """
        # Loại bỏ khoảng trắng và dấu gạch
        number = re.sub(r'[\s\-]', '', card_number)

        if len(number) < 4:
            return '*' * len(number)

        last_four = number[-4:]
        masked_length = len(number) - 4

        # Tạo chuỗi đã che với format ****-****-****-1234
        masked_parts = []
        for i in range(0, masked_length, 4):
            masked_parts.append('****')
        masked_parts.append(last_four)

        return '-'.join(masked_parts)

    @staticmethod
    def get_last_four(card_number: str) -> str:
        """
        Lấy 4 số cuối của thẻ
        
        Args:
            card_number: Số thẻ
            
        Returns:
            4 số cuối
        """
        number = re.sub(r'[\s\-]', '', card_number)
        return number[-4:] if len(number) >= 4 else number

    @staticmethod
    def validate_cvv(cvv: str, card_type: Optional[str] = None) -> bool:
        """
        Kiểm tra CVV hợp lệ
        
        Args:
            cvv: Mã CVV
            card_type: Loại thẻ (optional)
            
        Returns:
            True nếu CVV hợp lệ
        """
        if not cvv or not cvv.isdigit():
            return False

        # American Express có 4 số, các loại khác có 3 số
        # Hiện tại chỉ hỗ trợ Visa/Mastercard/JCB nên CVV là 3 số
        return len(cvv) == 3

    @staticmethod
    def validate_card(
            card_number: str,
            expiry_month: int,
            expiry_year: int,
            cvv: str,
            cardholder_name: str
    ) -> dict:
        """
        Xác thực đầy đủ thông tin thẻ
        
        Args:
            card_number: Số thẻ
            expiry_month: Tháng hết hạn
            expiry_year: Năm hết hạn
            cvv: Mã CVV
            cardholder_name: Tên chủ thẻ
            
        Returns:
            Dict với 'valid' (bool) và 'errors' (list) hoặc 'card_type' nếu hợp lệ
        """
        errors = []

        # Kiểm tra tên chủ thẻ
        if not cardholder_name or len(cardholder_name.strip()) < 2:
            errors.append('Vui lòng nhập tên chủ thẻ')

        # Kiểm tra loại thẻ
        card_type = CardValidator.detect_card_type(card_number)
        if not card_type:
            errors.append('Loại thẻ không được hỗ trợ (chỉ hỗ trợ Visa, Mastercard, JCB)')

        # Kiểm tra số thẻ bằng Luhn
        if not CardValidator.validate_luhn(card_number):
            errors.append('Số thẻ không hợp lệ')

        # Kiểm tra ngày hết hạn
        if not CardValidator.validate_expiry(expiry_month, expiry_year):
            errors.append('Thẻ đã hết hạn hoặc ngày hết hạn không hợp lệ')

        # Kiểm tra CVV
        if not CardValidator.validate_cvv(cvv, card_type):
            errors.append('Mã CVV không hợp lệ (phải là 3 chữ số)')

        if errors:
            return {'valid': False, 'errors': errors}

        return {
            'valid': True,
            'card_type': card_type,
            'masked_number': CardValidator.mask_card_number(card_number),
            'last_four': CardValidator.get_last_four(card_number)
        }
