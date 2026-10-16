from contextlib import contextmanager
from pathlib import Path

import allure

from selenium_object.driver_manager import DriverConfig, DriverManager

SCREENSHOT_DIR = Path("test-results/screenshots")


# --- 共用 helper（純函式 / context manager，非 fixture）-------------------------
# 各產品（travel / car / ...）的子 conftest 以 `from tests.ui_test.conftest import ...` 取用，
# 各自只需帶入不同的 base_url 等 DriverConfig 參數。


def resolve_headless(request) -> bool:
    """帶 --headed → 開視窗；未帶 → headless（預設）。"""
    return not request.config.getoption("--headed")


@contextmanager
def session_driver(request, **config):
    """各產品共用的 session-scope 瀏覽器樣板：launch → yield manager → quit。"""
    manager = DriverManager(
        DriverConfig(
            headless=resolve_headless(request),
            browser=request.config.getoption("--browser-name"),
            **config,
        )
    )
    manager.start()
    try:
        yield manager
    finally:
        manager.stop()


def capture_screenshot_on_failure(manager: DriverManager, request) -> None:
    """TC 失敗（setup 或 call）時截圖存 test-results/screenshots/{test_name}.png 並附到 allure。"""
    rep_setup = getattr(request.node, "rep_setup", None)
    rep_call = getattr(request.node, "rep_call", None)
    if not ((rep_setup and rep_setup.failed) or (rep_call and rep_call.failed)):
        return

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = SCREENSHOT_DIR / f"{request.node.name}.png"
    try:
        manager.driver.save_screenshot(str(path))
        allure.attach.file(str(path), name="screenshot", attachment_type=allure.attachment_type.PNG)
        allure.attach(manager.driver.current_url, name="url", attachment_type=allure.attachment_type.TEXT)
    except Exception:
        pass
