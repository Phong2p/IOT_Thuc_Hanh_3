"""Bài 2: GET dữ liệu cảm biến mỗi 3 giây và cảnh báo nhiệt độ, độ ẩm."""

import argparse
import asyncio
from datetime import datetime
import json
import math

import aiocoap
from aiocoap.error import Error
from aiocoap.numbers.contentformat import ContentFormat


SERVER = "coap://127.0.0.1:5683"
POLL_INTERVAL = 3.0


def display_sensor_data(payload):
    """Kiểm tra JSON trước khi hiển thị và áp dụng các ngưỡng trong đề."""
    data = json.loads(payload.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Du lieu JSON phai la mot doi tuong.")
    device_id = data.get("device_id")
    if not isinstance(device_id, str) or not device_id.strip():
        raise ValueError("Du lieu thieu ma thiet bi device_id hop le.")
    for field in ("temperature", "humidity"):
        value = data.get(field)
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
        ):
            raise ValueError(f"Truong {field} phai la mot so huu han.")

    temperature = data["temperature"]
    humidity = data["humidity"]
    print(f"\n[{datetime.now():%H:%M:%S}] Received sensor data")
    print(f"Device: {device_id}")
    print(f"Temperature: {temperature} C")
    print(f"Humidity: {humidity} %")
    if temperature > 35:
        print("CANH BAO: Nhiet do cao")
    if humidity < 40:
        print("CANH BAO: Do am thap")
    if temperature <= 35 and humidity >= 40:
        print("Trang thai: Binh thuong")
    print("-" * 30)


async def main(server=SERVER, timeout=5.0):
    protocol = None
    uri = f"{server.rstrip('/')}/iot/lab/sensor01/data"
    loop = asyncio.get_running_loop()
    try:
        protocol = await aiocoap.Context.create_client_context()
        print(f"Monitoring CoAP Client: {uri}")
        print(f"Gui GET moi {POLL_INTERVAL:g} giay. Nhan Ctrl+C de dung.")
        while True:
            started_at = loop.time()
            request = aiocoap.Message(
                code=aiocoap.GET, uri=uri, accept=ContentFormat.JSON
            )
            try:
                response = await asyncio.wait_for(
                    protocol.request(request).response, timeout
                )
                if not response.code.is_successful():
                    print(
                        f"Loi CoAP: {response.code} - "
                        f"{response.payload.decode('utf-8', errors='replace')}"
                    )
                elif response.opt.content_format != ContentFormat.JSON:
                    print("Loi du lieu: Server khong tra ve application/json.")
                else:
                    display_sensor_data(response.payload)
            except asyncio.TimeoutError:
                print(f"Loi: Server khong phan hoi trong {timeout:g} giay.")
            except (Error, OSError) as exc:
                print(f"Loi ket noi CoAP: {exc}")
            except ValueError as exc:
                print(f"Loi du lieu cam bien: {exc}")

            # Tính cả thời gian chờ phản hồi vào chu kỳ GET 3 giây.
            elapsed = loop.time() - started_at
            await asyncio.sleep(max(0.0, POLL_INTERVAL - elapsed))
    except (Error, OSError, ValueError) as exc:
        print(f"Loi khoi dong Monitoring CoAP Client: {exc}")
        return 1
    finally:
        if protocol is not None:
            await protocol.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--server", default=SERVER, help="Dia chi Server, vi du: coap://127.0.0.1:5683"
    )
    parser.add_argument(
        "--timeout", type=float, default=5.0,
        help="Thoi gian cho moi phan hoi, tinh bang giay",
    )
    args = parser.parse_args()
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("Timeout phai la mot so huu han lon hon 0.")
    try:
        raise SystemExit(asyncio.run(main(args.server, args.timeout)))
    except KeyboardInterrupt:
        print("\nDa dung Monitoring CoAP Client.")
