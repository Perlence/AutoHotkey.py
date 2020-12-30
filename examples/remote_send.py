"""Receive keys over TCP and replay them.

Example::

   $ ahkpy remote_send.py &
   Listening on localhost 3033
   $ printf "#r" | nc localhost 3033
"""

import argparse
import asyncio
import sys

import ahkpy as ahk


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("HOST", nargs="?", default="localhost")
    parser.add_argument("PORT", nargs="?", default=3033, type=int)
    args = parser.parse_args()

    try:
        asyncio.run(serve(args.HOST, args.PORT))
    except KeyboardInterrupt:
        sys.exit()


async def serve(host, port):
    srv = await asyncio.start_server(handle, host, port)
    print("Listening on", host, port)

    # Schedule a function that will check AHK message queue repeatedly.
    loop = asyncio.get_running_loop()
    loop.call_soon(sleeper, loop)

    await srv.serve_forever()


async def handle(reader, writer):
    try:
        send_bytes = await reader.read()
        send_str = send_bytes.decode()

        print(repr(send_str))
        ahk.send(send_str)
    finally:
        writer.close()


def sleeper(loop):
    ahk.sleep(0.01)
    loop.call_soon(sleeper, loop)


if __name__ == "__main__":
    main()
