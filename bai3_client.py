"""
Bài 3: CoAP Client – Observe (giám sát tài nguyên thời gian thực)
Client đăng ký Observe và nhận thông báo tự động từ server.
"""

import asyncio
import aiocoap
import json

SERVER = "coap://127.0.0.1"


async def observe_resource(protocol, path, label, duration=30):
    """Đăng ký Observe trên một tài nguyên trong `duration` giây."""
    print(f"\n[OBSERVE] {SERVER}/{path}  (trong {duration} giay)")
    print("  Dang cho nhan thong bao tu server...\n")

    request = aiocoap.Message(
        code=aiocoap.GET,
        uri=f"{SERVER}/{path}",
        observe=0   # 0 = đăng ký observe
    )

    obs_request = protocol.request(request)

    async def _watch():
        async for response in obs_request.observation:
            if response.code.is_successful():
                try:
                    data = json.loads(response.payload.decode("utf-8"))
                    print(f"  [{label}] {json.dumps(data, ensure_ascii=False)}")
                except Exception:
                    print(f"  [{label}] {response.payload.decode('utf-8')}")
            else:
                print(f"  [Loi] {response.code}")

    # Nhận phản hồi đầu tiên
    first_response = await obs_request.response
    try:
        data = json.loads(first_response.payload.decode("utf-8"))
        print(f"  [{label}] (ban dau) {json.dumps(data, ensure_ascii=False)}")
    except Exception:
        print(f"  [{label}] (ban dau) {first_response.payload.decode('utf-8')}")

    # Chạy vòng lặp Observe song song
    watch_task = asyncio.ensure_future(_watch())

    # Dừng sau `duration` giây
    await asyncio.sleep(duration)
    obs_request.observation.cancel()
    watch_task.cancel()
    print(f"\n  [OBSERVE] Dung quan sat {path}")


async def main():
    protocol = await aiocoap.Context.create_client_context()

    # Observe cả sensors và alert đồng thời
    await asyncio.gather(
        observe_resource(protocol, "monitor/sensors", "SENSOR", duration=30),
        observe_resource(protocol, "monitor/alert",   "ALERT",  duration=30),
    )


if __name__ == "__main__":
    asyncio.run(main())
