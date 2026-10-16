import logging

import pytest

from configs.settings import load_settings

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def suppress_noisy_loggers():
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("selenium").setLevel(logging.WARNING)


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default=None,
        choices=["prod"],
        help="Target environment（必填，沒有預設值）：prod",
    )
    # --- UI（Selenium）---
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="開瀏覽器視窗執行（預設 headless）；需要人工輸入驗證碼的 TC 必須加",
    )
    parser.addoption(
        "--browser-name",
        action="store",
        default="chrome",
        choices=["chrome", "edge", "firefox"],
        help="瀏覽器種類（預設 chrome）",
    )


def pytest_configure(config):
    if not config.getoption("--env") and not config.getoption("--collect-only"):
        raise pytest.UsageError("--env 必填（例如 --env=prod）")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """記錄每個 phase 的結果，讓 fixture 透過 request.node.rep_call 判斷是否失敗（失敗截圖用）。"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(scope="session")
def settings(pytestconfig):
    """依 --env 載入設定，整個 session 只初始化一次。"""
    yield load_settings(pytestconfig.getoption("--env"))
