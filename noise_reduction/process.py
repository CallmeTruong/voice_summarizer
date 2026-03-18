# process.py
import numpy as np
from noise_reduction import wiener, VAD
from noise_reduction.smart_filter import SmartVoiceFilter

_smart_filter = SmartVoiceFilter(fs=16000)

def process_audio_pipeline(raw_signal, fs=16000, vad_threshold=0.3):

    # Wiener filter
    clean_signal = wiener.wiener_filter(raw_signal, fs=fs, noise_frames=5)

    # VAD — tách thành segments
    vad = VAD.VADGate(fs=fs, threshold=vad_threshold)
    segments = vad.filter_signal(clean_signal)
    if not segments:
        return np.array([])

    kept = []
    for seg in segments:
        keep, info = _smart_filter.should_keep(seg)
        print(f"  Score:{info['score']} | SNR:{info['snr_db']}dB | "
              f"Pitch:{info['pitch_stability']} → {info['decision']}")
        if keep:
            kept.append(seg)

    if not kept:
        return np.array([])

    return np.concatenate(kept)