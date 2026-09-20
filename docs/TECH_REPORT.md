# Bean & Leaf — Technical Report

## Kiến trúc

Ứng dụng theo Django MVT, tách theo trách nhiệm:

- `core`: layout, trang tĩnh và context processor.
- `products`: model, selector truy vấn, UI catalogue và REST API.
- `cart`: thao tác giỏ session và tính tổng đơn hàng.
- `accounts`: đăng ký/đăng nhập và signal cấp voucher chào mừng.
- `promotions`: model/admin cho voucher.
- `orders`: luồng checkout COD.

## Tối ưu dữ liệu

Catalogue dùng `select_related('category')` trong selector, detail view và API để tránh N+1 query. Hai database index phục vụ các tổ hợp filter phổ biến: `is_active + category` và `is_active + roast_level`.

## API

Django REST Framework cung cấp API đọc-only cho frontend/mobile sau này. API giới hạn sản phẩm `is_active=True`, thực hiện `select_related('category')`, hỗ trợ `search`, `category` và `roast`.

## Thanh toán SePay

Khi khách chọn SePay, server tạo `Order`/`OrderItem`, sinh mã `BL…` duy nhất và dựng form checkout đã ký HMAC để SePay hiển thị QR chuyển khoản. IPN kiểm tra `X-Secret-Key`, chỉ chấp nhận `ORDER_PAID` có invoice number/số tiền khớp; xử lý lặp lại là idempotent.

## Bảo mật và trải nghiệm

Form POST có CSRF token. Voucher gắn với tài khoản người dùng, chỉ áp dụng khi chưa dùng. Giao diện dùng Bootstrap 5 làm nền responsive, CSS thương hiệu riêng và tôn trọng `prefers-reduced-motion`.

## Kiểm thử

Bộ test hiện xác nhận catalog filter, product detail, session cart, cấp/áp dụng voucher và hai API catalogue.
