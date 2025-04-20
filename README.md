# Speech to Text Web Project

## 專案說明

本專案提供一個基於 OpenAI Whisper 與 GPT 的語音轉文字服務，包含後端 API 與前端網頁介面，支援即時錄音與檔案上傳。

## 功能

- 使用 Whisper 進行高準確度語音轉文字
- 使用 GPT 進行文字優化與重點摘要
- 前端支援即時錄音與檔案上傳
- 後端提供 REST API 與 WebSocket 即時狀態回報

## 環境需求

- Python 3.9+
- ffmpeg
- 相關 Python 套件請參考 requirements.txt

## 安裝

```bash
pip install -r requirements.txt
brew install ffmpeg  # macOS
```

## 啟動

1. 啟動後端伺服器

```bash
uvicorn app:app --reload
```

2. 開啟前端 `index.html`，或將前端整合至後端靜態服務

## 使用說明

- 可透過前端網頁即時錄音或上傳錄音檔案
- 轉錄結果與重點摘要會即時顯示

## 注意事項

- 請確保已安裝 ffmpeg
- 需設定 OpenAI API Key

## 聯絡

如有問題，請聯絡開發者
