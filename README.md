# Bean & Leaf

Bean & Leaf là website bán cà phê xây dựng bằng Django. Khách có thể duyệt sản phẩm, tìm kiếm và lọc catalogue, thêm hàng vào giỏ, đặt đơn thanh toán khi nhận hàng (COD), viết đánh giá và chia sẻ sản phẩm. Quản trị viên quản lý catalogue, voucher và trạng thái đơn trong Django Admin.

## Công nghệ

- Python và Django 5.2; Django REST Framework cho API catalogue.
- Django Templates, CSS tùy chỉnh và Bootstrap 5 cho giao diện responsive.
- SQLite khi phát triển; có thể cấu hình PostgreSQL bằng `DATABASE_URL`.
- Pillow xử lý ảnh; WhiteNoise phục vụ static files.

## Chạy ở môi trường local

Cần Python, pip và PowerShell. Tại thư mục có `manage.py`, chạy:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Nếu chưa có `.env`, sao chép file mẫu rồi bật chế độ phát triển. Với cấu hình mặc định, ứng dụng dùng SQLite và tự tạo `SECRET_KEY` ngẫu nhiên cho mỗi lần khởi động:

```powershell
if (-not (Test-Path -LiteralPath .env)) { Copy-Item .env.example .env }
(Get-Content .env) -replace '^DEBUG=.*$', 'DEBUG=1' | Set-Content .env
```

Chạy migration, tạo dữ liệu mẫu và khởi động server:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_catalog
.\.venv\Scripts\python.exe manage.py runserver
```

Mở [website](http://127.0.0.1:8000/). Để vào Admin, tạo tài khoản quản trị trong một terminal khác:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

Các lệnh trên gọi Python trực tiếp trong `.venv`, không cần chạy `Activate.ps1`. Bỏ qua bước tạo môi trường nếu đã có môi trường phù hợp.

`seed_catalog` tạo 3 danh mục và 8 sản phẩm mẫu. Chạy lại lệnh sẽ cập nhật một số trường sản phẩm theo dữ liệu demo, bao gồm giá và tồn kho (đặt lại tồn kho thành 25). Chỉ chạy seed trên database dùng thử.

## Sử dụng website

1. Mở [catalogue](http://127.0.0.1:8000/products/) để tìm theo tên/mô tả hoặc lọc theo danh mục, mức rang và khoảng giá. Danh sách HTML hiển thị 9 sản phẩm mỗi trang.
2. Mở trang sản phẩm để xem thông tin, hàng liên quan và đánh giá. Thêm sản phẩm vào giỏ, rồi thay đổi số lượng hoặc xóa hàng tại [giỏ hàng](http://127.0.0.1:8000/cart/). Giỏ được lưu trong session của trình duyệt.
3. Đăng ký hoặc đăng nhập để nhận và sử dụng voucher miễn phí vận chuyển. Tài khoản mới nhận voucher có mã dạng `FREESHIP-00001` (phần số lấy từ ID tài khoản). Voucher gắn với tài khoản, chỉ dùng một lần. Phí giao hàng là 30.000đ cho giỏ có hàng; voucher hợp lệ đưa phí về 0đ.
4. Tại [checkout](http://127.0.0.1:8000/checkout/), nhập tên, số điện thoại, email và địa chỉ. Phương thức thanh toán duy nhất hiện có là **COD — thanh toán khi nhận hàng**. Khách không đăng nhập vẫn có thể đặt hàng. Sau khi đặt thành công, trang xác nhận hiển thị mã đơn và giỏ được làm trống.
5. Người dùng đã đăng nhập có thể vào [hồ sơ](http://127.0.0.1:8000/accounts/profile/) để đổi ảnh đại diện, xem tối đa 20 lần đăng nhập gần nhất và các đơn được gắn với tài khoản. Đơn đặt với tư cách khách vãng lai không tự liên kết với tài khoản sau này.
6. Đánh giá sản phẩm hiển thị công khai. Người dùng đã đăng nhập có thể gửi đánh giá 1–5 sao và nhận xét tùy chọn tối đa 2.000 ký tự. Mỗi tài khoản có một đánh giá cho mỗi sản phẩm; gửi lại sẽ cập nhật đánh giá đó. Không yêu cầu đã mua sản phẩm.
7. Trang chi tiết có tùy chọn chia sẻ qua Facebook, Zalo hoặc sao chép liên kết. Đặt `ZALO_OA_ID` trong `.env` để bật widget Zalo. Metadata Open Graph dùng ảnh sản phẩm hoặc ảnh mặc định; trình xem trước mạng xã hội cần URL công khai.

## Quản lý đơn hàng

Đăng nhập tại `/admin/` bằng tài khoản superuser. Trong **Orders** (`/admin/orders/order/`), có thể tìm đơn theo mã/thông tin khách và lọc theo trạng thái. Đơn mới có trạng thái giao hàng **Đang đóng gói** (`packing`) và thanh toán **Chờ thanh toán** (`pending`).

Quản trị viên cập nhật `delivery_status` và `payment_status` riêng biệt. Các trạng thái giao hàng gồm `packing` (Đang đóng gói), `shipping` (Đang giao), `delivered` (Đã giao); trạng thái thanh toán gồm `pending` (Chờ thanh toán) và `paid` (Đã thanh toán). Đánh dấu đơn đã giao không tự ghi nhận đã thu tiền COD.

## API catalogue

API chỉ đọc và không yêu cầu đăng nhập. Các endpoint chỉ trả sản phẩm đang hoạt động (`is_active=True`):

| Endpoint | Kết quả |
| --- | --- |
| `GET /api/products/` | Mảng JSON sản phẩm |
| `GET /api/products/<slug>/` | Một object JSON theo slug |

Endpoint danh sách hỗ trợ các tham số có thể kết hợp:

| Tham số | Ý nghĩa | Ví dụ |
| --- | --- | --- |
| `search` | Tìm trong tên, mô tả và xuất xứ | `search=Laura` |
| `category` | Lọc theo slug danh mục | `category=ca-phe-hat` |
| `roast` | Lọc theo mức rang `light`, `medium`, `dark` | `roast=dark` |

API hiện trả danh sách trực tiếp, chưa phân trang và không có bộ lọc giá. Không tìm thấy sản phẩm trong danh sách trả `[]`; slug không tồn tại hoặc sản phẩm đã tắt trả HTTP 404. Gửi POST tới các endpoint này trả HTTP 405.

Ví dụ gọi API bằng PowerShell khi server đang chạy:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/products/?search=Laura&category=ca-phe-hat&roast=dark' -Headers @{ Accept = 'application/json' } | ConvertTo-Json -Depth 5
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/products/laura-coffee-blend-xam/' -Headers @{ Accept = 'application/json' } | ConvertTo-Json -Depth 5
```

Response bao gồm `id`, `name`, `slug`, `url`, `category`, `category_slug`, `description`, `price`, `roast_level`, `roast_label`, `origin`, `stock` và `is_featured`. Giá là số nguyên theo VND; danh mục được trả về dưới dạng tên và slug, không phải object lồng. API chưa trả ảnh hoặc đánh giá. Chi tiết được định nghĩa trong [serializer](products/serializers.py) và [API views](products/api_views.py).

## Cấu hình và triển khai

Các biến được đọc từ `.env` ở thư mục gốc; biến môi trường của tiến trình được ưu tiên. File `.env` không được đưa lên Git. Các biến chính:

| Biến | Mục đích |
| --- | --- |
| `DEBUG` | Dùng `1` khi phát triển local; production đặt `0` |
| `SECRET_KEY` | Production phải cung cấp khóa riêng, bí mật và ổn định. Local có thể để trống để ứng dụng sinh khóa tạm thời |
| `ALLOWED_HOSTS` | Danh sách hostname được phép, phân cách bằng dấu phẩy; bắt buộc khi `DEBUG=0` |
| `CSRF_TRUSTED_ORIGINS` | Các origin tin cậy, gồm scheme như `https://`, phân cách bằng dấu phẩy |
| `DATABASE_URL` | Tùy chọn; khi có giá trị, cấu hình database từ URL, ví dụ PostgreSQL |
| `ZALO_OA_ID` | Tùy chọn; ID Official Account cho widget Zalo |
| `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` | Có thể ghi đè thiết lập HTTPS/cookie bảo mật; mặc định bật khi `DEBUG=0` |
| `SECURE_HSTS_SECONDS` | Thời hạn HSTS; mặc định 31.536.000 giây khi `DEBUG=0`, chỉ gửi header qua HTTPS |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS`, `SECURE_HSTS_PRELOAD` | Mặc định tắt; chỉ bật khi chính sách HTTPS trên toàn domain đã được xác nhận |
| `USE_X_FORWARDED_PROTO` | Chỉ bật sau reverse proxy TLS đáng tin cậy, có cấu hình ghi đè `X-Forwarded-Proto` |

Khi triển khai, cần cấp secret và hostname thật, cấu hình HTTPS/TLS và reverse proxy phù hợp, chạy `collectstatic`, phục vụ thư mục `staticfiles/`, lưu trữ media bền vững và sao lưu database/media. WhiteNoise được bật cho static files. Ứng dụng chỉ thêm route phục vụ media khi `DEBUG=1`; cần cấu hình nơi lưu và phục vụ media cho production. `runserver` chỉ dành cho phát triển; dự án cung cấp WSGI entry point tại [config/wsgi.py](config/wsgi.py). File mẫu có thiết lập gợi ý cho môi trường triển khai; hãy chỉnh `DEBUG=1` khi dùng file đó cho local.

## Kiểm tra và tài liệu khác

Các lệnh kiểm tra thủ công:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py check --deploy
```

`check --deploy` trên cấu hình local sẽ báo các thiết lập HTTPS/DEBUG chưa bật. Đây là kiểm tra cấu hình Django, không xác minh TLS hoặc reverse proxy trên server thật. Kết quả kiểm thử và kiến trúc được trình bày trong [báo cáo kỹ thuật](docs/TECH_REPORT.md); kịch bản demo ở [docs/DEMO.md](docs/DEMO.md).
