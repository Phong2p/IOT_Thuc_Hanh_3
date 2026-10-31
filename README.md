# Thực hành IoT với Python và CoAP

Ba bài thực hành sử dụng thư viện `aiocoap` để gửi thông điệp, giám sát cảm biến và điều khiển đèn thông minh theo mô hình Client–Server.

## Thông tin thực hiện

| STT | Họ và tên | Mã sinh viên | Nhóm | github |
| --- | --- | --- | --- | --- |
| 1 | Hứa Xuân Thiệu | B23DCCN788 | 09 | [thieuhua](https://github.com/thieuhua) |
| 2 | Bùi Hồng Phong | B23DCCN641 | 09 | [Phong2p](https://github.com/Phong2p) |

## Môi trường và cài đặt

- Python 3.10 trở lên.
- Thư viện `aiocoap`.
- Đã kiểm thử trên Windows với Python 3.11.4 và aiocoap 0.4.17.

Mở PowerShell tại thư mục gốc của dự án:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install aiocoap==0.4.17
```

Các lệnh bên dưới gọi trực tiếp Python trong môi trường ảo, không cần kích hoạt môi trường.

## Cấu trúc mã nguồn

```text
.
├── bai1/
│   ├── coap_server_bai1.py
│   └── coap_client_bai1.py
├── bai2/
│   ├── sensor_server_bai2.py
│   └── monitor_client_bai2.py
├── bai3/
│   ├── light_server_bai3.py
│   ├── light_controller_bai3.py
│   └── light_monitor_bai3.py
├── .gitignore
└── README.md
```

## Địa chỉ tài nguyên

Mặc định các chương trình chạy trên cùng máy tại `127.0.0.1`, sử dụng UDP cổng `5683`.

| Bài | URI | Phương thức | Nội dung |
| --- | --- | --- | --- |
| 1 | `coap://127.0.0.1:5683/iot/lab/message` | GET, POST | Thông điệp văn bản UTF-8 |
| 2 | `coap://127.0.0.1:5683/iot/lab/sensor01/data` | GET | JSON dữ liệu cảm biến |
| 3 | `coap://127.0.0.1:5683/iot/lab/light01/status` | GET, PUT, Observe | JSON trạng thái đèn |

**Chỉ chạy một server tại cổng 5683 trong mỗi lần thực hành.** Dừng server của bài trước bằng Ctrl+C trước khi chuyển bài.

## Bài 1 — Gửi và nhận thông điệp

Server trả lời chào khi nhận GET. Khi nhận POST, server hiển thị nội dung thông điệp, thời điểm nhận và phản hồi xác nhận.

Terminal 1 — chạy server:

```powershell
.\.venv\Scripts\python.exe bai1\coap_server_bai1.py
```

Terminal 2 — chạy client; thay MSSV và họ tên ví dụ bằng thông tin của mình:

```powershell
.\.venv\Scripts\python.exe bai1\coap_client_bai1.py --student-id B23DCCN001 --name "Nguyen Van A"
```

Nếu không truyền thông tin, client dùng MSSV và họ tên mẫu trong đề.

Kết quả mong đợi:

```text
Sending GET request...
Code: 2.05 Content
Payload: Xin chao tu CoAP Server

Sending POST request...
Payload: Xin chao tu CoAP Client - B23DCCN001 - Nguyen Van A
Code: 2.04 Changed
Payload: Server da nhan thong diep
```

Server ghi log `Payload` và `Time` của POST. Thông điệp rỗng hoặc không đúng UTF-8 bị từ chối với mã `4.00 Bad Request`.

## Bài 2 — Giám sát nhiệt độ và độ ẩm

Server mô phỏng `sensor01`, sinh nhiệt độ 20–40°C và độ ẩm 30–80%, cập nhật mỗi 3 giây. GET trả về mẫu mới nhất với Content-Format `application/json`.

Terminal 1 — chạy server:

```powershell
.\.venv\Scripts\python.exe bai2\sensor_server_bai2.py
```

Terminal 2 — chạy client:

```powershell
.\.venv\Scripts\python.exe bai2\monitor_client_bai2.py
```

Ví dụ payload:

```json
{
  "device_id": "sensor01",
  "temperature": 36.1,
  "humidity": 38.7
}
```

Client GET mỗi 3 giây, hiển thị mã thiết bị, nhiệt độ, độ ẩm và giờ nhận. Các điều kiện cảnh báo:

| Điều kiện | Thông báo |
| --- | --- |
| Nhiệt độ > 35°C | `CANH BAO: Nhiet do cao` |
| Độ ẩm < 40% | `CANH BAO: Do am thap` |
| Không vi phạm ngưỡng | `Trang thai: Binh thuong` |

Hai cảnh báo xuất hiện cùng lúc nếu cả hai điều kiện đều đúng. Nhiệt độ đúng 35°C và độ ẩm đúng 40% không gây cảnh báo.

Ví dụ đầu ra:

```text
[10:20:03] Received sensor data
Device: sensor01
Temperature: 36.1 C
Humidity: 38.7 %
CANH BAO: Nhiet do cao
CANH BAO: Do am thap
------------------------------
```

Client tiếp tục thử lại sau timeout, lỗi kết nối, mã lỗi CoAP hoặc dữ liệu không hợp lệ. Nhấn Ctrl+C để dừng giám sát.

## Bài 3 — Giám sát và điều khiển đèn bằng Observe

Server mô phỏng đèn `light01` với trạng thái ban đầu `OFF`. Controller dùng PUT để bật/tắt và GET để đọc trạng thái. Monitoring Client đăng ký CoAP Observe để nhận trạng thái ban đầu và các thay đổi từ server.

Terminal 1 — chạy server:

```powershell
.\.venv\Scripts\python.exe bai3\light_server_bai3.py
```

Terminal 2 — chạy Monitoring Client:

```powershell
.\.venv\Scripts\python.exe bai3\light_monitor_bai3.py
```

Terminal 3 — chạy Controller Client:

```powershell
.\.venv\Scripts\python.exe bai3\light_controller_bai3.py
```

Nhập các lệnh tại Controller:

| Lệnh | Chức năng |
| --- | --- |
| `ON` | PUT để bật đèn |
| `OFF` | PUT để tắt đèn |
| `STATUS` | GET để đọc trạng thái |
| `EXIT` | Thoát Controller |

Thử lần lượt `ON`, `STATUS`, `OFF`, `EXIT`. Quan sát trạng thái tương ứng ở terminal Monitoring Client.

Payload điều khiển:

```json
{
  "device_id": "light01",
  "command": "ON"
}
```

Payload trạng thái khi đọc bằng GET hoặc nhận qua Observe:

```json
{
  "device_id": "light01",
  "status": "ON"
}
```

Server chỉ thông báo Observe khi trạng thái thực sự thay đổi. Gửi lại `ON` khi đèn đang bật vẫn nhận xác nhận PUT nhưng không phát sinh thông báo mới. Nhiều Monitoring Client có thể Observe cùng tài nguyên.

Ví dụ đầu ra của Monitoring Client:

```text
[10:30:00] Initial State
Device: light01
Status: OFF

[10:30:15] State Updated
Device: light01
Status: ON
```

Monitoring Client chờ thông báo bằng Observe, không GET định kỳ và không tự dừng sau 30 giây. Nhấn Ctrl+C để dừng.

## Chạy trên hai máy hoặc đổi cổng

Các server hỗ trợ `--host`, `--port`; các client hỗ trợ `--server`, `--timeout`.

Ví dụ chạy Bài 3 trên hai máy, thay IP dưới đây bằng IP thật của máy server:

```powershell
# Máy server
.\.venv\Scripts\python.exe bai3\light_server_bai3.py --host 192.168.1.10 --port 5683

# Máy client: Monitoring
.\.venv\Scripts\python.exe bai3\light_monitor_bai3.py --server coap://192.168.1.10:5683 --timeout 5

# Máy client: Controller, mở ở terminal khác
.\.venv\Scripts\python.exe bai3\light_controller_bai3.py --server coap://192.168.1.10:5683 --timeout 5
```

Cho phép UDP cổng 5683 qua tường lửa trên máy server. Nếu đổi `--port`, cập nhật cùng cổng trong `--server` của client.

Timeout mặc định là 5 giây cho mỗi yêu cầu. Với Monitoring Client Bài 3, timeout áp dụng cho bước đăng ký Observe; khi đã đăng ký, client tiếp tục chờ thay đổi trạng thái.

## Kết quả kiểm thử cục bộ

| Nội dung | Kết quả |
| --- | --- |
| Cú pháp của cả 7 chương trình | Đạt |
| Bài 1: GET, POST, họ tên tiếng Việt, log thời điểm nhận | Đạt |
| Bài 1: thông điệp rỗng/sai UTF-8, URI không tồn tại, timeout | Đạt |
| Bài 2: JSON đúng trường, Content-Format và dữ liệu trong khoảng mô phỏng | Đạt |
| Bài 2: cập nhật và GET theo chu kỳ 3 giây | Đạt |
| Bài 2: hai cảnh báo, giá trị sát ngưỡng và trạng thái bình thường | Đạt |
| Bài 2: tiếp tục giám sát sau timeout, JSON lỗi hoặc phản hồi lỗi | Đạt |
| Bài 3: trạng thái ban đầu OFF, GET và PUT ON/OFF | Đạt |
| Bài 3: từ chối JSON, mã thiết bị hoặc lệnh không hợp lệ | Đạt |
| Bài 3: nhiều client Observe, nhận cập nhật và không thông báo khi trạng thái giữ nguyên | Đạt |
| Bài 3: Controller nhập ON/OFF/STATUS/EXIT và xử lý lệnh sai | Đạt |
| Bài 3: timeout và tài nguyên không hỗ trợ Observe | Đạt |

**Minh chứng thực hành:** [Bổ sung ảnh chụp terminal hoặc log chạy thực tế của sinh viên/nhóm.]
