"""
Bài 1: CoAP Client cơ bản
Gửi GET và POST đến server.
"""

import asyncio
import aiocoap
import json


SERVER = "coap://127.0.0.1"


async def main():
    protocol = await aiocoap.Context.create_client_context()

    # ── 1. GET /hello ──────────────────────────────────────────────────
    print("\n[GET] coap://127.0.0.1/hello")
    request = aiocoap.Message(code=aiocoap.GET, uri=f"{SERVER}/hello")
    response = await protocol.request(request).response
    print(f"  Code   : {response.code}")
    print(f"  Payload: {response.payload.decode('utf-8')}")

    # ── 2. GET /sensor ─────────────────────────────────────────────────
    print("\n[GET] coap://127.0.0.1/sensor")
    request = aiocoap.Message(code=aiocoap.GET, uri=f"{SERVER}/sensor")
    response = await protocol.request(request).response
    print(f"  Code   : {response.code}")
    data = json.loads(response.payload.decode("utf-8"))
    print(f"  Payload: {json.dumps(data, indent=4, ensure_ascii=False)}")

    # ── 3. POST /sensor (cập nhật giá trị) ────────────────────────────
    print("\n[POST] coap://127.0.0.1/sensor")
    new_data = {"temperature": 30.5, "humidity": 75.0}
    payload = json.dumps(new_data).encode("utf-8")
    request = aiocoap.Message(
        code=aiocoap.POST, uri=f"{SERVER}/sensor", payload=payload
    )
    response = await protocol.request(request).response
    print(f"  Code   : {response.code}")
    print(f"  Payload: {response.payload.decode('utf-8')}")

    # ── 4. GET /sensor sau khi POST ────────────────────────────────────
    print("\n[GET] coap://127.0.0.1/sensor (sau POST)")
    request = aiocoap.Message(code=aiocoap.GET, uri=f"{SERVER}/sensor")
    response = await protocol.request(request).response
    data = json.loads(response.payload.decode("utf-8"))
    print(f"  Payload: {json.dumps(data, indent=4, ensure_ascii=False)}")


if __name__ == "__main__":
    asyncio.run(main())
