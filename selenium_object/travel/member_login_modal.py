from __future__ import annotations

import time

from selenium.common.exceptions import TimeoutException

from selenium_object.locators.travel.travel_locator import TravelCommonLocators
from selenium_object.locators.travel.travel_locator import TravelLoginModalLocators as L
from selenium_object.travel.travel_base_page import TravelBasePage


class TravelMemberLoginModal(TravelBasePage):
    """「選擇投保身分」→「會員帳號登入」（帳號 + 密碼 + 圖形驗證碼）。不走手機 OTP。"""

    # 驗證碼最短長度：輸入值穩定且達到這個長度才視為人工輸入完成
    CAPTCHA_MIN_LEN = 4
    # 【等滿】人工輸入驗證碼後，值要維持不變這麼久才當作打完（避免打到一半就送出）
    CAPTCHA_STABLE_S = 2.0

    def confirm_identity(self) -> TravelMemberLoginModal:
        """「選擇投保身分」只有「會員登入/註冊」一個選項，直接按確認。"""
        self.wait_visible(L.IDENTITY_TITLE)
        self.click(L.IDENTITY_CONFIRM)
        self.wait_visible(L.TAB_MEMBER)
        return self

    def switch_to_member_tab(self) -> TravelMemberLoginModal:
        """預設是「手機驗證登入」（OTP），切到「會員帳號登入」。"""
        self.click(L.TAB_MEMBER)
        self.wait_until(lambda d: d.find_element(*L.TAB_MEMBER_RADIO).is_selected(), "沒有切到會員帳號登入")
        self.wait_visible(L.MEMBER_PWD)
        self.wait_visible(L.CAPTCHA_IMAGE)
        return self

    def member_account(self) -> str:
        """帳號欄位是 disabled，由前一步的身分證自動帶入。"""
        return self.value_of(L.MEMBER_ID)

    def fill_password(self, password: str) -> TravelMemberLoginModal:
        self.fill(L.MEMBER_PWD, password)
        return self

    def fill_captcha(self, code: str) -> TravelMemberLoginModal:
        self.fill(L.CAPTCHA_INPUT, code)
        return self

    def wait_manual_captcha(self, timeout_s: float = 180) -> str:
        """停住等人在瀏覽器上輸入驗證碼（需 --headed）。

        值長度 >= CAPTCHA_MIN_LEN 且連續 CAPTCHA_STABLE_S 秒沒變，就當作輸入完成並回傳。
        """
        captcha = self.scroll_into_view(self.wait_visible(L.CAPTCHA_INPUT))
        self.driver.execute_script("arguments[0].style.outline='3px solid #ff5151'; arguments[0].focus();", captcha)
        self.logger.warning("⌨️  請在瀏覽器輸入圖形驗證碼（最多等 %s 秒）…", int(timeout_s))

        deadline = time.monotonic() + timeout_s
        last, since = "", time.monotonic()
        while time.monotonic() < deadline:
            value = (self.find(L.CAPTCHA_INPUT).get_attribute("value") or "").strip()
            if value != last:
                last, since = value, time.monotonic()
            elif len(value) >= self.CAPTCHA_MIN_LEN and time.monotonic() - since >= self.CAPTCHA_STABLE_S:
                return value
            time.sleep(self.POLL_INTERVAL_S)
        raise TimeoutException(f"{int(timeout_s)} 秒內沒有輸入驗證碼")

    def submit(self) -> TravelMemberLoginModal:
        self.click(L.MEMBER_LOGIN_BTN)
        return self

    def assert_login_success(self, timeout_s: float = 30) -> TravelMemberLoginModal:
        """登入成功 = 登入 modal 關閉，且沒有跳出錯誤對話框。

        錯誤（密碼/驗證碼錯）會以 SweetAlert 呈現，帶出內容方便判讀。
        """
        try:
            self.wait_invisible(L.MEMBER_PWD, timeout_s)
        except TimeoutException:
            popups = [e for e in self.driver.find_elements(*L.MODAL) if e.is_displayed()]
            detail = self.swal_text() if self._swal_visible() else (popups[0].text if popups else "")
            raise AssertionError(f"會員登入失敗，畫面訊息：{detail!r}")
        assert not self._swal_visible(), f"登入後跳出對話框：{self.swal_text()!r}"
        self.wait_loaded()
        return self

    def _swal_visible(self) -> bool:
        return any(e.is_displayed() for e in self.driver.find_elements(*TravelCommonLocators.SWAL_POPUP))
