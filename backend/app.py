import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import shutil
from speech_to_text_project.main import SpeechToTextProcessor
from fastapi.responses import JSONResponse
import asyncio

app = FastAPI()

# 允許跨域請求，前端可在不同端口運行
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

processor = SpeechToTextProcessor()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/status")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # 這裏可根據需求處理前端訊息
            await manager.send_message(f"收到訊息: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

import yt_dlp

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    # 檢查檔案格式
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".wav", ".mp3", ".flac", ".mov", ".mp4"]:
        raise HTTPException(status_code=400, detail="不支援的檔案格式")
    
    # 儲存上傳檔案到更新
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, filename)
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 非同步執行語音轉文字，並通過 WebSocket 傳送狀態
    def process_and_notify():
        import time
        time.sleep(0.1)
        success = processor.process_audio(temp_path)
        base_output_dir = "/Users/andy/Desktop/speech_to_text_project"
        output_dir = os.path.join(base_output_dir, processor.config.OUTPUT_DIR)
        base_name = os.path.splitext(filename)[0]
        def get_latest_file(suffix):
            files = [f for f in os.listdir(output_dir) if f.endswith(suffix) and base_name in f]
            files.sort(reverse=True)
            if files:
                with open(os.path.join(output_dir, files[0]), 'r', encoding='utf-8') as f:
                    return f.read()
            return ""
        original_text = get_latest_file("_original.txt")
        processed_text = get_latest_file("_processed.txt")
        summary_text = get_latest_file("_summary.txt")
        os.remove(temp_path)
        if not success:
            raise HTTPException(status_code=500, detail="語音轉文字處理失敗")
        return original_text, processed_text, summary_text

    original_text, processed_text, summary_text = await asyncio.to_thread(process_and_notify)

    return JSONResponse(content={
        "original_text": original_text,
        "processed_text": processed_text,
        "summary": summary_text
    })

@app.post("/transcribe_youtube")
async def transcribe_youtube(url_data: dict):
    url = url_data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="缺少 YouTube 畫面網址")
    
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_audio_path = os.path.join(temp_dir, "youtube_audio.%(ext)s")
    
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": temp_audio_path,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
        "no_warnings": True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"YouTube 畫面下載失敗: {str(e)}\n詳細錯誤:\n{error_msg}")
        raise HTTPException(status_code=500, detail=f"YouTube 畫面下載失敗: {str(e)}\n詳細錯誤:\n{error_msg}")
    
    # 下載後獲取實際檔案路徑
    downloaded_files = [f for f in os.listdir(temp_dir) if f.startswith("youtube_audio") and f.endswith(".mp3")]
    if not downloaded_files:
        print("下載的音話檔案不存在")
        raise HTTPException(status_code=500, detail="下載的音話檔案不存在")
    actual_audio_path = os.path.join(temp_dir, downloaded_files[0])
    
    # 使用現有語音轉文字流程
    try:
        success = processor.process_audio(actual_audio_path)
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"語音轉文字處理失敗: {str(e)}\n詳細錯誤:\n{error_msg}")
        raise HTTPException(status_code=500, detail=f"語音轉文字處理失敗: {str(e)}\n詳細錯誤:\n{error_msg}")
    
    base_output_dir = "/Users/andy/Desktop/speech_to_text_project"
    output_dir = os.path.join(base_output_dir, processor.config.OUTPUT_DIR)
    base_name = "youtube_audio"
    
    def get_latest_file(suffix):
        files = [f for f in os.listdir(output_dir) if f.endswith(suffix) and base_name in f]
        files.sort(reverse=True)
        if files:
            with open(os.path.join(output_dir, files[0]), 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    original_text = get_latest_file("_original.txt")
    processed_text = get_latest_file("_processed.txt")
    summary_text = get_latest_file("_summary.txt")
    
    os.remove(actual_audio_path)
    
    if not success:
        print("語音轉文字處理失敗")
        raise HTTPException(status_code=500, detail="語音轉文字處理失敗")
    
    return JSONResponse(content={
        "original_text": original_text,
        "processed_text": processed_text,
        "summary": summary_text
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
