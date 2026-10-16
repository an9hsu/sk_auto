"""
旅遊險 網路投保 E2E（正式機）
URL: https://www.sk858.com.tw/skechas/has/travel/home

⚠️ 正式機：流程只跑到「會員登入」為止，絕對不能進到線上繳費。
"""

import allure
import pytest

from selenium_object.travel.home_page import TravelHomePage
from selenium_object.travel.member_login_modal import TravelMemberLoginModal
from utils.date_utils import to_roc, trip_period

DESTINATION = "日本-沖繩"
START_AFTER_DAYS = 3  # 多人投保：保險開始時間須選擇 3 天後
TRIP_DAYS = 4


@pytest.mark.travel
@allure.feature("旅遊險")
@allure.story("網路投保-多人")
class TestTravelOnlineInsureMultiPeople:
    """TC: 多人投保 → 試算 → 要保人資料 → 會員帳號登入頁（不送出登入）"""

    def _go_to_member_login(self, home: TravelHomePage, account) -> TravelMemberLoginModal:
        """首頁試算 → 確認期間 → 填要保人 → 同意聲明 → 選投保身分 → 切到「會員帳號登入」。"""
        start, end = trip_period(START_AFTER_DAYS, TRIP_DAYS)

        with allure.step(f"試算：多人 / {DESTINATION} / {start} ~ {end}"):
            home.choose_multi_people()
            home.choose_destination(DESTINATION)
            home.choose_period(start, end)
            assert home.period_value() == f"{start:%Y-%m-%d} ~ {end:%Y-%m-%d}"

        with allure.step("確認旅遊保險期間"):
            confirm_text = home.submit().swal_text()
            assert f"旅遊地點：{DESTINATION}" in confirm_text, confirm_text
            assert to_roc(start) in confirm_text and to_roc(end) in confirm_text, confirm_text
            assert f"共 {TRIP_DAYS}天" in confirm_text, confirm_text
            product = home.confirm_period_and_go()

        with allure.step("填寫要保人資料並同意聲明事項"):
            assert product.has_selected_plan(), "保費試算頁沒有預選方案"
            assert product.is_natural_person(), "要保人對象預設應為「自然人」"
            product.fill_proposer(account.PROPOSER_ID, account.PROPOSER_BIRTHDAY)
            product.agree_terms()
            login = product.submit()

        with allure.step("選擇投保身分 → 會員帳號登入"):
            login.confirm_identity().switch_to_member_tab()
            assert login.member_account() == account.MEMBER_ACCOUNT, "會員帳號未自動帶入身分證字號"
        return login

    def test_multi_people_reach_member_login(self, travel_home: TravelHomePage, travel_account):
        """TC-1：多人投保試算一路走到「會員帳號登入」，帳號自動帶入（可 headless 跑，不送出登入）。"""
        self._go_to_member_login(travel_home, travel_account)
