import torch
from pyannote.audio import Pipeline
import warnings

# Tắt cảnh báo cho màn hình sạch đẹp
warnings.filterwarnings("ignore")

LOCAL_CONFIG_PATH = "pyannote_local_model/config.yaml"

# Ép cứng vào file test.wav
AUDIO_FILE = "Record.mp3" 

print("⏳ Đang nạp não bộ AI từ ổ cứng cục bộ (100% OFFLINE)...")
pipeline = Pipeline.from_pretrained(LOCAL_CONFIG_PATH)

if torch.cuda.is_available():
    pipeline.to(torch.device("cuda"))
    print("🚀 Đã nạp lên GPU NVIDIA thành công!")

print(f"\n🎧 Đang nghe và phân tích file '{AUDIO_FILE}'...")
try:
    diarization = pipeline(AUDIO_FILE)

    print("\n" + "="*50)
    print("📊 KẾT QUẢ PHÂN VAI (SPEAKER DIARIZATION):")
    print("="*50)

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        print(f"⏳ [{turn.start:05.1f}s - {turn.end:05.1f}s] 🗣️: {speaker}")

    print("\n✅ Hoàn tất!")
except FileNotFoundError:
    print(f"\n❌ Lỗi: Không tìm thấy file '{AUDIO_FILE}'. Bạn lấy điện thoại ghi âm 1 đoạn, lưu thành test.wav rồi chép vào thư mục F:\\L-Company\\ nhé!")
except Exception as e:
    print(f"\n❌ Lỗi hệ thống: {e}")