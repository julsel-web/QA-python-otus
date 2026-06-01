import re

import pytest
import requests


def test_response_format(host, port):
    response = requests.get(f"http://{host}:{port}")

    assert response.status_code == 200

    lines = response.text.split("\r\n")
    assert lines[0] == "Request Method: GET"
    assert re.match(r"Request Source: \('\d{1,3}(?:\.\d{1,3}){3}', \d+\)", lines[1]) is not None
    assert lines[2] == "Response Status: 200 OK"


def test_default_headers(host, port):
    response = requests.get(f"http://{host}:{port}")

    for header in response.request.headers.items():
        assert f"{header[0]}: {header[1]}" in response.text


def test_custom_header(host, port):
    key, value = "MyHeader", "Agr"
    response = requests.get(f"http://{host}:{port}", headers={key: value})

    assert f"{key}: {value}" in response.text


@pytest.mark.parametrize(
    "code, expected_code",
    [
        (200, 200),
        (201, 201),
        (404, 404),
        (503, 503),
        ("a", 200),
        ("", 200),
    ],
)
def test_status_code(host, port, code, expected_code):
    response = requests.get(f"http://{host}:{port}/?status={code}")

    assert response.status_code == expected_code


def test_status_second_parameter(host, port):
    response = requests.get(f"http://{host}:{port}/?a=1&status=500")

    assert response.status_code == 500


def test_post_method(host, port):
    response = requests.post(f"http://{host}:{port}")

    assert "Request Method: POST" in response.text


def test_server_alive(host, port):
    for _ in range(2):
        response = requests.get(f"http://{host}:{port}")
        assert response.status_code == 200
