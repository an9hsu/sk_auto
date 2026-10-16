// Allure 3 報表設定：npx allure generate 會讀這個檔
import { defineConfig } from "allure";

export default defineConfig({
  name: "新光產物 自動化測試報告",
  output: "./allure-report",
  // 每次產生報表都記一筆，報表裡就看得到歷次通過率的趨勢
  historyPath: "./allure-history/history.jsonl",
  plugins: {
    awesome: {
      options: {
        reportLanguage: "zh-TW",
        // 整份報表包成單一 HTML 檔，可以直接寄給別人、雙擊就能打開
        singleFile: true,
        groupBy: ["feature", "story"],
      },
    },
  },
});
