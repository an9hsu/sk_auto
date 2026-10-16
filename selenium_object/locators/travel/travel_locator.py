from selenium.webdriver.common.by import By

# 站台是 Blazor：沒有 data-testid，class 有 scoped hash（b-xxxx 屬性），
# 這裡只用語意 class / id / name / 文字，不用 b-xxxx 屬性（每次部署都會變）。


class TravelCommonLocators:
    LOADING_OVERLAY_CSS = ".loading-overlay"  # 「資料處理中，請勿關閉頁面...」
    SWAL_POPUP = (By.CSS_SELECTOR, ".swal2-popup")
    SWAL_TITLE = (By.CSS_SELECTOR, ".swal2-popup .swal2-title")
    SWAL_CONTENT = (By.CSS_SELECTOR, ".swal2-popup .swal2-html-container")
    SWAL_CONFIRM = (By.CSS_SELECTOR, ".swal2-popup button.swal2-confirm")


class TravelHomeLocators:
    """首頁：海外旅遊保險試算表單"""

    PEOPLE_ONE = (By.CSS_SELECTOR, "label[for='declarePeopleGroup1']")
    PEOPLE_MORE = (By.CSS_SELECTOR, "label[for='declarePeopleGroup2']")
    PEOPLE_MORE_RADIO = (By.ID, "declarePeopleGroup2")
    ASSURE_TARGET_SELECT = (By.CSS_SELECTOR, "#insPeopleSection select")

    @staticmethod
    def assure_target_option(value: str):
        return (By.CSS_SELECTOR, f"#insPeopleSection select option[value='{value}']")

    DESTINATION_INPUT = (By.CSS_SELECTOR, ".location-selector__input")
    QUICK_PILLS = (By.CSS_SELECTOR, ".location-selector__quick-pill")

    @staticmethod
    def quick_pill(name: str):
        return (
            By.XPATH,
            f"//div[contains(@class,'location-selector__quick-pill') and normalize-space()='{name}']",
        )

    # 日期欄位的 <input readonly> 本身點不到（被外層 container 吃掉點擊），要點 container
    PERIOD_TRIGGER = (By.CSS_SELECTOR, ".input-container")
    PERIOD_INPUT = (By.CSS_SELECTOR, ".input-container input[readonly]")

    DATEPICKER = (By.CSS_SELECTOR, ".datepicker")
    DATEPICKER_LEFT_MONTH = (By.CSS_SELECTOR, ".datepicker .calendar-header .month")
    DATEPICKER_RIGHT_MONTH = (By.CSS_SELECTOR, ".datepicker .NextMonthDisplay .month_Next")
    DATEPICKER_NEXT_BTN = (By.CSS_SELECTOR, ".datepicker .NextMonthDisplay button")
    DATEPICKER_CONFIRM = (By.CSS_SELECTOR, ".datepicker button.confirm")

    @staticmethod
    def datepicker_enabled_days(panel_index: int):
        """panel_index 那個月份所有可點的日子。"""
        return (
            By.XPATH,
            f"(//div[@class='datepicker']//div[contains(@class,'calendarTitle')])[{panel_index}]"
            "/div[contains(@class,'day') and not(contains(@class,'disabled')) and not(contains(@class,'weekday'))]",
        )

    @staticmethod
    def datepicker_day(panel_index: int, day: int):
        """panel_index：1 = 左邊（當月）、2 = 右邊（下個月）。只挑可點的日子（排除 disabled）。"""
        return (
            By.XPATH,
            f"(//div[@class='datepicker']//div[contains(@class,'calendarTitle')])[{panel_index}]"
            f"/div[contains(@class,'day') and not(contains(@class,'disabled')) and normalize-space()='{day}']",
        )

    NEXT_BTN = (By.CSS_SELECTOR, "button.sys-button__next")


class TravelProductLocators:
    """/travel/product：保費試算 + 要保人資訊 + 聲明事項"""

    PLAN_SELECTED = (By.CSS_SELECTOR, ".plan-selector.active")
    # 方案比較表最上面那排標頭（另有 sticky / 手機版的同名 class，這裡只取桌機標頭）
    PLAN_HEADERS = (By.CSS_SELECTOR, ".grid-cell.plan-header.plan-selector")
    PLAN_NAME = (By.CSS_SELECTOR, ".plan-name")
    PLAN_PRICE = (By.CSS_SELECTOR, ".plan-price")

    @staticmethod
    def plan_header(name: str):
        return (
            By.XPATH,
            "//div[contains(@class,'plan-header') and contains(@class,'plan-selector')]"
            f"[.//div[contains(@class,'plan-name') and normalize-space()='{name}']]",
        )

    IDENTITY_NATIVE_RADIO = (By.ID, "declareIdentityGroup1")
    PROPOSER_ID = (By.NAME, "_VM.Proposer.ID")
    BIRTHDAY_INPUT = (By.CSS_SELECTOR, ".datepicker-wrapper input.date-input")

    TERMS_SCROLL_BOX = (By.ID, "scroll1")
    TERMS_CHECKBOX = (By.ID, "scroll1_termCheck")
    TERMS_AGREE = (By.ID, "scroll1_btnName")  # 「我已閱讀並同意以上聲明事項」
    RETURN_FORM_AGREE = (By.CSS_SELECTOR, ".terms__tabsbtn")  # 「我同意 3 日內回傳要保書」
    VALIDATION_MESSAGE = (By.CSS_SELECTOR, ".validation-message")

    NEXT_BTN = (By.CSS_SELECTOR, "button.sys-button__next")


class TravelLoginModalLocators:
    """點「下一步」後跳出的「選擇投保身分」→ 會員登入 modal"""

    IDENTITY_TITLE = (By.CSS_SELECTOR, ".identity-title")
    IDENTITY_CONFIRM = (By.CSS_SELECTOR, ".modal-overlay a.sys-button__next")

    TAB_MEMBER = (By.XPATH, "//label[contains(@class,'modal-tabs__button')][.//input[@value='會員帳號登入']]")
    TAB_MEMBER_RADIO = (By.CSS_SELECTOR, "input[name='brandTab'][value='會員帳號登入']")
    TAB_OTP = (By.XPATH, "//label[contains(@class,'modal-tabs__button')][.//input[@value='手機驗證登入']]")

    MEMBER_ID = (By.NAME, "_vD.memberId")
    MEMBER_PWD = (By.NAME, "_vD.memberPwd")
    CAPTCHA_INPUT = (By.NAME, "_vD.memberCode")
    CAPTCHA_IMAGE = (By.CSS_SELECTOR, "img.captcha-image")
    CAPTCHA_REFRESH = (By.CSS_SELECTOR, ".captcha-container .refresh-icon")
    MEMBER_LOGIN_BTN = (By.XPATH, "//a[contains(@class,'sys-button__next')][normalize-space()='會員登入']")

    MODAL = (By.CSS_SELECTOR, ".modal-overlay")
