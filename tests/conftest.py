import pytest
import requests




@pytest.fixture(scope="session")
def session():
    session = requests.Session()
    yield session
    session.close()

@pytest.fixture(scope="session")
def dog_api():
    return "https://dog.ceo/api"


@pytest.fixture(scope="session")
def brewery_api():
    return "https://api.openbrewerydb.org/v1/breweries"


@pytest.fixture(scope="session")
def json_api():
    return "https://jsonplaceholder.typicode.com"


def pytest_addoption(parser):
    parser.addoption("--url",  default="https://ya.ru", help="This is request url")
    parser.addoption("--code", type=int, default=200, help="This is request code")


@pytest.fixture(scope="session")
def base_url(request):
    url = request.config.getoption("--url")
    return url

@pytest.fixture(scope="session")
def base_code(request):
    code = request.config.getoption("--code")
    return code

def test_status_code(base_url, base_code):
    url = base_url
    code = base_code
    response = requests.get(url)
    assert response.status_code == code





