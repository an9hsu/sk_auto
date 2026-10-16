from __future__ import annotations

import re
from dataclasses import dataclass

from selenium_object.locators.travel.travel_locator import TravelProductLocators as L
from selenium_object.travel.member_login_modal import TravelMemberLoginModal
from selenium_object.travel.travel_base_page import TravelBasePage


@dataclass(frozen=True)
class Plan:
    name: str
    price: int  # 每人保費（元）
    selected: bool


class TravelProductPage(TravelBasePage):
    """STEP 1 保費試算：方案、要保人(付款人)資訊、聲明事項"""

    PATH = "/product"

    def wait_ready_for_input(self) -> TravelProductPage:
        """要保人欄位出現 + loading 遮罩連續消失，才開始填（遮罩消失前欄位不可操作）。"""
        self.wait_url_contains("/travel/product")
        self.wait_present(L.PROPOSER_ID)
        self.wait_loaded()
        return self

    def has_selected_plan(self) -> bool:
        return any(e.is_displayed() for e in self.driver.find_elements(*L.PLAN_SELECTED))

    def plans(self) -> list[Plan]:
        """方案比較表的每個方案：名稱、每人保費、是否為目前選取的方案。"""
        return [
            Plan(
                name=e.find_element(*L.PLAN_NAME).text.strip(),
                price=int(re.sub(r"\D", "", e.find_element(*L.PLAN_PRICE).text)),
                selected="active" in (e.get_attribute("class") or "").split(),
            )
            for e in self.driver.find_elements(*L.PLAN_HEADERS)
        ]

    def selected_plan(self) -> Plan:
        selected = [p for p in self.plans() if p.selected]
        assert len(selected) == 1, f"應該剛好選取 1 個方案，實際：{selected}"
        return selected[0]

    def select_plan(self, name: str) -> TravelProductPage:
        self.click(L.plan_header(name))
        # 切換瞬間會短暫沒有任何方案是 active，所以只等「選到的剛好是它」，不用 selected_plan() 的斷言
        self.wait_until(
            lambda _d: [p.name for p in self.plans() if p.selected] == [name],
            f"沒有切換到「{name}」",
        )
        self.wait_loaded()
        return self

    def is_terms_unlocked(self) -> bool:
        """聲明事項勾選框：內容捲到底之前是 disabled。"""
        return self.find(L.TERMS_CHECKBOX).is_enabled()

    def validation_messages(self) -> list[str]:
        return [e.text.strip() for e in self.driver.find_elements(*L.VALIDATION_MESSAGE) if e.is_displayed()]

    def is_natural_person(self) -> bool:
        return self.find(L.IDENTITY_NATIVE_RADIO).is_selected()

    def fill_proposer(self, id_no: str, birthday: str) -> TravelProductPage:
        """填身分證字號與出生日期（西元 YYYY/MM/DD；生日欄預設就是「西元」）。"""
        self.fill(L.PROPOSER_ID, id_no)
        self.fill(L.BIRTHDAY_INPUT, birthday)
        return self

    def agree_terms(self) -> TravelProductPage:
        """聲明事項要先把內容捲到底才會解鎖勾選框，接著勾「3 日內回傳要保書」。"""
        self.scroll_element_to_bottom(L.TERMS_SCROLL_BOX)
        self.wait_until(lambda d: d.find_element(*L.TERMS_CHECKBOX).is_enabled(), "聲明事項勾選框未解鎖")
        self.click(L.TERMS_AGREE)
        self.wait_until(lambda d: d.find_element(*L.TERMS_CHECKBOX).is_selected(), "聲明事項未勾選")
        self.click(L.RETURN_FORM_AGREE)
        return self

    def submit_expect_invalid(self) -> list[str]:
        """按「下一步」但預期被擋下：等驗證訊息出現並回傳（停在本頁）。"""
        self.click(L.NEXT_BTN)
        self.wait_until(lambda _d: self.validation_messages(), "按下一步後沒有出現驗證訊息")
        return self.validation_messages()

    def submit(self) -> TravelMemberLoginModal:
        """按「下一步」→ 跳出「選擇投保身分」modal。"""
        self.click(L.NEXT_BTN)
        return TravelMemberLoginModal(self.driver, base_url=self.base_url, timeout_s=self.timeout_s)
