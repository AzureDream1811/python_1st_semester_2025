"""
QR Service for ElectroShop
Tạo mã QR cho thanh toán chuyển khoản và ví điện tử
"""
import qrcode
import base64
from io import BytesIO
from decimal import Decimal
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class QRService:
    """Service tạo mã QR thanh toán"""

    # VietQR API URL
    VIETQR_API = "https://img.vietqr.io/image"

    @staticmethod
    def generate_transfer_content(order_number: str, phone: str) -> str:
        """
        Tạo nội dung chuyển khoản theo định dạng chuẩn
        
        Args:
            order_number: Mã đơn hàng
            phone: Số điện thoại khách hàng
            
        Returns:
            Nội dung chuyển khoản: "DH{order_number} {4_số_cuối_phone}"
        """
        # Lấy 4 số cuối của số điện thoại
        phone_clean = ''.join(filter(str.isdigit, phone or ''))
        last_four = phone_clean[-4:] if len(phone_clean) >= 4 else phone_clean

        order_number = (order_number or '').strip()
        prefix = '' if order_number.upper().startswith('DH') else 'DH'
        content = f"{prefix}{order_number}"
        if last_four:
            content = f"{content} {last_four}"
        return content

    @classmethod
    def generate_vietqr_url(
            cls,
            bank_code: str,
            account_number: str,
            amount: Decimal,
            content: str,
            account_name: str = ""
    ) -> str:
        """
        Tạo URL VietQR image
        
        Args:
            bank_code: Mã ngân hàng (VCB, TCB, MB, ...)
            account_number: Số tài khoản
            amount: Số tiền
            content: Nội dung chuyển khoản
            account_name: Tên tài khoản (optional)
            
        Returns:
            URL của hình ảnh QR code
        """
        # VietQR URL format: https://img.vietqr.io/image/{bank_code}-{account_number}-{template}.png?amount={amount}&addInfo={content}&accountName={name}
        amount_int = int(amount)

        # URL encode content
        import urllib.parse
        content_encoded = urllib.parse.quote(content)
        account_name_encoded = urllib.parse.quote(account_name) if account_name else ""

        url = f"{cls.VIETQR_API}/{bank_code}-{account_number}-compact2.png"
        url += f"?amount={amount_int}&addInfo={content_encoded}"

        if account_name_encoded:
            url += f"&accountName={account_name_encoded}"

        return url

    @classmethod
    def generate_vietqr(
            cls,
            bank_code: str,
            account_number: str,
            amount: Decimal,
            content: str,
            account_name: str = ""
    ) -> dict:
        """
        Tạo VietQR code cho chuyển khoản ngân hàng
        
        Args:
            bank_code: Mã ngân hàng
            account_number: Số tài khoản
            amount: Số tiền
            content: Nội dung chuyển khoản
            account_name: Tên tài khoản
            
        Returns:
            Dict với qr_url, qr_data, và thông tin thanh toán
        """
        qr_url = cls.generate_vietqr_url(
            bank_code, account_number, amount, content, account_name
        )

        # Tạo QR data string theo chuẩn VietQR
        qr_data = cls._build_vietqr_data(
            bank_code, account_number, amount, content
        )

        return {
            'qr_url': qr_url,
            'qr_data': qr_data,
            'bank_code': bank_code,
            'account_number': account_number,
            'account_name': account_name,
            'amount': amount,
            'content': content
        }

    @staticmethod
    def _build_vietqr_data(
            bank_code: str,
            account_number: str,
            amount: Decimal,
            content: str
    ) -> str:
        """
        Xây dựng chuỗi dữ liệu QR theo chuẩn EMVCo
        Đây là simplified version, production nên dùng VietQR API
        """
        # Simplified QR data - trong production nên dùng thư viện VietQR chính thức
        return f"VIETQR|{bank_code}|{account_number}|{int(amount)}|{content}"

    @classmethod
    def generate_momo_qr(
            cls,
            phone: str,
            amount: Decimal,
            content: str
    ) -> dict:
        """
        Tạo QR code MoMo
        
        Args:
            phone: Số điện thoại MoMo
            amount: Số tiền
            content: Nội dung chuyển khoản
            
        Returns:
            Dict với qr_base64, qr_data, và thông tin thanh toán
        """
        # MoMo QR format (simplified)
        # Trong production nên tích hợp MoMo API chính thức
        qr_data = f"2|99|{phone}|||0|0|{int(amount)}|{content}|transfer_myqr"

        # Tạo QR code image
        qr_base64 = cls._generate_qr_image(qr_data)

        return {
            'qr_base64': qr_base64,
            'qr_data': qr_data,
            'wallet_type': 'momo',
            'wallet_id': phone,
            'amount': amount,
            'content': content
        }

    @classmethod
    def generate_zalopay_qr(
            cls,
            wallet_id: str,
            amount: Decimal,
            content: str
    ) -> dict:
        """
        Tạo QR code ZaloPay
        
        Args:
            wallet_id: ID ví ZaloPay (số điện thoại)
            amount: Số tiền
            content: Nội dung chuyển khoản
            
        Returns:
            Dict với qr_base64, qr_data, và thông tin thanh toán
        """
        # ZaloPay QR format (simplified)
        # Trong production nên tích hợp ZaloPay API chính thức
        qr_data = f"ZALOPAY|{wallet_id}|{int(amount)}|{content}"

        # Tạo QR code image
        qr_base64 = cls._generate_qr_image(qr_data)

        return {
            'qr_base64': qr_base64,
            'qr_data': qr_data,
            'wallet_type': 'zalopay',
            'wallet_id': wallet_id,
            'amount': amount,
            'content': content
        }

    @staticmethod
    def _generate_qr_image(data: str, size: int = 300) -> str:
        """
        Tạo QR code image và trả về base64
        
        Args:
            data: Dữ liệu để encode
            size: Kích thước QR (pixels)
            
        Returns:
            Base64 encoded PNG image
        """
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # Resize nếu cần
            img = img.resize((size, size))

            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()

            return f"data:image/png;base64,{img_str}"

        except Exception as e:
            logger.error(f"Lỗi tạo QR code: {e}")
            return ""

    @classmethod
    def generate_generic_qr(cls, data: str) -> str:
        """
        Tạo QR code generic từ bất kỳ dữ liệu nào
        
        Args:
            data: Dữ liệu để encode
            
        Returns:
            Base64 encoded PNG image
        """
        return cls._generate_qr_image(data)

    @staticmethod
    def decode_vietqr(qr_data: str) -> Optional[dict]:
        """
        Giải mã VietQR data (simplified version)
        
        Args:
            qr_data: Chuỗi dữ liệu QR
            
        Returns:
            Dict với thông tin thanh toán hoặc None
        """
        try:
            if qr_data.startswith('VIETQR|'):
                parts = qr_data.split('|')
                if len(parts) >= 5:
                    return {
                        'bank_code': parts[1],
                        'account_number': parts[2],
                        'amount': Decimal(parts[3]),
                        'content': parts[4]
                    }
            return None
        except Exception:
            return None

    @staticmethod
    def decode_ewallet_qr(qr_data: str) -> Optional[dict]:
        """
        Giải mã E-wallet QR data (simplified version)
        
        Args:
            qr_data: Chuỗi dữ liệu QR
            
        Returns:
            Dict với thông tin thanh toán hoặc None
        """
        try:
            # MoMo format
            if qr_data.startswith('2|99|'):
                parts = qr_data.split('|')
                if len(parts) >= 9:
                    return {
                        'wallet_type': 'momo',
                        'wallet_id': parts[2],
                        'amount': Decimal(parts[7]),
                        'content': parts[8]
                    }

            # ZaloPay format
            if qr_data.startswith('ZALOPAY|'):
                parts = qr_data.split('|')
                if len(parts) >= 4:
                    return {
                        'wallet_type': 'zalopay',
                        'wallet_id': parts[1],
                        'amount': Decimal(parts[2]),
                        'content': parts[3]
                    }

            return None
        except Exception:
            return None
