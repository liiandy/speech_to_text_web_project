# 專案部署與環境變數設定說明

本文件說明如何部署「語音轉文字服務」專案，並設定必要的環境變數以確保敏感資訊安全。

---

## 一、環境需求

- Python 3.9 以上
- ffmpeg（音訊處理工具）
- 相關 Python 套件（請參考 `requirements.txt`）

---

## 二、安裝依賴

1. 安裝 Python 套件：

```bash
pip install -r requirements.txt
```

2. 安裝 ffmpeg：

- macOS（使用 Homebrew）：

```bash
brew install ffmpeg
```

- Windows / Linux 請參考官方安裝說明。

---

## 三、環境變數設定

請在系統環境中設定以下變數：

- `OPENAI_API_KEY`：您的 OpenAI API 金鑰，必須設定才能使用 GPT 相關功能。
- `OPENAI_MODEL`：使用的模型名稱，預設為 `gpt-4`，可依需求調整。

### macOS / Linux 範例

在終端機輸入：

```bash
export OPENAI_API_KEY="您的API金鑰"
export OPENAI_MODEL="gpt-4"
```

### Windows 範例（PowerShell）

```powershell
setx OPENAI_API_KEY "您的API金鑰"
setx OPENAI_MODEL "gpt-4"
```

設定後，請重新啟動終端機或系統以使變數生效。

---

## 四、啟動後端伺服器

在專案 `backend` 目錄下執行：

```bash
uvicorn app:app --reload
```

伺服器預設監聽 `http://0.0.0.0:8000`。

---

## 五、部署前端

將 `frontend` 目錄中的靜態檔案部署至 GitHub Pages、Netlify 或其他靜態網站服務。

---

## 六、測試

- 使用前端頁面進行即時錄音或上傳音訊檔案。
- 輸入 YouTube 影片網址進行轉錄。
- 確認轉錄結果與重點摘要正常顯示。

---

## 七、注意事項

- 請勿將 API 金鑰硬編碼於程式碼中。
- 確保伺服器與前端間的 CORS 設定正確。
- 若使用雲端服務，請妥善管理環境變數與密鑰。

---

如有任何問題，請隨時聯繫開發者。
