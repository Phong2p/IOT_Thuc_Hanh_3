"""Bài 1: GET lời chào và POST thông điệp chứa mã sinh viên, họ tên."""

import argparse
import asyncio

import aiocoap
from aiocoap.error import Error
from aiocoap.numbers.contentformat import ContentFormat


SERVER = "coap://127.0.0.1:5683"


async def main(server=SERVER, student_id="B23DCCN001", name="Nguyen Van A", timeout=5.0):
    protocol = None
    uri = f"{server.rstrip('/')}/iot/lab/message"
    message = f"Xin chao tu CoAP Client - {student_id} - {name}"

    try:
        protocol = await aiocoap.Context.create_client_context()
        print("CoAP Client")
        for method, payload in ((aiocoap.GET, b""), (aiocoap.POST, message.encode("utf-8"))):
            print(f"\nSending {method} request...")
            print(f"URI: {uri}")
            if payload:
                print(f"Payload: {message}")
            request = aiocoap.Message(code=method, uri=uri, payload=payload)
            if method == aiocoap.POST:
                request.opt.content_format = ContentFormat.TEXT
            response = await asyncio.wait_for(protocol.request(request).response, timeout)
            print("\nResponse:")
            print(f"Code: {response.code}")
            print(f"Payload: {response.payload.decode('utf-8', errors='replace')}")
            if not response.code.is_successful():
                print("Loi: Server tu choi yeu cau. Hay kiem tra URI va noi dung thong diep.")
                return 1
        return 0
    except asyncio.TimeoutError:
        print(f"Loi: Server khong phan hoi trong {timeout:g} giay. Hay kiem tra Server va dia chi IP.")
        return 1
    except (Error, OSError, ValueError) as exc:
        print(f"Loi gui yeu cau CoAP: {exc}")
        return 1
    finally:
        if protocol is not None:
            await protocol.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", default=SERVER, help="Dia chi Server, vi du: coap://127.0.0.1:5683")
    parser.add_argument("--student-id", default="B23DCCN001", help="Ma sinh vien (mac dinh la vi du trong de)")
    parser.add_argument("--name", default="Nguyen Van A", help="Ho ten sinh vien (mac dinh la vi du trong de)")
    parser.add_argument("--timeout", type=float, default=5.0, help="Thoi gian cho moi phan hoi, tinh bang giay")
    args = parser.parse_args()
    if not args.student_id.strip() or not args.name.strip():
        parser.error("Ma sinh vien va ho ten khong duoc de trong.")
    if not args.timeout > 0:
        parser.error("Timeout phai lon hon 0.")
    try:
        raise SystemExit(asyncio.run(main(args.server, args.student_id.strip(), args.name.strip(), args.timeout)))
    except KeyboardInterrupt:
        print("\nDa dung CoAP Client.")
