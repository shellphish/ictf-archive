import argparse
import base64
import subprocess
from pwn import *


def parse_args():
    parser = argparse.ArgumentParser(description="Helper to submit the solution")

    parser.add_argument(
        "--ip",
        type=str,
    )

    parser.add_argument(
        "--port",
        type=str,
    )

    parser.add_argument(
        "--image",
        type=str,
    )

    return parser.parse_args()


def main():
    args = parse_args()

    with open(args.image, "rb") as f:
        image_b64 = base64.b64encode(f.read())

    conn = remote(args.ip, args.port)

    pow_line = (
        conn.recvuntil(b"===================").split(b"with:\n")[1].split(b"\n")[0]
    )

    pow_answer = subprocess.check_output(
        f'bash -c "{pow_line.decode()}"', shell=True, stderr=subprocess.DEVNULL
    ).strip()

    conn.sendlineafter(b"Solution? ", pow_answer)
    conn.sendlineafter(b"Enter your input: ", image_b64)

    print(conn.recvall().decode())


if __name__ == "__main__":
    main()
