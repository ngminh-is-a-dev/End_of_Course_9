# Bean & Leaf — Kịch bản thuyết trình 13 phút

Kịch bản có 12 phút trình bày và 1 phút hỏi đáp. Nếu cần kết thúc trong 10 phút, bỏ thao tác review/chia sẻ trực tiếp, rút phần catalogue còn 1 phút và nêu kết quả truy vấn bằng một câu; vẫn giữ luồng đặt hàng, Admin và API.

## Chuẩn bị trước buổi trình bày

Làm theo [README](../README.md) để cài và khởi động ứng dụng. Với cấu hình local, đặt `DEBUG=1` trong `.env`; dùng SQLite mặc định. Chạy migration, seed dữ liệu và server trước khi bắt đầu:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_catalog
.\.venv\Scripts\python.exe manage.py runserver
```

Tạo trước tài khoản superuser và một tài khoản khách demo. Đăng nhập khách để kiểm tra voucher freeship, dọn giỏ hàng và chuẩn bị đăng nhập sẵn. Không chiếu `.env` hoặc mật khẩu. `seed_catalog` tạo/cập nhật 3 danh mục, 8 sản phẩm và đặt tồn kho sản phẩm mẫu về 25; chỉ chạy trên database demo. Widget Zalo là tùy chọn; localhost không tạo preview Facebook/Zalo.

Mở hai session trình duyệt: session khách và cửa sổ riêng tư cho Admin. Để sẵn các trang `/`, `/products/`, trang chi tiết Laura, `/accounts/profile/`, `/cart/`, API và `/admin/orders/order/`. Có thể tạo một đơn COD dự phòng trước buổi, không dùng voucher; ghi mã đơn và xác nhận đơn thuộc tài khoản demo. Nếu không tạo đơn dự phòng, lưu sẵn response API và ảnh chụp các màn hình cần thiết.

## Lịch trình 13 phút

| Thời gian | Thao tác | Lời dẫn gợi ý |
| --- | --- | --- |
| 00:00–01:00 | Giới thiệu tại trang chủ | “Bean & Leaf là cửa hàng cà phê trực tuyến. Website dùng Django để phục vụ giao diện và Django REST Framework cho API catalogue. Khách có thể đặt hàng COD; quản trị viên xử lý đơn trong Admin.” |
| 01:00–03:00 | Tìm sản phẩm, lọc catalogue, mở Laura Coffee Blend | “Catalogue cho phép tìm theo tên hoặc mô tả, lọc theo danh mục, giá và mức rang. Trang danh sách có phân trang HTML. Trang chi tiết trình bày giá, tồn kho, sản phẩm liên quan và đánh giá.” Thu nhỏ cửa sổ để minh họa responsive nếu thao tác nhanh. |
| 03:00–04:00 | Mở hồ sơ khách; xem voucher/lịch sử đăng nhập và đơn | “Tài khoản mới được cấp voucher freeship riêng. Hồ sơ hiển thị tối đa 20 lần đăng nhập gần nhất và những đơn gắn với tài khoản này. Khách vãng lai vẫn đặt được hàng, nhưng đơn đó không tự gắn vào tài khoản sau này.” |
| 04:00–05:00 | Gửi hoặc cập nhật review; sao chép liên kết sản phẩm | “Đánh giá hiển thị công khai. Người đăng nhập có thể chấm từ 1 đến 5 sao; mỗi người có một đánh giá cho mỗi sản phẩm và có thể sửa đánh giá của mình. Chia sẻ có Facebook, Zalo và sao chép URL; preview mạng xã hội cần URL công khai.” |
| 05:00–08:00 | Thêm sản phẩm, đổi số lượng, áp voucher rồi checkout COD | “Giỏ hàng được lưu trong session. Phí giao tiêu chuẩn là 30.000 đồng và voucher hợp lệ đưa phí về 0. Checkout kiểm tra tồn kho và hỗ trợ thanh toán khi nhận hàng. Sau khi đặt thành công, mã đơn xuất hiện ở trang xác nhận, giỏ được làm trống và tồn kho được cập nhật.” Dùng thông tin giả lập khi nhập form. |
| 08:00–10:00 | Admin tìm đơn, cập nhật giao hàng; refresh hồ sơ khách | “Đơn mới bắt đầu ở trạng thái Đang đóng gói và Chờ thanh toán. Admin quản lý giao hàng và thu tiền ở hai trường riêng. Vì vậy, chuyển sang Đã giao không tự đánh dấu Đã thanh toán.” Lưu mỗi lần cập nhật; có thể dừng ở Đang giao nếu cần tiết kiệm thời gian. |
| 10:00–11:00 | Mở API list có bộ lọc và API detail | “API công khai chỉ đọc, trả sản phẩm đang hoạt động. Danh sách hỗ trợ tìm kiếm, danh mục và mức rang; response là mảng JSON chưa phân trang. Endpoint detail trả một object theo slug.” |
| 11:00–12:00 | Mở bảng đo truy vấn trong [báo cáo kỹ thuật](TECH_REPORT.md) | “Trong lần đo trên SQLite local, truy vấn trang giỏ giảm từ 3 xuống 2 với một sản phẩm và từ 5 xuống 2 với ba sản phẩm. Profile giảm từ 7 xuống 6. Đây là số query trong fixture test, không phải benchmark tải hay độ trễ production.” |
| 12:00–13:00 | Nêu giới hạn và trả lời câu hỏi | “Các giới hạn hiện tại gồm API chưa phân trang, chưa có thanh toán trực tuyến và chưa kiểm thử tải/đồng thời trên production. Phần tiếp theo nên ưu tiên theo quy mô catalogue và yêu cầu vận hành thực tế.” Dành phút cuối cho câu hỏi. |

## Luồng demo chi tiết

### Checkout và Admin

Đăng nhập trước khi checkout để đơn gắn vào tài khoản demo. Nhập tên, điện thoại và địa chỉ giả lập; có thể dùng email thuộc `example.com`. Chọn **Thanh toán khi nhận hàng**. Checkout kiểm tra tồn kho và trừ số lượng trong cùng transaction tạo đơn. Trang thành công chỉ xác nhận đã tạo đơn, không có nghĩa đơn đã giao.

Trong Admin, tìm theo mã `BL…` vừa tạo. Cột `delivery_status` có thể sửa ở danh sách nhưng cần bấm lưu. Cập nhật `packing` sang `shipping`, rồi refresh hồ sơ khách để xem trạng thái mới. Chỉ đổi `payment_status` sang **Đã thanh toán** nếu đang minh họa tình huống đã thu COD; không tự suy ra trạng thái này từ việc giao hàng.

### API

Khi server đang chạy, có thể gọi hai endpoint trong PowerShell:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/products/?search=Laura&category=ca-phe-hat&roast=dark' -Headers @{ Accept = 'application/json' } | ConvertTo-Json -Depth 5
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/products/laura-coffee-blend-xam/' -Headers @{ Accept = 'application/json' } | ConvertTo-Json -Depth 5
```

PowerShell đôi khi trình bày mảng một phần tử như object trong pipeline; response API danh sách vẫn là mảng. Không giới thiệu `page` là phân trang API hoặc nói API trả ảnh/review.

## Phương án dự phòng

| Nếu gặp tình huống | Cách xử lý |
| --- | --- |
| Voucher đã dùng | Giữ nguyên tài khoản; tiếp tục demo giỏ với phí giao 30.000đ. |
| Checkout lỗi | Dùng đơn dự phòng đã xác nhận thuộc đúng tài khoản; nói rõ đây là đơn chuẩn bị trước. |
| Avatar tải chậm hoặc chia sẻ mạng xã hội không mở | Bỏ thao tác đó, chuyển thẳng sang nội dung kế tiếp. |
| API hoặc server gián đoạn | Dùng response JSON/ảnh chụp đã lưu và nói rõ phần đó không chạy trực tiếp. |

## Kết thúc và dọn dữ liệu demo

Sau buổi trình bày, đăng xuất hai session và dừng server bằng `Ctrl+C`. Seed không khôi phục voucher đã dùng. Khi tập lại, dùng user demo mới nếu cần voucher chưa sử dụng; chỉ chỉnh hoặc xóa đơn/review demo đã nhận diện trong database demo.
