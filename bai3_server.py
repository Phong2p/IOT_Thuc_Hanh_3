"""Bài 3: Điều khiển và Observe trạng thái đèn tại /iot/lab/light01/status."""

import argparse
import asyncio
import json

import aiocoap
import aiocoap.resource as resource
from aiocoap.error import Error
from aiocoap.numbers.contentformat import ContentFormat


class LightResource(resource.ObservableResource):
    """Đèn light01 ban đầu OFF; chỉ thông báo khi trạng thái thay đổi."""

    def __init__(self):
        super().__init__()
        self.status = "OFF"

    def state_response(self, code=aiocoap.CONTENT):
        data = {"device_id": "light01", "status": self.status}
        return aiocoap.Message(
            code=code,
            payload=json.dumps(data).encode("utf-8"),
            content_format=ContentFormat.JSON,
        )

    def update_observation_count(self, newcount):
        print(f"Observers: {newcount}")

    async def render_get(self, request):
        return self.state_response()

    async def render_put(self, request):
        try:
            data = json.loads(request.payload.decode("utf-8"))
            if not isinstance(data, dict):
                raise ValueError("Payload phai la mot doi tuong JSON.")
            if data.get("device_id") != "light01":
                raise ValueError("device_id phai la light01.")
            command = data.get("command")
            if command not in ("ON", "OFF"):
                raise ValueError("Lenh dieu khien phai la ON hoac OFF.")
        except ValueError as exc:
            return aiocoap.Message(
                code=aiocoap.BAD_REQUEST,
                payload=f"Loi: {exc}".encode("utf-8"),
                content_format=ContentFormat.TEXT,
            )

        print("PUT request received:")
        print("Device: light01")
        print(f"Command: {command}")
        previous = self.status
        self.status = command
        if previous != self.status:
            print(f"Light state changed: {previous} -> {self.status}")
            self.updated_state()
            print(f"Notify observers: {self.status}")
        else:
            print(f"Light state unchanged: {self.status}")
        return self.state_response(aiocoap.CHANGED)


async def main(host="127.0.0.1", port=5683):
    root = resource.Site()
    root.add_resource(["iot", "lab", "light01", "status"], LightResource())
    root.add_resource(
        [".well-known", "core"],
        resource.WKCResource(root.get_resources_as_linkheader),
    )
    context = await aiocoap.Context.create_server_context(root, bind=(host, port))
    try:
        print(f"CoAP Smart Light Server started on port {port}")
        print(f"Resource: coap://{host}:{port}/iot/lab/light01/status")
        print("Initial State: OFF")
        await asyncio.get_running_loop().create_future()
    finally:
        await context.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="Dia chi IP cua may Server")
    parser.add_argument("--port", type=int, default=5683, help="Cong CoAP")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("Cong CoAP phai nam trong khoang 1-65535.")
    try:
        asyncio.run(main(args.host, args.port))
    except KeyboardInterrupt:
        print("\nDa dung Smart Light Server.")
    except (Error, OSError) as exc:
        raise SystemExit(f"Loi khoi dong CoAP Server: {exc}")
