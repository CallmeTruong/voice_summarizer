from transformers import AutoProcessor

LOCAL_DIR = "phowhisper_local_model"

print("Đang tải nốt 'đôi tai' (Processor/Feature Extractor) về...")
# Tải bộ xử lý âm thanh của PhoWhisper
processor = AutoProcessor.from_pretrained("vinai/PhoWhisper-medium")

# Lưu bổ sung vào thư mục hiện tại của bạn
processor.save_pretrained(LOCAL_DIR)

print(f"✅ Đã vá lỗi xong! File preprocessor_config.json đã được thêm vào {LOCAL_DIR}.")