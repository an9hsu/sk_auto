# sk_auto

新光產物各產品的**網頁自動化測試**：讓電腦自己打開瀏覽器、照著劇本點網頁、填資料，並檢查畫面結果對不對。

> 第一次接觸？照著「一、先懂幾個名詞」→「二、安裝」→「三、設定」→「四、執行」→「五、看結果」做，就能跑起來。
> 之後要改測試、網站改版測試壞掉，看「六、日常維護」。

---

## 一、先懂幾個名詞

| 名詞 | 白話解釋 |
|---|---|
| **自動化測試** | 把「人工點網頁檢查」寫成程式，之後一鍵重跑，不用每次手點。 |
| **Python** | 這個專案使用的程式語言。 |
| **pytest** | 跑測試的工具。輸入 `pytest ...` 指令，它會找出所有測試並逐一執行，最後告訴你哪些通過（passed）、哪些失敗（failed）。 |
| **Selenium** | 控制瀏覽器的工具。程式透過它去「點按鈕」、「輸入文字」，就像真人在操作。 |
| **TC（Test Case）** | 一個測試案例，也就是一段劇本，例如「多人投保一路走到會員登入頁」。 |
| **headless / headed** | headless：瀏覽器在背景跑，看不到視窗（預設）。headed：會開出視窗，看得到操作過程。 |
| **終端機（Terminal）** | 輸入指令的黑色視窗。Mac：「終端機」App；Windows：「PowerShell」。下面所有指令都在這裡輸入。 |
| **虛擬環境（.venv）** | 專案專用的 Python 套件資料夾，跟電腦上其他程式互不干擾。 |

---

## 二、安裝（只需做一次）

### 1. 安裝必要軟體

| 軟體 | 用途 | 下載 |
|---|---|---|
| **Python 3.12** | 執行程式 | <https://www.python.org/downloads/>（選 3.12.x）。Windows 安裝時**務必勾選「Add python.exe to PATH」** |
| **Google Chrome** | 測試用的瀏覽器 | <https://www.google.com/chrome/> |
| **Git** | 下載專案原始碼 | <https://git-scm.com/downloads>（Mac 通常已內建） |
| **Node.js** | 產生 Allure 3 測試報表用 | <https://nodejs.org/>（選 LTS 版，一路按下一步即可） |

> 不用另外裝 chromedriver（瀏覽器驅動程式），Selenium 第一次執行時會自動下載。

裝好後打開終端機，確認版本：

```bash
python3.12 --version     # Mac，應顯示 Python 3.12.x
py -3.12 --version       # Windows
node --version           # 有顯示版本號就代表 Node.js 裝好了
```

### 2. 下載專案

```bash
git clone <專案的 git 網址>
cd sk_auto
```

> **之後所有指令都要在 `sk_auto` 資料夾裡執行**，不然會找不到設定檔。

### 3. 建立虛擬環境並安裝套件

**Mac：**

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows（PowerShell）：**

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

成功啟用後，終端機最前面會出現 `(.venv)`。

> ⚠️ **每次重新打開終端機，都要先重跑一次啟用指令**（Mac：`source .venv/bin/activate`；Windows：`.venv\Scripts\Activate.ps1`），否則會出現 `pytest: command not found`。
>
> Windows 若出現「因為這個系統上已停用指令碼執行」，先執行一次：`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### 4. 安裝報表工具（Allure 3）

```bash
npm install
```

會依照 `package.json` 把 Allure 3 裝進專案的 `node_modules/` 資料夾（只有這個專案用得到，不影響電腦其他地方）。

裝好後確認版本：

```bash
npx allure --version     # 應顯示 3.20.1
```

> 一定要先 `npm install`。沒裝的話，`npx allure` 會改用電腦上其他版本的 Allure，或詢問要不要從網路下載最新版，產生出來的報表可能和說明不一樣。

---

## 三、設定帳號資料（只需做一次）

測試需要用到身分證、生日、會員帳號。這些是**個資**，所以不放在程式裡，而是放在只存在你電腦上的檔案（已設定不會被上傳到 git）。

把範本複製一份，檔名前面多一個點 `.`：

```bash
cp configs/account_prod.yml.sample configs/.account_prod.yml      # Mac
copy configs\account_prod.yml.sample configs\.account_prod.yml    # Windows
```

用文字編輯器（VS Code、記事本皆可）打開 `configs/.account_prod.yml`，把假資料換成真的：

```yaml
travel:
  proposer:
    id: A123456789           # 要保人身分證字號
    birthday: "1990/01/01"   # 西元 YYYY/MM/DD，要加雙引號
  member:
    account: A123456789      # 會員帳號
```

> Mac 的 Finder 預設看不到「.」開頭的檔案，按 `Cmd + Shift + .` 可以顯示。

---

## 四、執行測試

```bash
# 跑旅遊險全部測試（背景執行，看不到視窗）
pytest --env=prod -m travel

# 開出瀏覽器視窗，看得到操作過程
pytest --env=prod -m travel --headed

# 只跑某一個 TC（-k 後面接 TC 名稱的一部分）
pytest --env=prod -k reach_member_login --headed

# 換成 Edge / Firefox
pytest --env=prod -m travel --browser-name=edge
```

指令的每個部分代表：

| 參數 | 意思 |
|---|---|
| `--env=prod` | 要測哪個環境。**必填**，目前只有 `prod`（正式機）。 |
| `-m travel` | 只跑標記為「旅遊險」的測試。 |
| `--headed` | 開出瀏覽器視窗。 |
| `-k 關鍵字` | 只跑名稱含有這個關鍵字的測試。 |
| `--browser-name=` | 換瀏覽器：`chrome`（預設）、`edge`、`firefox`。 |

---

## 五、看結果

### 終端機上的結果

跑完最後一行會有總結，例如：

```
==== 1 passed in 45.12s ====
```

- `passed`：通過 ✅
- `failed`：失敗 ❌（上方會印出原因，搜尋 `AssertionError` 或 `Error` 找原因）

### 失敗截圖

測試失敗時會自動截圖，存在 `test-results/screenshots/<TC 名稱>.png`，打開就知道停在哪個畫面。

### Allure 網頁報表

每次跑測試，結果會自動存進 `allure-results/` 資料夾（每次執行會先清掉上一次的結果）。跑完後執行：

```bash
npx allure generate allure-results --open
```

報表會產生在 `allure-report/index.html`，並自動用瀏覽器打開。報表是繁體中文，可以看到：

- 每個 TC 通過或失敗、花了多久
- 每個 TC 裡的每一步（例如「試算」、「填寫要保人資料」），失敗時看得出停在哪一步
- 失敗時的截圖和當下的網址
- 歷次執行的通過率趨勢（紀錄存在 `allure-history/`，刪掉就從頭算）

看完回到終端機按 `Ctrl + C` 結束。

> 想把報表傳給別人：直接把 `allure-report/index.html` 這**一個檔案**寄給對方即可，對方不用裝任何東西，雙擊就能用瀏覽器打開。
>
> 報表的名稱、語言等設定在 `allurerc.mjs`。

---

## 六、日常維護

### 專案結構（哪個檔案負責什麼）

```
sk_auto/
├── configs/                          設定
│   ├── env_prod.yml                    各產品的網址
│   ├── .account_prod.yml               你的個資（自己建，不進 git）
│   ├── account_prod.yml.sample         上面那個檔案的範本
│   └── settings.py                     讀取設定的程式
├── selenium_object/                  「怎麼操作網頁」
│   ├── locators/travel/                網頁元素的位置（按鈕、輸入框在哪）
│   ├── travel/                         每一頁能做的動作（選地點、填身分證…）
│   └── base_page.py                    所有頁面共用的動作（點擊、等待、輸入）
├── tests/ui_test/travel/             「測試劇本」
│   ├── test_travel_online_insure.py    旅遊險：投保到會員登入頁
│   └── test_travel_quote.py            旅遊險：首頁試算、保費試算頁
├── utils/                            共用小工具（例如日期計算）
├── pytest.ini                        pytest 設定（產品標記 markers 在這裡）
├── requirements.txt                  Python 套件清單（pip install 依這個安裝）
├── allurerc.mjs                      Allure 3 報表設定（名稱、語言）
└── package.json                      Allure 3 的版本（npm install 依這個安裝）
```

整個專案分三層，改東西時先想清楚要改哪一層：

| 層 | 回答的問題 | 位置 | 什麼時候改 |
|---|---|---|---|
| **Locator（元素位置）** | 按鈕在畫面的哪裡？ | `selenium_object/locators/` | 網站改版、按鈕換位置／換名字 |
| **Page Object（頁面動作）** | 這一頁可以做什麼？ | `selenium_object/<產品>/` | 網站流程變了、要新增操作 |
| **Test（測試劇本）** | 要依什麼順序做、檢查什麼？ | `tests/ui_test/<產品>/` | 要新增／修改測試情境 |

### 情境 1：網站改版，測試突然壞掉

最常見的原因是**網頁上的元素換了位置或名稱**，程式找不到。

1. 看失敗訊息和截圖，找出是哪一步、哪個元素。訊息通常會寫 `TimeoutException` 或「找不到」。
2. 用 Chrome 打開該網頁，在元素上按右鍵 →「檢查」，看它現在的 `id`、`name`、`class`。
3. 到 `selenium_object/locators/travel/travel_locator.py` 找到對應那一行，改成新的值。例如：

   ```python
   NEXT_BTN = (By.CSS_SELECTOR, "button.sys-button__next")
   #          ↑ 用什麼方式找    ↑ 要找的值
   ```

   常用的找法：`By.ID`（用 id）、`By.NAME`（用 name）、`By.CSS_SELECTOR`（用 class 等，class 前面加 `.`）、`By.XPATH`（用文字找）。
4. 加 `--headed` 重跑，確認通過。

> ⚠️ 旅遊險網站 class 裡像 `b-a1b2c3d4` 這種亂碼屬性**每次部署都會變**，不要拿來當定位依據。

### 情境 2：修改測試資料

| 想改的 | 改哪裡 |
|---|---|
| 旅遊地點、幾天後出發、旅遊天數 | 各測試檔最上方的常數：`test_travel_online_insure.py` 的 `DESTINATION`、`START_AFTER_DAYS`、`TRIP_DAYS`；`test_travel_quote.py` 的 `DESTINATION`、`START_AFTER_DAYS`、`MIN_TRIP_DAYS` |
| 身分證、生日、會員帳號 | `configs/.account_prod.yml` |
| 網址 | `configs/env_prod.yml` |

### 情境 3：新增一個 TC

1. 在 `tests/ui_test/travel/` 的測試檔裡新增一個 `test_` 開頭的函式。pytest 只認 `test_` 開頭的函式。
   - 到首頁或保費試算頁為止的 TC：放 `test_travel_quote.py`
   - 會走到會員登入的 TC：放 `test_travel_online_insure.py`
2. 用 Page Object 已有的動作組合出流程，可參考現有的 `go_to_product`（走到保費試算頁）、`_go_to_member_login`（走到會員登入頁）。
3. 如果需要新的操作（例如點新的按鈕）：先在 locators 加元素位置，再到 `selenium_object/travel/` 對應頁面加一個方法。

### 情境 4：新增一個產品（例如車險）

1. `selenium_object/locators/car/`：元素位置
2. `selenium_object/car/`：頁面動作（繼承 `BasePage`）
3. `tests/ui_test/car/conftest.py` + `test_xxx.py`：測試
4. `configs/env_prod.yml` 加網址，`configs/settings.py` 的 `UrlConfig` 加同名欄位
5. `pytest.ini` 的 `markers` 加 `car`

---

## 七、⚠️ 一定要遵守的規則

1. **正式機絕對不能自動跑到「繳費」步驟**。流程最多停在繳費前（目前旅遊險停在會員登入）。
2. **個資（身分證、生日、帳號）不可寫進程式碼**，只能放 `configs/.account_prod.yml`。
3. **不要用 `time.sleep()` 硬等**，用 `BasePage` 提供的 `wait_*` 系列方法。

---

## 八、常見問題

| 狀況 | 解法 |
|---|---|
| `pytest: command not found` / `不是內部或外部命令` | 沒啟用虛擬環境，先執行 `source .venv/bin/activate`（Windows：`.venv\Scripts\Activate.ps1`） |
| `--env 必填` | 指令要加 `--env=prod` |
| `Env yaml not found` | 不在專案根目錄，先 `cd sk_auto` |
| log 出現 `Account yaml not found` | 還沒建 `configs/.account_prod.yml`，見「三、設定帳號資料」 |
| 第一次執行卡很久 | Selenium 在下載瀏覽器驅動程式，等一下即可 |
| `npx: command not found` / `npm: command not found` | Node.js 沒裝好，見「二、安裝」；裝完要重開終端機 |
| `npx allure --version` 顯示的不是 3.20.1，或出現 `Need to install the following packages` | 還沒在專案資料夾執行 `npm install`；看到詢問先按 `n`，再執行 `npm install` |
| 全部 TC 一起失敗、截圖是維護公告 | 網站在系統維護（首頁「重要事項」會公告時段），等維護結束再跑 |
| 偶爾失敗、重跑又過 | 網站慢或不穩，先重跑一次；常常發生再看截圖找原因 |

---

## 目前涵蓋的測試

全部都停在繳費前；除了 TC-1 會到會員登入畫面（不送出登入），其他最多到保費試算頁。

| 檔案 | TC | 檢查什麼 | 停止點 |
|---|---|---|---|
| `test_travel_online_insure.py` | TC-1 `test_multi_people_reach_member_login` | 多人 → 日本-沖繩 → 3 天後出發共 4 天 → 要保人身分證／生日 → 同意聲明 → 會員帳號登入頁（帳號自動帶入） | 登入前 |
| `test_travel_quote.py` | `test_every_quick_destination_selectable` | 每個熱門地點都點得到，並帶進旅遊地點欄位 | 首頁 |
| `test_travel_quote.py` | `test_multi_people_earliest_start_is_3_days_later` | 多人投保的月曆最早只能選 3 天後 | 首頁 |
| `test_travel_quote.py` | `test_trip_days_shown_in_confirm`（3 天、30 天跨月） | 確認框的地點、起訖日、天數正確，保費試算頁有保費 | 保費試算頁 |
| `test_travel_quote.py` | `test_trip_shorter_than_min_days_blocked` | 保期只有 2 天 → 提示「保險期間至少 3日」 | 首頁 |
| `test_travel_quote.py` | `test_submit_empty_form_blocked` | 什麼都沒填就按下一步 → 被擋下 | 首頁 |
| `test_travel_quote.py` | `test_period_picker_confirm_without_dates_alerts` | 月曆沒選日期就按確定 → 提示「請選擇出發與結束日期」 | 首頁 |
| `test_travel_quote.py` | `test_switch_plan` | 每個方案都有保費且不同；切換方案後選取狀態跟著換 | 保費試算頁 |
| `test_travel_quote.py` | `test_terms_required_before_next` | 聲明事項沒捲到底不能勾；沒同意就按下一步會出現驗證訊息 | 保費試算頁 |
