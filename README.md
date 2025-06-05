# Instagram 照片下載

此專案提供一個簡易的 Python 腳本，利用 Selenium 從公開的 Instagram 帳號下載圖片。

## 需求

- Python 3
- 已安裝 Google Chrome 與對應版本的 ChromeDriver，並放在 `PATH`
- 需要的套件：
  ```bash
  pip install selenium requests
  ```

## 設定

在專案根目錄建立 `config.json`，內容如下：

```json
{
  "username": "your_instagram_username",
  "password": "your_instagram_password"
}
```

`config.json` 已列在 `.gitignore`，不會被加入版本控制。

## 使用方式

執行主程式：

```bash
python main.py
```

流程簡述：

1. 讀取 `config.json` 中的帳號登入 Instagram。
2. 輸入要查詢的帳號名稱。
3. 檢查帳號是否存在且為公開狀態。
4. 指定要下載的貼文數量。
5. 下載圖片到 `downloads/` 目錄，每篇貼文一個資料夾。

腳本會跳過非目標帳號或包含影片的貼文，每張圖片下載後暫停，按 Enter 才會繼續。

## 其他注意事項

- 若要以無介面模式執行，請取消 `main.py` 中 `--headless` 的註解。
- IG 版面若有變動，選擇器可能需要調整。
