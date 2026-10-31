"""Bài 2: Cung cấp dữ liệu nhiệt độ, độ ẩm tại /iot/lab/sensor01/data."""

import argparse
import asyncio
from contextlib import suppress
from datetime import datetime
import json
import random

import aiocoap
import aiocoap.resource as resource
from aiocoap.error import Error
from aiocoap.numbers.contentformat import ContentFormat


UPDATE_INTERVAL = 3.0


class SensorResource(resource.Resource):
    """Lưu mẫu cảm biến mới nhất; GET không làm thay đổi dữ liệu."""

    def __init__(self):
        super().__init__()
        self.update_data()

    def update_data(self):
        self.data = {
            "device_id": "sensor01",
            "temperature": round(random.uniform(20.0, 40.0), 1),
            "humidity": round(random.uniform(30.0, 80.0), 1),
        }

    async def update_loop(self):
        while True:
            await asyncio.sleep(UPDATE_INTERVAL)
            self.update_data()
            print(f"[{datetime.now():%H:%M:%S}] Sensor updated: {self.data}")

    async def render_get(self, request):
        print("GET request received: /iot/lab/sensor01/data")
        return aiocoap.Message(
            code=aiocoap.CONTENT,
            payload=json.dumps(self.data).encode("utf-8"),
            content_format=ContentFormat.JSON,
        )


async def main(host="127.0.0.1", port=5683):
    sensor = SensorResource()
    root = resource.Site()
    root.add_resource(["iot", "lab", "sensor01", "data"], sensor)
    root.add_resource(
        [".well-known", "core"],
        resource.WKCResource(root.get_resources_as_linkheader),
    )

    context = await aiocoap.Context.create_server_context(root, bind=(host, port))
    update_task = asyncio.create_task(sensor.update_loop())
    try:
        print(f"Sensor CoAP Server started on port {port}")
        print(f"Resource: coap://{host}:{port}/iot/lab/sensor01/data (GET)")
        print(f"Du lieu cam bien duoc cap nhat moi {UPDATE_INTERVAL:g} giay.")
        await asyncio.get_running_loop().create_future()
    finally:
        update_task.cancel()
        with suppress(asyncio.CancelledError):
            await update_task
        await context.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="Dia chi IP cua may Server")
    parser.add_argument(
        "--port", type=int, default=5683, help="Cong CoAP (mac dinh: 5683)"
    )
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("Cong CoAP phai nam trong khoang 1-65535.")
    try:
        asyncio.run(main(args.host, args.port))
    except KeyboardInterrupt:
        print("\nDa dung Sensor CoAP Server.")
    except (Error, OSError) as exc:
        raise SystemExit(f"Loi khoi dong CoAP Server: {exc}")
