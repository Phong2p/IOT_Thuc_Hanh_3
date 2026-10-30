"""
README – Thực hành IoT với CoAP (aiocoap)
==========================================

Yêu cầu:
    pip install aiocoap

Cấu trúc file:
    bai1_server.py  – CoAP Server cơ bản (/hello, /sensor – GET, POST)
    bai1_client.py  – Client gửi GET và POST
    bai2_server.py  – Server quản lý thiết bị IoT (GET, POST, PUT)
    bai2_client.py  – Client điều khiển thiết bị
    bai3_server.py  – Server Observe (cảm biến tự cập nhật mỗi 3s)
    bai3_client.py  – Client Observe (nhận thông báo real-time)

─────────────────────────────────────────────────
Bài 1 – Gửi/nhận thông điệp CoAP cơ bản
─────────────────────────────────────────────────
  Terminal 1:  python bai1_server.py
  Terminal 2:  python bai1_client.py

  Tài nguyên server:
    coap://127.0.0.1/hello   → GET  → "Xin chao!"
    coap://127.0.0.1/sensor  → GET  → JSON dữ liệu cảm biến
    coap://127.0.0.1/sensor  → POST → Cập nhật giá trị cảm biến

─────────────────────────────────────────────────
Bài 2 – GET, POST, PUT điều khiển thiết bị
─────────────────────────────────────────────────
  Terminal 1:  python bai2_server.py
  Terminal 2:  python bai2_client.py

  Tài nguyên server:
    /device/den         → GET (đọc), POST (bật/tắt/toggle), PUT (cập nhật thuộc tính)
    /device/quat        → GET, POST, PUT
    /device/dieu-hoa    → GET, POST, PUT
    /sensor/temperature → GET (Observe)

  Ví dụ POST body:
    {"action": "on"}        → bật thiết bị
    {"action": "off"}       → tắt thiết bị
    {"action": "toggle"}    → đảo trạng thái

  Ví dụ PUT body:
    {"brightness": 80}      → đặt độ sáng đèn
    {"speed": 3}            → đặt tốc độ quạt
    {"status":"on","temp_set":24}  → điều hòa

─────────────────────────────────────────────────
Bài 3 – CoAP Observe (giám sát real-time)
─────────────────────────────────────────────────
  Terminal 1:  python bai3_server.py
  Terminal 2:  python bai3_client.py

  Server tự động cập nhật cảm biến mỗi 3 giây.
  Client nhận thông báo ngay khi có thay đổi (không cần polling).

  Tài nguyên:
    /monitor/sensors  → Dữ liệu đa cảm biến (nhiệt độ, độ ẩm, ánh sáng, chuyển động)
    /monitor/alert    → Cảnh báo tự động khi vượt ngưỡng nhiệt độ

─────────────────────────────────────────────────
Lưu ý:
  - Chỉ chạy MỘT server mỗi lần (cùng dùng cổng 5683).
  - Dùng Ctrl+C để dừng server.
"""
