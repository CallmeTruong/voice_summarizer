import torch
import torchaudio
import warnings
from pyannote.audio import Pipeline
from transformers import pipeline as hf_pipeline

# Tắt cảnh báo nhiễu
warnings.filterwarnings("ignore")

# ==========================================
# CẤU HÌNH ĐƯỜNG DẪN
# ==========================================
AUDIO_FILE = "Record.mp3"  # Thay bằng tên file âm thanh thật của bạn
PYANNOTE_CONFIG = "pyannote_local_model/config.yaml"
WHISPER_MODEL = "vinai/PhoWhisper-medium" # Có thể đổi thành bản tiny, base hoặc thư mục local của bạn

print("⏳ [1/4] Đang khởi động não bộ Phân vai (Pyannote)...")
diarization_pipeline = Pipeline.from_pretrained(PYANNOTE_CONFIG)

print("⏳ [2/4] Đang khởi động não bộ Dịch thuật (PhoWhisper)...")
# Nạp Whisper lên GPU (nếu có) để dịch siêu tốc
device_id = 0 if torch.cuda.is_available() else -1
transcriber = hf_pipeline("automatic-speech-recognition", model=WHISPER_MODEL, device=device_id)

if torch.cuda.is_available():
    diarization_pipeline.to(torch.device("cuda"))
    print("🚀 Cả 2 AI đã nạp lên GPU NVIDIA thành công!")

print(f"\n🎧 [3/4] Đang phân tích ranh giới người nói cho file '{AUDIO_FILE}'...")
diarization = diarization_pipeline(AUDIO_FILE)

# Nạp file âm thanh gốc vào bộ nhớ để chuẩn bị cắt
waveform, sample_rate = torchaudio.load(AUDIO_FILE)

print("\n" + "="*60)
print("📝 BIÊN BẢN CUỘC HỌP TỰ ĐỘNG:")
print("="*60)

window_size = 10
windows = {}

for turn, _, speaker in diarization.itertracks(yield_label=True):

    start_time = turn.start
    end_time = turn.end

    start_frame = int(start_time * sample_rate)
    end_frame = int(end_time * sample_rate)

    segment = waveform[:, start_frame:end_frame]

    temp_file = "temp_segment.wav"
    torchaudio.save(temp_file, segment, sample_rate)

    result = transcriber(temp_file)
    text = result["text"].strip()

    window_id = int(start_time // window_size)

    if window_id not in windows:
        windows[window_id] = {}

    if speaker not in windows[window_id]:
        windows[window_id][speaker] = []

    windows[window_id][speaker].append(text)

# ==========================================
# IN KẾT QUẢ
# ==========================================
for window_id in sorted(windows.keys()):

    start = window_id * window_size
    end = start + window_size

    print(f"\n[{start}-{end}s]")

    for speaker, texts in windows[window_id].items():

        combined = " ".join(texts)
        print(f"{speaker}: {combined}")