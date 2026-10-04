# Kịch bản demo Bean & Leaf

## Chuẩn bị

1. Chạy migrate và `seed_catalog`.
2. Khởi động `py -3 manage.py runserver`.
3. Mở trang chủ tại `http://127.0.0.1:8000/`.

## Trình diễn trong 5 phút

1. **UI/UX**: thu/phóng màn hình để minh họa desktop và mobile responsive; mở trang catalogue và drawer lọc trên điện thoại.
2. **Catalogue**: tìm kiếm, chọn danh mục/mức rang, mở product detail.
3. **Authentication**: tạo tài khoản mới để hiện thông báo voucher `FREESHIP-xxxxx`.
4. **Cart & voucher**: thêm sản phẩm, áp dụng voucher freeship, kiểm tra phí giao hàng về 0đ, tiếp tục checkout COD.
5. **Admin**: vào `/admin/` để minh họa quản lý product/category/voucher.
6. **API**: mở `/api/products/?category=ca-phe-hat` để xem JSON catalogue.

## Lệnh QA

```powershell
py -3 manage.py check
py -3 manage.py test
```
