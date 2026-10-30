"""
Bài 2: CoAP Client – điều khiển thiết bị IoT
Sử dụng GET, POST, PUT để đọc và điều khiển thiết bị.
"""

import asyncio
import aiocoap
import json

SERVER = "coap://127.0.0.1"


async def coap_get(protocol, path):
    request = aiocoap.Message(code=aiocoap.GET, uri=f"{SERVER}/{path}")
    response = await protocol.request(request).response
    return response


async def coap_post(protocol, path, data: dict):
    payload = json.dumps(data).encode("utf-8")
    request = aiocoap.Message(
        code=aiocoap.POST, uri=f"{SERVER}/{path}", payload=payload
    )
    response = await protocol.request(request).response
    return response


async def coap_put(protocol, path, data: dict):
    payload = json.dumps(data).encode("utf-8")
    request = aiocoap.Message(
        code=aiocoap.PUT, uri=f"{SERVER}/{path}", payload=payload
    )
    response = await protocol.request(request).response
    return response


async def main():
    protocol = await aiocoap.Context.create_client_context()

    # ── 1. Đọc trạng thái đèn ─────────────────────────────────────
    print("\n[GET] Trang thai den:")
    r = await coap_get(protocol, "device/den")
    print(f"  {r.payload.decode('utf-8')}")

    # ── 2. Bật đèn bằng POST ──────────────────────────────────────
    print("\n[POST] Bat den (action=on):")
    r = await coap_post(protocol, "device/den", {"action": "on"})
    print(f"  {r.payload.decode('utf-8')}")

    # ── 3. Cập nhật độ sáng bằng PUT ─────────────────────────────
    print("\n[PUT] Cap nhat do sang den = 50%:")
    r = await coap_put(protocol, "device/den", {"brightness": 50})
    print(f"  {r.payload.decode('utf-8')}")

    # ── 4. Toggle quạt ────────────────────────────────────────────
    print("\n[POST] Toggle quat:")
    r = await coap_post(protocol, "device/quat", {"action": "toggle"})
    print(f"  {r.payload.decode('utf-8')}")

    # ── 5. Đặt nhiệt độ điều hòa bằng PUT ────────────────────────
    print("\n[PUT] Cap nhat dieu hoa (nhiet do dat = 24, bat):")
    r = await coap_put(protocol, "device/dieu-hoa", {"status": "on", "temp_set": 24})
    print(f"  {r.payload.decode('utf-8')}")

    # ── 6. Đọc cảm biến nhiệt độ ──────────────────────────────────
    print("\n[GET] Cam bien nhiet do:")
    r = await coap_get(protocol, "sensor/temperature")
    data = json.loads(r.payload.decode("utf-8"))
    print(f"  {json.dumps(data, indent=4, ensure_ascii=False)}")


if __name__ == "__main__":
    asyncio.run(main())
