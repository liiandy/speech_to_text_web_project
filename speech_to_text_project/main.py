import os
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)
import whisper
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from config import Config
import openai
import os
from datetime import datetime

class SpeechToTextProcessor:
    def __init__(self):
        self.config = Config()
        openai.api_key = self.config.OPENAI_API_KEY
        self.model = whisper.load_model("base")  # 可根據需求選擇模型大小：tiny, base, small, medium, large
        
    def process_audio(self, audio_path):
        """處理音頻檔案並回取轉碼結果"""
        self.audio_path = audio_path  # 儲存音頻路徑供其他方法使用
        try:
            # 使用 Whisper 進行語音轉文字
            result = self.model.transcribe(audio_path, language='zh', task='transcribe')
            text = result.get('text', '')
            print("Whisper 轉文字結果:", text)
            
            if not text.strip():
                raise Exception("Whisper 未能識判出任何文字。")
            
            # 先優化轉錄文字品質
            optimized_text = self._optimize_text(text)
            print("優化後的文字記錄:", optimized_text)
            
            # 使用GPT處理文本，組織成結構化記錄與簡報
            processed_text, summary = self._process_with_gpt(optimized_text)
            print("GPT處琈後的文字記錄:", processed_text)
            print("GPT簡報:", summary)
            
            # 儲存結果
            self._save_results(optimized_text, processed_text, summary)
            
            return True
            
        except Exception as e:
            print(f"處理過程中發生錯誤: {str(e)}")
            return False
    
    def _optimize_text(self, text):
        """使用GPT優化轉錄文字品質"""
        prompt = f"""
        請幫助優化令下轉錄文字，使其語句通順、語法正確，並保持繁體中文。
        
        {text}
        """
        response = openai.chat.completions.create(
            model=self.config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "你是一個專業的文字優化師"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        optimized_text = response.choices[0].message.content
        return optimized_text

    def _process_with_gpt(self, text):
        """使用GPT API處理文本"""
        prompt = f"""
        請將令下轉錄內容組織成結構化的文字記錄並提供一個簡要結記。
        
        {text}
        
        要求。
        1. 組織成段落分明的文字記錄
        2. 提供3-5個重點結要
        3. 使用繁體中文輸出
        """
        
        response = openai.chat.completions.create(
            model=self.config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "你是一個專業的語音轉文字組織師"},
                {"role": "user", "content": prompt}
            ],
            temperature=self.config.TEMPERATURE,
            max_tokens=self.config.MAX_TOKENS
        )
        processed_text = response.choices[0].message.content

        # 分割處理後的文本為記錄和簡簡
        parts = processed_text.split('\n\n')
        summary = parts[-1] if '重點摘要' in parts[-1] else ""
        record = '\n\n'.join(parts[:-1]) if summary else processed_text

        return record, summary
    
    def _save_results(self, original_text, processed_text, summary):
        """儲存處理結果到檔案"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_output_dir = "/Users/andy/Desktop/speech_to_text_project"
        output_dir = os.path.join(base_output_dir, self.config.OUTPUT_DIR)
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 取得輸入音頻檔案的基本名稱並不含強位
        base_name = os.path.splitext(os.path.basename(self.audio_path))[0]
        
        # 自動調整輸出檔案名稱，包含時間段與原始檔名
        original_filename = f"{timestamp}_{base_name}_original.txt"
        processed_filename = f"{timestamp}_{base_name}_processed.txt"
        summary_filename = f"{timestamp}_{base_name}_summary.txt"
        
        # 儲存原始轉錄
        with open(os.path.join(output_dir, original_filename), 'w', encoding='utf-8') as f:
            f.write(original_text)
        
        # 儲存處理後的記錄
        with open(os.path.join(output_dir, processed_filename), 'w', encoding='utf-8') as f:
            f.write(processed_text)
        
        # 儲存簡簡
        with open(os.path.join(output_dir, summary_filename), 'w', encoding='utf-8') as f:
            f.write(summary)

if __name__ == "__main__":
    processor = SpeechToTextProcessor()
    audio_file = input("請輸入音頻檔案路徑: ")
    processor.process_audio(audio_file)
