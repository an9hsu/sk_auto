# sk_auto

新光產物各產品的自動化測試框架（pytest + Selenium）。

## 安裝

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.sample .env   # 填入 TRAVEL_MEMBER_PWD
```

需要本機已安裝 Chrome；chromedriver 由 Selenium Manager 自動處理。

## 執行

```bash
pytest --env=prod -m travel            # headless
pytest --env=prod -m travel --headed   # 開視窗（會員登入 TC 需要人工輸入圖形驗證碼）
```

失敗截圖：`test-results/screenshots/`；Allure 結果：`allure-results/`（`allure serve allure-results`）。

## 目錄

```
configs/                 settings.py、env_{env}.yml（URL）、account_{env}.yml（帳號資料）
selenium_object/         base_page.py、driver_manager.py
  locators/<product>/    selector 定義
  <product>/             Page Objects
tests/
  conftest.py            --env / --headed / --browser-name、settings fixture
  ui_test/conftest.py    各產品共用的 driver / 截圖 helper
  ui_test/<product>/     各產品的 conftest + test
utils/                   date_utils 等共用工具
```

## 目前涵蓋

| 產品 | TC | 流程 | 停止點 |
|---|---|---|---|
| 旅遊險 travel | TC-1 `test_multi_people_reach_member_login` | 多人 → 日本-沖繩 → 3 天後出發共 4 天 → 要保人身分證/生日 → 同意聲明 → 會員帳號登入頁（帳號自動帶入） | 登入前 |
| 旅遊險 travel | TC-2 `test_multi_people_member_login`（`--headed`） | 同上 + 密碼 + 人工輸入驗證碼 → 登入成功 | 登入後（繳費前） |
