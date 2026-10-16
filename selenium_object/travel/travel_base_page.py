from __future__ import annotations

from selenium_object.base_page import BasePage
from selenium_object.locators.travel.travel_locator import TravelCommonLocators


class TravelBasePage(BasePage):
    """旅遊險（Blazor）共用：loading 遮罩、SweetAlert 對話框。"""

    def wait_loaded(self):
        self.wait_overlay_gone(TravelCommonLocators.LOADING_OVERLAY_CSS)
        return self

    def swal_text(self) -> str:
        self.wait_visible(TravelCommonLocators.SWAL_POPUP)
        return self.text_of(TravelCommonLocators.SWAL_CONTENT)

    def swal_confirm(self):
        self.click(TravelCommonLocators.SWAL_CONFIRM)
        self.wait_invisible(TravelCommonLocators.SWAL_POPUP)
        return self
