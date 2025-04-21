import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI API 配置，從環境變數讀取，避免硬編碼
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # 音頻處理配置
    AUDIO_DIR = "audio_files"
    OUTPUT_DIR = "output"
    SUPPORTED_FORMATS = ['.wav', '.mp3', '.flac', '.mov']
    
    # 文字處理配置
    MAX_TOKENS = 2000
    TEMPERATURE = 0.7
