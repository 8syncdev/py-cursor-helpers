# Hướng dẫn sử dụng công cụ Py Cursor Tools

[Video hướng dẫn sử dụng công Py Cursor Tools](https://www.youtube.com/watch?v=kzQ7d9BKm_g)



## Giới thiệu

Py Cursor Tools là một công cụ được phát triển để tạo và quản lý ID máy cho ứng dụng Cursor. Công cụ này cho phép người dùng tạo mới các ID máy, giúp khắc phục các vấn đề liên quan đến xác thực và giấy phép của Cursor.

## Chức năng chính

1. **Tạo ID máy mới**: Tạo mới các ID như machineId, macMachineId và devDeviceId
2. **Quản lý file cấu hình**: Tự động tìm và cập nhật file cấu hình của Cursor
3. **Hỗ trợ đa nền tảng**: Hoạt động trên Windows, macOS và Linux
4. **Tự động yêu cầu quyền admin**: Đảm bảo có đủ quyền để thực hiện các thay đổi

## Cấu trúc thư mục

```
dist/
├── mac_machine_id.exe    # Phiên bản thực thi cho macOS
├── machine_id.exe        # Phiên bản thực thi cho Windows
src/
├── README.md             # Tài liệu hướng dẫn
```

## Cách sử dụng

1. **Chạy ứng dụng**:
   - Trên Windows: Chạy file `machine_id.exe` với quyền quản trị viên
   - Trên macOS: Chạy file `mac_machine_id.exe`

2. **Quy trình hoạt động**:
   - Công cụ sẽ tự động kiểm tra quyền admin và yêu cầu nâng cấp nếu cần
   - Đóng tất cả các tiến trình Cursor đang chạy
   - Tìm file cấu hình Cursor trên hệ thống
   - Hiển thị các ID hiện tại
   - Tạo và cập nhật các ID mới
   - Đặt quyền file cấu hình thành chỉ đọc để bảo vệ

3. **Sau khi chạy**:
   - Khởi động lại Cursor để áp dụng các thay đổi

## Các ID được quản lý

- **machineId**: ID máy chính (chuỗi 64 ký tự hex)
- **macMachineId**: ID máy cho macOS (chuỗi 64 ký tự hex)
- **devDeviceId**: ID thiết bị (định dạng UUID)
- **sqmId**: ID theo dõi sử dụng (được giữ nguyên nếu đã tồn tại)

## Lưu ý bảo mật

- Công cụ yêu cầu quyền quản trị để thay đổi file cấu hình
- Sau khi cập nhật, file cấu hình sẽ được đặt thành chỉ đọc để tránh thay đổi không mong muốn
- Đảm bảo tắt Cursor trước khi chạy công cụ (công cụ sẽ tự động thực hiện điều này)

## Xử lý sự cố

- Nếu không tìm thấy file cấu hình, hãy đảm bảo Cursor đã được cài đặt đúng cách
- Nếu không thể nâng cấp quyền, hãy thử chạy công cụ với quyền quản trị thủ công
- Nếu gặp lỗi khi đóng Cursor, hãy đóng ứng dụng thủ công trước khi chạy công cụ

## Yêu cầu hệ thống

- Windows, macOS hoặc Linux
- Cursor đã được cài đặt
- Quyền quản trị viên/root để thực hiện thay đổi

**Youtube:** [Dev8Sync](https://www.youtube.com/@Dev8Sync/featured)

**Facebook:** [8sync](https://www.facebook.com/8sync)

**Tiktok:** [@_8_sync_](https://www.tiktok.com/@_8_sync_)

**Zalo:** [0703930513](https://zalo.me/0703930513)

**Zalo Group:** [mitxdi486](https://zalo.me/g/mitxdi486)

**Email:** 8sync.dev.1111@gmail.com

**Website:** [syncdev8.com](https://syncdev8.com/)

# Phân tích mã nguồn

## Phân tích chi tiết mã nguồn

Từ mã nguồn được cung cấp, chúng ta có thể hiểu chi tiết hơn về cách công cụ Py Cursor Tools hoạt động:

### 1. Cơ chế tạo ID

- **machineId**: Sử dụng hàm `generate_machine_id()` để tạo dữ liệu ngẫu nhiên 32 byte thông qua `os.urandom()`, sau đó mã hóa bằng SHA-256 và trả về dạng hex viết thường (64 ký tự)
- **macMachineId**: Sử dụng cùng cơ chế với machineId
- **devDeviceId**: Tạo UUID phiên bản 4 (ngẫu nhiên) thông qua `uuid.uuid4()`
- **sqmId**: Giữ nguyên nếu đã tồn tại, nếu chưa thì tạo UUID mới

### 2. Xác định vị trí file cấu hình

Công cụ tự động phát hiện hệ điều hành và tìm file cấu hình `storage.json` ở vị trí:
- **Windows**: `%APPDATA%\Cursor\User\globalStorage\storage.json`
- **macOS**: `~/Library/Application Support/Cursor/User/globalStorage/storage.json`
- **Linux**: `~/.config/Cursor/User/globalStorage/storage.json`

### 3. Quản lý quyền và bảo mật

- Kiểm tra quyền admin/root thông qua `check_admin_privileges()`
- Tự động yêu cầu nâng cấp quyền nếu cần thiết
- Đóng tất cả các tiến trình Cursor đang chạy trước khi sửa đổi
- Đặt file cấu hình thành chỉ đọc sau khi hoàn tất để ngăn sửa đổi không mong muốn

### 4. Quy trình xử lý

1. Kiểm tra và yêu cầu quyền quản trị
2. Đóng tất cả tiến trình Cursor
3. Tìm file cấu hình
4. Sao lưu và hiển thị các ID hiện tại
5. Tạo ID mới và cập nhật file cấu hình
6. Bảo vệ file bằng cách đặt chế độ chỉ đọc

## Hướng dẫn video

Để hiểu rõ hơn về cách sử dụng công cụ Py Cursor Tools, bạn có thể xem hướng dẫn chi tiết tại video YouTube: [Hướng dẫn sử dụng công cụ Py Cursor Tools](https://www.youtube.com/watch?v=kzQ7d9BKm_g)

## Chi tiết kỹ thuật

1. **Cách tạo machineId**:
   ```python
   def generate_machine_id():
       data = os.urandom(32)  # Tạo 32 byte ngẫu nhiên
       hash_object = hashlib.sha256()
       hash_object.update(data)
       return hash_object.hexdigest()  # Trả về chuỗi 64 ký tự hex
   ```

2. **Cách xử lý quyền file**:
   ```python
   def set_file_permissions(file_path, read_only=True):
       # Đặt file thành chỉ đọc hoặc cấp quyền ghi
       # Khác nhau giữa Windows và macOS/Linux
   ```

3. **Tự động đóng Cursor**:
   ```python
   def kill_cursor_processes():
       # Sử dụng taskkill trên Windows hoặc pkill trên macOS/Linux
       # Đợi 1 giây để tiến trình tắt hoàn toàn
   ```

## Lưu ý quan trọng

- Công cụ sẽ thay đổi 3 ID: `machineId`, `macMachineId` và `devDeviceId`
- ID `sqmId` sẽ được giữ nguyên nếu đã tồn tại
- Cần khởi động lại Cursor sau khi sử dụng công cụ để thay đổi có hiệu lực
- Nên lưu ý ID cũ trước khi thay đổi, phòng trường hợp cần khôi phục



