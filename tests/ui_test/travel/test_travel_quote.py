"""
旅遊險 首頁試算 / 保費試算頁 E2E（正式機）

⚠️ 正式機：這裡的 TC 最多只到「保費試算頁」，不會進到會員登入，更不會進到繳費。
"""

from dataclasses import replace
from datetime import date, timedelta

import allure
import pytest

from selenium_object.travel.home_page import TravelHomePage
from selenium_object.travel.product_page import TravelProductPage
from utils.date_utils import to_roc, trip_period

START_AFTER_DAYS = 3  # 多人投保：保險開始時間須選擇 3 天後
MIN_TRIP_DAYS = 3  # 站台規定保險期間至少 3 日
DESTINATION = "香港"


def go_to_product(home: TravelHomePage, trip_days: int = 4) -> TravelProductPage:
    """多人 → 香港 → 3 天後出發 → 確認期間 → 保費試算頁。"""
    start, end = trip_period(START_AFTER_DAYS, trip_days)
    home.choose_multi_people()
    home.choose_destination(DESTINATION)
    home.choose_period(start, end)
    home.submit()
    return home.confirm_period_and_go()


@pytest.mark.travel
@allure.feature("旅遊險")
@allure.story("首頁試算")
class TestTravelHomeQuote:
    def test_every_quick_destination_selectable(self, travel_home: TravelHomePage):
        """A1：每個「熱門地點」都點得到，且會帶進旅遊地點欄位。"""
        names = travel_home.quick_destinations()
        assert names, "首頁沒有任何熱門地點"
        for name in names:
            with allure.step(f"選擇熱門地點：{name}"):
                travel_home.choose_destination(name)

    def test_multi_people_earliest_start_is_3_days_later(self, travel_home: TravelHomePage):
        """A2：多人投保的月曆，最早只能選 3 天後（3 天內的日期是 disabled）。"""
        travel_home.choose_multi_people()
        travel_home.open_period_picker()
        selectable = travel_home.selectable_dates_in_view()
        assert selectable, "月曆上沒有任何可選的日期"
        assert selectable[0] == date.today() + timedelta(days=START_AFTER_DAYS), selectable[:5]

    @pytest.mark.parametrize("trip_days", [MIN_TRIP_DAYS, 30], ids=["最短3天", "30天跨月"])
    def test_trip_days_shown_in_confirm(self, travel_home: TravelHomePage, trip_days: int):
        """A4：不同旅遊天數，確認框顯示的地點、起訖日、天數正確；保費試算頁有保費。"""
        start, end = trip_period(START_AFTER_DAYS, trip_days)
        travel_home.choose_multi_people()
        travel_home.choose_destination(DESTINATION)
        travel_home.choose_period(start, end)

        confirm_text = travel_home.submit().swal_text()
        assert f"旅遊地點：{DESTINATION}" in confirm_text, confirm_text
        assert to_roc(start) in confirm_text and to_roc(end) in confirm_text, confirm_text
        assert f"共 {trip_days}天" in confirm_text, confirm_text

        product = travel_home.confirm_period_and_go()
        assert product.selected_plan().price > 0

    def test_trip_shorter_than_min_days_blocked(self, travel_home: TravelHomePage):
        """A4：保險期間少於 3 天 → 跳出「保險期間至少 3日」，停在首頁。"""
        start, end = trip_period(START_AFTER_DAYS, MIN_TRIP_DAYS - 1)
        travel_home.choose_multi_people()
        travel_home.choose_destination(DESTINATION)
        travel_home.choose_period(start, end)

        assert "保險期間至少 3日" in travel_home.submit().swal_text()
        travel_home.swal_confirm()
        travel_home.assert_url_contains("/travel/home")

    def test_submit_empty_form_blocked(self, travel_home: TravelHomePage):
        """A6：什麼都沒填就按「下一步」→ 跳出「保險期間至少 3日」，停在首頁。

        註：只選地點、沒選期間就按「下一步」時，站台目前沒有任何提示也不換頁，所以不寫成 TC。
        """
        assert "保險期間至少 3日" in travel_home.submit().swal_text()
        travel_home.swal_confirm()
        travel_home.assert_url_contains("/travel/home")

    def test_period_picker_confirm_without_dates_alerts(self, travel_home: TravelHomePage):
        """A6：月曆沒選日期就按「確定」→ 提醒「請選擇出發與結束日期」。"""
        travel_home.open_period_picker()
        assert travel_home.confirm_period_expect_alert() == "請選擇出發與結束日期"


@pytest.mark.travel
@allure.feature("旅遊險")
@allure.story("保費試算頁")
class TestTravelProductPage:
    def test_switch_plan(self, travel_home: TravelHomePage):
        """B1：每個方案都有保費；切換到另一個方案後，選取狀態跟著換。"""
        product = go_to_product(travel_home)
        plans = product.plans()
        assert len(plans) >= 2, f"方案少於 2 個：{plans}"
        assert all(p.price > 0 for p in plans), plans
        assert len({p.price for p in plans}) == len(plans), f"不同方案的保費應該不同：{plans}"

        other = next(p for p in plans if not p.selected)
        with allure.step(f"切換到「{other.name}」"):
            product.select_plan(other.name)
        assert product.selected_plan() == replace(other, selected=True)

    def test_terms_required_before_next(self, travel_home: TravelHomePage, travel_account):
        """B3：聲明事項沒捲到底前不能勾；沒同意就按「下一步」會被擋下，停在本頁。"""
        product = go_to_product(travel_home)
        assert not product.is_terms_unlocked(), "聲明事項還沒捲到底，勾選框就已經可以勾"

        product.fill_proposer(travel_account.PROPOSER_ID, travel_account.PROPOSER_BIRTHDAY)
        messages = product.submit_expect_invalid()
        assert "聲明事項必須閱讀" in messages, messages
        assert any("3日內回傳要保書" in m for m in messages), messages
        product.assert_url_contains("/travel/product")
