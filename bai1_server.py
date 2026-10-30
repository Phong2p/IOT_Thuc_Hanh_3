"""
Bài 1: CoAP Server cơ bản
Định nghĩa tài nguyên /hello và /sensor trên server.
Hỗ trợ GET và POST.
"""

import asyncio
import aiocoap
import aiocoap.resource as resource
import json
import datetime


# ─────────────────────────────────────────────
# Tài nguyên /hello  (GET)
# ─────────────────────────────────────────────
class HelloResource(resource.Resource):
    """Tài nguyên đơn giản trả về lời chào."""

    async def render_get(self, request):
        payload = b"Xin chao! Day la CoAP Server IoT."
        return aiocoap.Message(payload=payload)


# ─────────────────────────────────────────────
# Tài nguyên /sensor  (GET + POST)
# ─────────────────────────────────────────────
class SensorResource(resource.Resource):
    """
    Mô phỏng cảm biến IoT.
    - GET  : đọc giá trị hiện tại
    - POST : cập nhật giá trị (client gửi lên)
    """

    def __init__(self):
        super().__init__()
        self.data = {
            "temperature": 25.0,
            "humidity": 60.0,
            "unit": "Celsius/%RH",
            "timestamp": datetime.datetime.now().isoformat()
        }

    async def render_get(self, request):
        payload = json.dumps(self.data, ensure_ascii=False).encode("utf-8")
        return aiocoap.Message(payload=payload)

    async def render_post(self, request):
        try:
            received = json.loads(request.payload.decode("utf-8"))
            self.data.update(received)
            self.data["timestamp"] = datetime.datetime.now().isoformat()
            # (Observe được hỗ trợ đầy đủ ở Bài 3)
            response_payload = json.dumps(
                {"status": "ok", "updated": received}, ensure_ascii=False
            ).encode("utf-8")
            return aiocoap.Message(
                code=aiocoap.CHANGED, payload=response_payload
            )
        except Exception as e:
            return aiocoap.Message(
                code=aiocoap.BAD_REQUEST,
                payload=f"Loi: {e}".encode("utf-8")
            )


# ─────────────────────────────────────────────
# Khởi động server
# ─────────────────────────────────────────────
async def main():
    root = resource.Site()
    root.add_resource(["hello"], HelloResource())
    root.add_resource(["sensor"], SensorResource())

    # WKC (Well-Known Core) để client discovery tài nguyên
    root.add_resource(
        [".well-known", "core"],
        resource.WKCResource(root.get_resources_as_linkheader)
    )

    await aiocoap.Context.create_server_context(root, bind=("127.0.0.1", 5683))
    print("=== CoAP Server dang chay tai coap://127.0.0.1:5683 ===")
    print("  Tai nguyen: /hello  (GET)")
    print("  Tai nguyen: /sensor (GET, POST, Observe)")
    await asyncio.get_event_loop().create_future()   # chạy mãi


if __name__ == "__main__":
    asyncio.run(main())
