import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest


SERVER_PATH = Path(__file__).resolve().parents[1] / "echo_server.py"


@pytest.fixture(scope="session")
def host():
    return "127.0.0.1"


@pytest.fixture(scope="session")
def port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="session", autouse=True)
def echo_server(host, port):
    process = subprocess.Popen(
        [sys.executable, str(SERVER_PATH), "--host", host, "--port", str(port)]
    )

    deadline = time.time() + 10
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex((host, int(port))) == 0:
                break
        time.sleep(0.1)
    else:
        process.terminate()
        process.wait(timeout=5)
        raise RuntimeError("Echo server did not start in time")

    yield process

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)
