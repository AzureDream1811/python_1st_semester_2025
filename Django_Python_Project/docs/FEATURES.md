# 📦 ElectroShop - Các Chức Năng Chính

> Hệ thống E-commerce bán đồ điện gia dụng với Django + MySQL + FastText Sentiment Analysis

---

## 📋 Mục Lục

1. [Sản phẩm / Catalog](#1-sản-phẩm--catalog)
2. [Giỏ hàng](#2-giỏ-hàng)
3. [Đơn hàng](#3-đơn-hàng)
4. [Thanh toán](#4-thanh-toán)
5. [Khuyến mãi](#5-khuyến-mãi-voucher--flash-sale--combo)
6. [Đánh giá & Sentiment](#6-đánh-giá--sentiment-analysis)
7. [Dashboard quản trị](#7-dashboard-quản-trị)
8. [Thông báo & Gợi ý](#8-thông-báo--gợi-ý)

---

## 1. Sản phẩm / Catalog

### 🎯 Chức năng
Quản lý danh mục, thương hiệu, sản phẩm, hình ảnh và thông số kỹ thuật; hiển thị trang danh sách & chi tiết sản phẩm.

### 💡 Ý nghĩa cho người dùng
- Khách hàng dễ dàng tìm kiếm, duyệt và so sánh sản phẩm
- Thông tin chi tiết giúp quyết định mua hàng chính xác
- Giảm tỷ lệ trả hàng do hiểu rõ sản phẩm trước khi mua

### 📊 When / Why / How / What

| Khía cạnh | Mô tả |
|-----------|-------|
| **When** | Khi người dùng muốn duyệt, tìm kiếm hoặc xem chi tiết một sản phẩm |
| **Why** | Thông tin rõ ràng tăng tỷ lệ chuyển đổi và giảm tỷ lệ trả hàng |
| **How** | Dữ liệu sản phẩm lưu trong DB (Product, Category, Brand); Template hiển thị danh sách với bộ lọc và trang chi tiết |
| **What** | Người dùng thấy trang danh sách sản phẩm, bộ lọc theo danh mục/giá/thương hiệu, trang chi tiết với ảnh/spec/giá |

### 🔧 Models liên quan
- `Product` - Thông tin sản phẩm
- `Category` - Danh mục sản phẩm
- `Brand` - Thương hiệu
- `ProductImage` - Hình ảnh sản phẩm

---

## 2. Giỏ hàng

### 🎯 Chức năng
Thêm/xóa sản phẩm, lưu mua sau (saved for later), tính subtotal/giảm giá/tổng, áp dụng/xóa voucher.

### 💡 Ý nghĩa cho người dùng
- Gom nhiều sản phẩm trước khi thanh toán
- Kiểm tra chi phí và áp dụng mã giảm giá
- Lưu sản phẩm để mua sau khi chưa sẵn sàng

### 📊 When / Why / How / What

| Khía cạnh | Mô tả |
|-----------|-------|
| **When** | Khi người dùng chọn mua nhiều sản phẩm, muốn lưu sản phẩm hoặc áp dụng mã giảm giá |
| **Why** | Trải nghiệm checkout mượt mà giúp giữ chân khách và tăng giá trị đơn hàng trung bình (AOV) |
| **How** | Model `Cart` + `CartItem` lưu liên kết user/session; phương thức `apply_voucher()` tính toán giảm giá tự động |
| **What** | Người dùng thấy giỏ hàng với danh sách sản phẩm, tổng tiền hàng, số tiền giảm giá, tổng thanh toán |

### 🔧 Models liên quan
- `Cart` - Giỏ hàng (liên kết user hoặc session)
- `CartItem` - Sản phẩm trong giỏ

### 📝 Tính năng nổi bật
```python
# Áp dụng voucher
cart.apply_voucher(voucher)

# Tính toán tự động
cart.subtotal   # Tổng tiền hàng
cart.discount   # Số tiền được giảm
cart.total      # Tổng thanh toán
```

---

## 3. Đơn hàng

### 🎯 Chức năng
Tạo đơn hàng, lưu lịch sử, quản lý trạng thái đơn (pending → confirmed → shipping → delivered → completed), trang chi tiết đơn.

### 💡 Ý nghĩa cho người dùng
- Theo dõi toàn bộ vòng đời đơn hàng
- Biết được trạng thái giao hàng real-time
- Lịch sử mua hàng để tham khảo và mua lại

### 📊 When / Why / How / What

| Khía cạnh | Mô tả |
|-----------|-------|
| **When** | Khi người dùng hoàn tất thanh toán hoặc admin xử lý đơn hàng |
| **Why** | Đảm bảo quy trình giao nhận, chăm sóc khách hàng và minh bạch trạng thái đơn |
| **How** | `Order`/`OrderItem` + `OrderHistory` model; workflow chuyển trạng thái và ghi log tự động |
| **What** | Người dùng/admin thấy lịch sử đơn hàng, trạng thái hiện tại, chi tiết giao hàng và timeline |

### 🔧 Models liên quan
- `Order` - Đơn hàng
- `OrderItem` - Chi tiết sản phẩm trong đơn
- `OrderHistory` - Lịch sử thay đổi trạng thái

### 📈 Workflow trạng thái
```
pending → confirmed → processing → shipping → delivered → completed
                                                      ↘ cancelled
                                                      ↘ refunded
```

---

## 4. Thanh toán

### 🎯 Chức năng
Kết nối cổng thanh toán, lưu giao dịch, cập nhật trạng thái thanh toán, hỗ trợ nhiều phương thức.

### 💡 Ý nghĩa cho người dùng
- Thanh toán an toàn, tiện lợi
- Nhiều lựa chọn phương thức thanh toán
- Xác nhận thanh toán tức thì

### 📊 When / Why / How / What

| Khía cạnh | Mô tả |
|-----------|-------|
| **When** | Khi người dùng thanh toán đơn hàng (online hoặc COD) |
| **Why** | Thanh toán tin cậy là bước quyết định để hoàn tất đơn hàng |
| **How** | Form/endpoint tích hợp SDK/API của cổng thanh toán, callback để xác nhận |
| **What** | Người dùng thấy các phương thức thanh toán, xác nhận thành công/thất bại |

### 💳 Phương thức hỗ trợ
- COD (Thanh toán khi nhận hàng)
- VNPay
- MoMo
- Chuyển khoản ngân hàng

---

## 5. Khuyến mãi (Voucher / Flash Sale / Combo)

### 🎯 Chức năng
Tạo và quản lý voucher, flash sale (giảm giá sốc có thời hạn), combo deal; kiểm tra hiệu lực, giới hạn sử dụng, lưu lịch sử.

### 💡 Ý nghĩa cho người dùng
- Tiết kiệm chi phí khi mua hàng
- Trải nghiệm mua sắm thú vị với deal sốc
- Combo tiện lợi khi mua nhiều sản phẩm

### 📊 When / Why / How / What

| Khía cạnh | Mô tả |
|-----------|-------|
| **When** | Khi triển khai chương trình khuyến mãi (mùa sale, ngày lễ, mã giảm giá) |
| **Why** | Tăng tỷ lệ chuyển đổi, thúc đẩy mua thêm, điều hướng tồn kho |
| **How** | `Voucher`/`FlashSale`/`ComboDeal` model với `is_valid()` kiểm tra hiệu lực; `VoucherUsage` ghi nhật ký sử dụng |
| **What** | Người dùng thấy mã giảm giá, giá sau giảm, thông báo hợp lệ/không hợp lệ, đồng hồ đếm ngược flash sale |

### 🔧 Models liên quan
- `Voucher` - Mã giảm giá (% hoặc số tiền cố định)
- `VoucherUsage` - Lịch sử sử dụng voucher
- `FlashSale` - Giảm giá sốc có thời hạn và số lượng giới hạn
- `ComboDeal` - Combo sản phẩm

### 📝 Ví dụ Voucher
```python
# Kiểm tra voucher có hợp lệ không
if voucher.is_valid():
    cart.apply_voucher(voucher)
    # Giảm 10% tối đa 100.000đ
```

---

## 6. Đánh giá & Sentiment Analysis

### 🎯 Chức năng
CRUD review (thêm/sửa/xóa), phê duyệt review, phân tích sentiment bằng AI (FastText) kết hợp nội dung text và số sao.

### 💡 Ý nghĩa cho người dùng
- Tham khảo đánh giá từ người mua thực
- Quyết định mua hàng dựa trên phản hồi cộng đồng
- Admin giám sát chất lượng sản phẩm qua sentiment

### 📊 When / Why / How / What

| Khía cạnh | Mô tả |
|-----------|-------|
| **When** | Sau khi mua hàng, người dùng để lại đánh giá; Admin kiểm duyệt review |
| **Why** | Review ảnh hưởng lớn đến uy tín sản phẩm và tỷ lệ mua lại |
| **How** | Lưu review, chạy `SentimentAnalyzer.analyze(text, rating)`, lưu label/score; hiển thị badge sentiment |
| **What** | Người dùng thấy điểm sentiment, badge (Tích cực/Tiêu cực/Trung lập), nút sửa review của mình |

### 🔧 Models liên quan
- `Review` - Đánh giá sản phẩm
- `ReviewHelpful` - Đánh dấu review hữu ích

### 🤖 Công thức Sentiment
```python
# Kết hợp text sentiment (60%) + star rating (40%)
final_score = 0.6 × text_score + 0.4 × rating_score

# Phân loại
score > 0.2  → Positive (Tích cực)
score < -0.2 → Negative (Tiêu cực)
else         → Neutral (Trung lập)
```

### 🏷️ Sentiment Badge
| Sentiment | Màu sắc | Hiển thị |
|-----------|---------|----------|
| Positive | 🟢 Xanh lá | "Tích cực" |
| Negative | 🔴 Đỏ | "Tiêu cực" |
| Neutral | ⚫ Xám | "Trung lập" |

---

## 7. Dashboard quản trị

### 🎯 Chức năng
KPI tổng quan (doanh thu, đơn hàng, khách hàng, sản phẩm), biểu đồ theo thời gian, báo cáo khuyến mãi, top sản phẩm, so sánh kỳ trước.

### 💡 Ý nghĩa cho người dùng (Admin)
- Cái nhìn nhanh về tình hình kinh doanh
- Phát hiện xu hướng và vấn đề kịp thời
- Ra quyết định dựa trên dữ liệu

### 📊 When / Why / How / What

| Khía cạnh | Mô tả |
|-----------|-------|
| **When** | Admin truy cập để kiểm tra tình hình bán hàng, chạy chiến dịch |
| **Why** | Giúp phát hiện xu hướng, vấn đề kịp thời, tối ưu hóa chiến lược kinh doanh |
| **How** | `DashboardStatistics` service tổng hợp từ DB, endpoint cung cấp dữ liệu cho Chart.js |
| **What** | Admin thấy đồ thị doanh thu, biểu đồ trạng thái đơn, KPI cards với % thay đổi so với kỳ trước |

### 📈 KPI hiển thị
| Metric | Mô tả | So sánh |
|--------|-------|---------|
| 💰 Doanh thu | Tổng doanh thu theo kỳ | ↑↓ % vs kỳ trước |
| 📦 Đơn hàng | Tổng số đơn hàng | ↑↓ % vs kỳ trước |
| 👥 Khách hàng | Khách hàng mới | ↑↓ % vs kỳ trước |
| 🛍️ Sản phẩm | Sản phẩm mới | ↑↓ % vs kỳ trước |

### 📊 Biểu đồ
- **Revenue Chart** - Doanh thu theo ngày (Line chart)
- **Order Status Chart** - Phân bố trạng thái đơn (Doughnut chart)
- **Promotion Stats** - Thống kê voucher và flash sale

---

## 8. Thông báo & Gợi ý

### 🎯 Chức năng
Đẩy thông báo (unread/realtime), gợi ý sản phẩm liên quan, recommendations dựa trên lịch sử.

### 💡 Ý nghĩa cho người dùng
- Cập nhật nhanh về đơn hàng, khuyến mãi
- Khám phá sản phẩm phù hợp sở thích
- Không bỏ lỡ deal hấp dẫn

### 📊 When / Why / How / What

| Khía cạnh | Mô tả |
|-----------|-------|
| **When** | Khi có cập nhật đơn hàng, khuyến mãi mới, hoặc khi người dùng xem sản phẩm |
| **Why** | Giữ chân người dùng, tăng tỷ lệ mua thêm, cải thiện trải nghiệm |
| **How** | Consumer/WebSocket cho realtime notifications; Services gợi ý dựa trên lịch sử mua/xem |
| **What** | Người dùng nhận popup/badge thông báo, thấy list sản phẩm đề xuất "Có thể bạn quan tâm" |

### 🔔 Loại thông báo
- Cập nhật trạng thái đơn hàng
- Khuyến mãi mới
- Flash sale sắp bắt đầu
- Sản phẩm yêu thích giảm giá

---

## 🛠️ Công nghệ sử dụng

| Thành phần | Công nghệ |
|------------|-----------|
| Backend | Django 4.2 |
| Database | MySQL 8.0 |
| Frontend | Bootstrap 5, Chart.js |
| AI/ML | FastText (Sentiment Analysis) |
| Task Queue | Celery + Redis |
| Realtime | Django Channels |

---

## 📁 Cấu trúc Apps

```
apps/
├── accounts/       # Quản lý tài khoản người dùng
├── products/       # Sản phẩm, danh mục, thương hiệu
├── cart/           # Giỏ hàng
├── orders/         # Đơn hàng
├── payments/       # Thanh toán
├── promotions/     # Voucher, Flash Sale, Combo
├── reviews/        # Đánh giá + Sentiment
├── admin_dashboard/# Dashboard quản trị
├── notifications/  # Thông báo
├── recommendations/# Gợi ý sản phẩm
└── search/         # Tìm kiếm
```

---

## 📞 Liên hệ

**ElectroShop** - Hệ thống E-commerce đồ điện gia dụng  
Phát triển bởi: Student Project - 1st Semester 2025

---

*Tài liệu được tạo tự động - Cập nhật: Tháng 1/2026*
