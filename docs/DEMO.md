# Bean & Leaf — Kịch bản thuyết trình 18 phút

## Chuẩn bị trước buổi trình bày

Cài môi trường theo [README](../README.md). Từ thư mục chứa `manage.py`, dùng `.venv` đã có dependencies:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_catalog
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

Bỏ qua `createsuperuser` nếu đã có tài khoản quản trị; không có mật khẩu admin mặc định. Demo HTTP local dùng DEBUG=True theo file mẫu; không chiếu `.env` hoặc mật khẩu. Chạy server trước giờ và giữ terminal mở; dùng cửa sổ PowerShell khác nếu gọi API.

`seed_catalog` tạo/cập nhật 3 danh mục, 8 sản phẩm, tồn kho 25; không tạo user/review/đơn/ảnh. Seed lại ghi giá và tồn kho mẫu, chỉ dùng trên database demo. Kiểm tra `/products/laura-coffee-blend-xam/` còn hoạt động nếu đã sửa dữ liệu trước đó. Chuẩn bị ảnh PNG/JPEG nhỏ để upload avatar; có thể dùng avatar mặc định nếu bỏ qua thao tác tùy chọn này.

Dùng hai cửa sổ có session riêng: cửa sổ thường cho khách, cửa sổ riêng tư cho superuser. Đăng nhập Admin trước, để sẵn `/admin/orders/order/`; không dùng chung session với khách. Tạo tài khoản khách demo mới tại `/accounts/signup/` trước buổi, ghi username và mã voucher thực hiển thị trong giỏ. Dùng đúng tài khoản này xuyên suốt phần live và đơn dự phòng. Phần số phụ thuộc ID user, không giả định luôn là `FREESHIP-00001`.

Khi vẫn đăng nhập đúng tài khoản khách sẽ dùng live, tạo một đơn COD dự phòng **không áp voucher**; nếu giỏ đang có mã thì gỡ mã trước checkout. Ghi mã `BL…`, mở profile của chính tài khoản đó để xác nhận đơn xuất hiện, kiểm tra voucher vẫn chưa dùng và đặt đơn dự phòng ở **Đang đóng gói** trong Admin. Sau đó đăng xuất bằng nút navbar để sẵn màn hình login. Có thể lưu màn hình profile/đơn và JSON từ lần tập dượt; khi dùng dự phòng phải nói rõ đây là kết quả chuẩn bị trước.

Mở sẵn các tab `/`, `/products/`, `/accounts/login/`, `/accounts/profile/`, `/cart/`, API và Admin. Localhost không tạo preview trên Facebook/Zalo. Widget Zalo chỉ là tùy chọn khi có `ZALO_OA_ID`; sao chép liên kết đủ để demo. Không cần đăng bài lên mạng xã hội.

## Lịch trình: 18 phút

Tổng **1 + 2 + 2 + 2 + 3 + 2 + 2 + 2 + 2 = 18 phút**, nằm trong yêu cầu 15–20 phút. Tập theo đồng hồ, hết mốc chuyển bước; hỏi đáp ở 2 phút cuối.

| Mốc | Thời lượng | Thao tác | Điểm cần nói |
| --- | ---: | --- | --- |
| 00:00–01:00 | 1 phút | Giới thiệu tại `/` | Bán cà phê; Django MVT + DRF + SQLite; khách đặt COD, Admin quản lý giao hàng |
| 01:00–03:00 | 2 phút | Trang chủ → `/products/`, tìm Laura, lọc danh mục/mức rang; thu hẹp cửa sổ, mở chi tiết | Responsive; HTML phân trang 9 nhưng seed có 8 nên không cần có trang 2 |
| 03:00–05:00 | 2 phút | Login khách tại `/accounts/login/`; profile: tên/avatar/IP/thời gian; upload ảnh nếu đã chuẩn bị | Cần đăng nhập; 20 lần đăng nhập gần nhất; IP local thường loopback; chỉ đơn gắn với tài khoản |
| 05:00–07:00 | 2 phút | `/products/laura-coffee-blend-xam/`: gửi 5 sao/nhận xét rồi sửa 4 sao; sao chép liên kết; chỉ Facebook/Zalo và `og:` trong source | Một review mỗi người/sản phẩm, gửi lại là sửa; không cần đã mua; preview cần URL công khai |
| 07:00–10:00 | 3 phút | Thêm hàng, `/cart/`, đổi số lượng, áp voucher chưa dùng; `/checkout/`, nhập thông tin giả lập, đặt COD | Phí 30.000đ → 0đ khi voucher hợp lệ; ghi mã đơn trên trang thành công; giỏ trống |
| 10:00–12:00 | 2 phút | Admin tìm mã tại `/admin/orders/order/`; đổi packing → shipping → delivered, lưu từng lần; refresh profile khách | Đang đóng gói → Đang giao → Đã giao; giao hàng và thanh toán là hai trường độc lập |
| 12:00–14:00 | 2 phút | API list có filter, rồi detail; chỉ mảng/object và category/price | GET công khai, search/category/roast; raw list chưa phân trang; chỉ sản phẩm hoạt động |
| 14:00–16:00 | 2 phút | Mở bảng query/bảo mật trong [báo cáo](TECH_REPORT.md), chỉ kết quả QA chuẩn bị trước | Giỏ 3/5 → 2/2 query, profile 7/7 → 6/6; CSRF/escaping có test; settings chưa chứng minh server có TLS |
| 16:00–18:00 | 2 phút | Tổng kết và hỏi đáp | Giới hạn: chưa test tải, API raw list, checkout chưa trừ tồn kho/khóa đồng thời; mở rộng cần thiết kế và đo tiếp |

## Thao tác cần tập kỹ

**Checkout (07:00–10:00):** dùng tên/điện thoại/địa chỉ giả lập, email thuộc `example.com`; chọn **Thanh toán khi nhận hàng**. `/checkout/success/<mã-đơn>/` xác nhận đơn đã ghi nhận và **Đang đóng gói**, không nói đã giao ngay khi đặt. Login trước checkout để đơn vào profile; đơn khách vãng lai không tự gắn lại về sau.

**Admin (10:00–12:00):** cần superuser. Cột `delivery_status` sửa ngay tại danh sách nhưng phải bấm lưu. Sau mỗi lần lưu, refresh profile khách để chỉ nhãn mới. `payment_status` ở trang sửa đơn chỉ đổi **Đã thanh toán** khi minh họa đã thu COD; đây là thao tác thủ công, không tự đổi khi giao. Admin chưa ép trình tự trạng thái.

**API (12:00–14:00):** mở URL trong trình duyệt hoặc chạy ở PowerShell khi server đang hoạt động:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/products/?search=Laura&category=ca-phe-hat&roast=dark' -Headers @{ Accept = 'application/json' } | ConvertTo-Json -Depth 5
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/products/laura-coffee-blend-xam/' -Headers @{ Accept = 'application/json' } | ConvertTo-Json -Depth 5
```

Pipeline PowerShell có thể trình bày mảng một phần tử như object; chỉ response trình duyệt hoặc README để giải thích list là mảng, detail là object. Không giới thiệu `page=2` là phân trang API hoặc nói API trả ảnh/review.

## Dự phòng trong cùng thời lượng

| Tình huống | Thay thế tại đúng mốc |
| --- | --- |
| Avatar upload chậm/không có ảnh | Chỉ avatar mặc định/form rồi chuyển lịch sử/đơn |
| Facebook/Zalo không mở, thiếu OA ID, clipboard bị chặn | Chỉ URL sản phẩm và `og:` trong page source; giải thích OA/URL công khai, không chờ dịch vụ ngoài |
| Voucher đã dùng | Giữ nguyên tài khoản khách đang live, minh họa phí thường 30.000đ; không chuyển tài khoản hoặc sửa voucher của người thật |
| Checkout live lỗi | Dùng mã đơn dự phòng đã xác nhận thuộc đúng tài khoản khách đang live để demo Admin → profile; nói rõ đơn dự phòng và ghi lại lỗi |
| API/server lỗi | Dùng JSON/màn hình lưu từ tập dượt, nói rõ live bị gián đoạn; không cài lại dependencies giữa bài |

## QA, tập dượt và đặt lại dữ liệu

Chạy trước buổi, không chờ full suite trong 18 phút:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py check --deploy
```

Tuần 6 đã ghi nhận 40 test đạt. Local `check --deploy` có 5 cảnh báo HTTP/DEBUG dự kiến; không bật redirect HTTPS trên server HTTP chỉ để che cảnh báo. Ranh giới production được giải thích trong [báo cáo](TECH_REPORT.md#6-bảo-mật-và-ranh-giới-triển-khai).

Sau mỗi lần tập: ghi mã đơn; xóa/cập nhật sản phẩm bằng giao diện giỏ để chuẩn bị lại. Seed không làm mới voucher đã dùng. Muốn dùng voucher từ đầu ở lần trình bày tiếp theo, chuẩn bị user demo mới trước buổi và lặp lại toàn bộ bước tạo đơn dự phòng không áp voucher cho chính user mới, xác nhận đơn trong profile và ghi lại cặp username/mã đơn mới. Không dùng đơn dự phòng của tài khoản cũ cho user mới. Trong một lần live giữ nguyên tài khoản; nếu voucher hết thì dùng nhánh phí thường ở trên. Review gửi lại sửa review cũ, có thể giữ để demo tính sửa. Admin có thể đặt đúng đơn demo về **Đang đóng gói** trước lần tập sau. Nếu cần xóa dữ liệu thử, chỉ xóa đúng review/đơn demo đã nhận diện qua Admin trên database demo; không xóa database hay dữ liệu khách thật. Kết thúc bằng đăng xuất hai session, `Ctrl+C` terminal server.
