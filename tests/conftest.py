import pytest
import requests

try:
    from appium import webdriver
    from appium.options.common import AppiumOptions
    from selenium.webdriver.remote.command import Command
except ImportError:
    webdriver = None
    AppiumOptions = None
    Command = object


DEFAULT_APPIUM_URL = "http://127.0.0.1:4723"
DEFAULT_APK_PATH = "/Users/uliatuz/Downloads/pnv_486875_ece65f-582630-edb363.apk"
DEFAULT_APP_PACKAGE = "com.csdroid.pkg"
DEFAULT_REPORT_PATH = "report.html"


class ReportCommand(Command):
    GET_REPORT = "getReport"
    DELETE_REPORT = "deleteReport"
    SET_TEST_INFO = "setTestInfo"


def wait_for_service(service_url, attempts=10, sleep_seconds=2):
    for _ in range(attempts):
        try:
            response = requests.get(service_url, timeout=3)
            response.raise_for_status()
            return
        except Exception:
            import time
            time.sleep(sleep_seconds)
    raise RuntimeError(f"Сервис недоступен по адресу {service_url}")


def register_report_commands(driver):
    driver.command_executor._commands = {
        **driver.command_executor._commands,
        ReportCommand.GET_REPORT: ("GET", "/getReport"),
        ReportCommand.DELETE_REPORT: ("DELETE", "/deleteReportData"),
        ReportCommand.SET_TEST_INFO: ("POST", "/setTestInfo"),
    }

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
    parser.addoption("--appium-url", default=DEFAULT_APPIUM_URL, help="URL Appium сервера")
    parser.addoption("--appium-apk", default=DEFAULT_APK_PATH, help="Путь до apk файла")
    parser.addoption("--appium-device-name", default="Android", help="Имя Android устройства или эмулятора")
    parser.addoption("--appium-platform-version", default="", help="Версия Android устройства")
    parser.addoption("--app-package", default=DEFAULT_APP_PACKAGE, help="Package тестируемого apk")
    parser.addoption("--report-path", default=DEFAULT_REPORT_PATH, help="Путь сохранения html-отчета")


def pytest_configure(config):
    config.addinivalue_line("markers", "mobile: mark test as mobile app test")


@pytest.fixture(scope="session")
def base_url(request):
    url = request.config.getoption("--url")
    return url

@pytest.fixture(scope="session")
def base_code(request):
    code = request.config.getoption("--code")
    return code


@pytest.fixture(scope="function")
def driver(request):
    if webdriver is None or AppiumOptions is None:
        pytest.skip("Для mobile-тестов установите Appium-Python-Client в окружение проекта")

    appium_url = request.config.getoption("--appium-url").rstrip("/")
    appium_apk = request.config.getoption("--appium-apk")
    device_name = request.config.getoption("--appium-device-name")
    platform_version = request.config.getoption("--appium-platform-version")

    wait_for_service(f"{appium_url}/status")

    options = AppiumOptions()
    capabilities = {
        "platformName": "Android",
        "appium:automationName": "UiAutomator2",
        "appium:deviceName": device_name,
        "appium:app": appium_apk,
        "appium:autoGrantPermissions": True,
    }
    if platform_version:
        capabilities["appium:platformVersion"] = platform_version
    options.load_capabilities(capabilities)

    android_driver = webdriver.Remote(appium_url, options=options)
    register_report_commands(android_driver)
    yield android_driver
    android_driver.quit()


@pytest.fixture(scope="function")
def app_package(request):
    return request.config.getoption("--app-package")


@pytest.fixture(scope="function")
def report(driver):
    driver.execute(ReportCommand.DELETE_REPORT)
    yield

def test_status_code(base_url, base_code):
    url = base_url
    code = base_code
    response = requests.get(url)
    assert response.status_code == code


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        item.add_marker(pytest.mark.status(status=rep.outcome))


