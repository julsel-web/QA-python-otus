import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from tests.conftest import ReportCommand

AppiumBy = pytest.importorskip("appium.webdriver.common.appiumby").AppiumBy


@pytest.mark.mobile
@pytest.mark.usefixtures("report")
def test_open_calendar_from_pnv(driver, app_package, request):
    element_names = []

    try:
        for _ in range(15):
            elements = driver.find_elements(AppiumBy.ID, "com.csdroid.pkg:id/tv_title")
            element_names = [element.text for element in elements]

            if "Calendar" in element_names:
                calendar_app = next(
                    element for element in elements if element.text == "Calendar"
                )
                calendar_app.click()
                break

            assert len(elements) >= 2, "Недостаточно элементов на экране для свайпа"

            driver.swipe(
                elements[1].rect["x"],
                elements[1].rect["y"],
                elements[0].rect["x"],
                elements[0].rect["y"],
            )
        else:
            pytest.fail("Не удалось найти приложение Calendar после серии свайпов")

        try:
            open_button = WebDriverWait(driver, 5).until(
                lambda current_driver: current_driver.find_element(
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    'new UiSelector().textMatches("(?i)open")',
                )
            )
            open_button.click()
        except TimeoutException:
            pass

        WebDriverWait(driver, 15).until(
            lambda current_driver: current_driver.current_package != app_package
        )
    finally:
        test_result = getattr(request.node, "rep_call", None)
        test_status = test_result.outcome if test_result else "unknown"

        driver.execute(
            ReportCommand.SET_TEST_INFO,
            {
                "sessionId": driver.session_id,
                "testName": request.node.name,
                "testStatus": test_status,
            },
        )
        html = driver.execute(ReportCommand.GET_REPORT)
        with open("report.html", "w", encoding="utf-8") as report_file:
            report_file.write(html["value"])

    assert driver.current_package != app_package, (
        "После клика по Calendar приложение PNV осталось активным: "
        f"{driver.current_package}"
    )
