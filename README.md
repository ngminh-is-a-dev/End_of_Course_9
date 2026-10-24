# Bean & Leaf

Website thương mại điện tử cà phê viết bằng Django: giao diện responsive dùng Django Templates, CSS tùy biến và Bootstrap 5; catalogue, giỏ hàng session, checkout COD, tài khoản, đánh giá, chia sẻ sản phẩm, REST API và Django Admin. Dữ liệu mặc định lưu trong SQLite (`db.sqlite3`).

## Cài đặt trên Windows

Chuẩn bị Python có Python Launcher (`py`), pip và PowerShell. Môi trường local đã kiểm tra dùng Python 3.14.7. [requirements.txt](requirements.txt) khai báo Django `>=5.2,<6`, Pillow `>=12`, Django REST Framework `>=3.15,<4` và python-dotenv `>=1.0,<2`; các khoảng phiên bản chưa được khóa thành một bộ phiên bản cố định.

Mở PowerShell trong thư mục chứa `manage.py` và chạy:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path -LiteralPath .env)) { Copy-Item -LiteralPath .env.example -Destination .env }
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_catalog
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

Các lệnh gọi trực tiếp Python trong `.venv`, không cần kích hoạt `Activate.ps1`. Nếu đã có `.venv` phù hợp, bỏ qua bước tạo môi trường. `createsuperuser` yêu cầu nhập tài khoản/mật khẩu trong terminal; dự án không cung cấp mật khẩu quản trị mặc định.

Mở [trang chủ](http://127.0.0.1:8000/) và [trang quản trị](http://127.0.0.1:8000/admin/). Dừng server bằng `Ctrl+C`, chạy lại bằng lệnh `runserver` ở trên.

`migrate` tạo/cập nhật cấu trúc database. `seed_catalog` tạo 3 danh mục và tạo/cập nhật 8 sản phẩm theo slug, tồn kho mẫu 25 mỗi sản phẩm. Chạy lại seed sẽ cập nhật các trường dữ liệu mẫu, gồm giá và tồn kho; dùng khi chuẩn bị demo. Ảnh sản phẩm có thể tải lên qua Admin.

## Sử dụng

1. Vào [catalogue](http://127.0.0.1:8000/products/) để tìm theo tên/mô tả, lọc danh mục, khoảng giá và mức rang. Giao diện HTML phân trang 9 sản phẩm mỗi trang, dùng `q`, `category`, `price`, `roast`; tham số API được mô tả riêng bên dưới.
2. Mở chi tiết sản phẩm để xem giá, tồn kho và tối đa 4 sản phẩm liên quan cùng danh mục. Chọn số lượng, thêm vào giỏ; vào [giỏ hàng](http://127.0.0.1:8000/cart/) để cập nhật số lượng hoặc xóa sản phẩm. Giỏ lưu trong session trình duyệt.
3. [Đăng ký](http://127.0.0.1:8000/accounts/signup/) hoặc [đăng nhập](http://127.0.0.1:8000/accounts/login/) để dùng voucher của tài khoản. Người dùng mới nhận mã dạng `FREESHIP-00001`; áp dụng/gỡ mã tại giỏ. Voucher chỉ dùng cho tài khoản sở hữu và được đánh dấu đã dùng khi tạo đơn. Phí vận chuyển hiện là 30.000đ cho giỏ có hàng, hoặc 0đ khi áp dụng voucher hợp lệ.
4. Từ giỏ sang [checkout](http://127.0.0.1:8000/checkout/), nhập họ tên, điện thoại, email, địa chỉ và đặt hàng. Checkout hỗ trợ **duy nhất COD — Thanh toán khi nhận hàng**; khách chưa đăng nhập vẫn có thể đặt hàng. Sau khi tạo đơn, trang xác nhận hiển thị mã đơn và giỏ được làm trống.
5. Khi đăng nhập, vào [hồ sơ](http://127.0.0.1:8000/accounts/profile/) để cập nhật ảnh đại diện, xem tối đa 20 lần đăng nhập gần nhất (IP/thời gian) và đơn hàng gắn với tài khoản. Đơn hiển thị tên sản phẩm đã lưu lúc mua, số lượng, tổng tiền và trạng thái giao hàng. Đơn đặt khi chưa đăng nhập không được tự gắn vào tài khoản về sau. Dùng nút **Đăng xuất** trên thanh điều hướng để thoát.
6. Tại chi tiết sản phẩm, mọi người xem được đánh giá, số lượng và điểm trung bình. Người đăng nhập được chấm 1–5 sao, viết nhận xét tùy chọn tối đa 2.000 ký tự; gửi lại sẽ sửa đánh giá của chính mình, mỗi tài khoản có một đánh giá cho mỗi sản phẩm.
7. Dùng nút Facebook, Zalo hoặc sao chép liên kết ở chi tiết sản phẩm. Để hiện widget Zalo chính thức, đặt `ZALO_OA_ID` bằng ID Official Account trong `.env`, rồi khởi động lại server. Khi chưa cấu hình, nút sao chép liên kết để chia sẻ trên Zalo vẫn hiển thị. Trang có metadata Open Graph; ảnh dùng ảnh sản phẩm hoặc [ảnh mặc định](static/images/coffee-hero.png).

### Quản lý đơn trong Admin

Đăng nhập bằng superuser tại `/admin/`. Admin quản lý danh mục, sản phẩm, đánh giá, voucher và đơn hàng. Vào danh sách **Orders** tại `/admin/orders/order/`, tìm theo mã đơn/thông tin khách hoặc lọc theo phương thức thanh toán, trạng thái thanh toán và giao hàng.

Đổi `delivery_status` ngay trong danh sách rồi lưu, hoặc mở đơn để chỉnh và lưu. Các giá trị/nhãn hiện có:

| Trường | Giá trị | Nhãn |
| --- | --- | --- |
| `delivery_status` | `packing` | Đang đóng gói |
| `delivery_status` | `shipping` | Đang giao |
| `delivery_status` | `delivered` | Đã giao |
| `payment_status` | `pending` | Chờ thanh toán |
| `payment_status` | `paid` | Đã thanh toán |

Đơn mới mặc định `packing` và `pending`. Khi đã thu tiền COD, quản trị viên có thể cập nhật `payment_status` trong trang sửa đơn. Hai trường được chỉnh riêng; đổi giao hàng sang **Đã giao** không tự đổi sang **Đã thanh toán**. Khách xem trạng thái giao hàng mới trong hồ sơ sau khi tải lại trang.

## API catalogue

API công khai, chỉ đọc; dùng `GET` lấy dữ liệu, không cần đăng nhập. Các endpoint chỉ trả sản phẩm có `is_active=True`. Base URL local: `http://127.0.0.1:8000`.

| Endpoint | Kết quả |
| --- | --- |
| `GET /api/products/` | Mảng JSON các sản phẩm đang bán |
| `GET /api/products/<slug>/` | Một object JSON sản phẩm theo slug |

| Tham số danh sách | Ý nghĩa | Ví dụ |
| --- | --- | --- |
| `search` | Tìm trên tên, mô tả, xuất xứ bằng DRF SearchFilter | `search=Laura` |
| `category` | Lọc đúng slug danh mục | `category=ca-phe-hat` |
| `roast` | Mức rang: `light`, `medium`, `dark` | `roast=dark` |

Có thể kết hợp cả ba tham số. API hiện **chưa phân trang**: response là mảng trực tiếp, không có `count`, `next`, `previous`, `results`; `page` không chia dữ liệu thành trang. Không có bộ lọc giá trong API. Không có kết quả trả `[]`; slug không tồn tại hoặc sản phẩm không hoạt động trả HTTP 404. POST không được hỗ trợ (HTTP 405).

Trong cửa sổ PowerShell khác, khi server đang chạy:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/products/?search=Laura&category=ca-phe-hat&roast=dark' -Headers @{ Accept = 'application/json' } | ConvertTo-Json -Depth 5
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/products/laura-coffee-blend-xam/' -Headers @{ Accept = 'application/json' } | ConvertTo-Json -Depth 5
```

PowerShell có thể trình bày mảng một phần tử thành object khi truyền qua pipeline. Response JSON của endpoint danh sách vẫn là mảng. Ví dụ response HTTP sau khi migrate/seed trên database mới (ID có thể khác nếu đã có dữ liệu):

```json
[
  {
    "id": 1,
    "name": "Cà Phê Laura Coffee Blend Xám",
    "slug": "laura-coffee-blend-xam",
    "url": "http://127.0.0.1:8000/api/products/laura-coffee-blend-xam/",
    "category": "Cà phê hạt",
    "category_slug": "ca-phe-hat",
    "description": "Hậu vị chocolate, đậm đà và cân bằng. Phù hợp cho espresso hoặc phin truyền thống.",
    "price": 150000,
    "roast_level": "dark",
    "roast_label": "Rang đậm",
    "origin": "Đà Lạt, Việt Nam",
    "stock": 25,
    "is_featured": true
  }
]
```

Endpoint chi tiết trả chính object bên trong mảng này. Trường được định nghĩa trong [ProductSerializer](products/serializers.py):

| Trường | Kiểu JSON / ý nghĩa |
| --- | --- |
| `id` | Số nguyên, khóa sản phẩm |
| `name`, `slug` | Chuỗi tên và slug sản phẩm |
| `url` | Chuỗi URL tuyệt đối tới API chi tiết, theo host/protocol của request |
| `category`, `category_slug` | Chuỗi tên và slug danh mục; `category` không phải object lồng |
| `description` | Chuỗi mô tả |
| `price` | Số nguyên, giá VND |
| `roast_level`, `roast_label` | Mã mức rang và nhãn tiếng Việt: Rang nhạt / Rang vừa / Rang đậm |
| `origin` | Chuỗi xuất xứ, có thể rỗng |
| `stock` | Số nguyên tồn kho |
| `is_featured` | Boolean đánh dấu sản phẩm nổi bật |

Serializer hiện không trả ảnh, đánh giá hoặc ngày tạo. Xem [routes API](products/api_urls.py) và [API views](products/api_views.py) cho hành vi hiện tại.

## Cấu hình local và production

File [.env.example](.env.example) mô tả các biến môi trường. `.env` được đọc từ thư mục gốc; biến đã đặt trong môi trường tiến trình được ưu tiên. [.gitignore](.gitignore) có quy tắc bỏ qua `.env`; không đưa file chứa bí mật vào kho mã.

| Cấu hình | Local | Production |
| --- | --- | --- |
| `DEBUG` | `True` để dùng HTTP local | Đặt `False` |
| `SECRET_KEY` | Để trống sẽ sinh khóa ngẫu nhiên mỗi tiến trình; có thể đặt khóa local ổn định để giữ session qua lần khởi động | Bắt buộc đặt khóa bí mật riêng, ngẫu nhiên và ổn định |
| `ALLOWED_HOSTS` | `127.0.0.1,localhost,testserver` trong file mẫu | Bắt buộc đặt danh sách hostname thật, ngăn cách bằng dấu phẩy |
| `CSRF_TRUSTED_ORIGINS` | Trống theo file mẫu | Thêm origin HTTPS phù hợp khi cần, gồm scheme, ngăn cách bằng dấu phẩy |
| `SECURE_SSL_REDIRECT` | Mặc định `False` | Mặc định `True` khi `DEBUG=False` |
| `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` | Mặc định `False` | Mặc định `True` khi `DEBUG=False` |
| `SECURE_HSTS_SECONDS` | Mặc định `0` | Mặc định `31536000` khi `DEBUG=False`; header chỉ gửi trên HTTPS |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS`, `SECURE_HSTS_PRELOAD` | `False` | Mặc định `False`; chỉ bật sau khi xác nhận chính sách HTTPS của domain/subdomain |
| `USE_X_FORWARDED_PROTO` | `False` | Chỉ đặt `True` sau reverse proxy TLS đáng tin cậy tự ghi đè `X-Forwarded-Proto` |
| `ZALO_OA_ID` | Tùy chọn | ID Official Account để bật widget chia sẻ Zalo |

Để trống các biến ghi đè HTTPS/cookie/HSTS-duration sẽ dùng mặc định theo `DEBUG`. Thiết lập nằm trong [config/settings.py](config/settings.py). Form POST dùng CSRF middleware/token và template giữ autoescape mặc định; nội dung người dùng cần tiếp tục được escape khi hiển thị.

Hạ tầng triển khai chịu trách nhiệm chứng chỉ HTTPS, TLS termination, cấu hình proxy, tiến trình WSGI (entry point [config/wsgi.py](config/wsgi.py)), sao lưu database/media và phục vụ static/media. `runserver` dùng cho phát triển. Cấu hình hiện chưa đặt `STATIC_ROOT`; nếu dùng `collectstatic`, bên triển khai cần cấu hình thư mục đích và web server/CDN phục vụ thư mục đó. `MEDIA_ROOT` là `media/`; Django chỉ thêm route phục vụ media khi `DEBUG=True`. Cần URL công khai cho static/media và hostname phù hợp trong `ALLOWED_HOSTS` để crawler mạng xã hội đọc metadata và ảnh Open Graph.

## Kiểm tra chất lượng

Chạy từ thư mục chứa `manage.py`:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py check --deploy
```

`check --deploy` với cấu hình local có 5 cảnh báo dự kiến: HSTS, HTTPS redirect, secure session/CSRF cookies và DEBUG. Kiểm tra production trong tiến trình riêng với cấu hình kiểm soát đã xác nhận các mặc định HTTPS ở trên; còn 2 cảnh báo về HSTS include-subdomains/preload, là lựa chọn của bên triển khai. Kết quả này không xác nhận TLS hoặc reverse proxy của server thật.

Đợt kiểm tra Week 6 ghi nhận 40 test đạt, gồm kiểm tra POST đánh giá thiếu CSRF bị từ chối và nội dung HTML trong đánh giá được escape. Đo số truy vấn trên SQLite khi render trang giỏ với 1/3 sản phẩm cho kết quả 2/2 truy vấn sau tối ưu (trước đó 3/5); hồ sơ với 1/3 đơn và item là 6/6 (trước đó 7/7). Đây là số truy vấn trên fixture local, không phải đo tải hoặc độ trễ production.

Xem [TECH_REPORT.md](docs/TECH_REPORT.md) cho kiến trúc/kỹ thuật và [DEMO.md](docs/DEMO.md) cho kịch bản trình diễn. Routes và cấu hình hiện hành trong mã nguồn là căn cứ cho hướng dẫn API/deploy ở trên.
