from transformers import WhisperForConditionalGeneration, AutoTokenizer
import os

def download_model():
    LOCAL_DIR = "phowhisper_local_model"
    os.makedirs(LOCAL_DIR, exist_ok=True)

    print("Đang kéo model và tokenizer từ Hugging Face về (cần internet)...")
    tokenizer = AutoTokenizer.from_pretrained("vinai/PhoWhisper-medium")
    model = WhisperForConditionalGeneration.from_pretrained("vinai/PhoWhisper-medium")

    print("Đang lưu vĩnh viễn xuống ổ cứng máy tính...")
    tokenizer.save_pretrained(LOCAL_DIR)
    model.save_pretrained(LOCAL_DIR)

    print(f"Xong! Model đã được lưu trọn gói tại thư mục: {LOCAL_DIR}")
    print("Từ bây giờ bạn có thể tắt mạng và sử dụng offline!")

# BẮT BUỘC PHẢI CÓ DÒNG NÀY TRÊN WINDOWS
if __name__ == "__main__":
    download_model()