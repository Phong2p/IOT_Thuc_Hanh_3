"""Bài 3: Nhập ON/OFF/STATUS/EXIT để điều khiển đèn light01."""

import argparse
import asyncio
import json
import math

import aiocoap
from aiocoap.error import Error
from aiocoap.numbers.contentformat import ContentFormat


SERVER = "coap://127.0.0.1:5683"


async def send_command(command, server=SERVER, timeout=5.0):
    protocol = None
    uri = f"{server.rstrip('/')}/iot/lab/light01/status"
    try:
        protocol = await aiocoap.Context.create_client_context()
        if command == "STATUS":
            request = aiocoap.Message(
                code=aiocoap.GET, uri=uri, accept=ContentFormat.JSON
            )
        else:
            payload = json.dumps(
                {"device_id": "light01", "command": command}
            ).encode("utf-8")
            request = aiocoap.Message(
                code=aiocoap.PUT, uri=uri, payload=payload,
                content_format=ContentFormat.JSON, accept=ContentFormat.JSON,
            )
        print(f"\nSending {request.code} request...")
        response = await asyncio.wait_for(protocol.request(request).response, timeout)
        print(f"Response Code: {response.code}")
        if not response.code.is_successful():
            print(f"Loi: {response.payload.decode('utf-8', errors='replace')}")
            return 1
        if response.opt.content_format != ContentFormat.JSON:
            raise ValueError("Server khong tra ve application/json.")
        data = json.loads(response.payload.decode("utf-8"))
        if (
            not isinstance(data, dict)
            or data.get("device_id") != "light01"
            or data.get("status") not in ("ON", "OFF")
        ):
            raise ValueError("Du lieu trang thai den khong hop le.")
        if command != "STATUS" and data["status"] != command:
            raise ValueError("Trang thai phan hoi khong khop voi lenh dieu khien.")
        print("Response:")
        print(json.dumps(data, ensure_ascii=False))
        if command != "STATUS":
            print("Da bat den light01" if command == "ON" else "Da tat den light01")
        return 0
    except asyncio.TimeoutError:
        print(f"Loi: Server khong phan hoi trong {timeout:g} giay.")
        return 1
    except (Error, OSError, ValueError) as exc:
        print(f"Loi dieu khien CoAP: {exc}")
        return 1
    finally:
        if protocol is not None:
            await protocol.shutdown()


def main(server=SERVER, timeout=5.0):
    while True:
        command = input("\nNhap lenh (ON/OFF/STATUS/EXIT): ").strip().upper()
        if command == "EXIT":
            return 0
        if command not in ("ON", "OFF", "STATUS"):
            print("Lenh khong hop le. Hay nhap ON, OFF, STATUS hoac EXIT.")
            continue
        # Mỗi lệnh có một context riêng, đóng trước khi chờ nhập lệnh tiếp.
        asyncio.run(send_command(command, server, timeout))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", default=SERVER, help="Dia chi CoAP Server")
    parser.add_argument(
        "--timeout", type=float, default=5.0,
        help="Thoi gian cho moi phan hoi, tinh bang giay",
    )
    args = parser.parse_args()
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("Timeout phai la mot so huu han lon hon 0.")
    try:
        raise SystemExit(main(args.server, args.timeout))
    except (KeyboardInterrupt, EOFError):
        print("\nDa dung Controller Client.")
