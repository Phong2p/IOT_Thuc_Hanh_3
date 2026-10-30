"""
Bài 2: CoAP Server với PUT (cập nhật trạng thái thiết bị)
Mô hình thiết bị IoT: đèn, quạt, nhiệt độ.
Hỗ trợ GET, POST, PUT.
"""

import asyncio
import aiocoap
import aiocoap.resource as resource
import json
import datetime


# ─────────────────────────────────────────────────────────────────
# Tài nguyên /device/{name}  (GET + PUT)
# ─────────────────────────────────────────────────────────────────
class DeviceResource(resource.ObservableResource):
    """
    Đại diện cho một thiết bị IoT (đèn, quạt, …).
    URI pattern: /device/<ten_thiet_bi>
    """

    def __init__(self, name: str, initial_state: dict):
        super().__init__()
        self.name = name
        self.state = initial_state
        self.state["last_updated"] = datetime.datetime.now().isoformat()

    # GET – đọc trạng thái hiện tại
    async def render_get(self, request):
        payload = json.dumps(self.state, ensure_ascii=False).encode("utf-8")
        return aiocoap.Message(payload=payload)

    # PUT – cập nhật (thay thế) trạng thái
    async def render_put(self, request):
        try:
            new_state = json.loads(request.payload.decode("utf-8"))
            self.state.update(new_state)
            self.state["last_updated"] = datetime.datetime.now().isoformat()
            self.updated_state()
            resp = json.dumps(
                {"status": "updated", "device": self.name, "state": self.state},
                ensure_ascii=False
            ).encode("utf-8")
            return aiocoap.Message(code=aiocoap.CHANGED, payload=resp)
        except Exception as e:
            return aiocoap.Message(
                code=aiocoap.BAD_REQUEST,
                payload=f"Loi: {e}".encode("utf-8")
            )

    # POST – nhận lệnh điều khiển
    async def render_post(self, request):
        try:
            cmd = json.loads(request.payload.decode("utf-8"))
            action = cmd.get("action", "")
            if action == "toggle":
                current = self.state.get("status", "off")
                self.state["status"] = "off" if current == "on" else "on"
            elif action in ("on", "off"):
                self.state["status"] = action
            else:
                self.state.update(cmd)
            self.state["last_updated"] = datetime.datetime.now().isoformat()
            self.updated_state()
            resp = json.dumps(
                {"status": "ok", "device": self.name, "state": self.state},
                ensure_ascii=False
            ).encode("utf-8")
            return aiocoap.Message(code=aiocoap.CHANGED, payload=resp)
        except Exception as e:
            return aiocoap.Message(
                code=aiocoap.BAD_REQUEST,
                payload=f"Loi: {e}".encode("utf-8")
            )


# ─────────────────────────────────────────────────────────────────
# Tài nguyên /sensor/temperature  (GET, Observe)
# ─────────────────────────────────────────────────────────────────
class TemperatureResource(resource.ObservableResource):
    """Cảm biến nhiệt độ tự động tăng mỗi 5 giây."""

    def __init__(self):
        super().__init__()
        self.temp = 22.0
        asyncio.get_event_loop().call_soon(
            lambda: asyncio.ensure_future(self._auto_update())
        )

    async def _auto_update(self):
        import random
        while True:
            await asyncio.sleep(5)
            self.temp = round(20 + random.uniform(0, 10), 1)
            self.updated_state()
            print(f"  [Sensor] Nhiet do cap nhat: {self.temp}°C")

    async def render_get(self, request):
        data = {
            "sensor": "temperature",
            "value": self.temp,
            "unit": "Celsius",
            "timestamp": datetime.datetime.now().isoformat()
        }
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        return aiocoap.Message(payload=payload)


# ─────────────────────────────────────────────────────────────────
# Khởi động server
# ─────────────────────────────────────────────────────────────────
async def main():
    root = resource.Site()

    # Thiết bị
    root.add_resource(["device", "den"],  DeviceResource("den",  {"status": "off", "brightness": 100}))
    root.add_resource(["device", "quat"], DeviceResource("quat", {"status": "off", "speed": 1}))
    root.add_resource(["device", "dieu-hoa"], DeviceResource("dieu-hoa", {"status": "off", "temp_set": 26}))

    # Cảm biến
    root.add_resource(["sensor", "temperature"], TemperatureResource())

    root.add_resource(
        [".well-known", "core"],
        resource.WKCResource(root.get_resources_as_linkheader)
    )

    await aiocoap.Context.create_server_context(root, bind=("127.0.0.1", 5683))
    print("=== CoAP Server Bai 2 dang chay tai coap://127.0.0.1:5683 ===")
    print("  /device/den        (GET, POST, PUT)")
    print("  /device/quat       (GET, POST, PUT)")
    print("  /device/dieu-hoa   (GET, POST, PUT)")
    print("  /sensor/temperature (GET, Observe)")
    await asyncio.get_event_loop().create_future()


if __name__ == "__main__":
    asyncio.run(main())
