import pytest

from selenium_object.travel.home_page import TravelHomePage
from tests.ui_test.conftest import capture_screenshot_on_failure, session_driver


@pytest.fixture(scope="session")
def travel_driver(request, settings):
    """Session-scope 瀏覽器，整個 session 只 launch 一次；TC 間隔離由 travel_home 清 cookies 達成。"""
    with session_driver(request, base_url=settings.urls.TRAVEL_BASE_URL) as manager:
        yield manager


@pytest.fixture
def travel_home(travel_driver) -> TravelHomePage:
    """每個 TC 清掉 cookies / storage 後，回傳已載入完成的旅遊險首頁。"""
    travel_driver.reset()
    return travel_driver.open(TravelHomePage).load()


@pytest.fixture(autouse=True)
def screenshot_on_failure(request, travel_driver):
    yield
    capture_screenshot_on_failure(travel_driver, request)


@pytest.fixture
def travel_account(settings):
    return settings.account.TRAVEL
