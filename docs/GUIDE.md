# Gợi ý làm bài

## Khi log thiếu correlation ID

Theo dõi một request từ middleware đến response. Kiểm tra context có được xóa trước request mới, gán vào logger và trả lại trong response header hay chưa.

## Khi log thiếu metadata

Xác định metadata nào thuộc toàn request và metadata nào chỉ xuất hiện sau khi agent chạy xong. Bind context trước dòng `request_received` để các log sau dùng chung context.

## Khi còn PII trong log

Kiểm tra thứ tự processor: dữ liệu phải được scrub trước khi JSON được render và ghi xuống file. Thử với email, số điện thoại và số thẻ mẫu.

## Khi metrics báo xấu nhưng chưa biết nguyên nhân

1. Dùng metrics xác định khoảng thời gian và loại triệu chứng.
2. Mở một trace bất thường trong khoảng đó.
3. So sánh thời gian các span.
4. Tìm log có cùng correlation ID.
5. Chỉ kết luận khi evidence khớp ở cả ba lớp.

## Khi dashboard khó đọc

Mỗi panel cần tên, đơn vị, khoảng thời gian và threshold. Ưu tiên 6 panel chính thay vì thêm nhiều biểu đồ không phục vụ quyết định.
