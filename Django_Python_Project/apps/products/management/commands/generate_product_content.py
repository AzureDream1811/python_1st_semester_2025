from django.core.management.base import BaseCommand
from apps.products.models import Product, Category
import json


class Command(BaseCommand):
    help = 'Generate sample descriptions and specifications for products'

    def handle(self, *args, **options):
        products = Product.objects.all()
        updated = 0

        for product in products:
            category_name = product.category.name if product.category else ''
            brand_name = product.brand.name if product.brand else 'ElectroShop'

            # Generate detailed description based on category
            detailed_desc = self.generate_description(product, category_name, brand_name)

            # Generate specifications based on category
            specs = self.generate_specifications(product, category_name, brand_name)

            # Generate highlights
            highlights = self.generate_highlights(product, category_name)

            product.detailed_description = detailed_desc
            product.specifications = specs
            product.highlights = highlights
            product.save()
            updated += 1
            self.stdout.write(f'Updated: {product.name}')

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated} products'))

    def generate_description(self, product, category, brand):
        templates = {
            'Tivi': f'''
<h3>Đặc điểm nổi bật</h3>
<p>{product.name} mang đến trải nghiệm hình ảnh sống động với công nghệ hiển thị tiên tiến. 
Sản phẩm được thiết kế tinh tế, phù hợp với mọi không gian nội thất hiện đại.</p>

<h4>Công nghệ hình ảnh vượt trội</h4>
<ul>
    <li>Độ phân giải cao cho hình ảnh sắc nét đến từng chi tiết</li>
    <li>Công nghệ HDR tái hiện màu sắc chân thực</li>
    <li>Tần số quét cao, mượt mà khi xem phim hành động hay chơi game</li>
</ul>

<h4>Âm thanh sống động</h4>
<ul>
    <li>Hệ thống loa tích hợp công suất lớn</li>
    <li>Công nghệ Dolby Audio cho âm thanh vòm</li>
    <li>Hỗ trợ kết nối soundbar qua HDMI ARC</li>
</ul>

<h4>Tính năng thông minh</h4>
<p>Tích hợp hệ điều hành thông minh với kho ứng dụng phong phú. Dễ dàng truy cập Netflix, YouTube, 
VTV Go và nhiều ứng dụng giải trí khác. Điều khiển bằng giọng nói tiện lợi với trợ lý ảo.</p>

<h4>Thiết kế sang trọng</h4>
<p>Viền mỏng hiện đại, chân đế chắc chắn. Có thể treo tường hoặc đặt bàn linh hoạt. 
Phù hợp với phòng khách, phòng ngủ và phòng làm việc.</p>
''',
            'Điều hòa': f'''
<h3>Đặc điểm nổi bật</h3>
<p>{product.name} là giải pháp làm mát hoàn hảo cho không gian sống của bạn. 
Công nghệ tiết kiệm điện kết hợp khả năng làm lạnh nhanh mang đến sự thoải mái tối ưu.</p>

<h4>Làm lạnh nhanh chóng</h4>
<ul>
    <li>Công nghệ làm lạnh nhanh chỉ trong vài phút</li>
    <li>Luồng gió 3D phân phối đều khắp phòng</li>
    <li>Chế độ ngủ thông minh tự điều chỉnh nhiệt độ</li>
</ul>

<h4>Tiết kiệm điện tối ưu</h4>
<ul>
    <li>Công nghệ Inverter tiết kiệm đến 60% điện năng</li>
    <li>Đạt tiêu chuẩn năng lượng 5 sao</li>
    <li>Chế độ Eco thân thiện môi trường</li>
</ul>

<h4>Lọc không khí hiệu quả</h4>
<p>Bộ lọc đa lớp loại bỏ bụi bẩn, vi khuẩn và các tác nhân gây dị ứng. 
Công nghệ khử mùi giữ không khí trong lành. Chức năng tự làm sạch dàn lạnh tiện lợi.</p>

<h4>Vận hành êm ái</h4>
<p>Độ ồn chỉ từ 19dB, yên tĩnh như trong thư viện. Phù hợp cho phòng ngủ và phòng làm việc.</p>
''',
            'Tủ lạnh': f'''
<h3>Đặc điểm nổi bật</h3>
<p>{product.name} - người bạn đồng hành lý tưởng cho gian bếp hiện đại. 
Dung tích lớn, công nghệ bảo quản tiên tiến giữ thực phẩm tươi ngon lâu hơn.</p>

<h4>Công nghệ bảo quản</h4>
<ul>
    <li>Công nghệ làm lạnh đa chiều</li>
    <li>Ngăn đông mềm giữ thịt cá tươi không cần rã đông</li>
    <li>Ngăn rau quả độ ẩm tối ưu giữ rau xanh tươi đến 7 ngày</li>
</ul>

<h4>Tiết kiệm điện</h4>
<ul>
    <li>Máy nén Inverter vận hành êm ái, bền bỉ</li>
    <li>Tiết kiệm đến 50% điện năng so với tủ lạnh thường</li>
    <li>Công nghệ cảm biến thông minh tự điều chỉnh nhiệt độ</li>
</ul>

<h4>Thiết kế thông minh</h4>
<p>Mặt kính cường lực sang trọng, dễ vệ sinh. Các ngăn có thể điều chỉnh linh hoạt. 
Đèn LED tiết kiệm điện chiếu sáng toàn bộ không gian bên trong.</p>

<h4>Khử mùi kháng khuẩn</h4>
<p>Bộ lọc than hoạt tính khử mùi hiệu quả. Công nghệ kháng khuẩn bảo vệ thực phẩm an toàn.</p>
''',
            'Máy giặt': f'''
<h3>Đặc điểm nổi bật</h3>
<p>{product.name} mang đến giải pháp giặt giũ thông minh cho gia đình bạn. 
Công nghệ giặt sạch sâu kết hợp chế độ tiết kiệm nước và điện.</p>

<h4>Giặt sạch vượt trội</h4>
<ul>
    <li>Công nghệ giặt xoáy loại bỏ vết bẩn cứng đầu</li>
    <li>Giặt nước nóng diệt khuẩn 99.9%</li>
    <li>Nhiều chế độ giặt chuyên biệt: đồ len, đồ thể thao, đồ trẻ em</li>
</ul>

<h4>Tiết kiệm nước & điện</h4>
<ul>
    <li>Cảm biến thông minh tự động điều chỉnh lượng nước</li>
    <li>Motor Inverter tiết kiệm điện, vận hành êm ái</li>
    <li>Chế độ giặt nhanh 15 phút cho quần áo ít bẩn</li>
</ul>

<h4>Bảo vệ quần áo</h4>
<p>Lồng giặt thép không gỉ với các cánh khuấy mềm mại, bảo vệ sợi vải. 
Chế độ giặt nhẹ nhàng cho đồ lụa, len mỏng manh.</p>

<h4>Thiết kế hiện đại</h4>
<p>Bảng điều khiển cảm ứng trực quan. Cửa lồng giặt lớn dễ lấy đồ. 
Khóa trẻ em an toàn.</p>
''',
            'Nồi cơm điện': f'''
<h3>Đặc điểm nổi bật</h3>
<p>{product.name} - nấu cơm ngon như mẹ nấu. Công nghệ nấu tiên tiến cho hạt cơm dẻo thơm, 
đều đặn từ trên xuống dưới.</p>

<h4>Công nghệ nấu</h4>
<ul>
    <li>Công nghệ gia nhiệt 3D nấu đều</li>
    <li>Chế độ nấu thông minh tự động điều chỉnh nhiệt</li>
    <li>Giữ ấm đến 24 giờ không lo cơm khô cứng</li>
</ul>

<h4>Đa chức năng</h4>
<ul>
    <li>Nấu cơm, cháo, xôi, hầm, hấp</li>
    <li>Chế độ nấu nhanh tiết kiệm thời gian</li>
    <li>Hẹn giờ nấu tiện lợi</li>
</ul>

<h4>Lòng nồi cao cấp</h4>
<p>Lòng nồi phủ men ceramic/chống dính cao cấp, dễ vệ sinh. 
Dày dặn, giữ nhiệt tốt, bền với thời gian.</p>

<h4>An toàn sử dụng</h4>
<p>Nắp nồi có van xả áp an toàn. Tay cầm cách nhiệt. Chân đế chống trượt.</p>
''',
            'Bếp từ': f'''
<h3>Đặc điểm nổi bật</h3>
<p>{product.name} mang đến trải nghiệm nấu ăn hiện đại, an toàn và tiết kiệm. 
Công nghệ từ tiên tiến nấu nhanh hơn bếp gas thông thường.</p>

<h4>Hiệu suất cao</h4>
<ul>
    <li>Hiệu suất nhiệt lên đến 90%</li>
    <li>Nấu nhanh hơn bếp gas 50%</li>
    <li>Điều chỉnh nhiệt chính xác theo từng cấp độ</li>
</ul>

<h4>An toàn tuyệt đối</h4>
<ul>
    <li>Mặt kính không nóng khi có nồi</li>
    <li>Tự ngắt khi không có nồi hoặc nồi không phù hợp</li>
    <li>Khóa trẻ em thông minh</li>
</ul>

<h4>Dễ vệ sinh</h4>
<p>Mặt kính phẳng dễ lau chùi. Không có ngọn lửa nên không có bụi than. 
Giữ không gian bếp luôn sạch sẽ.</p>

<h4>Thiết kế sang trọng</h4>
<p>Mặt kính cường lực chịu lực tốt. Bảng điều khiển cảm ứng hiện đại. 
Đồng hồ hẹn giờ tiện lợi.</p>
''',
            'Máy lọc nước': f'''
<h3>Đặc điểm nổi bật</h3>
<p>{product.name} cung cấp nguồn nước tinh khiết, an toàn cho sức khỏe gia đình bạn. 
Công nghệ lọc đa tầng loại bỏ tạp chất, vi khuẩn, giữ lại khoáng chất có lợi.</p>

<h4>Công nghệ lọc</h4>
<ul>
    <li>Màng lọc RO/Nano tinh lọc cấp độ phân tử</li>
    <li>Loại bỏ 99.9% vi khuẩn, virus, kim loại nặng</li>
    <li>Giữ lại khoáng chất thiết yếu cho cơ thể</li>
</ul>

<h4>Tiện lợi sử dụng</h4>
<ul>
    <li>Bình chứa dung tích lớn</li>
    <li>Vòi nước nóng/lạnh tùy chọn</li>
    <li>Đèn báo thay lõi lọc thông minh</li>
</ul>

<h4>Tiết kiệm & bền bỉ</h4>
<p>Lõi lọc sử dụng lâu dài, tiết kiệm chi phí thay thế. 
Vận hành êm ái, tiết kiệm điện năng.</p>

<h4>An toàn vệ sinh</h4>
<p>Chất liệu cao cấp không chứa BPA. Dễ dàng tháo lắp vệ sinh.</p>
''',
        }

        # Find matching template
        for key in templates:
            if key.lower() in category.lower() or key.lower() in product.name.lower():
                return templates[key]

        # Default template
        return f'''
<h3>Giới thiệu sản phẩm</h3>
<p>{product.name} là sản phẩm chất lượng cao từ thương hiệu {brand}. 
Sản phẩm được thiết kế với công nghệ tiên tiến, đáp ứng nhu cầu sử dụng hàng ngày của gia đình.</p>

<h4>Tính năng nổi bật</h4>
<ul>
    <li>Chất lượng đảm bảo, thương hiệu uy tín</li>
    <li>Thiết kế hiện đại, phù hợp mọi không gian</li>
    <li>Tiết kiệm điện năng</li>
    <li>Dễ sử dụng và bảo trì</li>
</ul>

<h4>Chế độ bảo hành</h4>
<p>Sản phẩm được bảo hành chính hãng. Hỗ trợ kỹ thuật 24/7.</p>
'''

    def generate_specifications(self, product, category, brand):
        base_specs = {
            'Thương hiệu': brand,
            'Model': product.sku,
            'Xuất xứ': 'Chính hãng',
            'Bảo hành': '24 tháng',
        }

        category_specs = {
            'Tivi': {
                'Kích thước màn hình': '55 inch',
                'Độ phân giải': '4K Ultra HD (3840 x 2160)',
                'Tần số quét': '120Hz',
                'Công nghệ hình ảnh': 'HDR10+, Dolby Vision',
                'Hệ điều hành': 'Smart TV',
                'Kết nối': 'HDMI x3, USB x2, Wifi, Bluetooth 5.0',
                'Công suất loa': '20W',
                'Kích thước (DxRxC)': '1232 x 715 x 60 mm',
                'Trọng lượng': '14.5 kg',
            },
            'Điều hòa': {
                'Công suất làm lạnh': '9000 BTU',
                'Phạm vi làm lạnh': '15 - 20 m²',
                'Công nghệ Inverter': 'Có',
                'Hiệu suất năng lượng': '5 sao',
                'Công suất tiêu thụ': '750W',
                'Độ ồn': '19 - 38 dB',
                'Gas làm lạnh': 'R32',
                'Chế độ hoạt động': 'Làm lạnh, Sưởi ấm, Hút ẩm, Quạt gió',
                'Bộ lọc': 'Kháng khuẩn, Khử mùi',
            },
            'Tủ lạnh': {
                'Dung tích tổng': '300 lít',
                'Dung tích ngăn lạnh': '200 lít',
                'Dung tích ngăn đông': '100 lít',
                'Công nghệ Inverter': 'Có',
                'Công nghệ làm lạnh': 'Làm lạnh đa chiều',
                'Công suất tiêu thụ': '150W/ngày',
                'Số cửa': '2 cửa',
                'Kích thước (DxRxC)': '600 x 700 x 1700 mm',
                'Trọng lượng': '65 kg',
            },
            'Máy giặt': {
                'Khối lượng giặt': '9 kg',
                'Tốc độ quay vắt': '1200 vòng/phút',
                'Công nghệ giặt': 'Giặt hơi nước, Giặt nước nóng',
                'Số chương trình giặt': '16 chương trình',
                'Motor Inverter': 'Có',
                'Công suất tiêu thụ': '2000W',
                'Tiêu thụ nước': '45 lít/chu kỳ',
                'Kích thước (DxRxC)': '600 x 560 x 850 mm',
                'Trọng lượng': '62 kg',
            },
            'Nồi cơm': {
                'Dung tích': '1.8 lít (1kg gạo)',
                'Công suất': '860W',
                'Lòng nồi': 'Phủ men ceramic chống dính',
                'Chức năng': 'Nấu cơm, Cháo, Xôi, Hấp, Hầm',
                'Giữ ấm': 'Tự động đến 24 giờ',
                'Hẹn giờ': 'Có (lên đến 24 giờ)',
                'Điện áp': '220V - 50Hz',
                'Trọng lượng': '4.2 kg',
            },
            'Bếp từ': {
                'Số bếp': '2 bếp',
                'Công suất tổng': '4000W',
                'Mặt kính': 'Kính cường lực Schott Ceran',
                'Điều khiển': 'Cảm ứng',
                'Số mức nhiệt': '9 mức',
                'Hẹn giờ': 'Có (lên đến 180 phút)',
                'An toàn': 'Khóa trẻ em, Tự ngắt, Cảnh báo quá nhiệt',
                'Kích thước': '730 x 420 x 60 mm',
            },
            'Máy lọc nước': {
                'Công nghệ lọc': 'RO 10 cấp lọc',
                'Lưu lượng lọc': '10 lít/giờ',
                'Dung tích bình chứa': '10 lít',
                'Tổng chất rắn hòa tan (TDS)': '< 50 ppm',
                'Công suất': '65W',
                'Vòi nước': 'Nóng - Lạnh - Thường',
                'Lõi lọc': '10 lõi',
                'Thời gian thay lõi': '6-12 tháng tùy lõi',
            },
        }

        # Find matching specs
        for key in category_specs:
            if key.lower() in category.lower() or key.lower() in product.name.lower():
                return {**base_specs, **category_specs[key]}

        return base_specs

    def generate_highlights(self, product, category):
        category_highlights = {
            'Tivi': [
                'Màn hình 4K sắc nét',
                'Công nghệ HDR rực rỡ',
                'Smart TV kho ứng dụng phong phú',
                'Điều khiển giọng nói thông minh',
            ],
            'Điều hòa': [
                'Inverter tiết kiệm điện',
                'Làm lạnh nhanh trong 30 giây',
                'Vận hành siêu êm 19dB',
                'Bộ lọc kháng khuẩn',
            ],
            'Tủ lạnh': [
                'Inverter tiết kiệm điện',
                'Làm lạnh đa chiều',
                'Ngăn đông mềm tiện lợi',
                'Kháng khuẩn khử mùi',
            ],
            'Máy giặt': [
                'Motor Inverter bền bỉ 10 năm',
                'Giặt hơi nước diệt khuẩn',
                'Tiết kiệm nước và điện',
                'Nhiều chế độ giặt chuyên biệt',
            ],
            'Nồi cơm': [
                'Nấu cơm dẻo thơm đều',
                'Đa chức năng: cháo, xôi, hấp',
                'Giữ ấm 24 giờ',
                'Lòng nồi cao cấp chống dính',
            ],
            'Bếp từ': [
                'Mặt kính cường lực cao cấp',
                'Nấu nhanh tiết kiệm điện',
                'An toàn tuyệt đối',
                'Dễ vệ sinh sạch sẽ',
            ],
        }

        for key in category_highlights:
            if key.lower() in category.lower() or key.lower() in product.name.lower():
                return category_highlights[key]

        return ['Chất lượng đảm bảo', 'Bảo hành chính hãng', 'Tiết kiệm điện', 'Thiết kế hiện đại']
