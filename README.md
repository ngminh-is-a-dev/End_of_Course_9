# Bean & Leaf

Website thương mại điện tử cà phê viết bằng Django. Dự án có giao diện responsive, catalogue/tìm kiếm/lọc sản phẩm, đăng ký–đăng nhập, voucher freeship cho người dùng mới, giỏ hàng session, checkout COD, REST API và Django Admin.

## Chạy local

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_catalog
python manage.py runserver
```

Nếu PowerShell chặn script kích hoạt, chạy `Set-ExecutionPolicy -Scope Process Bypass` trong cửa sổ hiện tại, rồi kích hoạt lại. Có thể dùng trực tiếp `.\.venv\Scripts\python.exe manage.py <lệnh>` mà không cần kích hoạt môi trường.

Mở `http://127.0.0.1:8000/`. Tạo tài khoản quản trị bằng `py -3 manage.py createsuperuser`, sau đó truy cập `/admin/`.

## Tính năng

- Responsive storefront sử dụng Django Templates, CSS tùy biến và Bootstrap 5.
- Catalog có phân trang, tìm kiếm và lọc theo danh mục, giá, mức rang.
- Product detail, sản phẩm liên quan và tồn kho.
- Đăng ký, đăng nhập/đăng xuất; người dùng mới nhận `FREESHIP-xxxxx`.
- Giỏ session, điều chỉnh số lượng, áp dụng/gỡ voucher và checkout COD.
- Product REST API đọc-only: `GET /api/products/` và `GET /api/products/<slug>/`.
- SePay Payment Gateway: tạo trang QR chuyển khoản theo mã đơn, nội dung riêng và IPN xác nhận tự động.
- Django Admin cho danh mục, sản phẩm và voucher.

## API catalogue

| Endpoint | Mô tả |
| --- | --- |
| `/api/products/` | Danh sách sản phẩm đang bán |
| `/api/products/?search=arabica` | Tìm kiếm theo tên, mô tả, xuất xứ |
| `/api/products/?category=ca-phe-hat&roast=dark` | Lọc theo danh mục/mức rang |
| `/api/products/<slug>/` | Chi tiết sản phẩm |

## SePay / VietQR

Merchant ID và Secret Key test đã nằm trong `.env` cục bộ, không được commit Git. Khi deploy, thay bằng thông tin production và đặt `SITE_URL` là domain HTTPS. Trong SePay Dashboard, cấu hình IPN là `POST https://<domain>/checkout/webhooks/sepay/`. SePay gửi header `X-Secret-Key`; hệ thống chỉ xác nhận `ORDER_PAID` có invoice number/số tiền khớp. Trang `/checkout/sepay/<code>/` tạo form đã ký để SePay hiển thị QR chuyển khoản.

## Kiểm tra chất lượng

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
```

Xem [TECH_REPORT.md](docs/TECH_REPORT.md) cho kiến trúc/kỹ thuật và [DEMO.md](docs/DEMO.md) cho kịch bản trình diễn.
