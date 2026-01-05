from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Shipment, ShipmentTracking
from .services.shipping_service import ShippingService


@login_required
def calculate_shipping(request):
    """API: Tính phí vận chuyển"""
    if request.method == 'POST':
        province = request.POST.get('province')
        district = request.POST.get('district')
        ward = request.POST.get('ward')

        # Get cart items weight/dimensions
        from apps.cart.models import CartItem
        cart_items = CartItem.objects.filter(cart__user=request.user)

        items = []
        for item in cart_items:
            items.append({
                'weight': getattr(item.product, 'weight', 500),  # grams
                'quantity': item.quantity,
            })

        address = {
            'province': province,
            'district': district,
            'ward': ward,
        }

        result = ShippingService.calculate_shipping_fee(address, items)
        return JsonResponse(result)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def track_shipment(request, tracking_code):
    """Tracking vận đơn"""
    shipment = get_object_or_404(
        Shipment,
        tracking_code=tracking_code,
        order__user=request.user
    )

    # Sync latest status from carrier
    ShippingService.sync_shipping_status(shipment.id)

    # Get tracking history
    tracking_history = ShipmentTracking.objects.filter(
        shipment=shipment
    ).order_by('-timestamp')

    context = {
        'shipment': shipment,
        'tracking_history': tracking_history,
    }
    return render(request, 'shipping/tracking.html', context)


def get_provinces(request):
    """API: Danh sách tỉnh/thành"""
    provinces = ShippingService.get_provinces()
    return JsonResponse({'provinces': provinces})


def get_districts(request, province_id):
    """API: Danh sách quận/huyện"""
    districts = ShippingService.get_districts(province_id)
    return JsonResponse({'districts': districts})


def get_wards(request, district_id):
    """API: Danh sách phường/xã"""
    wards = ShippingService.get_wards(district_id)
    return JsonResponse({'wards': wards})
