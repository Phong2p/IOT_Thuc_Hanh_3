"""Bài 3: Observe trạng thái đèn light01 cho đến khi nhấn Ctrl+C."""

import argparse
import asyncio
from datetime import datetime
import json
import math

import aiocoap
from aiocoap.error import Error
from aiocoap.numbers.contentformat import ContentFormat


SERVER = "coap://127.0.0.1:5683"


def display_state(response, label):
    if not response.code.is_successful():
        raise ValueError(
            f"CoAP {response.code}: "
            f"{response.payload.decode('utf-8', errors='replace')}"
        )
    if response.opt.content_format != ContentFormat.JSON:
        raise ValueError("Server khong tra ve application/json.")
    data = json.loads(response.payload.decode("utf-8"))
    if (
        not isinstance(data, dict)
        or data.get("device_id") != "light01"
        or data.get("status") not in ("ON", "OFF")
    ):
        raise ValueError("Du lieu trang thai den khong hop le.")
    print(f"\n[{datetime.now():%H:%M:%S}] {label}")
    print(f"Device: {data['device_id']}")
    print(f"Status: {data['status']}")


async def main(server=SERVER, timeout=5.0):
    protocol = None
    exchange = None
    uri = f"{server.rstrip('/')}/iot/lab/light01/status"
    try:
        protocol = await aiocoap.Context.create_client_context()
        print(f"Registering CoAP Observe: {uri}")
        request = aiocoap.Message(
            code=aiocoap.GET, uri=uri, observe=0, accept=ContentFormat.JSON
        )
        exchange = protocol.request(request)
        first = await asyncio.wait_for(exchange.response, timeout)
        if first.code.is_successful() and first.opt.observe is None:
            raise ValueError("Tai nguyen khong ho tro CoAP Observe.")
        display_state(first, "Initial State")
        print("Observe registration successful. Nhan Ctrl+C de dung.")
        async for response in exchange.observation:
            display_state(response, "State Updated")
        print("Server da ket thuc Observe.")
        return 1
    except asyncio.TimeoutError:
        print(f"Loi: Server khong phan hoi dang ky Observe trong {timeout:g} giay.")
        return 1
    except (Error, OSError, ValueError) as exc:
        print(f"Loi Observe: {exc}")
        return 1
    finally:
        if exchange is not None and not exchange.observation.cancelled:
            exchange.observation.cancel()
        if protocol is not None:
            await protocol.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", default=SERVER, help="Dia chi CoAP Server")
    parser.add_argument(
        "--timeout", type=float, default=5.0,
        help="Thoi gian cho phan hoi dang ky Observe, tinh bang giay",
    )
    args = parser.parse_args()
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("Timeout phai la mot so huu han lon hon 0.")
    try:
        raise SystemExit(asyncio.run(main(args.server, args.timeout)))
    except KeyboardInterrupt:
        print("\nDa dung Monitoring Client.")
