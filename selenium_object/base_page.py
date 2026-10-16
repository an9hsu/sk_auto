from __future__ import annotations

import logging
import time
from typing import Callable, Optional, Tuple

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

Locator = Tuple[str, str]

# 會被重試的「暫時性」錯誤：Blazor 重繪造成元素失效、loading 遮罩擋住點擊、元素還沒可操作
_RETRYABLE = (
    StaleElementReferenceException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
)


class BasePage:
    """
    Base POM（Selenium 版）:
    - holds WebDriver
    - goto()：依 PATH 導頁
    - 顯性等待 / 點擊 / 輸入 / 斷言 helpers（內建 stale 重試）
    """

    PATH: str = "/"

    # ── 共用等待時間（秒）；統一管理，改一處全站生效 ──────────────
    """
    兩種等待，性質不同：
    -【上限】  等某件事發生，事情好了就馬上往下走，最多等到這個秒數才放棄
    -【等滿】  畫面看不出事情做完沒，只能傻傻睡滿這個秒數再往下走（越少越好）
    """
    LOADING_STABLE_S = 1.0  # 【等滿】loading 遮罩要「連續消失」這麼久才算真的載完（它會閃爍）
    RETRY_INTERVAL_S = 0.3  # 【等滿】重試前喘口氣的間隔
    POLL_INTERVAL_S = 0.2  # 【等滿】輪詢間隔

    def __init__(self, driver: WebDriver, *, base_url: str, timeout_s: int = 30):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self.logger = logging.getLogger(self.__class__.__name__)

    # ── 導頁 / 等待 ─────────────────────────────────────────────

    def goto(self, *, path: Optional[str] = None):
        """導向頁面。不給 path 就用該 class 的 PATH；給了就導向指定路徑。"""
        p = path or self.PATH
        url = p if p.startswith("http") else f"{self.base_url}/{p.lstrip('/')}"
        self.driver.get(url)
        return self

    def wait(self, timeout_s: Optional[float] = None) -> WebDriverWait:
        return WebDriverWait(
            self.driver,
            timeout_s or self.timeout_s,
            poll_frequency=self.POLL_INTERVAL_S,
            ignored_exceptions=[StaleElementReferenceException],
        )

    def wait_until(self, cond: Callable, message: str = "", timeout_s: Optional[float] = None):
        return self.wait(timeout_s).until(cond, message)

    def wait_ready(self):
        """等 document.readyState == complete（只代表 HTML 載完，SPA 內容可能還在畫）。"""
        self.wait_until(
            lambda d: d.execute_script("return document.readyState") == "complete",
            "document.readyState 未到 complete",
        )
        return self

    def wait_url_contains(self, fragment: str, timeout_s: Optional[float] = None):
        self.wait_until(EC.url_contains(fragment), f"URL 未包含 {fragment!r}", timeout_s)
        return self

    def wait_visible(self, locator: Locator, timeout_s: Optional[float] = None) -> WebElement:
        return self.wait_until(EC.visibility_of_element_located(locator), f"元素未出現：{locator}", timeout_s)

    def wait_invisible(self, locator: Locator, timeout_s: Optional[float] = None):
        self.wait_until(EC.invisibility_of_element_located(locator), f"元素未消失：{locator}", timeout_s)
        return self

    def wait_present(self, locator: Locator, timeout_s: Optional[float] = None) -> WebElement:
        return self.wait_until(EC.presence_of_element_located(locator), f"元素不在 DOM：{locator}", timeout_s)

    def wait_overlay_gone(
        self,
        overlay_css: str,
        *,
        stable_s: float = LOADING_STABLE_S,
        timeout_s: Optional[float] = None,
    ):
        """等 loading 遮罩「連續 stable_s 秒都不可見」。

        遮罩在換頁 / 打 API 時會閃好幾次（消失 0.5 秒又出現），
        只等一次 invisibility 會太早往下走，所以要求連續消失一段時間才算真的載完。
        """
        js = (
            "return [...document.querySelectorAll(arguments[0])]"
            ".some(e => e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden')"
        )
        deadline = time.monotonic() + (timeout_s or self.timeout_s)
        clear_since: Optional[float] = None
        while time.monotonic() < deadline:
            if self.driver.execute_script(js, overlay_css):
                clear_since = None
            else:
                clear_since = clear_since or time.monotonic()
                if time.monotonic() - clear_since >= stable_s:
                    return self
            time.sleep(self.POLL_INTERVAL_S)
        raise TimeoutException(f"loading 遮罩 {overlay_css!r} 一直沒消失")

    # ── 操作 ────────────────────────────────────────────────────

    def find(self, locator: Locator) -> WebElement:
        return self.driver.find_element(*locator)

    def scroll_into_view(self, el: WebElement) -> WebElement:
        # behavior:'instant'：站台有 scroll-behavior:smooth，平滑捲動還沒到位就點會點歪
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center', behavior:'instant'})", el)
        return el

    def _retry(self, action: Callable[[], object], what: str, timeout_s: Optional[float] = None):
        """遇到 stale / 被遮擋 / 不可操作就重新找元素再做一次，直到逾時。"""
        deadline = time.monotonic() + (timeout_s or self.timeout_s)
        last: Optional[Exception] = None
        while time.monotonic() < deadline:
            try:
                return action()
            except _RETRYABLE as e:
                last = e
                time.sleep(self.RETRY_INTERVAL_S)
        raise TimeoutException(f"{what} 逾時：{type(last).__name__ if last else ''} {last}")

    def click(self, locator: Locator, timeout_s: Optional[float] = None):
        """等可見 → 捲到畫面中央 → 點擊；Blazor 重繪造成的 stale 會自動重試。"""

        def _do():
            el = self.wait_visible(locator, timeout_s)
            self.scroll_into_view(el).click()

        self._retry(_do, f"點擊 {locator}", timeout_s)
        return self

    def fill(self, locator: Locator, text: str, *, clear: bool = True, blur: bool = True):
        """逐字輸入（觸發 keyup 等前端事件）。

        - 欄位有值才 clear：對空欄位 clear() 會送出一次空值 change，Blazor 驗證會卡在「格式不正確」
        - blur=True：輸入後移開焦點，觸發 change → 前端驗證以最終值重算
        """

        def _do():
            el = self.scroll_into_view(self.wait_visible(locator))
            if clear and el.get_attribute("value"):
                el.clear()
            el.send_keys(text)
            if blur:
                self.driver.execute_script("arguments[0].blur()", el)

        self._retry(_do, f"輸入 {locator}")
        return self

    def select_by_value(self, locator: Locator, value: str):
        self._retry(
            lambda: Select(self.scroll_into_view(self.wait_visible(locator))).select_by_value(value),
            f"下拉選單 {locator} 選 {value!r}",
        )
        return self

    def selected_text(self, locator: Locator) -> str:
        return Select(self.find(locator)).first_selected_option.text.strip()

    def text_of(self, locator: Locator) -> str:
        return self._retry(lambda: self.wait_visible(locator).text.strip(), f"讀取文字 {locator}")

    def value_of(self, locator: Locator) -> str:
        return self._retry(lambda: self.wait_present(locator).get_attribute("value") or "", f"讀取值 {locator}")

    def scroll_element_to_bottom(self, locator: Locator):
        """把「內部可捲動」的區塊捲到底（例如聲明事項，要捲到底才解鎖勾選框）。"""
        el = self.scroll_into_view(self.wait_visible(locator))
        self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", el)
        return self

    def refresh(self):
        self.driver.refresh()
        return self

    # ── 斷言 ────────────────────────────────────────────────────

    def assert_url_contains(self, fragment: str):
        self.wait_url_contains(fragment)
        return self

    def assert_text_contains(self, locator: Locator, expected: str):
        """等到元素文字包含 expected；不符就以實際文字報錯。"""
        try:
            self.wait_until(lambda d: expected in d.find_element(*locator).text, timeout_s=10)
        except TimeoutException:
            actual = self.find(locator).text
            raise AssertionError(f"{locator} 文字未包含 {expected!r}，實際：{actual!r}")
        return self

    def assert_value_equals(self, locator: Locator, expected: str):
        actual = self.value_of(locator)
        assert actual == expected, f"{locator} 值不符：期望 {expected!r}，實際 {actual!r}"
        return self
