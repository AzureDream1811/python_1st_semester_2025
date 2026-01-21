import random
import json
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.contrib.auth.models import User
from apps.products.models import Category, Brand, Product
from apps.reviews.models import Review
from apps.reviews.sentiment import SentimentAnalyzer


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

    # Sample reviews theo rating với sentiment tương ứng
    SAMPLE_REVIEWS = {
        5: {  # 5 sao - Tích cực
            'sentiment': 'positive',
            'comments': [
                "Sản phẩm tuyệt vời, chất lượng vượt quá mong đợi! Đóng gói cẩn thận, giao hàng nhanh. Rất hài lòng!",
                "Đã dùng được 1 tháng, sản phẩm hoạt động hoàn hảo. Thiết kế đẹp, tiết kiệm điện. Sẽ giới thiệu cho bạn bè.",
                "Chất lượng xuất sắc, đúng như mô tả. Shop tư vấn nhiệt tình, giao hàng đúng hẹn. 10 điểm!",
                "Sản phẩm chính hãng, bảo hành uy tín. Sử dụng rất ổn định, không có gì để chê. Recommend!",
                "Quá tuyệt vời! Đây là lần mua hàng online hài lòng nhất. Sản phẩm đẹp, chạy êm, tiết kiệm điện.",
                "Mua cho gia đình dùng rất thích. Công nghệ hiện đại, dễ sử dụng. Giá cả hợp lý so với chất lượng.",
                "Sản phẩm đáng đồng tiền bát gạo. Thiết kế sang trọng, hoạt động mượt mà. Cảm ơn shop!",
                "Excellent! Rất đáng mua. Sử dụng 2 tuần không có vấn đề gì. Giao hàng cực nhanh, đóng gói kỹ.",
                "Chồng mình rất thích sản phẩm này. Chất lượng tốt, tiết kiệm điện, chạy êm ái. 5 sao xứng đáng!",
                "Mình đã so sánh nhiều nơi và quyết định mua ở đây. Không thất vọng chút nào. Sản phẩm tuyệt vời!",
                "Lần đầu mua online mà được hàng chuẩn như này. Sản phẩm y hệt hình, chất lượng thật sự tốt.",
                "Shop uy tín, sản phẩm chính hãng 100%. Đã kiểm tra kỹ, hoàn toàn hài lòng. Sẽ ủng hộ tiếp!",
            ]
        },
        4: {  # 4 sao - Tích cực (có chút góp ý nhỏ)
            'sentiment': 'positive',
            'comments': [
                "Sản phẩm tốt, đáng mua. Chỉ tiếc là giao hàng hơi lâu một chút. Nhưng overall vẫn hài lòng.",
                "Chất lượng ổn, thiết kế đẹp. Mong shop có thêm nhiều màu sắc để lựa chọn. Còn lại rất ok!",
                "Sản phẩm đúng như mô tả, hoạt động tốt. Hộp đựng bị móp nhẹ nhưng không ảnh hưởng máy.",
                "Dùng được 2 tuần, khá hài lòng. Chạy hơi ồn một chút lúc mới bật nhưng sau êm dần. Tốt!",
                "Giá hợp lý, chất lượng tương xứng. Shop tư vấn tốt. Trừ 1 sao vì không có quà tặng kèm.",
                "Sản phẩm ok, giao hàng nhanh. Thiếu sách hướng dẫn tiếng Việt, phải tự tìm hiểu. Còn lại tốt.",
                "Mua để thay thế máy cũ, dùng rất ổn. Tiết kiệm điện hơn. Thiết kế hơi đơn giản nhưng bền.",
                "Chất lượng tốt so với giá tiền. Đóng gói cẩn thận. Chỉ là remote hơi nhạy, cần cải thiện.",
                "Hài lòng với sản phẩm, đúng như kỳ vọng. Giao hàng cần nhanh hơn nữa thì hoàn hảo.",
                "Sản phẩm chính hãng, hoạt động ổn định. Bảo hành tốt. Chỉ là giá cao hơn nơi khác một chút.",
            ]
        },
        3: {  # 3 sao - Trung lập
            'sentiment': 'neutral',
            'comments': [
                "Sản phẩm bình thường, không có gì đặc biệt. Hoạt động được nhưng không quá ấn tượng.",
                "Tạm ổn so với giá tiền. Không tệ nhưng cũng không xuất sắc. Dùng được.",
                "Giao hàng chậm hơn dự kiến. Sản phẩm ok, nhưng đóng gói sơ sài. Cần cải thiện.",
                "Chất lượng trung bình khá. Có một số tính năng không như quảng cáo. Tạm chấp nhận được.",
                "Sản phẩm dùng được, nhưng hơi ồn. Thiết kế cũng bình thường. Giá thì hợp lý.",
                "Không quá hài lòng cũng không thất vọng. Sản phẩm hoạt động đúng chức năng cơ bản.",
                "Đã nhận hàng, sản phẩm tạm ổn. Cần dùng thêm thời gian mới đánh giá chính xác được.",
                "Sản phẩm y hình, nhưng chất liệu không được cao cấp như mong đợi. Giá tiền này thì ok.",
                "Dùng thử 1 tuần, không có vấn đề gì lớn. Tuy nhiên cũng không có gì nổi bật. 3 sao.",
                "Hàng nhận được bình thường, không bị lỗi gì. Nhưng tính năng hạn chế hơn tưởng tượng.",
            ]
        },
        2: {  # 2 sao - Tiêu cực (thất vọng)
            'sentiment': 'negative',
            'comments': [
                "Sản phẩm không như mong đợi. Chất lượng kém hơn so với giá tiền. Hơi thất vọng.",
                "Giao hàng chậm, sản phẩm bị trầy xước. Liên hệ shop thì phản hồi chậm. Không hài lòng.",
                "Dùng được 1 tuần thì bắt đầu có vấn đề. Tiếng ồn lớn, hoạt động không ổn định.",
                "Sản phẩm không giống hình. Chất liệu rẻ tiền, cảm giác không bền. Đáng lẽ nên mua hãng khác.",
                "Thất vọng về chất lượng. Quảng cáo hay nhưng thực tế không được như vậy.",
                "Đóng gói sơ sài, máy bị móp góc. Hoạt động được nhưng lo về độ bền. Không recommend.",
                "Sản phẩm tạm dùng được nhưng nhiều lỗi vặt. Hướng dẫn sử dụng không rõ ràng.",
                "Mua về dùng thử thì thấy không đáng tiền. Tính năng hạn chế, chất lượng trung bình.",
            ]
        },
        1: {  # 1 sao - Rất tiêu cực
            'sentiment': 'negative',
            'comments': [
                "Sản phẩm lỗi ngay khi nhận hàng. Liên hệ đổi trả rất khó khăn. Rất thất vọng!",
                "Quá tệ! Không hoạt động được, phải gửi bảo hành ngay. Mất thời gian và công sức.",
                "Sản phẩm giả, không phải hàng chính hãng như quảng cáo. Yêu cầu hoàn tiền!",
                "Giao hàng sai mẫu, liên hệ mãi không được. Dịch vụ quá kém. Không bao giờ mua lại!",
                "Chất lượng quá tệ, vừa dùng được 3 ngày đã hỏng. Tiền mất tật mang.",
                "Thất vọng hoàn toàn! Sản phẩm không đúng mô tả, chất lượng rất kém.",
                "Mình phải cho 1 sao vì sản phẩm bị lỗi và không được hỗ trợ đổi trả. Rất buồn!",
                "Đừng mua! Sản phẩm rất tệ, không đáng tiền. Shop không uy tín, phản hồi chậm.",
            ]
        }
    }

    # Tên người dùng mẫu cho reviews
    SAMPLE_USERNAMES = [
        'nguyen_van_a', 'tran_thi_b', 'le_van_c', 'pham_thi_d', 'hoang_van_e',
        'vu_thi_f', 'dang_van_g', 'bui_thi_h', 'do_van_i', 'ngo_thi_k',
        'duong_van_l', 'ly_thi_m', 'truong_van_n', 'dinh_thi_o', 'ha_van_p',
        'mai_thi_q', 'vo_van_r', 'tang_thi_s', 'phan_van_t', 'cao_thi_u',
        'lam_van_v', 'to_thi_x', 'trinh_van_y', 'nghiem_thi_z', 'chu_van_aa',
        'khuat_thi_bb', 'quach_van_cc', 'ta_thi_dd', 'mac_van_ee', 'huynh_thi_ff',
        'user_reviewer_01', 'user_reviewer_02', 'user_reviewer_03', 'user_reviewer_04',
        'khachhang_01', 'khachhang_02', 'khachhang_03', 'khachhang_04', 'khachhang_05',
        'customer_vn_01', 'customer_vn_02', 'customer_vn_03', 'customer_vn_04',
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
                'images': [
                    'https://cdn.hoanghamobile.vn/Uploads/2024/06/14/sony-google-tivi-oled-k-65xr80-06.jpg',
                    'https://cdn.tgdd.vn/Files/2017/02/11/948506/tivi-qled-cua-samsung-co-gia-bao-nhieu--11.jpg',
                    'https://dienmaygiare.net/wp-content/uploads/2025/12/smart-tivi-hisense-32-inch-32a4q-1-638921808926524429-700x467-1.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTSNr71Ztjncx27D4-jISVX5IWqIP1r-_h97g&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTSNr71Ztjncx27D4-jISVX5IWqIP1r-_h97g&s',
                    'https://dienmay247.com.vn/wp-content/uploads/2024/09/10.4.jpg',
                    'https://asher.com.vn/wp-content/uploads/2022/09/43-.png',
                    'https://asher.com.vn/wp-content/uploads/2022/09/Anh-web-ASHER-43-02-2048x1366.jpg',
                    'https://cdn2.fptshop.com.vn/unsafe/1920x0/filters:format(webp):quality(75)/2024_1_8_638403196055826396_tivi-re-nhat-1.jpg',
                    'https://cdn11.dienmaycholon.vn/filewebdmclnew/DMCL21/Picture//Apro/Apro_product_36163/smart-tivi-samsung-qled-4k-vision-ai-65-inch-qa65q7fa-main-327357.webp',
                    'https://cdnv2.tgdd.vn/mwg-static/dmx/Products/Images/1942/337819/smart-tivi-lg-ai-4k-55-inch-55ua8450psa-2-638822975892461982-700x467.jpg',
                    'https://cdnv2.tgdd.vn/mwg-static/dmx/Products/Images/1942/339083/google-tivi-sony-4k-43-inch-k-43s25vm2-2-638844797000223938-700x467.jpg',
                    'https://techcenter.vn/upload/source/tong-hop-2022/ban-gia-treo-tivi-di-dong-hq1700.png',
                    'https://techcenter.vn/upload/source/gia-treo-tivi/hq1700/gia-treo-tivi-di-dong-hq1700.png',
                    'https://techcenter.vn/upload/source/gia-treo-tivi/hq1700/ban-gia-treo-tivi-di-dong-hq1700.png',
                    'https://cdn.mediamart.vn/images/product/smart-tivi-samsung-4k-75-inch-75au7700-uhd_3b060d16.jpg',
                    'https://cdn.mediamart.vn/images/product/smart-tivi-tcl-4k-55p638-55-inch-google-tv_43dc709f.webp',
                    'https://cdn.mediamart.vn/images/product/smart-tivi-samsung-4k-43-inch-43du7700-crystal-uhd_61e2b41c.webp',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQryAZ2xeevgPLQJ3eznJMKU33BalQWgXqRag&s',
                    'https://product.hstatic.net/200000892961/product/qled-tivi-4k-toshiba-65m450np-65-inch-smart-tv_fdd4697f_7f7add6ec518477db0cd7bc2c05f7cd3.png',
                    'https://product.hstatic.net/200000335975/product/1_b2f61ee8f2a94f7981354425f9e5b814_master.jpeg',
                    'https://bepxanh.com/Uploads/smart-tivi-samsung-4k-50-inch-ua50tu8100.jpg',
                    'https://product.hstatic.net/200000574527/product/21_57ae5753d2c340939db2362ac0cac8eb.png',
                    'https://meta.vn/Data/image/2022/06/25/smart-tivi-lg-4k-43-inch-43uq8000psc-1.jpg',
                    'https://bizweb.dktcdn.net/100/377/070/products/77910ce37b303744a5a1fdb336602e.jpg?v=1581299169937',
                    'https://bizweb.dktcdn.net/thumb/1024x1024/100/443/782/products/smart-tivi-samsung-4k-43-inch-43au7000-uhd-gia-re-2.jpg?v=1672321942360',
                    'https://dienmaysaigon.com/wp-content/uploads/2024/01/Smart-Tivi-LG-4K-43-Inch-43UQ7050PSA-Dien-May-Sai-Gon.jpg',
                    'https://khodienmay.net/wp-content/uploads/2025/07/55.jpg',
                    'https://dienmaybanre.com/images/products/2023/04/13/large/smart-tivi-lg-oled-55a3psa-4k-55-inch_1681397365.jpg',
                    'https://dienmaybanre.com/images/products/2022/01/21/original/tivi-led-lg-55up7550ptc-9_1642738163.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTphEp-2ak5aP4pQxmXcE8FkbbRG6AXlv5SGw&s',
                    
                ],
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
                'images': [
                    'https://bizweb.dktcdn.net/100/549/276/files/2-tivi-oled-lg-cung-cap-do-phan-giai-len-den-8k-cho-moi-hinh-anh-chi-tiet-va-sac-net-hon-bao-gio-het-jpeg.jpg?v=1740972602263',
                    'https://bizweb.dktcdn.net/100/549/276/files/5-nguoi-dung-cam-thay-an-tuong-voi-do-tuong-phan-cao-cua-mau-tivi-sony-a8-oled-jpeg.jpg?v=1740972590071',
                    'https://muahangtaikho.vn/media/lib/11-10-2024/tivi-oled10.png',
                    'https://muahangtaikho.vn/media/lib/11-10-2024/tivi-oled8.png',
                    'https://cdnv2.tgdd.vn/mwg-static/dmx/Products/Images/1942/337482/smart-tivi-oled-evo-lg-ai-4k-55-inch-oled55c5psa-2-638814287666408461-700x467.jpg',
                    'https://bizweb.dktcdn.net/100/439/998/products/tivi-oled-lg-4k-77-inch-77c4psa-2-optimized-e69c3e4c-c17d-407f-8e23-a91a26f48f5c.jpg?v=1725609488910',
                    'https://mivietnam.vn/wp-content/uploads/2025/04/z7188388507500_8944b79d7eff5794b6e556d8936e990b.jpg',
                    'https://i.pinimg.com/1200x/c1/0d/61/c10d610cec713da08a00a4b03733443a.jpg',
                    'https://i.pinimg.com/736x/20/bb/81/20bb8165c7cd5a5919f66737773783a4.jpg',
                    'https://i.pinimg.com/1200x/26/5a/68/265a681155c007a9b43e4a08d1f8c66e.jpg',
                    'https://i.pinimg.com/736x/a1/8e/c1/a18ec1cab8915ef9916b446868a01e56.jpg',
                    'https://i.pinimg.com/1200x/31/a5/0f/31a50fc088a9c34b58f2bf5cb6c3a3c6.jpg',
                    'https://i.pinimg.com/736x/7d/4d/43/7d4d43ec98ce63b15be5f1feb155bb97.jpg',
                    'https://i.pinimg.com/1200x/46/48/c3/4648c31a14420a79bc68984c57f4f042.jpg',
                    'https://i.pinimg.com/1200x/ae/0b/88/ae0b88e51b92d906ff83ce9f66a7f732.jpg',
                    'https://i.pinimg.com/1200x/cc/e8/c5/cce8c51d6d1e5fdb6972e15cf80623a5.jpg',
                    'https://i.pinimg.com/736x/73/f9/82/73f9823687b4744fe3f107c4a1a86cf5.jpg',
                    'https://i.pinimg.com/736x/db/d5/1e/dbd51ecb0c57de585c4489e2c5bf1207.jpg',
                    'https://i.pinimg.com/1200x/c1/a1/59/c1a15954ce119ad68d9cd923dbdec27c.jpg',
                    'https://i.pinimg.com/736x/4b/5f/26/4b5f264a77247c0908e2b43d02a90aa7.jpg',
                    'https://i.pinimg.com/736x/03/36/2c/03362c0d017df3d0be6c65c04943559c.jpg',
                    'https://i.pinimg.com/1200x/db/38/56/db385683eeb65ebb8564581abd693c55.jpg',
                    'https://i.pinimg.com/1200x/20/3c/89/203c8971e3f0041a7fc9eee14c25910c.jpg',
                    'https://i.pinimg.com/1200x/b1/53/e7/b153e705c421d8a0d4e7956792b851b5.jpg',
                    'https://i.pinimg.com/1200x/b3/64/df/b364dfe5f51eb80271c29e2cc60882a6.jpg',
                    'https://i.pinimg.com/1200x/c6/7f/0a/c67f0a5b38b1f217499513cc706888c0.jpg',
                    'https://i.pinimg.com/1200x/39/65/44/39654439741157100debf12c106ea4bd.jpg',
                    'https://i.pinimg.com/1200x/2c/81/1e/2c811e993f30bb04d7b3f2cf84c79a01.jpg',
                    'https://i.pinimg.com/736x/f0/a1/ba/f0a1ba48518740ad8c0ddb91156c72fa.jpg',
                    'https://i.pinimg.com/1200x/3c/94/0a/3c940a45f150ddc07a52965205befe1d.jpg',
                    'https://i.pinimg.com/1200x/8a/4b/d8/8a4bd8df726dacce4ef23e7004e0b6ce.jpg',
                    'https://i.pinimg.com/736x/ea/40/10/ea4010ba25b65e06e23cbb839048931d.jpg',
                    'https://i.pinimg.com/736x/36/01/42/360142391fa8fefebc58dfbe708772ce.jpg',
                    'https://i.pinimg.com/1200x/e5/72/42/e57242476c69b83ad60a1b52e19fc03a.jpg',
                    
                ],
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
                'images': [
                    'https://ledlia.com/wp-content/uploads/2024/11/cau-tao-man-hinh-qled.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRwILE4irdfWkVlGOriOP0armw2phsI1naLDA&s',
                    'https://bizweb.dktcdn.net/100/444/251/files/cong-nghe-quantum-dot-color-tren-tivi-hisense.jpg?v=1744395054740',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR19ljecAALw_35DpzybYzpXW-VilWjDIDRag&s',
                    'https://cdn.tgdd.vn/Products/Images/1942/322672/Slider/1fix2-1020x570.jpg',
                    'https://bizweb.dktcdn.net/thumb/large/100/549/276/products/qa55q6faakxxv-6.jpg?v=1760493832453',
                    'https://cdn.tgdd.vn/Products/Images/1942/219254/samsung-qa49q80t-111122-033158-550x340.jpg',
                    'https://cdnv2.tgdd.vn/mwg-static/common/News/1582439/tivi-qd-mini-led-la-gi-5.jpg',
                    'https://i.pinimg.com/736x/d2/d9/f8/d2d9f8a6de3e6c5e64aa94ca914bcfd1.jpg',
                    'https://i.pinimg.com/736x/70/ad/49/70ad49eb8134a3e3eff0e2fea0924f54.jpg',
                    'https://i.pinimg.com/736x/f0/30/f2/f030f24b2dc7ddd23cd42bbb1b423c47.jpg',
                    'https://i.pinimg.com/736x/07/48/4e/07484ed25e1c6442d97d32bd3c9b421c.jpg',
                    'https://i.pinimg.com/736x/5b/15/8a/5b158a7c0898c289928ceae7723ddd65.jpg',
                    'https://i.pinimg.com/736x/3c/ba/6d/3cba6d9c8f94d30bec4711b98f45b7ed.jpg',
                    'https://i.pinimg.com/1200x/8a/4b/d8/8a4bd8df726dacce4ef23e7004e0b6ce.jpg',
                    'https://i.pinimg.com/736x/3c/58/3e/3c583e04e2cceff608a1b086b69af6ff.jpg',
                    'https://i.pinimg.com/736x/9a/10/d3/9a10d36fc476808bbd501e0ec2c7fb7f.jpg',
                    'https://i.pinimg.com/736x/03/36/2c/03362c0d017df3d0be6c65c04943559c.jpg',
                    'https://i.pinimg.com/1200x/2a/e1/14/2ae114a473c039bfb9258cf0c035a541.jpg',
                    'https://i.pinimg.com/1200x/c5/df/e0/c5dfe02aafa3a146238e3244fe4eb898.jpg',
                    'https://i.pinimg.com/736x/99/38/d7/9938d73b74049784e83f42df5db73829.jpg',
                    'https://i.pinimg.com/1200x/f8/96/9f/f8969f625fcd8fbdb4131bab956eda58.jpg',
                    'https://i.pinimg.com/736x/aa/23/d6/aa23d65366991e4d161d2a0fa9656e6b.jpg',
                    'https://i.pinimg.com/736x/be/01/e5/be01e51689bdb7e75288fbf2317dc6b9.jpg',
                    'https://i.pinimg.com/736x/c1/4d/08/c14d08322c07a4507f63144bfdcd8bff.jpg',
                    'https://i.pinimg.com/736x/4e/7a/3a/4e7a3aed3f0c4f38bf395f3e52766518.jpg',
                    'https://i.pinimg.com/736x/f9/31/08/f93108c5a91be69e3468b6a52f373f77.jpg',
                    'https://i.pinimg.com/736x/87/d3/e5/87d3e566266678c88ea0791fb2bd6a38.jpg',
                    'https://i.pinimg.com/736x/c4/40/9d/c4409debaa7c875cb594f99ae2f39277.jpg',
                    'https://i.pinimg.com/736x/c4/40/9d/c4409debaa7c875cb594f99ae2f39277.jpg',
                    'https://i.pinimg.com/736x/e0/36/1f/e0361faa5a104375be51db6d8c78f9d6.jpg'
                ],
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
                'images': [
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRuy562A6VL7TEjI3Fc7Au4OMtdW0VR1tz6Tw&s',
                    'https://tiki.vn/blog/wp-content/uploads/2023/10/co-nen-mua-tivi-xiaomi-3-compressed.jpg',
                    'https://bizweb.dktcdn.net/100/549/276/files/tivi-hinh2.jpg?v=1740988405638',
                    'https://cdn2.cellphones.com.vn/insecure/rs:fill:0:0/q:100/plain/https://cellphones.com.vn/media/wysiwyg/Tivi/tivi-full-hd-2.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSMZW_uqossE7DAJLuhQowkQCaxiqzf7VAduw&s',
                    'https://i.pinimg.com/736x/6b/0d/22/6b0d22adf6378d91f449567e3f35d7ce.jpg',
                    'https://i.pinimg.com/736x/6f/02/99/6f029995a3ec675152b1f1d54819abb9.jpg',
                    'https://i.pinimg.com/736x/cd/53/d4/cd53d47e68a5260d372dc48e41511fb3.jpg',
                    'https://i.pinimg.com/1200x/96/7b/08/967b086b0b5ef233c9814942043ff406.jpg',
                    'https://i.pinimg.com/736x/3d/6d/79/3d6d798bac905325e0c08bcb7490e3cd.jpg',
                    'https://i.pinimg.com/736x/fa/3c/67/fa3c673aa9e71cc05762086c12078606.jpg',
                    'https://i.pinimg.com/1200x/dd/b2/a4/ddb2a409eb039db5f612e17ca869f8b3.jpg',
                    'https://i.pinimg.com/1200x/ad/b9/29/adb929a15a3b8d8675f2bf9b749901a9.jpg',
                    'https://i.pinimg.com/736x/e8/0d/07/e80d07383edc674e1cfe59755e5f0704.jpg',
                    'https://i.pinimg.com/736x/46/ca/da/46cadaca1ae65f594fc498c3268edfed.jpg',
                    'https://i.pinimg.com/736x/c6/69/0b/c6690b0273c83fc5f16cd4e4358223fb.jpg',
                    'https://i.pinimg.com/1200x/c0/b2/84/c0b2841f3cc6bdf340e3a067e1bfbf12.jpg',
                    'https://i.pinimg.com/736x/16/1b/90/161b90013a60445fa8015a87660e48e2.jpg',
                    'https://i.pinimg.com/736x/09/71/42/0971424c7737ffa551ed5d2466fb21c7.jpg',
                    'https://i.pinimg.com/1200x/6b/0e/a0/6b0ea0c36b3f4220048525d6b5a25b6c.jpg',
                    'https://i.pinimg.com/736x/03/36/2c/03362c0d017df3d0be6c65c04943559c.jpg',
                    'https://i.pinimg.com/736x/4b/c1/92/4bc192ed6133c80bae4f1daab1a6ceb7.jpg',
                    'https://i.pinimg.com/736x/4d/ce/e9/4dcee96ffd48ebfdf73ef5dd74d32574.jpg',
                    'https://i.pinimg.com/736x/9a/20/23/9a2023f363db589e6a145551db2dc976.jpg',
                    'https://i.pinimg.com/736x/e9/2e/e6/e92ee682c173c05111b5530892f1076c.jpg',
                    'https://i.pinimg.com/736x/76/e1/98/76e198aed72b6b9a9dc21c04ee6512ad.jpg',
                    'https://i.pinimg.com/736x/bd/1d/eb/bd1debbcfcf4af7c4bfdd88f50082680.jpg',
                    'https://i.pinimg.com/1200x/9b/0a/b8/9b0ab8d96b5d205b014308b66a74fb92.jpg'
                ],
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
                'images': [
                    'https://cdn.tgdd.vn//News/1436081//smart-tivi-neo-qled-8k-65-inch-samsung-qa65qn800c-140323-021017-845x472.jpg',
                    'https://dienmaythienphu.vn/_next/image?url=https%3A%2F%2Fdienmaythienphu.vn%2Fwp-content%2Fuploads%2F2023%2F11%2Fsamsung-QA98QN990C-1.jpg&w=1920&q=100',
                    'https://cdn.tgdd.vn/Products/Images/1942/322639/Slider/1-1020x570.jpg',
                    'https://dienmaythienphu.vn/_next/image?url=https%3A%2F%2Fdienmaythienphu.vn%2Fwp-content%2Fuploads%2F2022%2F05%2FLG-QNED99SQB-1.jpg&w=1920&q=100',
                    'https://cdn11.dienmaycholon.vn/filewebdmclnew/DMCL21/Picture/Apro/Apro_product_36410/smart-ai-tivi-samsung-mini-led-8k-85-inch-qa85qn950f-main--494.png',
                    'https://i.pinimg.com/1200x/d3/f0/de/d3f0de3876c0528bdccfb09e19cc8681.jpg',
                    'https://i.pinimg.com/736x/c9/e4/3c/c9e43c3b2d9d45c36aa3bb55a3e9dd80.jpg',
                    'https://i.pinimg.com/1200x/85/78/2e/85782e95c143c0a5190e06bd1d0724bc.jpg',
                    'https://i.pinimg.com/1200x/15/99/f7/1599f7a5802ab308798b4b40e2f98b1f.jpg',
                    'https://i.pinimg.com/736x/85/ab/e2/85abe2aef21d747119c1b7184f838322.jpg',
                    'https://i.pinimg.com/1200x/cc/b1/3f/ccb13f5a8df1319987b1e8051e8affa7.jpg',
                    'https://i.pinimg.com/1200x/8d/43/6c/8d436c53dceecce90d0c9de47e2f8f68.jpg',
                    'https://i.pinimg.com/736x/76/2c/a3/762ca3f103211ceca2f9213ec2893ea0.jpg',
                    'https://i.pinimg.com/1200x/da/61/47/da6147230b33e44eed2607fda4adb104.jpg',
                    'https://i.pinimg.com/736x/58/dc/5c/58dc5cd211fc2ce5dafe2ae20d09fe3f.jpg',
                    'https://i.pinimg.com/736x/c6/5a/c9/c65ac9edb9d1621cb47c93cdb3f5f705.jpg',
                    'https://i.pinimg.com/736x/68/59/c2/6859c210a53a6c5c03936ddf56cd5f0e.jpg',
                    'https://i.pinimg.com/1200x/6c/a2/04/6ca20436f87a1223eb56a170c335ffb2.jpg',
                    'https://i.pinimg.com/736x/9e/97/e6/9e97e6d0d41846496e00f70930709eff.jpg',
                    'https://i.pinimg.com/736x/f1/8a/ad/f18aadfc93ca597e55f5848fdf68cf45.jpg',
                    'https://i.pinimg.com/1200x/23/71/d2/2371d2358adbabec5074a37e1ec58d13.jpg',
                    'https://i.pinimg.com/1200x/95/6b/46/956b469e2fa79b2acce0cf2f8d0b0acd.jpg',
                    'https://i.pinimg.com/736x/bb/16/ae/bb16ae2a8528f046bfe4437134b0b303.jpg',
                    'https://i.pinimg.com/1200x/ef/01/30/ef01307161f32c8c2125cbf5ac5ff5e3.jpg',
                    'https://i.pinimg.com/1200x/e6/09/10/e60910af013acd770d3ed3b220a4c92e.jpg',
                    'https://i.pinimg.com/736x/00/12/07/001207fb4e371538b2d6c1877cd7fdbb.jpg',
                    'https://i.pinimg.com/1200x/c3/5e/b1/c35eb19751116c17d5ab920960ec0cad.jpg'
                ],
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
                'images': [
                    'https://cdn11.dienmaycholon.vn/filewebdmclnew/DMCL21/Picture/News/News_expe_3940/3940_610.png.webp',
                    'https://cdn2.fptshop.com.vn/unsafe/1920x0/filters:format(webp):quality(75)/tu_lanh_inverter_tot_nhat_2025_253eb6343f.jpg',
                    'https://cdn2.fptshop.com.vn/unsafe/1920x0/filters:format(webp):quality(75)/2023_11_7_638349589404258558_b9-biars.jpg',
                    'https://dienmayhtech.com/_next/image?url=https%3A%2F%2Fimage.dienmayhtech.com%2FStaticFiles%2FImages%2F2024%2F09%2F20%2Ftu-lanh-hitachi-tiet-kiem-dien-1_3ae4.png&w=3840&q=75',
                    'https://file.hstatic.net/200000868155/file/73-post-tu-lanh-inverter-la-gi-uu-diem-voi-cong-nghe-inverter-la-gi--5.jpg',
                    'https://cdn.tgdd.vn/Products/Images/1943/328725/Slider/Tie%CC%82%CC%81t-kie%CC%A3%CC%82m-die%CC%A3%CC%82n-kha%CC%81ng-khua%CC%82%CC%89n-1920x1080.jpg',
                    'https://img.meta.com.vn/data/image/2024/05/22/1-cong-nghe-inverter-tren-tu,-lanh-casper.png',
                    'https://i.pinimg.com/736x/5d/ff/73/5dff735007d70867668864c7eca0964b.jpg',
                    'https://i.pinimg.com/736x/3e/30/f6/3e30f60920461d5f806e2d67ea928e93.jpg',
                    'https://i.pinimg.com/1200x/3a/cc/0f/3acc0f86ceef3d51a3cf41bcb39da60e.jpg'
                    'https://i.pinimg.com/736x/c4/fb/a0/c4fba04e583e9ae5ceeccd1e539847c1.jpg',
                    'https://i.pinimg.com/736x/02/97/cc/0297ccfd8895045d7d8e75610ee90751.jpg',
                    'https://i.pinimg.com/736x/2e/34/6b/2e346bacee9331198b7879a6ef521174.jpg',
                    'https://i.pinimg.com/736x/5d/f5/7e/5df57e4c00a9003ce5e76eb32e39f1ae.jpg',
                    'https://i.pinimg.com/736x/08/4c/8c/084c8c2677b7be404c32fbafc1417f69.jpg',
                    'https://i.pinimg.com/736x/46/59/24/465924b4ee1be8c4ae0742c7f2dbe6f5.jpg',
                    'https://i.pinimg.com/1200x/b3/b8/87/b3b88780c28e7a1f910cb27b1f186158.jpg',
                    'https://i.pinimg.com/1200x/d5/ee/ec/d5eeec5ff541465ceb28170163581f00.jpg',
                    'https://i.pinimg.com/736x/66/aa/59/66aa59e3f5ac8e77d0fd3d84b2fb0442.jpg',
                    'https://i.pinimg.com/1200x/79/29/fc/7929fcf2f062c8855768c6d1217213ec.jpg',
                    'https://i.pinimg.com/736x/e6/07/f4/e607f49a67a11f5ed457ec67d6519bb9.jpg',
                    'https://i.pinimg.com/736x/e6/a8/74/e6a8744d1d8fa6718903903bca91ed9e.jpg',
                    'https://i.pinimg.com/736x/da/45/3e/da453e9412699644e32fb0e8363bdca9.jpg',
                    'https://i.pinimg.com/736x/e3/ae/8c/e3ae8cc758922a7c2bb8fb97769e5d16.jpg',
                    'https://i.pinimg.com/736x/e7/f4/97/e7f49789cdc4d2d7cf60bd0b3806a010.jpg',
                    'https://i.pinimg.com/736x/fd/4e/27/fd4e272b09a12d847a428725526c8cbc.jpg',
                    'https://i.pinimg.com/1200x/cd/54/7d/cd547dcf78e7e16afe72aff8d2b811e5.jpg',
                    'https://i.pinimg.com/736x/75/8e/cf/758ecfae67ced5e6986cffd89ae9eea6.jpg',
                    'https://i.pinimg.com/1200x/ca/58/59/ca58596d3bd5b4c2e41f2c3236571899.jpg',
                    'https://i.pinimg.com/736x/0c/09/75/0c09755b4924d8452a48fe2f1dce42be.jpg',
                    'https://i.pinimg.com/1200x/41/a0/47/41a0472f7f429d65614e0f1448a63b80.jpg',
                    'https://i.pinimg.com/1200x/bc/ad/27/bcad275b5967e5a054f0df5cc38d1401.jpg',
                    'https://i.pinimg.com/1200x/a2/a2/c8/a2a2c848bf776077c13c968f47e5c215.jpg'
                
                ],
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
                'images': [
                    'https://dienlanhthinhphat.com.vn/wp-content/uploads/2023/09/thinh-phat-Tong-quan-ve-tu-lanh-side-by-side-la-gi.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSKjr5d1YpSN4Ex1O_CC0ewEq11mzodgiPNYQ&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQgY8_6Cm_rV_q1jog52okzYn0eHcTnkJUXog&s',
                    'https://uuvietsolutions.vn/wp-content/uploads/2025/01/tu-lanh-side-by-side-va-tu-lanh-4-canh-1-1024x1024.png',
                    'https://dienmaysieure.vn/wp-content/uploads/2024/11/tu-lanh-lg-inverter-641-lit-side-by-side-lsi63blma-1-638647747978087898-700x467-1.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTKkUdqA0FOzdE2I_0X5EmdG5fgdFojrU4xrw&s',
                    'https://www.electrolux.vn/globalassets/importimageproduct/original-first-image/ese5401a-bvn-img-fr-1500x1500.png?width=464',
                    'https://www.electrolux.vn/globalassets/d2c-vn/refrigerators/vn-ese5401a-bvn-front-1500x1500-min-upright-refrigerator-open.png?width=464',
                    'https://dienmaylepham.vn/wp-content/uploads/2024/11/z5462342417131_3e60b82d6cb1d9e246e56c9bd60ccd75-3.jpg',
                    'https://haingan.vn/wp-content/uploads/2023/12/2-4.jpg',
                    'https://bepkhanhtrang.vn/wp-content/uploads/2025/07/tu-lanh-side-by-side-kaff-kf-bcd523w-2-canh-mo-tren-2-ngan-rut-duoi-1599191834-1.jpg',
                    'https://bizweb.dktcdn.net/thumb/large/100/386/618/products/gr-d257mc.jpg?v=1716451611767',
                    'https://i.pinimg.com/736x/75/8e/cf/758ecfae67ced5e6986cffd89ae9eea6.jpg',
                    'https://i.pinimg.com/1200x/5c/01/c6/5c01c68aff9dc3ea835bf42a119992de.jpg',
                    'https://i.pinimg.com/1200x/b7/4d/83/b74d83e6007d67ad04328c2e36ecea5d.jpg',
                    'https://i.pinimg.com/1200x/09/6d/9e/096d9ed953480c23e1e79e30bd058ccb.jpg',
                    'https://i.pinimg.com/1200x/0a/0c/c4/0a0cc44d18a707ed1d301d4f62a3ede2.jpg',
                    'https://i.pinimg.com/1200x/b3/b8/87/b3b88780c28e7a1f910cb27b1f186158.jpg',
                    'https://i.pinimg.com/1200x/9d/9a/d7/9d9ad723039ed5cc47bab4b865167185.jpg',
                    'https://i.pinimg.com/736x/4e/bc/59/4ebc59f33185c9fc1cfd813e063dc6c2.jpg',
                    'https://i.pinimg.com/736x/e7/2b/19/e72b1970ad927b5f19c2111c6fec9cba.jpg',
                    'https://i.pinimg.com/736x/cc/44/dc/cc44dca5877e51005195b7fbdda8c55f.jpg',
                    'https://i.pinimg.com/736x/8f/3f/36/8f3f3647733265aa5d037d8eb8640005.jpg',
                    'https://i.pinimg.com/1200x/47/f3/62/47f362b890c83cd1bd9268af4c4e75ba.jpg',
                    'https://i.pinimg.com/736x/a4/24/4c/a4244ca44adf52706c7550edc945ae93.jpg',
                    'https://i.pinimg.com/736x/fd/57/0d/fd570d000def81927ba0ced587cddacb.jpg',
                    'https://i.pinimg.com/736x/ee/f6/0b/eef60b5b3ed4ae2907e1e55fd36c742d.jpg',
                    'https://i.pinimg.com/736x/f5/96/66/f596666330e7252f22a7a82d23ad558e.jpg',
                    'https://i.pinimg.com/736x/b9/56/8e/b9568e55e1660d610075fa5c79145235.jpg',
                    'https://i.pinimg.com/1200x/bb/bc/b1/bbbcb16c4c03a61d5830d597145e9efa.jpg',
                    'https://i.pinimg.com/1200x/9e/d1/1c/9ed11cbfce8f040027ac135a6c885a5c.jpg',
                    'https://i.pinimg.com/736x/e6/d1/df/e6d1df7df4023b707474287f11dbc44f.jpg',
                    'https://i.pinimg.com/1200x/2e/2b/eb/2e2beba24393ac9801c0efab2bf6a8bb.jpg'
                ],
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
                'images': [
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR1ysMD88EddPQhVsB9tOmWfYgJJPyvKtuacA&s',
                    'https://aloma.vn/tai-len/2024/05/tu-lanh-mini-28lit-SAST-BCD28L-gia-dung-aloma-12.jpg',
                    'https://kithome.com.vn/wp-content/uploads/2025/05/d073bebb-tu-lanh-mini-co-ngan-da.jpg',
                    'https://phuchoa.com.vn/wp-content/uploads/2024/08/review-tu-lanh-mini-Aqua-AQR-D59FA-BS.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRJXBJ9ZuBYxb9QncbdTDnko3AiAXMrnzzxGw&s',
                    'https://cdn.tgdd.vn/Files/2022/05/19/1433690/tu-lanh-mini-co-ngan-da-khong-top-tu-lanh-mini-dang-mua-5.jpg',
                    'https://bizweb.dktcdn.net/thumb/large/100/465/278/products/tu-lanh-aqua-90-lit-aqr-d100fa-bs-1.jpg?v=1724906570673',
                    'https://dienmaysaigon.com/wp-content/uploads/2022/05/AQ_0058_D59FA.jpg',
                    'https://cdn2.fptshop.com.vn/unsafe/1920x0/filters:format(webp):quality(75)/tu_lanh_mini_gia_duoi_2_trieu_fbb1cb01c3.jpg',
                    'https://bizweb.dktcdn.net/100/383/169/products/fr91cd.jpg?v=1672302366507',
                    'https://i.pinimg.com/1200x/64/3f/e6/643fe6ea82ac15204b5538ddd6edfae8.jpg'
                    'https://i.pinimg.com/1200x/c0/af/00/c0af00937acb00e14cd614b54af102b9.jpg'
                    'https://i.pinimg.com/1200x/e1/48/de/e148dec992b827e3fda9d8d88443a9d3.jpg'
                    'https://i.pinimg.com/736x/09/e4/73/09e473b86ed3150525c7a4f9cdc81a3f.jpg'
                    'https://i.pinimg.com/736x/63/26/3a/63263a81cec88882297bf75e42dbd2f6.jpg'
                    'https://i.pinimg.com/736x/a1/46/c8/a146c890f6875a1cda777c4cef179af7.jpg'
                    'https://i.pinimg.com/736x/f2/c1/3c/f2c13c49ab88cf7f63346e43e885725a.jpg'
                    'https://i.pinimg.com/736x/a0/10/00/a01000437aafe5242ab56557660dff0e.jpg'
                    'https://i.pinimg.com/736x/bd/a2/09/bda20939db70698d7e28debf2999e8ae.jpg'
                    'https://i.pinimg.com/736x/eb/ba/9b/ebba9b73e4f51123b386972c92ccd51b.jpg'
                    'https://i.pinimg.com/1200x/df/ef/9b/dfef9b846cba4f9f43bd19e1c3476dac.jpg'
                    'https://i.pinimg.com/736x/19/ce/d9/19ced923ae2af20dd5cd88546061162a.jpg'
                    'https://i.pinimg.com/1200x/d3/89/f9/d389f958549fd78da8fee83b76570622.jpg'
                    'https://i.pinimg.com/736x/02/af/5b/02af5b2b472477055346f4e95d96fd45.jpg'
                    'https://i.pinimg.com/1200x/63/4c/29/634c29468f1d4226b21476d3232ad906.jpg'
                    'https://i.pinimg.com/736x/3c/ef/fb/3ceffbab5b2fdb53a35e524fdd7fe4fc.jpg'
                    'https://i.pinimg.com/1200x/fb/36/d9/fb36d9b1e7985c7944e86aacef6126f4.jpg'
                    'https://i.pinimg.com/736x/6a/df/5e/6adf5ed46053438e9f01a698be8748e0.jpg'
                    'https://i.pinimg.com/736x/91/08/83/910883a4cbf2c94990e94b04383cf94d.jpg'
                    'https://i.pinimg.com/736x/14/2f/a1/142fa1c987f00f7da359bf7c9ce0c863.jpg'
                ],
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
                'images': [
                    'https://dienlanhthinhphat.com.vn/wp-content/uploads/2024/04/thinh-phat-Tim-hieu-ve-tu-lanh-co-cau-tao-la-gi.jpg',
                    'https://dienmaybanre.com/images/products/2024/01/04/original/tu-lanh-hitachi-inverter-464-lit-multi-door-hr4n7520dswdxvn-4_1704341812.jpg',
                    'https://media3.bosch-home.com/Images/400x300/19526229_Bosch_Refrigeration_French_Door_Familypage_VP2_1_1600x1200.jpg',
                    'https://cdn.tgdd.vn/Files/2021/09/02/1379688/loi-ich-tu-ngan-rau-khong-lo-tren-tu-lanh-panasonic_730x411.jpg',
                    'https://bizweb.dktcdn.net/thumb/medium/100/175/569/products/lfb61blgai.png?v=1742181632040',
                    'https://st.meta.vn/Data/image/2022/09/19/tu-lanh-mitsubishi-mr-cx35em-brw-v-inverter-272-lit.jpg',
                    'https://st.meta.vn/Data/image/2022/06/20/tu-lanh-mitsubishi-mr-cx35em-brw-v-inverter-272-lit-1.jpg',
                    'https://dienmayngohoang.com/image/cache/catalog/2023/07/z4483557772750-7bf3e6283ab18178aafa766db9ad9958-0x0.jpg',
                    'https://bizweb.dktcdn.net/thumb/large/100/380/176/products/600x-9003-ps-jpg.webp?v=1637133564220'
                ],
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
                'images': [
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT-CcNhT1rLsXStHDvQts49wJCbhEgELNUB5w&s',
                    'https://product.hstatic.net/200000335975/product/0_6f7ae81f552a471a9c0271bfabaed982_master.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQMUK_RrNFpfUnO0yuHdRb0d3d2zQ8ng_uUoQ&s',
                    'https://dienmaybanre.com/images/products/2022/03/08/large/may-giat-electrolux-inverter-ewf1024p5wb_1646735315.jpg',
                    'https://dienmayrenhat.com.vn/wp-content/uploads/2025/10/WW10DG6U34LBSV.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTX9IjPS55P_SLsVVDkQfvybo0L_uT9dsOgHQ&s',
                    'https://ctluxhome.vn/Upload/san-pham/may-giat-may-say/may-giat/2022/wat24480sg/anh-may-giat-wat24480sg_2000x2000.jpg',
                    'https://kinghome.vn/data/products/may-giat-electrolux-8kg-ultimatecare-500-ewf8025cqsa-king-home.jpg1662378615',
                    'https://suachuadienlanhhanoi.com.vn/wp-content/uploads/2024/04/uu-nhuoc-diem-cua-may-giat-cua-truoc.jpg',
                    'https://cdn2.fptshop.com.vn/unsafe/1920x0/filters:format(webp):quality(75)/co_nen_mua_may_giat_cua_truoc_7b33863dc8.jpg'
                ],
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
                'images': [
                    'https://cdn2.fptshop.com.vn/unsafe/1920x0/filters:format(webp):quality(75)/may_giat_aqua_ban_chay_nhat_thumb_ed984757af.png',
                    'https://dienmay247.com.vn/wp-content/uploads/2024/06/may-giat-lg-9-k_main_331_1020.png.webp',
                    'https://dienmaythienphu.vn/wp-content/uploads/2025/11/47cb846b3d66ff7d41112c4cca2b749d-1.jpg',
                    'https://magiamgia.com/wp-content/uploads/2019/02/may-giat-cua-truoc-inverter-electrolux-ewf12938.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRsCDK1YKp-ugGBlKizH4Th3nWsZGAddO0Idg&s',
                    'https://cdn.tgdd.vn/Products/Images/1944/236125/giat-hoi-nuoc-hygiene-steam.jpg',
                    'https://anhchinh.vn/media/product/12197_0.jpg',
                    'https://dienmaythiennamhoa.vn/static/images/Hinh-cam-nang/may-giat-cua-tren.jpg',
                    'https://www.casper-electric.com/wp-content/uploads/2023/10/may-giat-cua-tren-ecowash-WT-8NG2-03.jpg'
                ],
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
                'images': [
                    'https://cdn.tgdd.vn/Products/Images/1944/236189/may-giat-say-say-samsung-11kg-wd11t734dbx-sv-thumb-600x600.jpg',
                    'https://cdn.tgdd.vn/Products/Images/1944/304209/may-giat-say-toshiba-inverter-twd-bm135gf4v-mg-070823-042002-600x600.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRxV5npU-f_P4Dvc31X06xAl0hp3BkU7bWMZQ&s',
                    'https://cdn.tgdd.vn//News/946533//May-giat-hoi-nuoc-la-gi-uu-nhuoc-diem-cua-may-giat-hoi-nuoc-4-730x414.jpg',
                    'https://cdn.tgdd.vn/Products/Images/1944/326444/may-giat-say-toshiba-inverter-giat-10-5-kg-say-7-kg-twd-t21bu115uwv-mg-thumb-1-600x600.jpg',
                    'https://cdnv2.tgdd.vn/mwg-static/common/News/749976/co-nen-mua-may-giat-say-4.jpg',
                    'https://cdn.tgdd.vn/Products/Images/1944/319846/may-giat-say-lg-inverter-giat-12kg-say-7kg-0-600x600.jpg',
                    'https://dienmaybanre.com/images/products/2022/08/19/original/may-giat-say-panasonic-na-s056fr1bv-inverter-105-kg-1_1660901643.jpg',
                    'https://bizweb.dktcdn.net/thumb/1024x1024/100/386/618/products/may-giat-say-samsung-wd14bb944dgmsv-1-2.jpg?v=1701226002940',
                    'https://cdn11.dienmaycholon.vn/filewebdmclnew/DMCL21/Picture/News/News_expe_7513/7513.png?version=170116'
                ],
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
                'images': [
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRN6VY9YYDEVefnrgcAvPOXpRH9-3-U_4Q7bg&s',
                    'https://images.samsung.com/is/image/samsung/p6pim/vn/feature/others/vn-feature-wd8000dk-543281679?$FB_TYPE_A_MO_JPG$',
                    'https://www.electrolux.vn/globalassets/importimageproduct/2026-jan-vn/edh803j5wc-img-vn.jpg?width=464',
                    'https://bephungphu.com/wp-content/uploads/2023/10/may-say-beko-da9112rx0mb-6.png',
                    'https://www.electrolux.vn/globalassets/importimageproduct/2026-jan-vn/edh902r9sc-img-vn.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcToqrAVg0aeev85obF7VhJWff-t4vg8lAlypw&s',
                    'https://thegioidodung.vn/wp-content/uploads/2016/10/may-say-quan-ao-samsung-co-dieu-khien-khung-inox-thang.jpg.webp',
                    'https://kinghome.vn/data/products/500/may-say-quan-ao-electrolux-eds7552-1.jpg',
                    'https://bizweb.dktcdn.net/thumb/large/100/425/687/products/d6-4c38c6b6-fea0-46c3-8e4a-5388f91c08bb.jpg?v=1763948977970'
                ],
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
                'images': [
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR92jAki9IaZZp_nYexCeQXFmVhfdPDR-ziaQ&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQnDaAdDsR5uBaWHotOqkhZPa9nQ60GWykhGQ&s',
                    'https://cdn2.fptshop.com.vn/unsafe/1920x0/filters:format(webp):quality(75)/dieu_hoa_daikin_12000_1_chieu_inverter_thumb_4974c52c0c.png',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR2r5bUuJV1zewYy3vkREdZxeKydQoeJiIhKA&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRpGAUJQmIyFu_U0gR2b86m4acX5cgaBB4ZUw&s',
                    'https://cdn.mediamart.vn/images/uploads/news/202510/dieu-hoa-coex-1-chieu-inverter-1hp-9000b_i21322.webp',
                    'https://cdn11.dienmaycholon.vn/filewebdmclnew/public//userupload/images/may-lanh-inverter-la-gi-1.jpg',
                    'https://dienmaythudo.vn/wp-content/uploads/2020/02/Kry2S6.png'
                ],
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
                'images': [
                    'https://cdn.tgdd.vn//News/824169//panasonic-cu-cs-yz12wkh-8-writeee-7-730x405.jpg',
                    'https://cdn.tgdd.vn/Products/Images/2002/236419/Slider/1-1020x570.jpg',
                    'https://cdn.tgdd.vn//News/824169//daikin-fthf25vavmv-160421-0400080-730x408.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRNYtN9C_xTbRIHYec42bJ3cEzMF6tJXiojSQ&s',
                    'https://dienmayphuckhanh.vn/wp-content/uploads/2025/12/dieu-hoa-daikin-2-chieu.jpg',
                    'https://cafefcdn.com/203337114487263232/2023/11/24/photo-1-1700793081924703631333-17007930964531506153782-1700813903534-1700813903641632910135.jpg',
                    'https://www.lg.com/lk/images/AC/S3NQ18KL2FA/S3NQ18KL2FA_Wall-Air-Conditioners_Semi-R_2018_Feature_07_1_SlimDesign_D.jpg',
                    'https://bizweb.dktcdn.net/thumb/1024x1024/100/412/539/products/5d2nv7.jpg?v=1611215842553'
                    
                ],
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
                'images': [
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTtxbzB1RxiHJrTAq-rGdMuR765UajtcGRtAQ&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRKNGoxNPQEissQkCgNXOsv9kjhOGQG8iehRQ&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ7qdmX32JF2f2PXE4d1ArQtU7NZ43f-YZabg&s',
                    'https://dienmaythienphu.vn/wp-content/uploads/2025/11/fdf125csv-s5fdc125csv-s5-1.png',
                    'https://dienmaythienphu.vn/wp-content/uploads/2025/05/bia-cay-lg752025-1.jpg',
                    'https://daikinvietnam.co/wp-content/uploads/2021/07/dieu-hoa-tu-dung-daikin-1-chieu-khong-inverter.jpg',
                    'https://daikinvietnam.co/wp-content/uploads/2024/05/FVC140AV1V-RC140AGY1V.jpg',
                    'https://cdn.tgdd.vn//News/1118989//Nen-mua-dieu-hoa-tu-dung-cua-hang-nao-tot-nhat-hien-nay-3-730x517.jpg'
                ],
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
                'images': [
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTpJA3Tqr9uEVde9FRdZBaChW1SO6tRJ01JpA&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS_lw11cdXuzXVNvrzwKqhNCoq6IO4p3tLN-Q&s',
                    'https://mi-lux.vn/wp-content/uploads/2025/05/Gradient-xanh-duong-don-gian-de-thuong-khung-san-pham-dang-Instagram-23.png',
                    'https://mi-lux.vn/wp-content/uploads/59.png',
                    'https://mi-lux.vn/wp-content/uploads/2025/05/Gradient-xanh-duong-don-gian-de-thuong-khung-san-pham-dang-Instagram-2.png',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQVsZNc8tR1pQjfAqVDNt0N0YscjWj8qEsgGQ&s',
                    'https://img.gigadigital.vn/image/1725596848355-may-loc-khong-khi-lg-puricare-360-hit-as60ghwg0-ban-quoc-te-6.jpg',
                    'https://cdn.khongkhixanh.vn/media/lg%20as65gdwh0/m%C3%A1y%20l%E1%BB%8Dc%20kh%C3%B4ng%20kh%C3%AD%20lg%20puricare%201%20t%E1%BA%A7ng%20as65gdwh0%20safeplus%20kh%C3%B4ng%20kh%C3%AD%20xanh%20%E1%BA%A3nh%201.jpg',
                    'https://product.hstatic.net/200000547251/product/may-loc-khong-khi-lumias-bulma_049b5b366d924e7a8277746770744d8c_master.png',
                    'https://maylockhongkhitot.net/wp-content/uploads/2019/03/sharp-kcb70.jpg'
                ],
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
                'images': [
                    'https://cdn.tgdd.vn//News/1042485//cong-nghe-plasmacluster-ion-tren-may-loc-khong-khi-1-730x405.jpg',
                    'https://cdn.tgdd.vn//News/1042485//cong-nghe-plasmacluster-ion-tren-may-loc-khong-khi-3-730x405.jpg',
                    'https://reviewmaylockhongkhi.com/wp-content/uploads/2025/06/cong-nghe-plasmacluster-ion-3.jpg',
                    'https://cdn2.fptshop.com.vn/unsafe/Uploads/images/tin-tuc/137506/Originals/Plasmacluster-05.jpg',
                    'https://novadigital.net/wp-content/uploads/1-405.jpg',
                    'https://bizweb.dktcdn.net/thumb/large/100/465/278/products/1-1.jpg?v=1680514200240'
                ],
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
                    'images': [
                        'https://droppii.xyz/wp-content/uploads/2025/10/robot-hut-bui-lau-nha-ku-ppr3006-6.jpg',
                        'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR3qySjw1UQMA8kpQPyOO0bh_ZRlWx41cpBzg&s',
                        'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRt8QjNQR1k5JguZI4djC8KYDk1nVqX-FPfjw&s',
                        'https://cdn.tgdd.vn//News/1418736//cac-dieu-huong-tren-robot-hut-bui-3-min-730x500.jpg',
                        'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTLuHidtcHQlLTN_46NV9Nc1QuselrzdqfRgw&s',
                        'https://mivietnam.vn/wp-content/uploads/2025/05/jdhjhdjahs23423.jpg',
                        'https://mivietnam.vn/wp-content/uploads/2025/11/aqua-10-pro-track-1-1.jpg',
                        'https://homego.vn/Data/upload/images/Demax/s300.jpg'
                    ],
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
                'images': [
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTjTv3c0D1WTlY5SF4hNKS4UTXYSEhQau5fYA&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQsmWdszBKF9L-Xgm6xNKwg61zCFeJDkReF9g&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTGA4sZCmVtbv-X0yu8WJTSn3-Htm9o6-TMxg&s',
                    'https://down-vn.img.susercontent.com/file/55db3548602fef1ac667acf1c786d086',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSqzscYUoAo3zYou3ce23DoWGDEop-kKXsUog&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTq3CGwN8IbXgUhw-5WwBF504J7GNJB2Bf00w&s',
                    'https://hakawa.vn/wp-content/uploads/2023/11/may-hut-bui-k7.webp',
                    'https://mivietnam.vn/wp-content/uploads/2024/11/z7083959627791_5a602e1f55b3eae18980e08ac78c4361.jpg'
                ],
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
                'images': [
                    'https://maycongnghiepdaiviet.com/thumb/750x750/1/upload/hinhthem/mayhutbuicongnghiepdavicleandv115jphepa-6925.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSfKWUqnV4V0Uf7Fc4Xyo9mx0vmpucCtunKew&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSyl6dm5mlhXqO47GaHjVV4IXKmivyWIvcrpg&s',
                    'https://yenphat.vn/storage/2020/02/21/7576-may-hut-bui-phong-sach-gp127-hepa-iso5-2.webp',
                    'https://kumisai.vn/storage/photos/18/may-hut-bui-cong-nghiep-kumisai-kms70h-hepa.jpg',
                    'https://mediamart.vn/images/uploads/2024/5a25ab72-0b45-42db-8daf-08366ba0769f.png',
                    'https://hanhtinhxanh.com.vn/media/catalog/product/cache/4/image/800x800/5e06319eda06f020e43594a9c230972d/m/a/may_hut_bui_sc-603w_1/htx-m%C3%A1y-h%C3%BAt-b%E1%BB%A5i-c%C3%B4ng-su%E1%BA%A5t-l%E1%BB%9Bn-gi%C3%A0nh-cho-khu-c%C3%B4ng-nghi%E1%BB%87p-sc-603-33.jpg',
                    'https://dienmay248.vn/vnt_upload/product/08_2024/z5638696111327_e258abc21e4801f2476cffa88492f96b.jpg',
                ],
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
                'images': [
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQxD6qUhEiGgPsQV5DBGccsX6S8e2610k1E7Q&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQGkW0mAXJP5q0sksqqoUBMa4ZdQUxuSyMANQ&s',
                    'https://meta.vn/Data/Image/2025/09/18/lo-vi-song-sharp-r-205vn-s-1.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRqHPRypzzvfmaFF54QlmZDziraQod33ItRcw&s',
                    'https://cdn11.dienmaycholon.vn/filewebdmclnew/DMCL21/Picture/News/News_expe_13430/13430.png?version=150248',
                    'https://bephungphu.com/wp-content/uploads/2024/06/lo-vi-song-hap-nuong-panasonic-nn-ds59nbyue.png',
                    'https://bizweb.dktcdn.net/100/435/504/products/my5mby.png?v=1667787766987',
                    'https://bizweb.dktcdn.net/thumb/1024x1024/100/395/483/products/lo-vi-song-dien-tu-co-nuong-sharp-r678vnw-the-phan-home-01.jpg?v=1626160624267'
                ],
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
                'images': [
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRpOG-hwiIiqDzfv9GVAkR-q814zprIrP97wg&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQdWQp4c8BmCMw3s4K9kujUD3ArlsWoHqK5yw&s',
                    'https://cdn2.fptshop.com.vn/unsafe/1920x0/filters:format(webp):quality(75)/1_0da4aa7caa.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSLM_Kji3oRZlSZPDbQ02_6Q5VCD6_ASuKDHw&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQnsJfo_Gr-eZxTao5JeA7c20A2l9mcYL3Okw&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSECCYd4M5oG9NhKwIE5WAIu8rStCKujOg2NQ&s'
                ],
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
                'images': [
                    'https://unie.com.vn/wp-content/uploads/2021/09/cong-nghe-chien-dau-rapid-air.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT1_eq9Sg0EdqVFloyfIBRvgYfKV_u5olCvJA&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQZaj7Xqz2iruVkJzpSUrIQ-DWdUo50IYyAqA&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSzuBKMmX7wy6pESy7LLJNTwwWR-RbZKUm2qw&s',
                    'https://sunhouse.com.vn/pic/news/images/1-cong-nghe-noi-chien-khong-dau.jpeg',
                    'https://bizweb.dktcdn.net/100/404/512/files/3-162aa362-e8fb-45b7-9a21-d355baab968b.jpg?v=1708435562758'
                ],
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
                'images': [
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTnomS-IANNZmpnYMV8R0JMCIzXebK-s_Lhcw&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQC-fSXypmwqFsfy0yc2FnWE6qbEzhNT99U3g&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRBqclbUzKVevZoAj-E8KThIZHmlkvaBeai3Q&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTr91gyza-Zy7HjNyiVVln8c_WnbyF1DQAT4A&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSBY9umTm2pSerAy-6u06EaMiwyOhYkusTyUg&s',
                    'https://cdn.tgdd.vn/2025/11/timerseo/234841.jpg'
                ],
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
                'images': [
                    'https://hagaco.vn/wp-content/uploads/2022/06/noi-thuy-tinh-dung-tren-bep-hong-ngoai.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQxku-_ai71DaU0Foc2sEwVc4Dsmpe9vL30Hg&s',
                    'https://www.kaffvietnam.vn/image/cache/catalog/sanpham/bep-dien-tu/bep-hong-ngoai-doi-nhap-khau-kaff-kf-073cc-2-600x425-1400x875.jpg',
                    'https://cdn11.dienmaycholon.vn/filewebdmclnew/public/userupload/files/news/gia-dung/bep-hong-ngoai-dung-duoc-tat-ca-cac-loai-noi.jpg',
                    'https://cdn2.fptshop.com.vn/unsafe/1920x0/filters:format(webp):quality(75)/2023_3_14_638143824938718749_bep-hong-ngoai-co-ken-noi-khong-1.jpg',
                    'https://cdn.tgdd.vn/Products/Images/3305/316814/bep-hong-ngoai-crystal-p-27-1-700x467.jpg'
                ],
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
                'images': [
                    'https://thegioidodung.vn/wp-content/uploads/2025/12/bep-tu-don-daikiosan-db101-7.jpg',
                    'https://thegioidodung.vn/wp-content/uploads/2025/07/bep-tu-don-kidosu-kd-bt129-5.jpg',
                    'https://thegioidodung.vn/wp-content/uploads/2025/07/bep-tu-korichi-krc-3381-7.jpg',
                    'https://cdn.tgdd.vn/2026/01/timerseo/312917-600x600-1.png',
                    'https://product.hstatic.net/200000700229/product/6727_0193e5b7be104be38cc4c879e8f48424_master.png',
                    'https://product.hstatic.net/200000700229/product/icb-6729-01_47e71fa53e7e425596835ef56b4681b4_master.jpg'
                ],
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
                'images': [
                    'https://cdn.tgdd.vn/Products/Images/1985/241898/TimerThumb/241898-800x800-2.png',
                    'https://mitomo.com.vn/wp-content/uploads/2026/01/may-xay-sinh-to-cao-cap-mitomo-pro-ans-3380b-13.png',
                    'https://mitomo.com.vn/wp-content/uploads/2026/01/may-xay-sinh-to-cao-cap-mitomo-pro-ans-3380b-13.png',
                    'https://mitomo.com.vn/wp-content/uploads/2026/01/may-xay-sinh-to-cao-cap-mitomo-pro-ans-3380b.png',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR3XA0lx3X0DRzmV4KgxT56SHQY2eMoXZeJ3w&s',
                    'https://cdn.tgdd.vn/2023/06/CookRecipe/CookTipsNote/top-5-may-xay-da-nang-nhat-ban-ben-dep-chat-luong-tipsnote-800x450-1.jpg'
                ],
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
                'images': [
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSARIWp0YYKaVTG1_pi17Q7k3_y3SC497nS_g&s',
                    'https://thegioidodung.vn/wp-content/uploads/2020/05/may-ep-hoa-qua-cham-klarsteincua-duc-400w.jpg.webp',
                    'https://goldsun.vn/pic/ProductItem/images/M%C3%A1y%20%C3%A9p%20ch%E1%BA%ADm%20Goldsun%20GFJ4501%20(5).jpg',
                    'https://goldsun.vn/pic/ProductItem/May-ep-ch_637872769127961421.jpg',
                    'https://goldsun.vn/pic/ProductItem/images/M%C3%A1y%20%C3%A9p%20ch%E1%BA%ADm%20Goldsun%20GFJ4501%20(7)(1).jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSicBU3d8HIE8NWDJ0s6eGKLZrwVMKyIkrb4w&s'
                ],
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
                'images': [
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRrOzOhEdWLeYcPjJUkOayzyceFw_ZGFC4w3g&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRrG9nvAzlbkTWFaXqmZCNnUauCv_RJ1xSecw&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSNKJN-Wmu1WS7T3k3mL1tKKdK2rt9Lr46bmQ&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSdKzQ9W0dTkMXBnW3ZQAM8NkuqQPa1cgKc4Q&s',
                    'https://mitomo.com.vn/wp-content/uploads/2026/01/48.png',
                    'https://happyphone.vn/wp-content/uploads/2024/06/May-lam-sua-hat-Bear-PBJ-C16Q8-dung-tich-lon-1.5L-va-cong-suat-manh-me-1200W-1024x576.webp'
                ],
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
                'images': [
                    'https://bizweb.dktcdn.net/100/427/122/files/noi-com-dien-cao-cap-kalpen-r5-1-6.jpg?v=1685162062598',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSfG1DzorPtRt_jnzO3wBiRviqDAjT3WDj-gg&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQvbNixKhgS2YJystSCTmjxV9QFIJhKmHzXCw&s',
                    'https://bephungphu.com/wp-content/uploads/2025/01/noi-com-dien-tu-unie-urc612-4.jpg',
                    'https://cdn.tgdd.vn/2022/07/CookDish/8-mau-noi-com-dien-3d-hien-dai-de-nau-com-deo-thom-hap-dan-avt-1200x676-2.jpg',
                    'https://bizweb.dktcdn.net/100/427/122/files/noi-com-dien-cao-cap-kalpen-r5-1-2.jpg?v=1685162022479'
                ],
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
                'images': [
                    'https://bephungphu.com/wp-content/uploads/2025/07/noi-com-dien-cao-tan-olivo-rc900ih-6.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRaGlikyCwL_zd-v96JVM5HJ-cs_i4PaUDM7g&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ0wcXD6OXL2YLY8CIJvkgzUP981TAkgJhugA&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQO56Cl1zIHYndB5EmlYguHJWNMy2UbGOEgOw&s',
                    'https://bephungphu.com/wp-content/uploads/2025/07/noi-com-dien-cao-tan-olivo-rc900ih-3.jpg',
                    'https://bepvuson.vn/Data/upload/images/Hawonkoo/4(3).png'
                ],
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
                'images': [
                    'https://socdo.cdn.vccloud.vn/uploads/minh-hoa/noi-ap-suat-dien-da-nang-syntex-sp06-2-1757558137.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSyLbbu-uWGuBxaD-8jqMM34Uqhh1KiHSDOrg&s',
                    'https://sekavn.com/wp-content/uploads/2024/11/Noi-Ap-Suat-Dien-Da-Nang-SEKA-SK5858-02-min-scaled.jpg',
                    'https://thegioidodung.vn/wp-content/uploads/2016/08/noi-ap-suat-dien-da-nang-sunhouse-shd1562.jpg.webp',
                    'https://bephungphu.com/wp-content/uploads/2025/06/noi-ap-suat-dien-kalpen-p5-3.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRl93y1b7NfDLF20ZlVHbJ-78GMy3J_w6Qvtg&s'
                ],
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
                'images': [
                    'https://bizweb.dktcdn.net/100/435/502/products/1-86591edb-a039-49ee-a21f-c1d4bf56d846.png?v=1755851179373',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRJrUyQXmtPCHfgssF2g5zfjsog8TEUYzdtoQ&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS4RUw9iZ6iqLoPycufhZBlZcDrdjsMQ-T_qg&s',
                    'https://bizweb.dktcdn.net/100/448/192/files/cong-suat-lon.jpg?v=1681367836481',
                    'https://bizweb.dktcdn.net/100/435/504/products/7-fabe6627-12cd-4dcd-b6eb-938c62498edf.jpg?v=1657788243980',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTRBzTmuTqJFkREB2tnnJcEnH8eVKznvmFd0g&s'
                ],
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
                'images': [
                    'https://bephungphu.com/wp-content/uploads/2025/06/binh-thuy-dien-toshiba-plk-45sfwtvn-3.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTtae94uDWrT11TTrSDGH-yreq6Z7g4BbK25w&s',
                    'https://bizweb.dktcdn.net/100/350/598/products/binh-thuy-dien-toshiba-plk-45sf-wt-vn-4-5-lit-8.jpg?v=1645632428953',
                    'https://vietreview.vn/wp-content/uploads/2021/02/2-binh-giu-nhiet-Nagakawa-NAG0405-220x220.jpg',
                    'https://vietreview.vn/wp-content/uploads/2021/02/6-binh-thuy-dien-toshiba-350x350.jpg',
                    'https://cdn.tgdd.vn/Files/2016/06/10/839937/cac-chuc-nang-dac-biet-cua-binh-thuy-dien-8.jpg'
                ],
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
                'images': [
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSUUKpK80SENHVAmT5UAuy4XML4lM9UV7qllQ&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ5w8vUq_g9JZKHJKnM5aYFggrDWm6g_rvtHg&s',
                    'https://bizweb.dktcdn.net/100/500/389/products/1-d767d6a9-4504-46ff-8cf2-1697bbddd485.jpg?v=1751946498030',
                    'https://bizweb.dktcdn.net/100/500/389/files/3.jpg?v=1752804744876',
                    'https://genex.com.vn/wp-content/uploads/2024/03/May-dun-va-ham-nuoc-pha-sua-thuy-tinh-an-toan-HiQuick-2-1.png',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRThM1iD5xuPdqo8oaTzRRBjUvmw8gHOr5pSQ&s'
                ],
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
                'images': [
                    'https://bephungphu.com/wp-content/uploads/2025/07/quat-dung-sunhouse-shd7396b.jpg',
                    'https://bephungphu.com/wp-content/uploads/2025/07/quat-dung-sunhouse-shd7363b-2.jpg',
                    'https://bizweb.dktcdn.net/thumb/1024x1024/100/425/687/products/s6-71609949-2fb1-407b-bfc7-50c3ec77d0c4.jpg?v=1767689784953',
                    'https://bephungphu.com/wp-content/uploads/2025/04/quat-dung-toshiba-f-dsc50xvnw.jpg',
                    'https://bizweb.dktcdn.net/100/602/499/products/img-1770-jpeg.jpg?v=1758359094747',
                    'https://bepvuson.vn/Data/upload/images/Hawonkoo/noi_chien_hawonkoo/AC%20FAH-011-W%20(2).png'
                ],
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
                'images': [
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRZq-7dc_Y9m9CDiefQtzEF1P_nP2tvzi1Dmw&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSPj0Tfd9k9sfE6rF-7TSyDX1usHu2UsaLUzQ&s',
                    'https://bizweb.dktcdn.net/100/383/169/files/1-5.jpg?v=1686539612056',
                    'https://cdnv2.tgdd.vn/mwg-static/common/News/831809/cach-su-dung-quat-dieu-hoa-2.jpg',
                    'https://toanthuy.vn/upload/images/2023/Qu%E1%BA%A1t%20%C4%91i%E1%BB%81u%20h%C3%B2a/Daiichi%20HA-40A.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTIK2N_VQLEb7Rl-rYRh2U0cKaL0Pnnhjz2CA&s'
                ],
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
                'images': [
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSfnTKxMMNCHFC2nPkxK8r7CaWkjqu7JRddlA&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQCD1GDT7iYCAbV2oqvKESPSrv0q9_4xlHltg&s',
                    'https://mivietnam.vn/wp-content/uploads/2024/08/mivietnam-quat-khong-canh-lumias-t08-01.jpg',
                    'https://bear.com.vn/wp-content/uploads/2024/03/bear-dfs-a40j1.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTMrtIlxe-_gPMYLbdcwau199wYzBkJyYQMHw&s',
                    'https://afamilycdn.com/150157425591193600/2021/5/11/frame-12-1620719584084684297625.png'
                ],
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
                'images': [
                    'https://thudoden.vn/wp-content/uploads/2024/10/1-15.png',
                    'https://tapdoannangluongxanh.vn/wp-content/uploads/2021/02/denled_quat-tran-den-trang-tri-cao-cap-knq040-quat-vuong-gia-lap-biet-thu-3.jpg',
                    'https://thegioidodung.vn/wp-content/uploads/2022/08/quat-tran-den-trang-tri-glj-f06.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRPcK-5mtsBSC2BtRwTGZPATsVFHd8xyRSUYg&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQXq1EQbQfL6bmLE8HVsPyuMquBxuyVtHXJyg&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSNT4Eazm_Io46JBMcoyidFx-KyrOxTtimMlw&s'
                ],
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
                'images': [
                    'https://product.hstatic.net/1000069523/product/loc-ro-son-ha-10-loi-khong-tu_7df075018619440b87a2f0141758a13c.jpg',
                    'https://bizweb.dktcdn.net/100/383/169/files/9b3c06aadfba1ae443ab.jpg?v=1660751268028',
                    'https://bizweb.dktcdn.net/100/383/169/products/55b55c228532406c1923.jpg?v=1660751158863',
                    'https://maylocnuockangaroo.vn/wp-content/uploads/2021/05/maylocnuockangaroo.vn-KG100HG-KV.jpg',
                    'https://bizweb.dktcdn.net/thumb/1024x1024/100/428/291/products/maylocnuochoaphathwu1a10221dc2.jpg?v=1699407276007',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQpWJB8C2nN41pJsgc3CodBMgb3UgEZlF0VxA&s'
                ],
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
                'images': [
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQljBti1lAE8SQ9dOQHFPR4DhP7efFNSj-e9g&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRJMg-LzSuZzaYEG_nKx2kZPld1hUhjxSpwQg&s',
                    'https://file.hstatic.net/1000120355/file/may-loc-nuoc-khong-dung-dien-11_05018411757d479ab621aff40f623e9b_grande.gif',
                    'https://www.geyser.com.vn/wp-content/uploads/2024/09/geyser-ecotar-4-smart-anti-discharge.jpg',
                    'https://tiki.vn/blog/wp-content/uploads/2023/01/tieu-chi-chon-may-loc-nuoc-nano.jpg',
                    'https://cdn2.fptshop.com.vn/unsafe/Uploads/images/tin-tuc/136727/Originals/may-loc-nuoc-nano-khong-dung-dien.jpg'
                ],
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
                'images': [
                    'https://cdn.tgdd.vn//News/1503357//Thietkechuacoten-2023-01-18T013006.914-730x458.jpg',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRVvkk9zTD8T4HKin6h0AnwpBmKcHAc65uGqQ&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRwwibA0guyasNcGNgRLCi0idmWUnbcSgx1lw&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRDtGYlQQ8AEyQ9t77jXIxoYmNhiDCoAeHjbw&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR1Bw7y3o_4_SsGAFjYRjNsU4otFIK-2LEexw&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQQYd7-UkxYiawssqNZn17zHSr0asFMflSJBw&s'
                ],
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
                'images': [
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT2HOT48DJwV84pmfu4CNMLl6p6WieGfNOi9w&s',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRjeHdmLt3lDE-mBOASA6F0sNEFYaq3172mSw&s',
                    'https://www.locknlock.vn/dw/image/v2/BLBT_PRD/on/demandware.static/-/Sites-locknlock-shared-master/default/dwd8056c76/images/thumbnails/3.Small%20Appliances/2.Home%20Appliances/3.Irons&Steamers/ENI334BLK-B80023605_5.jpg?sw=800&q=69',
                    'https://bizweb.dktcdn.net/100/444/246/products/ban-ui-hoi-nuoc-philips-dst3040-70-30.jpg?v=1676447032320',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTFkuTzoGMAPKTcYco9glSNKhGccuF6-N8dNA&s',
                    'https://bizweb.dktcdn.net/100/443/453/products/12-b579bb26-9607-487a-9148-a437e4a27b78.jpg?v=1678682256063'
                ],
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
                'images': [
                    'https://vbingoo.com/wp-content/uploads/2024/11/Ban-ui-hoi-nuoc-dung-cao-cap-Mitomo-GC-899-Max.png',
                    'https://vbingoo.com/wp-content/uploads/2024/11/Ban-ui-hoi-nuoc-dung-Mitomo-GC-559.png',
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSKs9cYPLpQMCkKjtsTdnrTO9ERVSdR2BiUFQ&s',
                    'https://dienmaytonghopmiennam.com/wp-content/uploads/2024/02/ban-ui-hoi-nuoc-dung-kangaroo-kg758.jpg',
                    'https://dienmaytonghopmiennam.com/wp-content/uploads/2024/02/ban-ui-hoi-nuoc-dung-lock-lock-eni211.jpg',
                    'https://dienmaytonghopmiennam.com/wp-content/uploads/2024/02/ban-ui-hoi-nuoc-dung-electrolux-e5gs1-44mn.jpg'
                ],
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

        self.stdout.write(self.style.SUCCESS(f'\nHoàn thành tạo sản phẩm! Đã tạo:'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(self.CATEGORIES)} danh mục'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(self.BRANDS)} thương hiệu'))
        self.stdout.write(self.style.SUCCESS(f'  - {product_count} sản phẩm'))

        # Tạo reviews cho sản phẩm
        self.stdout.write(self.style.WARNING('\nBắt đầu tạo reviews...'))
        review_count = self.create_reviews_for_products()
        self.stdout.write(self.style.SUCCESS(f'  - {review_count} reviews đã được tạo'))

        self.stdout.write(self.style.SUCCESS('\n✓ Hoàn thành tất cả!'))

    def create_product(self, template, brand, category, index, **kwargs):
        size = kwargs.get('size')
        capacity = kwargs.get('capacity')
        btu = kwargs.get('btu')
        area = kwargs.get('area')
        power = kwargs.get('power')
        variant_index = 0
        format_args = {'brand': brand.name}
        if size:
            format_args['size'] = size
            # Lấy index của size trong danh sách sizes
            if 'sizes' in template:
                try:
                    variant_index = template['sizes'].index(size)
                except ValueError:
                    pass
        if capacity:
            format_args['capacity'] = capacity
            format_args['usable'] = int(capacity * 0.85)
            format_args['dry_capacity'] = int(capacity * 0.6)

            if 'capacity' in template:
                try:
                    variant_index = template['capacity'].index(capacity)
                except ValueError:
                    pass
        if btu:
            format_args['btu'] = btu
            format_args['heat_btu'] = int(btu * 0.9)
            area_map = {9000: 15, 12000: 20, 18000: 30, 24000: 40, 36000: 50, 48000: 70}
            format_args['area'] = area_map.get(btu, 25)

            if 'btu' in template:
                try:
                    variant_index = template['btu'].index(btu)
                except ValueError:
                    pass
        if area:
            format_args['area'] = area
            format_args['cadr'] = area * 8
            if 'areas' in template:
                try:
                    variant_index = template['areas'].index(area)
                except ValueError:
                    pass
        if power:
            format_args['power'] = power
            if 'powers' in template:
                try:
                    variant_index = template['powers'].index(power)
                except ValueError:
                    pass

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
        images_list = template.get('images', [])
        if images_list:
            # Lấy ảnh tại vị trí variant_index, nếu vượt quá thì lấy ảnh cuối
            image_url = images_list[min(variant_index, len(images_list) - 1)]
        else:
            # Fallback về image đơn nếu không có danh sách images
            image_url = template.get('image', '')
        product, created = Product.objects.get_or_create(
            sku=sku,
            defaults={
                'name': name,
                'slug': unique_slug,
                'description': description,
                'image': image_url,
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

    def create_reviews_for_products(self):
        """Tạo reviews cho tất cả sản phẩm"""
        from django.utils import timezone
        from datetime import timedelta

        products = Product.objects.filter(is_active=True)
        total_reviews = 0
        users_cache = {}

        self.stdout.write('Đang tạo reviews cho sản phẩm...')

        # Khởi tạo AI Sentiment Analyzer (load model 1 lần duy nhất)
        self.stdout.write('  Đang load AI Sentiment model...')
        analyzer = SentimentAnalyzer()
        self.stdout.write('  ✓ AI model đã sẵn sàng')

        for product in products:
            # Mỗi sản phẩm có từ 5-10 reviews
            num_reviews = random.randint(5, 10)

            # Phân bố rating: thiên về 4-5 sao (thực tế hơn)
            # Tỷ lệ: 5 sao (35%), 4 sao (30%), 3 sao (20%), 2 sao (10%), 1 sao (5%)
            rating_distribution = [5]*35 + [4]*30 + [3]*20 + [2]*10 + [1]*5

            for i in range(num_reviews):
                rating = random.choice(rating_distribution)
                review_data = self.SAMPLE_REVIEWS[rating]
                comment = random.choice(review_data['comments'])

                # Sử dụng AI FastText để phân tích sentiment thực sự
                # Kết hợp cả text và rating (text 60%, rating 40%)
                result = analyzer.analyze(comment, rating=rating)
                sentiment = result['sentiment']
                sentiment_score = result['score']

                # Tạo hoặc lấy user
                username = random.choice(self.SAMPLE_USERNAMES)
                if username not in users_cache:
                    user, _ = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'email': f'{username}@example.com',
                            'first_name': username.split('_')[0].title(),
                            'last_name': username.split('_')[-1].title() if '_' in username else '',
                            'is_active': True,
                        }
                    )
                    users_cache[username] = user
                else:
                    user = users_cache[username]

                # Kiểm tra xem user đã review sản phẩm này chưa
                if Review.objects.filter(product=product, user=user).exists():
                    continue

                # Tạo ngày review ngẫu nhiên trong 6 tháng qua
                days_ago = random.randint(1, 180)
                review_date = timezone.now() - timedelta(days=days_ago)

                # Tạo review
                review = Review.objects.create(
                    product=product,
                    user=user,
                    rating=rating,
                    comment=comment,
                    sentiment=sentiment,
                    sentiment_score=round(sentiment_score, 2),
                    is_approved=True,
                    is_verified_purchase=random.random() < 0.7,  # 70% là mua hàng xác thực
                    helpful_count=random.randint(0, 50),
                )
                review.created_at = review_date
                review.save(update_fields=['created_at'])

                total_reviews += 1

            # Cập nhật sentiment_score cho product
            product_reviews = Review.objects.filter(product=product, is_approved=True)
            if product_reviews.exists():
                # Cập nhật sentiment stats
                positive_count = product_reviews.filter(sentiment='positive').count()
                negative_count = product_reviews.filter(sentiment='negative').count()
                total_count = product_reviews.count()

                if total_count > 0:
                    product.sentiment_score = round((positive_count - negative_count) / total_count, 2)
                    product.positive_reviews = positive_count
                    product.negative_reviews = negative_count
                    product.save(update_fields=['sentiment_score', 'positive_reviews', 'negative_reviews'])

        return total_reviews

