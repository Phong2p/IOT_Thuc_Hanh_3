"""Bài 1: Gửi và nhận thông điệp tại /iot/lab/message bằng GET, POST."""

import argparse
import asyncio
from datetime import datetime

import aiocoap
import aiocoap.resource as resource
from aiocoap.error import Error
from aiocoap.numbers.contentformat import ContentFormat


class MessageResource(resource.Resource):
    """GET trả lời chào; POST nhận thông điệp UTF-8 từ sinh viên."""

    async def render_get(self, request):
        print("GET request received: /iot/lab/message")
        return aiocoap.Message(
            code=aiocoap.CONTENT,
            payload=b"Xin chao tu CoAP Server",
            content_format=ContentFormat.TEXT,
        )

    async def render_post(self, request):
        try:
            message = request.payload.decode("utf-8")
        except UnicodeDecodeError:
            return aiocoap.Message(
                code=aiocoap.BAD_REQUEST,
                payload=b"Loi: Thong diep phai su dung UTF-8",
                content_format=ContentFormat.TEXT,
            )

        if not message.strip():
            return aiocoap.Message(
                code=aiocoap.BAD_REQUEST,
                payload=b"Loi: Thong diep khong duoc de trong",
                content_format=ContentFormat.TEXT,
            )

        received_at = datetime.now().strftime("%H:%M:%S")
        print("POST request received:")
        print(f"Payload: {message}")
        print(f"Time: {received_at}")
        return aiocoap.Message(
            code=aiocoap.CHANGED,
            payload=b"Server da nhan thong diep",
            content_format=ContentFormat.TEXT,
        )


async def main(host="127.0.0.1", port=5683):
    root = resource.Site()
    root.add_resource(["iot", "lab", "message"], MessageResource())
    root.add_resource(
        [".well-known", "core"],
        resource.WKCResource(root.get_resources_as_linkheader),
    )

    context = await aiocoap.Context.create_server_context(root, bind=(host, port))
    try:
        print(f"CoAP Server started on port {port}")
        print(f"Resource: coap://{host}:{port}/iot/lab/message (GET, POST)")
        await asyncio.get_running_loop().create_future()
    finally:
        await context.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="Dia chi IP cua may Server")
    parser.add_argument("--port", type=int, default=5683, help="Cong CoAP (mac dinh: 5683)")
    args = parser.parse_args()
    try:
        asyncio.run(main(args.host, args.port))
    except KeyboardInterrupt:
        print("\nDa dung CoAP Server.")
    except (Error, OSError) as exc:
        raise SystemExit(f"Loi khoi dong CoAP Server: {exc}")
