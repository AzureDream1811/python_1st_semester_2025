"""
Shipping Service for ElectroShop
Shipping fee calculation, shipment creation, tracking
"""
import uuid
from decimal import Decimal
from typing import Dict, Any, List, Optional
from datetime import timedelta
from django.utils import timezone
from django.conf import settings

from apps.shipping.models import CarrierConfig, Shipment, ShipmentTracking, ShippingRate


class ShippingService:
    """Service for managing shipping"""

    def calculate_shipping_fee(self, address: Dict[str, str], items: List[Dict], carrier: str = None) -> Dict[str, Any]:
        """
        Calculate shipping fee
        """
        # Get carrier config
        if carrier:
            try:
                config = CarrierConfig.objects.get(carrier=carrier, is_active=True)
            except CarrierConfig.DoesNotExist:
                config = CarrierConfig.objects.filter(is_default=True, is_active=True).first()
        else:
            config = CarrierConfig.objects.filter(is_default=True, is_active=True).first()

        if not config:
            return {'success': False, 'error': 'Không có đơn vị vận chuyển khả dụng'}

        # Calculate total weight
        total_weight = sum(item.get('weight', 500) * item.get('quantity', 1) for item in items)

        # Get province from address
        to_province = address.get('city', address.get('province', ''))
        from_province = 'Hồ Chí Minh'  # Default warehouse location

        # Look up rate
        rate = ShippingRate.objects.filter(
            carrier=config.carrier,
            to_province__icontains=to_province,
            weight_from__lte=total_weight,
            weight_to__gte=total_weight
        ).first()

        if rate:
            fee = rate.price
        else:
            # Default fee calculation
            base_fee = Decimal('30000')
            weight_fee = Decimal(str(total_weight // 500 * 5000))
            fee = base_fee + weight_fee

        return {
            'success': True,
            'carrier': config.carrier,
            'carrier_name': config.name,
            'fee': fee,
            'weight': total_weight,
            'estimated_days': 3 if 'Hồ Chí Minh' in to_province or 'Hà Nội' in to_province else 5
        }

    def create_shipment(self, order, carrier: str = None) -> Shipment:
        """
        Create shipment for order
        """
        # Calculate shipping fee
        items = [{'weight': 500, 'quantity': item.quantity} for item in order.items.all()]
        address = {'city': order.city, 'district': order.district}
        fee_result = self.calculate_shipping_fee(address, items, carrier)

        carrier_code = fee_result.get('carrier', 'ghn')

        # Generate tracking code
        tracking_code = f"{carrier_code.upper()}-{uuid.uuid4().hex[:10].upper()}"

        # Create shipment
        shipment = Shipment.objects.create(
            order=order,
            carrier=carrier_code,
            tracking_code=tracking_code,
            shipping_fee=fee_result.get('fee', Decimal('30000')),
            status='pending',
            estimated_delivery=timezone.now().date() + timedelta(days=fee_result.get('estimated_days', 5)),
            weight=fee_result.get('weight', 0),
            cod_amount=order.total if order.payment_method == 'cod' else Decimal('0')
        )

        # Create initial tracking entry
        ShipmentTracking.objects.create(
            shipment=shipment,
            status='Đơn hàng đã được tạo',
            location='Kho hàng',
            description='Đơn hàng đang chờ lấy',
            timestamp=timezone.now()
        )

        return shipment

    def get_tracking_info(self, tracking_code: str) -> Dict[str, Any]:
        """
        Get tracking information
        """
        try:
            shipment = Shipment.objects.get(tracking_code=tracking_code)
        except Shipment.DoesNotExist:
            return {'success': False, 'error': 'Không tìm thấy vận đơn'}

        tracking_history = ShipmentTracking.objects.filter(
            shipment=shipment
        ).order_by('-timestamp')

        return {
            'success': True,
            'tracking_code': shipment.tracking_code,
            'carrier': shipment.carrier,
            'status': shipment.status,
            'estimated_delivery': shipment.estimated_delivery,
            'timeline': [
                {
                    'status': t.status,
                    'location': t.location,
                    'description': t.description,
                    'timestamp': t.timestamp.isoformat()
                }
                for t in tracking_history
            ]
        }

    def sync_shipping_status(self, shipment_id: int) -> bool:
        """
        Sync shipping status from carrier API
        """
        try:
            shipment = Shipment.objects.get(id=shipment_id)
        except Shipment.DoesNotExist:
            return False

        # TODO: Implement actual carrier API calls
        # This is a placeholder that simulates status updates

        return True

    def check_low_stock(self) -> List[Dict[str, Any]]:
        """
        Check products with low stock
        """
        from apps.products.models import Product

        threshold = getattr(settings, 'LOW_STOCK_THRESHOLD', 10)

        low_stock_products = Product.objects.filter(
            is_active=True,
            stock__lte=threshold,
            stock__gt=0
        ).values('id', 'name', 'stock')

        return list(low_stock_products)

    def generate_shipping_label(self, shipment_id: int) -> bytes:
        """
        Tạo nhãn vận chuyển với barcode

        Args:
            shipment_id: ID của shipment
            
        Returns:
            bytes: Dữ liệu hình ảnh barcode
        """
        try:
            shipment = Shipment.objects.select_related('order').get(id=shipment_id)
        except Shipment.DoesNotExist:
            return b''

        try:
            # Thử import barcode library
            import barcode
            from barcode.writer import ImageWriter
            from io import BytesIO

            # Tạo Code128 barcode
            code128 = barcode.get_barcode_class('code128')
            barcode_instance = code128(shipment.tracking_code, writer=ImageWriter())

            buffer = BytesIO()
            barcode_instance.write(buffer)

            # TODO: Tạo PDF label đầy đủ với thông tin đơn hàng
            # Hiện tại trả về hình ảnh barcode
            return buffer.getvalue()
        except ImportError:
            # Nếu không có thư viện barcode, trả về empty bytes
            # Log warning để biết cần cài đặt thư viện
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("Thư viện 'python-barcode' chưa được cài đặt. Chạy: pip install python-barcode")
            return b''
