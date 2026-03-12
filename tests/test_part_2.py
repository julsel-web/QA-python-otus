def pytest_addoption(parser):
    parser.addoption("--url", action="store", default="https://ya.ru")
    parser.addoption("--code", action="store", type=int, default=200)

import pytest
import requests

@pytest.fixture
def params_data(request):
    url = request.config.getoption("--url")
    code = request.config.getoption("--code")
    return url, code

def test_status_code(params_data):
    url,code = params_data
    response = requests.get(url)
    assert response.status_code == code
