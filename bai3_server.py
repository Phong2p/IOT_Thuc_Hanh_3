"""
Bài 3: CoAP Observe – giám sát thay đổi tài nguyên theo thời gian thực
Server tự động cập nhật dữ liệu cảm biến và thông báo cho Observer.
"""

import asyncio
import aiocoap
import aiocoap.resource as resource
import json
import datetime
import random


# ─────────────────────────────────────────────────────────────────
# Tài nguyên Observable: /monitor/sensors
# ─────────────────────────────────────────────────────────────────
class MultiSensorResource(resource.ObservableResource):
    """
    Tổng hợp nhiều cảm biến, tự cập nhật mỗi 3 giây.
    Hỗ trợ Observe để client nhận thông báo tự động.
    """

    def __init__(self):
        super().__init__()
        self.sensors = {
            "temperature": 25.0,
            "humidity": 60.0,
            "light": 800,        # lux
            "motion": False,
            "timestamp": datetime.datetime.now().isoformat()
        }
        asyncio.get_event_loop().call_soon(
            lambda: asyncio.ensure_future(self._update_loop())
        )

    async def _update_loop(self):
        """Mô phỏng cảm biến thay đổi liên tục."""
        while True:
            await asyncio.sleep(3)
            self.sensors["temperature"] = round(20 + random.uniform(0, 15), 1)
            self.sensors["humidity"]    = round(40 + random.uniform(0, 40), 1)
            self.sensors["light"]       = random.randint(0, 1000)
            self.sensors["motion"]      = random.choice([True, False])
            self.sensors["timestamp"]   = datetime.datetime.now().isoformat()
            self.updated_state()
            print(f"  [Update] {self.sensors}")

    async def render_get(self, request):
        payload = json.dumps(self.sensors, ensure_ascii=False).encode("utf-8")
        return aiocoap.Message(payload=payload)


# ─────────────────────────────────────────────────────────────────
# Tài nguyên Observable: /monitor/alert
# ─────────────────────────────────────────────────────────────────
class AlertResource(resource.ObservableResource):
    """
    Phát cảnh báo khi nhiệt độ vượt ngưỡng.
    Kết hợp với MultiSensorResource.
    """

    def __init__(self, sensor_resource: MultiSensorResource):
        super().__init__()
        self.sensor = sensor_resource
        self.alert = {"level": "normal", "message": "Tat ca binh thuong", "timestamp": ""}
        asyncio.get_event_loop().call_soon(
            lambda: asyncio.ensure_future(self._watch_loop())
        )

    async def _watch_loop(self):
        prev_level = "normal"
        while True:
            await asyncio.sleep(3.5)
            temp = self.sensor.sensors.get("temperature", 0)
            motion = self.sensor.sensors.get("motion", False)

            if temp > 32:
                level = "danger"
                msg = f"NGUY HIEM! Nhiet do cao: {temp}°C"
            elif temp > 28:
                level = "warning"
                msg = f"CANH BAO: Nhiet do cao: {temp}°C"
            elif motion:
                level = "info"
                msg = "Phat hien chuyen dong!"
            else:
                level = "normal"
                msg = "Tat ca binh thuong"

            self.alert = {
                "level": level,
                "message": msg,
                "temperature": temp,
                "timestamp": datetime.datetime.now().isoformat()
            }
            if level != prev_level:
                self.updated_state()
                prev_level = level

    async def render_get(self, request):
        payload = json.dumps(self.alert, ensure_ascii=False).encode("utf-8")
        return aiocoap.Message(payload=payload)


# ─────────────────────────────────────────────────────────────────
# Khởi động server
# ─────────────────────────────────────────────────────────────────
async def main():
    root = resource.Site()

    sensor_res = MultiSensorResource()
    root.add_resource(["monitor", "sensors"], sensor_res)
    root.add_resource(["monitor", "alert"],   AlertResource(sensor_res))

    root.add_resource(
        [".well-known", "core"],
        resource.WKCResource(root.get_resources_as_linkheader)
    )

    await aiocoap.Context.create_server_context(root, bind=("127.0.0.1", 5683))
    print("=== CoAP Server Bai 3 (Observe) dang chay ===")
    print("  /monitor/sensors  (GET, Observe)")
    print("  /monitor/alert    (GET, Observe)")
    print("  Du lieu tu dong cap nhat moi 3 giay...")
    await asyncio.get_event_loop().create_future()


if __name__ == "__main__":
    asyncio.run(main())
