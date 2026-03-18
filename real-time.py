import queue
import numpy as np
import sounddevice as sd
import torch
import warnings
import math
from scipy.signal import resample_poly
from transformers import pipeline
import transformers
import soundfile as sf
from noise_reduction import process

warnings.filterwarnings("ignore")
transformers.logging.set_verbosity_error()

MODEL_DIR = "phowhisper_local_model"
SAMPLE_RATE = 48000       # ← native mic rate
TARGET_RATE = 16000       # ← Silero + model cần
CHUNK_DURATION = 0.5
MAX_SILENCE_DURATION = 1.5
SENSITIVITY = 1.2
DEBUG = True

device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f"⏳ Đang nạp động cơ lên {device}...")

transcriber = pipeline(
    "automatic-speech-recognition",
    model=MODEL_DIR,
    tokenizer=MODEL_DIR,
    device=device,
    chunk_length_s=50,
    generate_kwargs={"num_beams": 5}
)

audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    audio_queue.put(indata.copy())

def get_rms(data):
    return np.sqrt(np.mean(data**2))

def resample_audio(audio, orig=48000, target=16000):
    if orig == target:
        return audio
    gcd = math.gcd(orig, target)
    return resample_poly(audio, target//gcd, orig//gcd).astype(np.float32)

def main():
    print("\n" + "="*50)
    print("🤫 ĐANG ĐO TIẾNG ỒN MÔI TRƯỜNG...")
    print("Vui lòng GIỮ IM LẶNG trong 2 giây...")

    try:
        noise_data = sd.rec(int(SAMPLE_RATE * 2), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
        sd.wait()
        baseline_noise = get_rms(noise_data)
        threshold = baseline_noise * SENSITIVITY
        print(f"✅ Ngưỡng chống ồn: {threshold:.5f}")
    except Exception:
        threshold = 0.015

    print("\n🚀 ĐỘNG CƠ ĐÃ SẴN SÀNG! HÃY NÓI VÀO MICRO...")
    print("="*50 + "\n")

    is_recording = False
    audio_buffer = []
    silence_chunks = 0
    max_silence_chunks = int(MAX_SILENCE_DURATION / CHUNK_DURATION)

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype='float32',
        callback=audio_callback,
        blocksize=int(SAMPLE_RATE * CHUNK_DURATION)
    ):
        while True:
            chunk = audio_queue.get()
            audio_data = chunk.flatten()
            current_volume = get_rms(audio_data)

            if current_volume >= threshold:
                if not is_recording:
                    print("🎙️ Đang nghe bạn nói...", end="", flush=True)
                    is_recording = True
                audio_buffer.append(audio_data)
                silence_chunks = 0
                print(".", end="", flush=True)

            else:
                if is_recording:
                    audio_buffer.append(audio_data)
                    silence_chunks += 1

                    if silence_chunks >= max_silence_chunks:
                        print(" [HẾT CÂU] ⏳ Đang dịch...")

                        final_audio = np.concatenate(audio_buffer)
                        print(f"[DEBUG] Trước resample: {final_audio.shape}")

                        final_audio_resampled = resample_audio(final_audio, SAMPLE_RATE, TARGET_RATE)
                        print(f"[DEBUG] Sau resample: {final_audio_resampled.shape}")

                        final_audio_clean = process.process_audio_pipeline(
                            final_audio_resampled, fs=TARGET_RATE
                        )

                        if final_audio_clean.size == 0:
                            print("Không phát hiện giọng nói đủ chất lượng\n")
                        else:
                            if DEBUG:
                                sf.write('filtered_signal.wav', final_audio_clean, TARGET_RATE)

                            result = transcriber({
                                "array": final_audio_clean,
                                "sampling_rate": TARGET_RATE
                            })
                            text = result["text"].strip()

                            if text and len(text) > 2 and text not in [".", ",", "!", "?"]:
                                print(f"👉 AI: {text}\n")
                            else:
                                print("🤷 AI: (Tiếng ồn không rõ)\n")

                        is_recording = False
                        audio_buffer = []
                        silence_chunks = 0

if __name__ == "__main__":
    main()