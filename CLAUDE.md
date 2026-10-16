# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

新光產物各產品／專案的自動化測試框架（架構參考 `~/Documents/Fork/qa_auto`）。目前只有 UI E2E（Selenium）。

## Architecture

- Runtime: Python 3.12, Pytest + Selenium 4（driver 由 Selenium Manager 自動下載）
- Page Object: `selenium_object/<product>/` — 全部繼承 `BasePage`（各產品可再包一層，如 `TravelBasePage`）
- Locators: `selenium_object/locators/<product>/` — `(By, value)` tuple，Page 內不寫死 selector
- Driver: `selenium_object/driver_manager.py` — `DriverManager.open(PageCls)` 產生 Page Object
- Config: frozen dataclasses in `configs/settings.py`；URL 在 `configs/env_{env}.yml`、帳號個資在 `configs/.account_{env}.yml`（gitignore，範本為 `account_{env}.yml.sample`）、密碼只從 env var（`.env`）
- Tests: `tests/ui_test/<product>/`；共用 helper（`session_driver`、`capture_screenshot_on_failure`）在 `tests/ui_test/conftest.py`

## Conventions

- 新產品：`selenium_object/<product>/` + `selenium_object/locators/<product>/` + `tests/ui_test/<product>/conftest.py`（用 `session_driver(request, base_url=...)`）+ `env_*.yml` 的 URL 欄位 + pytest.ini marker
- 不在 tests/fixtures 呼叫 `os.getenv()` — 一律用 `settings` fixture
- 不用 `time.sleep` 硬等；用 `BasePage.wait_*`。真的只能等滿的常數集中放在 class 上，註明【上限】或【等滿】
- 換頁的動作回傳下一頁的 Page Object（例：`TravelHomePage.confirm_period_and_go() -> TravelProductPage`）
- 旅遊險站台是 Blazor：class 上的 `b-xxxx` scoped 屬性每次部署會變，不可當 selector；換頁後要 `wait_loaded()`（`.loading-overlay` 會閃爍，需連續消失才算載完）

## Hard Constraints

- **正式機（prod）不可進到繳費步驟**：任何流程最多停在繳費前（目前旅遊險停在會員登入）
- 個資（身分證、生日、帳號）只能放 `configs/.account_{env}.yml`，不可寫進程式碼、測試或其他會進版控的檔案
- 目前不寫需要人工介入（如圖形驗證碼）的 TC；也不自動破解圖形驗證碼
- `--env` 必填，沒有預設值
- Run from project root（`Path.cwd()` 用來找 yml / .env）

## Commands

```bash
pytest --env=prod -m travel                         # headless
pytest --env=prod -m travel --headed                # 開視窗看操作過程
pytest --env=prod -m travel --browser-name=edge     # 換瀏覽器
npx allure generate allure-results --open           # Allure 3 報表（設定在 allurerc.mjs，產出單一 HTML）
```
