# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

新光產物各產品／專案的自動化測試框架（架構參考 `~/Documents/Fork/qa_auto`）。目前只有 UI E2E（Selenium）。

## Architecture

- Runtime: Python 3.12, Pytest + Selenium 4（driver 由 Selenium Manager 自動下載）
- Page Object: `selenium_object/<product>/` — 全部繼承 `BasePage`（各產品可再包一層，如 `TravelBasePage`）
- Locators: `selenium_object/locators/<product>/` — `(By, value)` tuple，Page 內不寫死 selector
- Driver: `selenium_object/driver_manager.py` — `DriverManager.open(PageCls)` 產生 Page Object
- Config: frozen dataclasses in `configs/settings.py`；URL 在 `configs/env_{env}.yml`、帳號資料在 `configs/account_{env}.yml`、密碼只從 env var（`.env`）
- Tests: `tests/ui_test/<product>/`；共用 helper（`session_driver`、`capture_screenshot_on_failure`）在 `tests/ui_test/conftest.py`

## Conventions

- 新產品：`selenium_object/<product>/` + `selenium_object/locators/<product>/` + `tests/ui_test/<product>/conftest.py`（用 `session_driver(request, base_url=...)`）+ `env_*.yml` 的 URL 欄位 + pytest.ini marker
- 不在 tests/fixtures 呼叫 `os.getenv()` — 一律用 `settings` fixture
- 不用 `time.sleep` 硬等；用 `BasePage.wait_*`。真的只能等滿的常數集中放在 class 上，註明【上限】或【等滿】
- 換頁的動作回傳下一頁的 Page Object（例：`TravelHomePage.confirm_period_and_go() -> TravelProductPage`）
- 旅遊險站台是 Blazor：class 上的 `b-xxxx` scoped 屬性每次部署會變，不可當 selector；換頁後要 `wait_loaded()`（`.loading-overlay` 會閃爍，需連續消失才算載完）

## Hard Constraints

- **正式機（prod）不可進到繳費步驟**：任何流程最多停在繳費前（目前旅遊險停在會員登入）
- 不自動破解圖形驗證碼；需要驗證碼的 TC 標 `requires_headed`，以 `--headed` 人工輸入
- `--env` 必填，沒有預設值
- Run from project root（`Path.cwd()` 用來找 yml / .env）
- 每次 commit 前通過 `make fix` 與 `make check`

## Commands

```bash
pytest --env=prod -m travel                         # headless（需人工驗證碼的 TC 會 skip）
pytest --env=prod -m travel --headed                # 開視窗，可手動輸入驗證碼
pytest --env=prod -m travel --browser-name=edge     # 換瀏覽器
```
