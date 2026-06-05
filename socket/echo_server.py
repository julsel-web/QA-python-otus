import argparse
import socket
from http import HTTPStatus
from urllib.parse import parse_qs, urlsplit


BUFFER_SIZE = 4096
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5000


def parse_request(raw_request: bytes) -> tuple[str, str, dict[str, str]]:
    request_text = raw_request.decode("iso-8859-1")
    request_head = request_text.split("\r\n\r\n", 1)[0]
    request_lines = request_head.split("\r\n")

    request_line = request_lines[0] if request_lines else ""
    method, target, _ = (request_line.split(" ", 2) + ["", "", ""])[:3]

    headers: dict[str, str] = {}
    for header_line in request_lines[1:]:
        if not header_line or ":" not in header_line:
            continue
        header_name, header_value = header_line.split(":", 1)
        headers[header_name.strip()] = header_value.strip()

    return method, target, headers


def get_status_code(target: str) -> int:
    try:
        query_string = urlsplit(target).query
        status_value = parse_qs(query_string).get("status", [""])[0]
        status_code = int(status_value)
        HTTPStatus(status_code)
        return status_code
    except (ValueError, TypeError):
        return HTTPStatus.OK


def build_response(
    method: str,
    client_address: tuple[str, int],
    request_headers: dict[str, str],
    status_code: int,
) -> bytes:
    status = HTTPStatus(status_code)
    body_lines = [
        f"Request Method: {method}",
        f"Request Source: {client_address}",
        f"Response Status: {status.value} {status.phrase}",
    ]
    body_lines.extend(f"{name}: {value}" for name, value in request_headers.items())
    body = "\r\n".join(body_lines).encode("utf-8")

    response_headers = [
        f"HTTP/1.1 {status.value} {status.phrase}",
        "Content-Type: text/plain; charset=utf-8",
        f"Content-Length: {len(body)}",
        "Connection: close",
        "",
        "",
    ]
    return "\r\n".join(response_headers).encode("ascii") + body


def handle_client_connection(client_socket: socket.socket, client_address: tuple[str, int]) -> None:
    request = client_socket.recv(BUFFER_SIZE)
    if not request:
        return

    method, target, headers = parse_request(request)
    status_code = get_status_code(target)
    response = build_response(method, client_address, headers, status_code)
    client_socket.sendall(response)


def serve_forever(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen()

        while True:
            client_socket, client_address = server_socket.accept()
            with client_socket:
                handle_client_connection(client_socket, client_address)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run echo HTTP server")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    serve_forever(host=arguments.host, port=arguments.port)
