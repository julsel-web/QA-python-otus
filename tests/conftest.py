import pytest
import pymysql
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
    parser.addoption("--db-host", default="localhost", help="MariaDB host")
    parser.addoption("--db-port", type=int, default=3306, help="MariaDB port")
    parser.addoption("--db-name", default="opencart", help="Database name")
    parser.addoption("--db-user", default="opencart", help="Database user")
    parser.addoption("--db-password", default="opencart", help="Database password")


@pytest.fixture(scope="session")
def base_url(request):
    url = request.config.getoption("--url")
    return url

@pytest.fixture(scope="session")
def base_code(request):
    code = request.config.getoption("--code")
    return code


@pytest.fixture(scope="session")
def connection(request):
    connection = pymysql.connect(
        host=request.config.getoption("--db-host"),
        port=request.config.getoption("--db-port"),
        user=request.config.getoption("--db-user"),
        password=request.config.getoption("--db-password"),
        database=request.config.getoption("--db-name"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )
    yield connection
    connection.close()

def test_status_code(base_url, base_code):
    url = base_url
    code = base_code
    response = requests.get(url)
    assert response.status_code == code




