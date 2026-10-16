from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, TypeVar

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from selenium_object.base_page import BasePage

P = TypeVar("P", bound=BasePage)


@dataclass
class DriverConfig:
    headless: bool = True
    base_url: str = ""
    browser: str = "chrome"  # chrome | firefox | edge
    window_width: int = 1280
    window_height: int = 900
    locale: str = "zh-TW"
    # 找元素的隱性等待一律關掉（0），全部靠 BasePage 的顯性等待，避免兩種等待疊加
    page_load_timeout_s: int = 60
    # 全站預設顯性等待上限（秒）：BasePage 所有 wait_* 未指定 timeout 時吃這個值
    default_timeout_s: int = 30


class DriverManager:
    """
    Selenium WebDriver 的生命週期包裝。
    - start / stop
    - .driver
    - open(PageObjectClass) 產生 Page Object
    driver 由 Selenium Manager 自動下載對應版本，不需手動裝 chromedriver。
    """

    def __init__(self, config: Optional[DriverConfig] = None):
        self.config = config or DriverConfig()
        self._driver: Optional[WebDriver] = None

    def start(self) -> WebDriver:
        c = self.config
        builders = {"chrome": self._chrome, "edge": self._edge, "firefox": self._firefox}
        if c.browser not in builders:
            raise ValueError(f"Unsupported browser: {c.browser}")
        self._driver = builders[c.browser]()

        self._driver.implicitly_wait(0)
        self._driver.set_page_load_timeout(c.page_load_timeout_s)
        return self._driver

    def _chrome(self) -> WebDriver:
        c = self.config
        opts = webdriver.ChromeOptions()
        if c.headless:
            opts.add_argument("--headless=new")
        opts.add_argument(f"--window-size={c.window_width},{c.window_height}")
        opts.add_argument(f"--lang={c.locale}")
        return webdriver.Chrome(options=opts)

    def _edge(self) -> WebDriver:
        c = self.config
        opts = webdriver.EdgeOptions()
        if c.headless:
            opts.add_argument("--headless=new")
        opts.add_argument(f"--window-size={c.window_width},{c.window_height}")
        opts.add_argument(f"--lang={c.locale}")
        return webdriver.Edge(options=opts)

    def _firefox(self) -> WebDriver:
        c = self.config
        opts = webdriver.FirefoxOptions()
        if c.headless:
            opts.add_argument("-headless")
        opts.set_preference("intl.accept_languages", c.locale)
        driver = webdriver.Firefox(options=opts)
        driver.set_window_size(c.window_width, c.window_height)
        return driver

    def stop(self) -> None:
        if self._driver:
            self._driver.quit()
            self._driver = None

    def reset(self) -> None:
        """清 cookies / storage，讓下一個 TC 從乾淨狀態開始（不重開瀏覽器，省時間）。"""
        if not self._driver:
            return
        self._driver.delete_all_cookies()
        try:
            self._driver.execute_script("localStorage.clear(); sessionStorage.clear();")
        except Exception:
            pass

    @property
    def driver(self) -> WebDriver:
        if not self._driver:
            raise RuntimeError("DriverManager not started. Call start() first.")
        return self._driver

    def open(self, page_cls: type[P], **kwargs) -> P:
        """把目前的 driver 包成 Page Object。"""
        return page_cls(
            self.driver,
            base_url=self.config.base_url,
            timeout_s=self.config.default_timeout_s,
            **kwargs,
        )
