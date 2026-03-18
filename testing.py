# test_debug.py — đặt ở thư mục Voice/
import sounddevice as sd
import numpy as np
import torch

print("=== TEST 1: Raw audio ===")
print("Đang thu 3 giây, hãy nói to...")
audio = sd.rec(int(16000 * 3), samplerate=16000, channels=1, dtype='float32')
sd.wait()
audio = audio.flatten()
print(f"Shape: {audio.shape}")
print(f"Max: {np.max(np.abs(audio)):.6f}")
print(f"Mean: {np.mean(np.abs(audio)):.6f}")
print(f"Sample values: {audio[8000:8010]}")  # giữa đoạn thu

print("\n=== TEST 2: Silero VAD trực tiếp trên raw audio ===")
model, utils = torch.hub.load(
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad',
    force_reload=False
)
(get_speech_ts, _, _, _, _) = utils

tensor = torch.FloatTensor(audio)
timestamps = get_speech_ts(tensor, model, threshold=0.3, sampling_rate=16000)
print(f"Timestamps: {timestamps}")
print(f"Số đoạn detect: {len(timestamps)}")