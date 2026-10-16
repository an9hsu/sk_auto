from __future__ import annotations

import random
import time
from datetime import date

from selenium.webdriver.support import expected_conditions as EC

from selenium_object.locators.travel.travel_locator import TravelHomeLocators as L
from selenium_object.travel.product_page import TravelProductPage
from selenium_object.travel.travel_base_page import TravelBasePage


class TravelHomePage(TravelBasePage):
    """海外旅遊保險試算（首頁下方表單）"""

    PATH = "/home"
    # 多人投保只有這一個保障對象選項（value=3）
    ASSURE_TARGET_FAMILY = "3"
    # 月曆最多往後翻幾個月找目標日期，避免日期算錯時無限翻頁
    MAX_MONTH_FLIPS = 12

    def load(self) -> TravelHomePage:
        """導頁並等 Blazor 接管完成。

        Blazor 先送一份 server prerender 的 HTML，連上 SignalR 後整頁重畫一次；
        在重畫前點到的元素會 stale，所以要等「投保人數」radio 可點、且 loading 遮罩消失。
        """
        self.goto()
        self.wait_ready()
        self.wait_visible(L.PEOPLE_MORE)
        self.wait_loaded()
        return self

    # ── 旅遊人數 ────────────────────────────────────────────────

    def choose_multi_people(self) -> TravelHomePage:
        """投保人數選「多人」，保障對象選「幫家人、自己與家人、員工及其家人投保」。"""
        self.click(L.PEOPLE_MORE)
        self.wait_until(lambda d: d.find_element(*L.PEOPLE_MORE_RADIO).is_selected(), "「多人」沒有被選取")
        # 選項會在 Blazor 重畫後才從「1 人」的版本換成「多人」的版本，選項出現前選不到
        self.wait_until(
            lambda d: d.find_elements(*L.assure_target_option(self.ASSURE_TARGET_FAMILY)),
            "保障對象沒有出現「多人」的選項",
        )
        self.select_by_value(L.ASSURE_TARGET_SELECT, self.ASSURE_TARGET_FAMILY)
        return self

    # ── 旅遊地點 ────────────────────────────────────────────────

    def quick_destinations(self) -> list[str]:
        return [e.text.strip() for e in self.driver.find_elements(*L.QUICK_PILLS) if e.text.strip()]

    def choose_destination(self, name: str) -> TravelHomePage:
        self.click(L.quick_pill(name))
        self.assert_text_contains(L.DESTINATION_INPUT, name)
        return self

    def choose_random_destination(self) -> str:
        """從「熱門地點」隨機挑一個，回傳選到的名稱。"""
        name = random.choice(self.quick_destinations())
        self.choose_destination(name)
        return name

    # ── 旅遊期間 ────────────────────────────────────────────────

    def choose_period(self, start: date, end: date) -> TravelHomePage:
        """打開月曆，依序點開始日、結束日，再按「確定」。"""
        self.click(L.PERIOD_TRIGGER)
        self.wait_visible(L.DATEPICKER)
        self._click_day(start)
        self._click_day(end)
        self.click(L.DATEPICKER_CONFIRM)
        self.wait_invisible(L.DATEPICKER)
        return self

    def open_period_picker(self) -> TravelHomePage:
        self.click(L.PERIOD_TRIGGER)
        self.wait_visible(L.DATEPICKER)
        return self

    def selectable_dates_in_view(self) -> list[date]:
        """月曆目前畫面（左右兩個月）上可以點的日期，由早到晚。"""
        result = []
        for panel, month_locator in ((1, L.DATEPICKER_LEFT_MONTH), (2, L.DATEPICKER_RIGHT_MONTH)):
            year, month = (int(x) for x in self.text_of(month_locator).split("/"))
            days = [e.text.strip() for e in self.driver.find_elements(*L.datepicker_enabled_days(panel))]
            result += [date(year, month, int(d)) for d in days if d.isdigit()]
        return sorted(result)

    def confirm_period_expect_alert(self) -> str:
        """月曆沒選日期就按「確定」→ 跳出瀏覽器原生 alert；回傳文字並關掉它。"""
        self.click(L.DATEPICKER_CONFIRM)
        alert = self.wait_until(EC.alert_is_present(), "沒有跳出提醒視窗")
        text = alert.text
        alert.accept()
        return text

    def _click_day(self, d: date) -> None:
        """月曆一次顯示兩個月（左：當月、右：下月）；目標月份不在畫面上就按 → 翻頁。"""
        target = f"{d.year} / {d.month:02d}"
        for _ in range(self.MAX_MONTH_FLIPS):
            if self.text_of(L.DATEPICKER_LEFT_MONTH) == target:
                self.click(L.datepicker_day(1, d.day))
                return
            if self.text_of(L.DATEPICKER_RIGHT_MONTH) == target:
                self.click(L.datepicker_day(2, d.day))
                return
            left_before = self.text_of(L.DATEPICKER_LEFT_MONTH)
            self.click(L.DATEPICKER_NEXT_BTN)
            self.wait_until(
                lambda _d: self.find(L.DATEPICKER_LEFT_MONTH).text.strip() != left_before,
                "月曆翻頁沒有反應",
            )
        raise AssertionError(f"月曆翻了 {self.MAX_MONTH_FLIPS} 個月仍找不到 {target}")

    def period_value(self) -> str:
        return self.value_of(L.PERIOD_INPUT)

    # ── 送出 ────────────────────────────────────────────────────

    def submit(self) -> TravelHomePage:
        """按「下一步」→ 跳出「請確認旅遊保險期間」確認框（不自動按確認，讓 TC 先驗內容）。"""
        self.click(L.NEXT_BTN)
        self.swal_text()  # 等確認框出現
        return self

    def confirm_period_and_go(self) -> TravelProductPage:
        """在確認框按「確認」，等導到 /travel/product 且欄位可輸入。"""
        self.swal_confirm()
        self.wait_url_contains("/travel/product")
        # 換頁後 loading 會閃一下，給 Blazor 一點時間掛上遮罩，避免 wait_loaded 太早判定完成
        time.sleep(self.RETRY_INTERVAL_S)
        return TravelProductPage(self.driver, base_url=self.base_url, timeout_s=self.timeout_s).wait_ready_for_input()
