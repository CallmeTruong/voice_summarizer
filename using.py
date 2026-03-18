import torch
from datasets import load_from_disk
from transformers import pipeline
import jiwer
from tqdm import tqdm

# ==========================================
# CẤU HÌNH ĐƯỜNG DẪN
# ==========================================
TEST_DATA_PATH = "vivos_local/test"
LOCAL_MODEL_DIR = "phowhisper_local_model"

def main():
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    print(f"🚀 Thiết bị chạy: {device}")

    # 1. Tải mô hình từ thư mục local của bạn
    print("⏳ Đang nạp mô hình từ ổ cứng...")
    transcriber = pipeline(
        "automatic-speech-recognition",
        model=LOCAL_MODEL_DIR,
        tokenizer=LOCAL_MODEL_DIR,
        device=device
    )

    # 2. Tải tập Test
    print("⏳ Đang nạp tập dữ liệu Test...")
    test_ds = load_from_disk(TEST_DATA_PATH)
    print(f"Tổng số mẫu cần đánh giá: {len(test_ds)}")

    predictions = []
    references = []

    # 3. Vòng lặp chạy dự đoán và so sánh
    print("🔥 Bắt đầu dự đoán...")
    # Dùng tqdm để hiện thanh tiến trình cho đỡ sốt ruột
    for item in tqdm(test_ds):
        # Lấy mảng âm thanh và câu gốc
        audio_array = item["audio"]["array"]
        ref_text = item["sentence"].lower()

        # Cho model nghe và dịch
        # Cấu trúc dict này giúp pipeline tự hiểu mảng numpy và tần số lấy mẫu
        result = transcriber({"array": audio_array, "sampling_rate": 16000})
        pred_text = result["text"].lower()

        # Xử lý bẫy lỗi chuỗi rỗng của thư viện jiwer
        if not pred_text.strip(): pred_text = "-"
        if not ref_text.strip(): ref_text = "-"

        predictions.append(pred_text)
        references.append(ref_text)

    # 4. Tính toán Word Error Rate (WER) tổng quát
    wer_score = jiwer.wer(references, predictions)
    
    print("\n" + "="*40)
    print("🎯 KẾT QUẢ ĐÁNH GIÁ (BASELINE)")
    print("="*40)
    print(f"Tổng số câu test: {len(references)}")
    print(f"Chỉ số WER      : {wer_score * 100:.2f}%")
    print("="*40)

if __name__ == "__main__":
    main()