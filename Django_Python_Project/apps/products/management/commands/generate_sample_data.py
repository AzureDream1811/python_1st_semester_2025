import random
import json
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import Category, Brand, Product


class Command(BaseCommand):
    help = 'Tạo dữ liệu mẫu chi tiết: danh mục, thương hiệu và 200+ sản phẩm đồ điện gia dụng với thông số kỹ thuật thực tế'

    CATEGORIES = [
        {
            'name': 'Tivi',
            'description': 'Tivi LED, OLED, QLED, Smart TV các kích thước từ 32 inch đến 85 inch. Công nghệ hình ảnh tiên tiến, kết nối thông minh, phù hợp mọi không gian.'
        },
        {
            'name': 'Tủ lạnh',
            'description': 'Tủ lạnh Inverter tiết kiệm điện, từ tủ mini đến Side by Side. Công nghệ làm lạnh đa chiều, khử mùi kháng khuẩn, bảo quản thực phẩm tươi lâu.'
        },
        {
            'name': 'Máy giặt',
            'description': 'Máy giặt cửa trước, cửa trên, máy sấy quần áo. Motor Inverter bền bỉ, giặt hơi nước diệt khuẩn, tiết kiệm nước và điện.'
        },
        {
            'name': 'Điều hòa',
            'description': 'Điều hòa Inverter 1 chiều, 2 chiều tiết kiệm điện. Làm lạnh nhanh, vận hành êm ái, lọc không khí kháng khuẩn.'
        },
        {
            'name': 'Máy lọc không khí',
            'description': 'Máy lọc không khí cao cấp, lọc bụi mịn PM2.5, diệt khuẩn virus, khử mùi hiệu quả. Phù hợp phòng ngủ, phòng khách.'
        },
        {
            'name': 'Máy hút bụi',
            'description': 'Máy hút bụi cầm tay không dây, robot hút bụi lau nhà thông minh. Hút mạnh, pin trâu, kết nối App điều khiển.'
        },
        {
            'name': 'Lò vi sóng',
            'description': 'Lò vi sóng điện tử, lò nướng đa năng, nồi chiên không dầu. Nhiều chế độ nấu, tiết kiệm thời gian, an toàn sức khỏe.'
        },
        {
            'name': 'Bếp điện',
            'description': 'Bếp từ, bếp hồng ngoại Inverter tiết kiệm điện. Mặt kính cường lực, an toàn tuyệt đối, dễ vệ sinh.'
        },
        {
            'name': 'Máy xay',
            'description': 'Máy xay sinh tố công suất cao, máy ép chậm giữ vitamin, máy làm sữa hạt. Cối thủy tinh an toàn, dễ vệ sinh.'
        },
        {
            'name': 'Nồi cơm điện',
            'description': 'Nồi cơm điện tử cao tần, nồi áp suất điện, nồi đa năng. Nấu cơm dẻo thơm, đa chức năng, giữ ấm 24h.'
        },
        {
            'name': 'Ấm siêu tốc',
            'description': 'Ấm siêu tốc inox 304, bình thủy điện, ấm đa nhiệt độ. Đun sôi nhanh, giữ nóng lâu, an toàn sử dụng.'
        },
        {
            'name': 'Quạt điện',
            'description': 'Quạt đứng, quạt treo tường, quạt điều hòa hơi nước, quạt tháp không cánh. Gió mạnh êm ái, tiết kiệm điện.'
        },
        {
            'name': 'Máy lọc nước',
            'description': 'Máy lọc nước RO, Nano cao cấp. Lọc sạch 99.9% tạp chất, giữ khoáng chất có lợi, nước tinh khiết an toàn.'
        },
        {
            'name': 'Máy sấy tóc',
            'description': 'Máy sấy tóc ion âm, máy uốn tóc, máy duỗi tóc. Bảo vệ tóc khỏi nhiệt, tạo kiểu nhanh chóng.'
        },
        {
            'name': 'Bàn ủi',
            'description': 'Bàn ủi hơi nước, bàn ủi đứng, bàn ủi cầm tay. Mặt đế chống dính, phun sương mạnh, ủi phẳng nhanh.'
        },
    ]

    BRANDS = [
        {'name': 'Samsung',
         'description': 'Thương hiệu điện tử số 1 Hàn Quốc, nổi tiếng với công nghệ tiên tiến và thiết kế sang trọng. Bảo hành uy tín toàn cầu.'},
        {'name': 'LG',
         'description': 'Thương hiệu điện tử cao cấp Hàn Quốc, đi đầu trong công nghệ OLED và Inverter. Sản phẩm bền bỉ, tiết kiệm điện.'},
        {'name': 'Sony',
         'description': 'Thương hiệu điện tử Nhật Bản hàng đầu thế giới, nổi tiếng với chất lượng hình ảnh và âm thanh vượt trội.'},
        {'name': 'Panasonic',
         'description': 'Thương hiệu Nhật Bản uy tín hơn 100 năm, chuyên về thiết bị điện gia dụng chất lượng cao và bền bỉ.'},
        {'name': 'Toshiba',
         'description': 'Thương hiệu Nhật Bản lâu đời với công nghệ tiên tiến, sản phẩm đa dạng từ TV đến thiết bị gia dụng.'},
        {'name': 'Sharp',
         'description': 'Thương hiệu Nhật Bản nổi tiếng với công nghệ Plasmacluster Ion độc quyền, sản phẩm thân thiện môi trường.'},
        {'name': 'Electrolux',
         'description': 'Thương hiệu Thụy Điển hàng đầu châu Âu, thiết kế tinh tế Bắc Âu, công nghệ tiết kiệm năng lượng.'},
        {'name': 'Philips',
         'description': 'Thương hiệu Hà Lan với lịch sử hơn 130 năm, chuyên về thiết bị chăm sóc sức khỏe và gia dụng cao cấp.'},
        {'name': 'Xiaomi',
         'description': 'Thương hiệu công nghệ Trung Quốc với giá thành hợp lý, tích hợp IoT thông minh, thiết kế trẻ trung.'},
        {'name': 'Midea',
         'description': 'Thương hiệu thiết bị gia dụng lớn nhất Trung Quốc, đa dạng sản phẩm với giá cả cạnh tranh.'},
        {'name': 'Aqua',
         'description': 'Thương hiệu Việt Nam - Nhật Bản, kết hợp công nghệ Nhật với giá Việt, phù hợp gia đình Việt.'},
        {'name': 'Daikin',
         'description': 'Thương hiệu điều hòa số 1 Nhật Bản và thế giới, công nghệ Inverter tiên tiến, tiết kiệm điện vượt trội.'},
        {'name': 'Hitachi',
         'description': 'Thương hiệu Nhật Bản với công nghệ sản xuất tiên tiến, máy nén Inverter bền bỉ 10 năm.'},
        {'name': 'Bosch',
         'description': 'Thương hiệu Đức nổi tiếng với chất lượng German Engineering, bền bỉ và hiệu suất cao.'},
        {'name': 'Sunhouse',
         'description': 'Thương hiệu Việt Nam với sản phẩm đa dạng, giá thành phù hợp, bảo hành tận nơi toàn quốc.'},
        {'name': 'Casper',
         'description': 'Thương hiệu Thái Lan chuyên về điều hòa và tủ lạnh, công nghệ hiện đại với giá thành hợp lý.'},
        {'name': 'TCL',
         'description': 'Thương hiệu TV lớn thứ 2 thế giới từ Trung Quốc, công nghệ QLED và Mini LED tiên tiến.'},
        {'name': 'Kangaroo',
         'description': 'Thương hiệu Việt Nam chuyên về máy lọc nước, được tin dùng bởi hàng triệu gia đình Việt.'},
        {'name': 'Dyson',
         'description': 'Thương hiệu Anh Quốc cao cấp, nổi tiếng với máy hút bụi và máy sấy tóc công nghệ số.'},
        {'name': 'Tefal',
         'description': 'Thương hiệu Pháp chuyên về bếp và dụng cụ nấu ăn, chống dính hàng đầu thế giới.'},
        {'name': 'Cuckoo', 'description': 'Thương hiệu Hàn Quốc chuyên về nồi cơm điện cao cấp và máy lọc nước.'},
        {'name': 'Hafele', 'description': 'Thương hiệu Đức chuyên về thiết bị nhà bếp cao cấp, bếp từ và lò nướng.'},
        {'name': 'Dreame',
         'description': 'Thương hiệu Trung Quốc chuyên về robot hút bụi và máy hút bụi không dây thông minh.'},
        {'name': 'Roborock',
         'description': 'Thương hiệu robot hút bụi cao cấp từ Trung Quốc, công nghệ LiDAR tiên tiến.'},
        {'name': 'Karofi', 'description': 'Thương hiệu Việt Nam chuyên về máy lọc nước RO, được tin dùng nhiều năm.'},
        {'name': 'Bluestone',
         'description': 'Thương hiệu Việt Nam chuyên về ấm siêu tốc, nồi cơm điện và thiết bị nhà bếp.'},
        {'name': 'Lock&Lock',
         'description': 'Thương hiệu Hàn Quốc chuyên về đồ gia dụng, bình thủy và hộp đựng thực phẩm.'},
        {'name': 'Korihome', 'description': 'Thương hiệu Hàn Quốc chuyên về máy lọc nước nóng lạnh cao cấp.'},
    ]

    BRAND_CATEGORY_MAPPING = {
        'Tivi': ['Samsung', 'LG', 'Sony', 'Panasonic', 'Toshiba', 'Sharp', 'TCL', 'Xiaomi'],
        'Tủ lạnh': ['Samsung', 'LG', 'Panasonic', 'Toshiba', 'Sharp', 'Electrolux', 'Hitachi', 'Aqua', 'Casper',
                    'Midea'],
        'Máy giặt': ['Samsung', 'LG', 'Panasonic', 'Toshiba', 'Electrolux', 'Aqua', 'Sharp', 'Bosch', 'Hitachi'],
        'Điều hòa': ['Daikin', 'Panasonic', 'LG', 'Samsung', 'Toshiba', 'Sharp', 'Mitsubishi Heavy', 'Casper', 'Midea',
                     'Aqua'],
        'Máy lọc không khí': ['Sharp', 'Panasonic', 'Xiaomi', 'Philips', 'Samsung', 'LG', 'Hitachi', 'Daikin'],
        'Máy hút bụi': ['Dyson', 'Xiaomi', 'Dreame', 'Roborock', 'Philips', 'Panasonic', 'Samsung', 'LG', 'Electrolux',
                        'Bosch'],
        'Lò vi sóng': ['Panasonic', 'Sharp', 'Samsung', 'LG', 'Toshiba', 'Electrolux', 'Philips', 'Sunhouse', 'Aqua'],
        'Bếp điện': ['Bosch', 'Hafele', 'Panasonic', 'Electrolux', 'Sunhouse', 'Tefal', 'Philips', 'Midea', 'Teka'],
        'Máy xay': ['Philips', 'Panasonic', 'Tefal', 'Sunhouse', 'Sharp', 'Electrolux', 'Bosch', 'Braun'],
        'Nồi cơm điện': ['Cuckoo', 'Panasonic', 'Toshiba', 'Sharp', 'Philips', 'Sunhouse', 'Bluestone', 'Aqua',
                         'Midea'],
        'Ấm siêu tốc': ['Philips', 'Panasonic', 'Sunhouse', 'Bluestone', 'Lock&Lock', 'Electrolux', 'Tefal', 'Sharp'],
        'Quạt điện': ['Panasonic', 'Mitsubishi', 'Toshiba', 'Sharp', 'Sunhouse', 'Midea', 'Aqua', 'Senko', 'Asia'],
        'Máy lọc nước': ['Kangaroo', 'Karofi', 'Korihome', 'Cuckoo', 'Aqua', 'Panasonic', 'Sharp', 'Sunhouse'],
        'Máy sấy tóc': ['Dyson', 'Philips', 'Panasonic', 'Tescom', 'Braun', 'Sunhouse', 'Xiaomi'],
        'Bàn ủi': ['Philips', 'Panasonic', 'Tefal', 'Electrolux', 'Sunhouse', 'Bosch', 'Braun'],
    }

    DETAILED_PRODUCTS = {
        'Tivi': [
            {
                'name_template': 'Smart Tivi 4K {brand} {size} inch',
                'description': 'Smart Tivi 4K với độ phân giải Ultra HD 3840x2160, công nghệ HDR10+ cho hình ảnh sống động. Hệ điều hành thông minh với kho ứng dụng phong phú, điều khiển giọng nói tiện lợi. Thiết kế viền mỏng sang trọng, phù hợp mọi không gian.',
                'sizes': [43, 50, 55, 65, 75],
                'specs_template': {
                    'Kích thước màn hình': '{size} inch',
                    'Độ phân giải': '4K Ultra HD (3840 x 2160)',
                    'Tần số quét': '60Hz',
                    'Công nghệ hình ảnh': 'HDR10+, HLG',
                    'Hệ điều hành': 'Smart TV',
                    'Loa': '20W (2 x 10W)',
                    'Cổng kết nối': 'HDMI x3, USB x2, AV, LAN, Wifi, Bluetooth',
                    'Điều khiển': 'Remote thông minh, Giọng nói',
                }
            },
            {
                'name_template': 'Tivi OLED {brand} {size} inch 4K',
                'description': 'Tivi OLED cao cấp với công nghệ điểm ảnh tự phát sáng, màu đen tuyệt đối, độ tương phản vô hạn. Góc nhìn 178 độ không đổi màu, thời gian phản hồi 0.1ms hoàn hảo cho gaming. Thiết kế siêu mỏng như tranh treo tường.',
                'sizes': [55, 65, 77, 83],
                'specs_template': {
                    'Kích thước màn hình': '{size} inch',
                    'Độ phân giải': '4K Ultra HD (3840 x 2160)',
                    'Công nghệ tấm nền': 'OLED',
                    'Tần số quét': '120Hz',
                    'Công nghệ hình ảnh': 'Dolby Vision IQ, HDR10, HLG',
                    'Hệ thống loa': '40W Dolby Atmos',
                    'Góc nhìn': '178 độ',
                    'Thời gian phản hồi': '0.1ms',
                }
            },
            {
                'name_template': 'Tivi QLED {brand} {size} inch 4K',
                'description': 'Tivi QLED với công nghệ Quantum Dot, hiển thị 1 tỷ màu sắc chính xác. Độ sáng cao 1000 nits, xem tốt cả trong ánh sáng mạnh. Công nghệ chống phản chiếu, bảo vệ mắt khi xem lâu.',
                'sizes': [50, 55, 65, 75, 85],
                'specs_template': {
                    'Kích thước màn hình': '{size} inch',
                    'Độ phân giải': '4K Ultra HD (3840 x 2160)',
                    'Công nghệ tấm nền': 'QLED Quantum Dot',
                    'Độ sáng': '1000 nits',
                    'Tần số quét': '120Hz',
                    'Công nghệ hình ảnh': 'Quantum HDR, HDR10+',
                    'Màu sắc': '100% Color Volume',
                    'Loa': '60W Object Tracking Sound',
                }
            },
            {
                'name_template': 'Tivi LED {brand} {size} inch Full HD',
                'description': 'Tivi LED Full HD kinh tế với hình ảnh sắc nét, màu sắc tự nhiên. Thiết kế mỏng nhẹ, tiết kiệm điện. Phù hợp phòng ngủ, phòng bếp hoặc phòng trọ.',
                'sizes': [32, 40, 43],
                'specs_template': {
                    'Kích thước màn hình': '{size} inch',
                    'Độ phân giải': 'Full HD (1920 x 1080)',
                    'Tấm nền': 'LED',
                    'Tần số quét': '60Hz',
                    'Loa': '10W (2 x 5W)',
                    'Cổng kết nối': 'HDMI x2, USB x1, AV',
                    'Công suất tiêu thụ': '45W',
                }
            },
            {
                'name_template': 'Smart Tivi 8K {brand} {size} inch Neo QLED',
                'description': 'Smart Tivi 8K đỉnh cao công nghệ với độ phân giải 7680x4320, gấp 4 lần 4K. AI Upscaling nâng cấp mọi nội dung lên gần 8K. Âm thanh vòm 3D theo chuyển động hình ảnh.',
                'sizes': [65, 75, 85],
                'specs_template': {
                    'Kích thước màn hình': '{size} inch',
                    'Độ phân giải': '8K (7680 x 4320)',
                    'Công nghệ tấm nền': 'Neo QLED Mini LED',
                    'Tần số quét': '120Hz native, 240Hz interpolation',
                    'Công nghệ hình ảnh': 'AI Upscaling, Neural Quantum Processor',
                    'Độ sáng': '2000 nits',
                    'Loa': '90W Object Tracking Sound Pro',
                    'Kết nối': 'HDMI 2.1 x4, USB x3, Wifi 6E, Bluetooth 5.2',
                }
            },
        ],
        'Tủ lạnh': [
            {
                'name_template': 'Tủ lạnh Inverter {brand} {capacity} lít',
                'description': 'Tủ lạnh Inverter tiết kiệm điện với công nghệ làm lạnh đa chiều, giữ thực phẩm tươi ngon lâu hơn. Máy nén Digital Inverter vận hành êm ái, bền bỉ 10 năm. Ngăn đông mềm -1°C tiện lợi.',
                'capacities': [256, 280, 320, 360, 400],
                'specs_template': {
                    'Dung tích tổng': '{capacity} lít',
                    'Dung tích sử dụng': '{usable} lít',
                    'Số cửa': '2 cửa',
                    'Công nghệ Inverter': 'Digital Inverter',
                    'Công nghệ làm lạnh': 'Làm lạnh đa chiều, Twin Cooling',
                    'Ngăn đông mềm': 'Optimal Fresh Zone (-1°C)',
                    'Khử mùi': 'Deodorizer than hoạt tính',
                    'Công suất tiêu thụ': '~1.2 kWh/ngày',
                    'Kích thước (RxSxC)': '60 x 65 x 170 cm',
                }
            },
            {
                'name_template': 'Tủ lạnh Side by Side {brand} {capacity} lít',
                'description': 'Tủ lạnh Side by Side sang trọng với dung tích siêu lớn, cửa kính cường lực. Ngăn lấy nước và đá ngoài tiện lợi. Công nghệ làm lạnh vòng cung, nhiệt độ đồng đều mọi ngóc ngách.',
                'capacities': [580, 620, 680, 750],
                'specs_template': {
                    'Dung tích tổng': '{capacity} lít',
                    'Kiểu tủ': 'Side by Side 2 cánh',
                    'Công nghệ Inverter': 'Linear Cooling Inverter',
                    'Lấy nước/đá ngoài': 'Có (Water & Ice Dispenser)',
                    'Công nghệ làm lạnh': 'Door Cooling+, Làm lạnh vòng cung',
                    'Ngăn chuyển đổi': 'Convertible Zone (-23°C đến 5°C)',
                    'Màn hình điều khiển': 'LED Touch ngoài cửa',
                    'Công suất tiêu thụ': '~1.8 kWh/ngày',
                    'Kích thước (RxSxC)': '91 x 72 x 178 cm',
                }
            },
            {
                'name_template': 'Tủ lạnh Mini {brand} {capacity} lít',
                'description': 'Tủ lạnh mini nhỏ gọn phù hợp phòng trọ, khách sạn, văn phòng. Tiết kiệm điện, vận hành êm ái. Ngăn đá riêng biệt, đủ dùng cho 1-2 người.',
                'capacities': [90, 100, 120, 150],
                'specs_template': {
                    'Dung tích tổng': '{capacity} lít',
                    'Kiểu tủ': 'Tủ mini 1 cửa',
                    'Ngăn đá': 'Ngăn đá trên riêng biệt',
                    'Công nghệ làm lạnh': 'Trực tiếp',
                    'Điều chỉnh nhiệt': 'Núm vặn 7 mức',
                    'Công suất tiêu thụ': '~0.6 kWh/ngày',
                    'Độ ồn': '38 dB',
                    'Kích thước (RxSxC)': '48 x 45 x 85 cm',
                }
            },
            {
                'name_template': 'Tủ lạnh 3 cửa {brand} {capacity} lít French Door',
                'description': 'Tủ lạnh French Door 3 cửa thiết kế hiện đại, ngăn rau quả rộng rãi ở dưới. Ngăn đông kéo riêng tiện lợi, công nghệ cấp đông mềm giữ thịt cá tươi ngon.',
                'capacities': [450, 520, 580],
                'specs_template': {
                    'Dung tích tổng': '{capacity} lít',
                    'Kiểu tủ': 'French Door 3 cửa',
                    'Công nghệ Inverter': 'Có',
                    'Ngăn cấp đông mềm': 'Prime Fresh -3°C',
                    'Công nghệ làm lạnh': 'Panorama làm lạnh 360°',
                    'Ngăn rau quả': 'Fresh Safe giữ ẩm tối ưu',
                    'Tiết kiệm điện': 'Nhãn năng lượng A++',
                    'Công suất tiêu thụ': '~1.5 kWh/ngày',
                }
            },
        ],
        'Máy giặt': [
            {
                'name_template': 'Máy giặt cửa trước {brand} Inverter {capacity} kg',
                'description': 'Máy giặt cửa trước với motor Inverter bền bỉ bảo hành 10 năm. Công nghệ giặt hơi nước diệt 99.9% vi khuẩn. Lồng giặt thép không gỉ, nhiều chế độ giặt chuyên biệt.',
                'capacities': [8, 9, 10, 11, 12],
                'specs_template': {
                    'Khối lượng giặt': '{capacity} kg',
                    'Kiểu máy': 'Cửa trước (Front Load)',
                    'Motor': 'Inverter Direct Drive (Bảo hành 10 năm)',
                    'Tốc độ vắt': '1200 vòng/phút',
                    'Công nghệ giặt': 'Steam Wash, TurboWash, 6 Motion DD',
                    'Số chương trình': '14 chương trình',
                    'Tiêu thụ điện': '~0.8 kWh/chu kỳ',
                    'Tiêu thụ nước': '45 lít/chu kỳ',
                    'Kích thước (RxSxC)': '60 x 56 x 85 cm',
                }
            },
            {
                'name_template': 'Máy giặt cửa trên {brand} {capacity} kg',
                'description': 'Máy giặt cửa trên tiện lợi, dễ cho đồ vào khi đang giặt. Mâm giặt sóng siêu âm giặt sạch nhẹ nhàng. Chế độ vệ sinh lồng giặt tự động.',
                'capacities': [7, 8, 9, 10, 12],
                'specs_template': {
                    'Khối lượng giặt': '{capacity} kg',
                    'Kiểu máy': 'Cửa trên (Top Load)',
                    'Motor': 'Inverter',
                    'Công nghệ giặt': 'Mâm giặt Sóng siêu âm, Xoáy nước',
                    'Tốc độ vắt': '700 vòng/phút',
                    'Số chương trình': '10 chương trình',
                    'Chức năng thêm đồ': 'Có thể thêm đồ khi đang giặt',
                    'Tiêu thụ nước': '120 lít/chu kỳ',
                    'Kích thước (RxSxC)': '55 x 56 x 95 cm',
                }
            },
            {
                'name_template': 'Máy giặt sấy {brand} {capacity} kg 2 trong 1',
                'description': 'Máy giặt tích hợp sấy tiện lợi trong 1 thiết bị. Sấy hơi nước không làm hư vải, giảm nếp nhăn. Phù hợp không gian nhỏ, tiết kiệm thời gian phơi.',
                'capacities': [9, 10, 12, 14],
                'specs_template': {
                    'Khối lượng giặt': '{capacity} kg',
                    'Khối lượng sấy': '{dry_capacity} kg',
                    'Kiểu máy': 'Washer Dryer Combo',
                    'Motor': 'AI Direct Drive Inverter',
                    'Công nghệ sấy': 'Hybrid Heat Pump, Sấy hơi nước',
                    'Tốc độ vắt': '1400 vòng/phút',
                    'Số chương trình': '16 chương trình giặt, 6 chương trình sấy',
                    'Điều khiển': 'WiFi, AI ThinQ App',
                    'Tiêu thụ điện sấy': '~2.5 kWh/chu kỳ sấy',
                }
            },
            {
                'name_template': 'Máy sấy quần áo {brand} {capacity} kg',
                'description': 'Máy sấy riêng biệt với công nghệ bơm nhiệt tiết kiệm điện. Cảm biến độ ẩm tự ngắt khi khô, bảo vệ vải. Bộ lọc xơ vải dễ vệ sinh.',
                'capacities': [7, 8, 9, 10],
                'specs_template': {
                    'Khối lượng sấy': '{capacity} kg',
                    'Công nghệ sấy': 'Heat Pump (Bơm nhiệt)',
                    'Cảm biến': 'Cảm biến độ ẩm tự động ngắt',
                    'Số chương trình sấy': '14 chương trình',
                    'Tiêu thụ điện': '~1.5 kWh/chu kỳ',
                    'Độ ồn': '65 dB',
                    'Bình chứa nước': '4 lít (tự động báo đầy)',
                    'Kích thước (RxSxC)': '60 x 60 x 85 cm',
                }
            },
        ],
        'Điều hòa': [
            {
                'name_template': 'Điều hòa Inverter {brand} {btu} BTU',
                'description': 'Điều hòa Inverter 1 chiều tiết kiệm điện lên đến 60%. Làm lạnh nhanh trong 30 giây, luồng gió 3D mát đều khắp phòng. Vận hành siêu êm chỉ 19dB, phù hợp phòng ngủ.',
                'btus': [9000, 12000, 18000, 24000],
                'specs_template': {
                    'Công suất lạnh': '{btu} BTU/h',
                    'Phạm vi làm lạnh': '{area} m²',
                    'Công nghệ': 'Inverter tiết kiệm điện',
                    'Loại điều hòa': '1 chiều (Chỉ làm lạnh)',
                    'Gas làm lạnh': 'R32 (Thân thiện môi trường)',
                    'Độ ồn dàn lạnh': '19 - 43 dB',
                    'Hiệu suất EER': '3.8 - 4.2',
                    'Chế độ': 'Cool, Dry, Fan, Sleep, Turbo',
                    'Bộ lọc': 'Kháng khuẩn, Khử mùi, Lọc bụi mịn',
                    'Điều khiển': 'Remote + WiFi App',
                }
            },
            {
                'name_template': 'Điều hòa 2 chiều {brand} {btu} BTU Inverter',
                'description': 'Điều hòa 2 chiều vừa làm lạnh mùa hè vừa sưởi ấm mùa đông. Công nghệ Inverter tiết kiệm điện, ổn định nhiệt độ. Bộ lọc Plasma diệt khuẩn, khử mùi hiệu quả.',
                'btus': [9000, 12000, 18000, 24000],
                'specs_template': {
                    'Công suất lạnh': '{btu} BTU/h',
                    'Công suất sưởi': '{heat_btu} BTU/h',
                    'Phạm vi': '{area} m²',
                    'Công nghệ': 'Inverter',
                    'Loại điều hòa': '2 chiều (Lạnh + Sưởi)',
                    'Gas làm lạnh': 'R32',
                    'Chế độ sưởi': 'Sưởi ấm đến 30°C',
                    'Bộ lọc': 'Plasma Ion, Vitamin C, Kháng khuẩn',
                    'Tính năng thông minh': 'Cảm biến người, Tự làm sạch',
                }
            },
            {
                'name_template': 'Điều hòa tủ đứng {brand} {btu} BTU',
                'description': 'Điều hòa tủ đứng công suất lớn phù hợp phòng khách rộng, showroom, văn phòng. Luồng gió mạnh phủ rộng, làm mát nhanh không gian lớn. Thiết kế sang trọng như tủ trang trí.',
                'btus': [24000, 36000, 48000],
                'specs_template': {
                    'Công suất lạnh': '{btu} BTU/h',
                    'Phạm vi': '{area} m²',
                    'Kiểu máy': 'Tủ đứng (Floor Standing)',
                    'Công nghệ': 'Inverter',
                    'Luồng gió': '4 hướng, phủ rộng 15m',
                    'Độ ồn': '40 - 52 dB',
                    'Điện nguồn': '220V/380V - 50Hz',
                    'Kích thước': '50 x 35 x 180 cm',
                }
            },
        ],
        'Máy lọc không khí': [
            {
                'name_template': 'Máy lọc không khí {brand} phòng {area}m²',
                'description': 'Máy lọc không khí với bộ lọc HEPA H13 lọc 99.97% bụi mịn PM2.5, phấn hoa, vi khuẩn. Cảm biến chất lượng không khí tự động điều chỉnh tốc độ. Vận hành êm ái ban đêm.',
                'areas': [20, 30, 40, 50, 60],
                'specs_template': {
                    'Diện tích phòng': 'Đến {area}m²',
                    'Bộ lọc': 'HEPA H13 + Carbon + Pre-filter',
                    'Lọc bụi mịn': 'PM2.5, PM0.3 (99.97%)',
                    'CADR (Lưu lượng)': '{cadr} m³/h',
                    'Cảm biến': 'Bụi PM2.5, Chất lượng không khí',
                    'Độ ồn': '20 - 50 dB',
                    'Chế độ': 'Auto, Sleep, Turbo',
                    'Điều khiển': 'Remote + App WiFi',
                    'Tuổi thọ lọc': '~12 tháng',
                }
            },
            {
                'name_template': 'Máy lọc không khí {brand} diệt khuẩn Ion',
                'description': 'Máy lọc không khí tích hợp công nghệ Plasmacluster Ion diệt 99.9% virus, vi khuẩn trong không khí. Khử mùi hiệu quả thuốc lá, nấu ăn. Nhỏ gọn đặt bàn hoặc phòng nhỏ.',
                'areas': [15, 20, 25],
                'specs_template': {
                    'Diện tích phòng': 'Đến {area}m²',
                    'Công nghệ': 'Plasmacluster Ion / Nanoe',
                    'Diệt khuẩn': '99.9% virus, vi khuẩn',
                    'Khử mùi': 'Thuốc lá, thức ăn, thú cưng',
                    'Bộ lọc': 'HEPA + Deodorizing',
                    'Độ ồn': '18 - 44 dB',
                    'Thiết kế': 'Nhỏ gọn để bàn',
                    'Công suất': '25W',
                }
            },
        ],
        'Máy hút bụi': [
            {
                'name_template': 'Robot hút bụi lau nhà {brand} thông minh',
                'description': 'Robot hút bụi lau nhà 2 trong 1 với công nghệ LiDAR lập bản đồ chính xác. Tự động sạc và tiếp tục dọn, lực hút 4000Pa. Điều khiển qua App, hẹn lịch dọn tự động.',
                'specs_template': {
                    'Công nghệ định vị': 'LiDAR Navigation',
                    'Lực hút': '4000 Pa',
                    'Dung tích hộp bụi': '470ml',
                    'Dung tích bình nước': '300ml',
                    'Thời gian hoạt động': '180 phút',
                    'Thời gian sạc': '4 giờ',
                    'Điều khiển': 'App Mi Home / Google Home / Alexa',
                    'Chế độ': 'Hút, Hút + Lau, Chỉ lau',
                    'Cảm biến': 'Chống rơi, Chống va chạm, Thảm',
                }
            },
            {
                'name_template': 'Máy hút bụi cầm tay không dây {brand}',
                'description': 'Máy hút bụi không dây với motor số hiệu suất cao, lực hút mạnh 150AW. Pin sạc cho 60 phút hoạt động. Đầu hút đa năng hút sàn, giường, sofa, khe hẹp.',
                'specs_template': {
                    'Kiểu máy': 'Cầm tay không dây (Stick Vacuum)',
                    'Lực hút': '150 AW',
                    'Thời gian dùng': '60 phút (chế độ Eco)',
                    'Thời gian sạc': '3.5 giờ',
                    'Dung tích hộp bụi': '0.5 lít',
                    'Trọng lượng': '2.5 kg',
                    'Đầu hút': '4 đầu (sàn, giường, khe, bàn chải)',
                    'Bộ lọc': 'HEPA lọc 99.97% bụi mịn',
                    'Phụ kiện': 'Dock sạc treo tường',
                }
            },
            {
                'name_template': 'Máy hút bụi công suất lớn {brand} {power}W',
                'description': 'Máy hút bụi có dây công suất lớn, hút sạch mọi loại bụi bẩn. Lọc HEPA giữ lại bụi mịn, không khí thải ra sạch. Dây điện 6m tiện dụng.',
                'powers': [1800, 2000, 2200],
                'specs_template': {
                    'Công suất': '{power}W',
                    'Lực hút': '400 AW',
                    'Dung tích hộp bụi': '3 lít',
                    'Chiều dài dây': '6m',
                    'Bộ lọc': 'HEPA H12',
                    'Đầu hút': '3 đầu (sàn, khe, bàn chải)',
                    'Độ ồn': '76 dB',
                    'Trọng lượng': '6 kg',
                }
            },
        ],
        'Lò vi sóng': [
            {
                'name_template': 'Lò vi sóng điện tử {brand} {capacity} lít',
                'description': 'Lò vi sóng điện tử với nhiều chế độ nấu sẵn cho các món Việt. Công suất 800W hâm nóng nhanh. Mâm xoay thủy tinh, lòng nồi chống dính dễ vệ sinh.',
                'capacities': [20, 23, 25, 28],
                'specs_template': {
                    'Dung tích': '{capacity} lít',
                    'Công suất vi sóng': '800W (5 mức)',
                    'Chế độ nấu': '8 chương trình tự động',
                    'Mâm xoay': 'Thủy tinh Φ27cm',
                    'Hẹn giờ': '99 phút',
                    'Chất liệu trong': 'Inox chống dính',
                    'Khóa trẻ em': 'Có',
                    'Kích thước ngoài': '48 x 36 x 28 cm',
                }
            },
            {
                'name_template': 'Lò nướng đa năng {brand} {capacity} lít',
                'description': 'Lò nướng điện đa năng với 4 thanh nhiệt trên dưới, nướng đều 2 mặt. Chế độ nướng đối lưu, quay xiên. Phù hợp nướng gà, pizza, bánh ngọt.',
                'capacities': [30, 35, 42, 50],
                'specs_template': {
                    'Dung tích': '{capacity} lít',
                    'Công suất': '1800W',
                    'Thanh nhiệt': '4 thanh (2 trên + 2 dưới)',
                    'Chế độ nướng': 'Trên, Dưới, 2 mặt, Đối lưu, Xiên quay',
                    'Nhiệt độ': '100 - 250°C',
                    'Hẹn giờ': '60 phút',
                    'Phụ kiện': 'Khay nướng, Vỉ nướng, Xiên quay, Kẹp gắp',
                    'Kích thước ngoài': '55 x 40 x 35 cm',
                }
            },
            {
                'name_template': 'Nồi chiên không dầu {brand} {capacity} lít',
                'description': 'Nồi chiên không dầu với công nghệ Rapid Air luân chuyển khí nóng 360 độ. Chiên giòn ngon mà ít dầu mỡ, tốt cho sức khỏe. Màn hình cảm ứng, 8 chế độ nấu sẵn.',
                'capacities': [4, 5, 6, 7, 8],
                'specs_template': {
                    'Dung tích': '{capacity} lít',
                    'Công suất': '1500W',
                    'Công nghệ': 'Rapid Air 360°',
                    'Nhiệt độ': '80 - 200°C',
                    'Chế độ nấu': '8 chương trình (Khoai, Gà, Cá, Thịt...)',
                    'Hẹn giờ': '60 phút',
                    'Điều khiển': 'Màn hình cảm ứng LED',
                    'Chất liệu rổ': 'Chống dính, tháo rời dễ rửa',
                }
            },
        ],
        'Bếp điện': [
            {
                'name_template': 'Bếp từ đôi {brand} Inverter',
                'description': 'Bếp từ đôi với mặt kính cường lực Schott Ceran của Đức, chịu lực và nhiệt tốt. Công nghệ Inverter tiết kiệm điện 30%. Nhiều mức điều chỉnh nhiệt, nấu chính xác.',
                'specs_template': {
                    'Số bếp': '2 vùng nấu',
                    'Công suất tổng': '4400W (2200W x 2)',
                    'Mặt kính': 'Schott Ceran (Đức)',
                    'Công nghệ': 'Inverter',
                    'Số mức nhiệt': '9 mức',
                    'Hẹn giờ': '180 phút',
                    'An toàn': 'Khóa trẻ em, Tự ngắt quá nhiệt, Cảnh báo nồi không phù hợp',
                    'Kích thước âm': '72 x 42 cm',
                    'Điều khiển': 'Cảm ứng trượt',
                }
            },
            {
                'name_template': 'Bếp hồng ngoại đôi {brand}',
                'description': 'Bếp hồng ngoại đôi dùng được mọi loại nồi (nhôm, đất, thủy tinh...). Không kén nồi như bếp từ, giá thành hợp lý. Mặt kính dễ vệ sinh.',
                'specs_template': {
                    'Số bếp': '2 vùng nấu',
                    'Công suất tổng': '4000W (2000W x 2)',
                    'Mặt kính': 'Kính cường lực chịu nhiệt',
                    'Loại nồi': 'Mọi loại (nhôm, inox, đất, thủy tinh...)',
                    'Số mức nhiệt': '9 mức',
                    'Hẹn giờ': '120 phút',
                    'An toàn': 'Khóa trẻ em, Tự ngắt',
                    'Điều khiển': 'Cảm ứng',
                }
            },
            {
                'name_template': 'Bếp từ đơn {brand} di động',
                'description': 'Bếp từ đơn nhỏ gọn, tiện mang đi hoặc dùng cho phòng trọ. Công suất 2000W nấu nhanh. Mặt kính chịu lực, có tay cầm di chuyển.',
                'specs_template': {
                    'Số bếp': '1 vùng nấu',
                    'Công suất': '2000W',
                    'Mặt kính': 'Kính cường lực',
                    'Số mức nhiệt': '8 mức',
                    'Chế độ nấu': 'Nấu lẩu, Xào, Chiên, Hâm nóng',
                    'Hẹn giờ': '180 phút',
                    'Trọng lượng': '2.3 kg',
                    'Kích thước': '30 x 38 x 6 cm',
                }
            },
        ],
        'Máy xay': [
            {
                'name_template': 'Máy xay sinh tố {brand} {power}W',
                'description': 'Máy xay sinh tố công suất cao với lưỡi dao 6 cánh bằng thép không gỉ. Cối thủy tinh dày chịu nhiệt, xay đá nhuyễn. 3 tốc độ và nút Pulse linh hoạt.',
                'powers': [800, 1000, 1200, 1500],
                'specs_template': {
                    'Công suất': '{power}W',
                    'Dung tích cối': '1.5 lít',
                    'Chất liệu cối': 'Thủy tinh chịu nhiệt',
                    'Lưỡi dao': '6 cánh thép không gỉ',
                    'Số tốc độ': '3 tốc độ + Pulse',
                    'Xay đá': 'Có',
                    'An toàn': 'Khóa nắp, chống quá tải',
                    'Phụ kiện': 'Cối xay khô 300ml',
                }
            },
            {
                'name_template': 'Máy ép trái cây chậm {brand}',
                'description': 'Máy ép chậm với trục ép xoắn ốc tốc độ 45 vòng/phút, không sinh nhiệt giữ nguyên vitamin. Tách bã khô, cho nước ép nguyên chất. Ép được rau củ cứng như cà rốt, củ cải.',
                'specs_template': {
                    'Công suất': '150W',
                    'Tốc độ ép': '45 vòng/phút (chậm, không sinh nhiệt)',
                    'Dung tích bình chứa': '1 lít',
                    'Đường kính miệng': '8cm (cho trái lớn)',
                    'Chất liệu trục ép': 'Ultem (bền gấp 8 lần nhựa thường)',
                    'Tách bã': 'Hoàn toàn, bã khô',
                    'Phù hợp': 'Trái cây, rau củ, đậu nành, hạt',
                    'Vệ sinh': 'Cọ vệ sinh đi kèm',
                }
            },
            {
                'name_template': 'Máy làm sữa hạt {brand} đa năng',
                'description': 'Máy làm sữa hạt tự động xay và nấu trong 20 phút. Làm được sữa đậu nành, sữa hạnh nhân, sữa óc chó, cháo, súp. Lọc tự động, không cần lược thêm.',
                'specs_template': {
                    'Công suất': '800W',
                    'Dung tích': '1.2 lít',
                    'Chế độ': 'Sữa đậu, Sữa hạt, Cháo, Súp, Nước trái cây',
                    'Thời gian': '20 phút tự động',
                    'Lưỡi dao': '4 cánh inox 304',
                    'Lọc': 'Tự lọc, nước mịn không cần lược',
                    'Giữ ấm': '2 giờ tự động',
                    'Vệ sinh': 'Chế độ tự rửa',
                }
            },
        ],
        'Nồi cơm điện': [
            {
                'name_template': 'Nồi cơm điện tử {brand} {capacity} lít',
                'description': 'Nồi cơm điện tử với công nghệ gia nhiệt 3D, cơm chín đều dẻo thơm. Nhiều chế độ nấu: cơm, cháo, xôi, hấp, làm bánh. Giữ ấm 24 giờ không khô cứng.',
                'capacities': [1.0, 1.5, 1.8, 2.0],
                'specs_template': {
                    'Dung tích': '{capacity} lít',
                    'Công suất': '860W',
                    'Công nghệ nấu': 'Gia nhiệt 3D',
                    'Lòng nồi': 'Phủ men ceramic chống dính',
                    'Chế độ nấu': '10 chế độ (Cơm, Cháo, Xôi, Hấp, Súp, Cake...)',
                    'Giữ ấm': '24 giờ tự động',
                    'Hẹn giờ': '24 giờ',
                    'Màn hình': 'LED hiển thị',
                    'Phụ kiện': 'Xửng hấp, Cốc đong, Muỗng',
                }
            },
            {
                'name_template': 'Nồi cơm cao tần IH {brand} {capacity} lít',
                'description': 'Nồi cơm cao tần IH với công nghệ gia nhiệt cảm ứng từ, nhiệt phân bố đều 360 độ. Cơm ngon như nấu bếp củi, giữ hương vị gạo. Lòng nồi nhiều lớp giữ nhiệt tốt.',
                'capacities': [1.0, 1.5, 1.8],
                'specs_template': {
                    'Dung tích': '{capacity} lít',
                    'Công suất': '1200W',
                    'Công nghệ': 'IH (Induction Heating) cao tần',
                    'Lòng nồi': 'Đa lớp: Nhôm + Thép + Men sứ',
                    'Áp suất': 'Có (1.05 atm)',
                    'Chế độ nấu': '16 chế độ thông minh',
                    'Giữ ấm': '24 giờ, cơm không vàng',
                    'Điều khiển': 'Màn hình cảm ứng',
                }
            },
            {
                'name_template': 'Nồi áp suất điện {brand} {capacity} lít',
                'description': 'Nồi áp suất điện đa năng nấu nhanh gấp 3 lần, giữ nguyên dinh dưỡng. Nấu cơm, hầm, hấp, làm sữa chua, làm bánh... Nhiều cơ chế an toàn, xả áp từ xa.',
                'capacities': [5, 6, 8],
                'specs_template': {
                    'Dung tích': '{capacity} lít',
                    'Công suất': '1000W',
                    'Áp suất tối đa': '70 kPa',
                    'Chế độ nấu': '14 chế độ (Cơm, Hầm, Hấp, Cháo, Sữa chua, Cake...)',
                    'An toàn': '12 cơ chế bảo vệ',
                    'Xả áp': 'Tự động + Xả từ xa',
                    'Giữ ấm': '12 giờ',
                    'Lòng nồi': 'Chống dính 5 lớp',
                }
            },
        ],
        'Ấm siêu tốc': [
            {
                'name_template': 'Ấm siêu tốc {brand} {capacity} lít inox 304',
                'description': 'Ấm siêu tốc với thân ấm inox 304 cao cấp, an toàn cho sức khỏe. Đun sôi 1.7L chỉ trong 5 phút. Tự ngắt khi sôi và khi cạn nước.',
                'capacities': [1.5, 1.7, 1.8, 2.0],
                'specs_template': {
                    'Dung tích': '{capacity} lít',
                    'Công suất': '1800W',
                    'Chất liệu': 'Inox 304 không gỉ',
                    'Thời gian đun': '~5 phút',
                    'An toàn': 'Tự ngắt khi sôi, Chống cạn',
                    'Đế xoay': '360 độ',
                    'Nắp': 'Mở nút bấm',
                    'Vạch nước': 'Có',
                }
            },
            {
                'name_template': 'Bình thủy điện {brand} {capacity} lít',
                'description': 'Bình thủy điện giữ nóng 24 giờ, 3 mức nhiệt độ 60/85/98 độ C. Rót nước bằng nút bấm điện hoặc bơm tay khi mất điện. Khóa an toàn chống đổ.',
                'capacities': [3.0, 4.0, 5.0],
                'specs_template': {
                    'Dung tích': '{capacity} lít',
                    'Công suất đun': '800W',
                    'Mức nhiệt giữ': '60°C / 85°C / 98°C',
                    'Giữ nóng': '24 giờ',
                    'Rót nước': 'Điện + Bơm tay',
                    'Chất liệu': 'Inox 304 bên trong',
                    'An toàn': 'Khóa chống rót, Chống cạn',
                    'Màn hình': 'LED hiển thị nhiệt độ',
                }
            },
            {
                'name_template': 'Ấm đun đa nhiệt độ {brand} {capacity} lít',
                'description': 'Ấm đun thông minh điều chỉnh nhiệt độ từ 40-100 độ C, phù hợp pha trà, cà phê, sữa. Giữ ấm tự động 2 giờ. Màn hình LED hiển thị nhiệt độ thực.',
                'capacities': [1.0, 1.5, 1.7],
                'specs_template': {
                    'Dung tích': '{capacity} lít',
                    'Công suất': '1500W',
                    'Nhiệt độ': 'Điều chỉnh 40 - 100°C (từng 5 độ)',
                    'Giữ ấm': '2 giờ tự động',
                    'Màn hình': 'LED hiển thị nhiệt độ',
                    'Chất liệu': 'Thủy tinh cao cấp / Inox 304',
                    'Phù hợp': 'Trà xanh 70°C, Cà phê 90°C, Sữa 40°C',
                    'Điều khiển': 'Nút bấm + Xoay',
                }
            },
        ],
        'Quạt điện': [
            {
                'name_template': 'Quạt đứng {brand} 5 cánh',
                'description': 'Quạt đứng 5 cánh gió mạnh, êm ái. Chế độ gió tự nhiên, ngủ đêm. Điều khiển từ xa tiện lợi. Động cơ bạc đạn bền bỉ.',
                'specs_template': {
                    'Loại quạt': 'Quạt đứng',
                    'Số cánh': '5 cánh',
                    'Đường kính cánh': '40cm',
                    'Công suất': '55W',
                    'Số mức gió': '3 mức',
                    'Chế độ': 'Bình thường, Gió tự nhiên, Ngủ',
                    'Hẹn giờ': '7.5 giờ',
                    'Điều khiển': 'Remote + Nút bấm',
                    'Độ ồn': '50 dB',
                }
            },
            {
                'name_template': 'Quạt điều hòa {brand} hơi nước',
                'description': 'Quạt điều hòa làm mát bằng hơi nước, giảm 5-8 độ C so với nhiệt độ phòng. Bình nước 8 lít, thêm đá mát hơn. Tiết kiệm điện hơn điều hòa 10 lần.',
                'specs_template': {
                    'Loại quạt': 'Quạt điều hòa hơi nước',
                    'Công suất': '80W',
                    'Dung tích bình nước': '8 lít',
                    'Lưu lượng gió': '2500 m³/h',
                    'Làm mát': 'Giảm 5-8°C',
                    'Phạm vi': '15 - 20 m²',
                    'Chế độ': '3 mức gió + Tự nhiên',
                    'Điều khiển': 'Remote + Cảm ứng',
                    'Bánh xe': 'Có (di chuyển linh hoạt)',
                }
            },
            {
                'name_template': 'Quạt tháp {brand} không cánh',
                'description': 'Quạt tháp không cánh an toàn với trẻ nhỏ, không cuốn tóc. Thiết kế tháp gọn đẹp, gió êm mát. Chế độ gió tự nhiên thay đổi cường độ.',
                'specs_template': {
                    'Loại quạt': 'Quạt tháp không cánh',
                    'Công suất': '45W',
                    'Chiều cao': '100cm',
                    'Góc quay': '80 độ',
                    'Số mức gió': '3 mức + Gió tự nhiên',
                    'Hẹn giờ': '8 giờ',
                    'Độ ồn': '45 dB',
                    'An toàn': 'Không cánh, an toàn trẻ em',
                    'Điều khiển': 'Remote',
                }
            },
            {
                'name_template': 'Quạt trần đèn LED {brand}',
                'description': 'Quạt trần kết hợp đèn LED chiếu sáng, tiết kiệm không gian. Cánh quạt thu gọn khi tắt, như đèn chùm trang trí. Điều khiển từ xa cả quạt và đèn.',
                'specs_template': {
                    'Loại quạt': 'Quạt trần đèn',
                    'Đường kính': '110cm (cánh mở)',
                    'Công suất quạt': '65W',
                    'Công suất đèn': '36W LED',
                    'Màu đèn': '3 màu (Trắng, Vàng, Trung tính)',
                    'Số mức gió': '6 mức',
                    'Chế độ quạt': 'Tiến, Lùi (mùa hè/đông)',
                    'Cánh': 'Thu gọn khi tắt',
                    'Điều khiển': 'Remote',
                }
            },
        ],
        'Máy lọc nước': [
            {
                'name_template': 'Máy lọc nước RO {brand} 10 lõi',
                'description': 'Máy lọc nước RO 10 cấp lọc, loại bỏ 99.99% tạp chất, kim loại nặng, vi khuẩn. Màng RO nhập khẩu Mỹ, tuổi thọ 3 năm. Nước uống trực tiếp ngay vòi.',
                'specs_template': {
                    'Công nghệ lọc': 'RO (Reverse Osmosis) 10 cấp',
                    'Màng lọc RO': 'DOW Filmtec (Mỹ)',
                    'Tốc độ lọc': '10 lít/giờ',
                    'Bình chứa': '10 lít',
                    'TDS sau lọc': '< 30 ppm',
                    'Vòi nước': 'Nóng - Lạnh - Thường',
                    'Công suất nóng': '500W',
                    'Tuổi thọ lõi': '6-36 tháng tùy lõi',
                    'Cảnh báo': 'Đèn báo thay lõi',
                }
            },
            {
                'name_template': 'Máy lọc nước {brand} Nano',
                'description': 'Máy lọc nước Nano giữ lại khoáng chất có lợi, không cần điện, không nước thải. Lõi lọc Nano cao cấp Nhật Bản. Phù hợp nguồn nước máy đạt chuẩn.',
                'specs_template': {
                    'Công nghệ lọc': 'Nano 6 cấp',
                    'Không cần điện': 'Hoạt động bằng áp lực nước',
                    'Không nước thải': 'Tiết kiệm nước',
                    'Giữ khoáng': 'Giữ lại Ca, Mg, K có lợi',
                    'Tốc độ lọc': '2 lít/phút',
                    'Tuổi thọ lõi': '12-24 tháng',
                    'Lắp đặt': 'Trên bồn rửa hoặc âm tủ',
                }
            },
        ],
        'Máy sấy tóc': [
            {
                'name_template': 'Máy sấy tóc Ion {brand} {power}W',
                'description': 'Máy sấy tóc công nghệ Ion âm giảm xơ rối, tóc bóng mượt. Nhiệt độ và gió điều chỉnh riêng. Đầu tạo kiểu đi kèm. Bảo vệ tóc khỏi nhiệt độ cao.',
                'powers': [1800, 2000, 2200],
                'specs_template': {
                    'Công suất': '{power}W',
                    'Công nghệ': 'Ion âm chăm sóc tóc',
                    'Nhiệt độ': '3 mức (Lạnh, Ấm, Nóng)',
                    'Tốc độ gió': '2 mức',
                    'Nút Cool': 'Có (Cố định nếp tóc)',
                    'Đầu sấy': '2 đầu (tập trung, tạo kiểu)',
                    'Dây điện': '1.8m xoay 360°',
                    'Trọng lượng': '520g',
                }
            },
        ],
        'Bàn ủi': [
            {
                'name_template': 'Bàn ủi hơi nước {brand} {power}W',
                'description': 'Bàn ủi hơi nước với mặt đế Ceramic chống dính, trượt mượt trên mọi loại vải. Phun hơi mạnh 40g/phút, ủi phẳng nếp nhăn cứng đầu. Chống cặn canxi tự động.',
                'powers': [2000, 2200, 2400],
                'specs_template': {
                    'Công suất': '{power}W',
                    'Mặt đế': 'Ceramic chống dính',
                    'Dung tích bình nước': '350ml',
                    'Phun hơi liên tục': '40g/phút',
                    'Phun hơi đột biến': '150g/phút',
                    'Chống cặn': 'Hệ thống Anti-Calc',
                    'Phun nước': 'Có',
                    'Dây điện': '2m xoay 360°',
                    'Tự ngắt an toàn': '8 phút không dùng',
                }
            },
            {
                'name_template': 'Bàn ủi hơi nước đứng {brand}',
                'description': 'Bàn ủi hơi nước đứng phun hơi mạnh, ủi thẳng trên móc áo. Tiện cho vest, áo dài, rèm cửa. Bình nước lớn 1.6L ủi liên tục 45 phút.',
                'specs_template': {
                    'Công suất': '1800W',
                    'Dung tích bình': '1.6 lít',
                    'Lượng hơi': '35g/phút',
                    'Thời gian ủi': '45 phút liên tục',
                    'Thời gian nóng': '45 giây',
                    'Móc treo': 'Đi kèm, gấp gọn',
                    'Đầu ủi': '2 đầu (vải, quần áo)',
                    'Bánh xe': 'Có (di chuyển dễ)',
                }
            },
        ],
    }

    def generate_sku(self, brand_name, category_name, index):
        brand_code = brand_name[:3].upper()
        cat_code = slugify(category_name)[:3].upper()
        return f"{brand_code}-{cat_code}-{index:04d}"

    def generate_price(self, category_name, is_premium=False):
        price_ranges = {
            'Tivi': (5000000, 80000000),
            'Tủ lạnh': (4000000, 55000000),
            'Máy giặt': (4500000, 35000000),
            'Điều hòa': (6000000, 45000000),
            'Máy lọc không khí': (2000000, 18000000),
            'Máy hút bụi': (1500000, 25000000),
            'Lò vi sóng': (1200000, 12000000),
            'Bếp điện': (1500000, 18000000),
            'Máy xay': (500000, 6000000),
            'Nồi cơm điện': (800000, 10000000),
            'Ấm siêu tốc': (250000, 2500000),
            'Quạt điện': (350000, 6000000),
            'Máy lọc nước': (3000000, 15000000),
            'Máy sấy tóc': (300000, 3000000),
            'Bàn ủi': (250000, 2000000),
        }
        min_price, max_price = price_ranges.get(category_name, (1000000, 10000000))
        if is_premium:
            min_price = int(max_price * 0.5)
        price = random.randint(min_price // 100000, max_price // 100000) * 100000
        return Decimal(str(price))

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Bắt đầu tạo dữ liệu mẫu chi tiết...'))

        self.stdout.write('Đang tạo danh mục...')
        categories = {}
        for cat_data in self.CATEGORIES:
            cat, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'is_active': True,
                }
            )
            categories[cat.name] = cat
            status = 'Tạo mới' if created else 'Đã tồn tại'
            self.stdout.write(f"  - {cat.name}: {status}")

        self.stdout.write('Đang tạo thương hiệu...')
        brands = {}
        for brand_data in self.BRANDS:
            brand, created = Brand.objects.get_or_create(
                name=brand_data['name'],
                defaults={
                    'description': brand_data['description'],
                    'is_active': True,
                }
            )
            brands[brand.name] = brand
            status = 'Tạo mới' if created else 'Đã tồn tại'
            self.stdout.write(f"  - {brand.name}: {status}")

        self.stdout.write('Đang tạo sản phẩm...')
        product_count = 0
        product_index = 1

        for category_name, product_templates in self.DETAILED_PRODUCTS.items():
            category = categories.get(category_name)
            if not category:
                continue

            for template in product_templates:
                allowed_brand_names = self.BRAND_CATEGORY_MAPPING.get(category_name, [])
                allowed_brands = [brands[name] for name in allowed_brand_names if name in brands]
                if not allowed_brands:
                    allowed_brands = list(brands.values())
                selected_brands = random.sample(allowed_brands, min(len(allowed_brands), random.randint(3, 5)))

                for brand in selected_brands:
                    if 'sizes' in template:
                        sizes = random.sample(template['sizes'], min(len(template['sizes']), 2))
                        for size in sizes:
                            product_count += self.create_product(
                                template, brand, category, product_index, size=size
                            )
                            product_index += 1
                    elif 'capacities' in template:
                        capacities = random.sample(template['capacities'], min(len(template['capacities']), 2))
                        for capacity in capacities:
                            product_count += self.create_product(
                                template, brand, category, product_index, capacity=capacity
                            )
                            product_index += 1
                    elif 'btus' in template:
                        btus = random.sample(template['btus'], min(len(template['btus']), 2))
                        for btu in btus:
                            product_count += self.create_product(
                                template, brand, category, product_index, btu=btu
                            )
                            product_index += 1
                    elif 'areas' in template:
                        areas = random.sample(template['areas'], min(len(template['areas']), 2))
                        for area in areas:
                            product_count += self.create_product(
                                template, brand, category, product_index, area=area
                            )
                            product_index += 1
                    elif 'powers' in template:
                        powers = random.sample(template['powers'], min(len(template['powers']), 2))
                        for power in powers:
                            product_count += self.create_product(
                                template, brand, category, product_index, power=power
                            )
                            product_index += 1
                    else:
                        product_count += self.create_product(
                            template, brand, category, product_index
                        )
                        product_index += 1

        self.stdout.write(self.style.SUCCESS(f'\nHoàn thành! Đã tạo:'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(self.CATEGORIES)} danh mục'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(self.BRANDS)} thương hiệu'))
        self.stdout.write(self.style.SUCCESS(f'  - {product_count} sản phẩm'))

    def create_product(self, template, brand, category, index, **kwargs):
        size = kwargs.get('size')
        capacity = kwargs.get('capacity')
        btu = kwargs.get('btu')
        area = kwargs.get('area')
        power = kwargs.get('power')

        format_args = {'brand': brand.name}
        if size:
            format_args['size'] = size
        if capacity:
            format_args['capacity'] = capacity
            format_args['usable'] = int(capacity * 0.85)
            format_args['dry_capacity'] = int(capacity * 0.6)
        if btu:
            format_args['btu'] = btu
            format_args['heat_btu'] = int(btu * 0.9)
            area_map = {9000: 15, 12000: 20, 18000: 30, 24000: 40, 36000: 50, 48000: 70}
            format_args['area'] = area_map.get(btu, 25)
        if area:
            format_args['area'] = area
            format_args['cadr'] = area * 8
        if power:
            format_args['power'] = power

        try:
            name = template['name_template'].format(**format_args)
        except KeyError:
            name = template['name_template'].replace('{brand}', brand.name)

        description = template['description']

        specs = {}
        specs['Thương hiệu'] = brand.name
        specs['Xuất xứ'] = random.choice(
            ['Việt Nam', 'Thái Lan', 'Malaysia', 'Indonesia', 'Trung Quốc', 'Hàn Quốc', 'Nhật Bản'])
        specs['Bảo hành'] = random.choice(['12 tháng', '24 tháng', '36 tháng'])

        for key, value in template.get('specs_template', {}).items():
            try:
                specs[key] = str(value).format(**format_args)
            except KeyError:
                specs[key] = value

        sku = self.generate_sku(brand.name, category.name, index)
        price = self.generate_price(category.name, 'premium' in name.lower() or 'cao cấp' in name.lower())

        sale_price = None
        if random.random() < 0.35:
            discount = random.choice([0.05, 0.10, 0.15, 0.20, 0.25, 0.30])
            sale_price = price * Decimal(str(1 - discount))
            sale_price = Decimal(str(int(sale_price / 100000) * 100000))

        unique_slug = f"{slugify(name)}-{index}"

        product, created = Product.objects.get_or_create(
            sku=sku,
            defaults={
                'name': name,
                'slug': unique_slug,
                'description': description,
                'category': category,
                'brand': brand,
                'price': price,
                'sale_price': sale_price,
                'stock': random.randint(5, 150),
                'is_active': True,
                'is_featured': random.random() < 0.12,
                'is_new': random.random() < 0.25,
                'specifications': specs,
                'views': random.randint(50, 8000),
                'sold': random.randint(5, 500),
            }
        )

        if created:
            return 1
        return 0
