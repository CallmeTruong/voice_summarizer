import numpy as np
from scipy.signal import butter, filtfilt
from scipy.fftpack import fft

class SmartVoiceFilter:
    """
    Tự động phân biệt giọng nói chính vs tiếng ồn/giọng phụ
    dựa trên chất lượng tín hiệu, không cần enroll trước.
    """
    def __init__(self, fs=16000, snr_threshold=7.0):
        self.fs = fs
        self.snr_threshold = snr_threshold  # dB
        self.noise_floor = None             # tự học noise floor
        self.alpha = 0.95                   # tốc độ cập nhật noise floor


    def estimate_snr(self, segment):
        """Ước tính SNR của đoạn audio (dB)"""
        # Năng lượng tổng
        signal_power = np.mean(segment ** 2)
        
        # Noise floor: lấy 10% frame yên tĩnh nhất
        frame_size = int(self.fs * 0.02)  # 20ms
        frames = [segment[i:i+frame_size] 
                  for i in range(0, len(segment)-frame_size, frame_size)]
        if not frames:
            return 0
        
        frame_energies = [np.mean(f**2) for f in frames]
        frame_energies.sort()
        noise_frames = frame_energies[:max(1, len(frame_energies)//10)]
        noise_power = np.mean(noise_frames)
        
        if noise_power < 1e-10:
            return 40.0  # sạch
        
        snr = 10 * np.log10(signal_power / noise_power)
        return snr

    def estimate_pitch_stability(self, segment):
        """
        Giọng người nói chủ đích có pitch ổn định.
        Tiếng ồn đám đông có pitch lộn xộn.
        """
        frame_size = int(self.fs * 0.04)  # 40ms
        hop = int(self.fs * 0.02)
        pitches = []

        for i in range(0, len(segment) - frame_size, hop):
            frame = segment[i:i+frame_size]
            # Autocorrelation để tìm pitch
            corr = np.correlate(frame, frame, mode='full')
            corr = corr[len(corr)//2:]
            
            # Tìm peak trong vùng pitch người (80-400Hz)
            min_lag = int(self.fs / 400)
            max_lag = int(self.fs / 80)
            
            if max_lag >= len(corr):
                continue
                
            peak_lag = np.argmax(corr[min_lag:max_lag]) + min_lag
            if corr[0] > 0:
                pitch_strength = corr[peak_lag] / corr[0]
                if pitch_strength > 0.3:  # có pitch rõ ràng
                    pitches.append(self.fs / peak_lag)

        if len(pitches) < 3:
            return 0.0  # không đủ pitch → không phải giọng người

        # Độ ổn định = 1 - (độ lệch chuẩn / trung bình)
        stability = 1.0 - (np.std(pitches) / (np.mean(pitches) + 1e-6))
        return max(0.0, stability)

    def compute_voice_score(self, segment):
        """
        Điểm tổng hợp: 0.0 (tiếng ồn) → 1.0 (giọng nói rõ)
        """
        snr = self.estimate_snr(segment)
        pitch_stability = self.estimate_pitch_stability(segment)
        
        # Normalize SNR về 0-1 (0dB=xấu, 20dB=tốt)
        snr_score = np.clip(snr / 20.0, 0.0, 1.0)
        
        # Kết hợp: SNR quan trọng hơn pitch
        score = 0.6 * snr_score + 0.4 * pitch_stability
        
        return score, snr, pitch_stability

    def extract_embedding(self, segment):
        """
        Embedding đơn giản từ MFCC-like features.
        Đủ để phân biệt giọng gần/xa, nam/nữ.
        """
        frame_size = int(self.fs * 0.025)
        if len(segment) < frame_size:
            return None

        spectrum = np.abs(fft(segment[:frame_size]))[:frame_size//2]
        
        # Chia thành 8 band tần số
        bands = np.array_split(spectrum, 8)
        features = np.array([np.mean(b) for b in bands])
        
        # Normalize
        norm = np.linalg.norm(features)
        if norm > 0:
            features = features / norm
        
        return features


    def should_keep(self, segment, min_score=0.35):
        """
        Quyết định giữ hay bỏ đoạn audio này.
        """
        if len(segment) < int(self.fs * 0.1):  # quá ngắn
            return False, {}
        
        score, snr, pitch_stability = self.compute_voice_score(segment)
        
        decision = score >= min_score
        
        info = {
            "score": round(score, 3),
            "snr_db": round(snr, 1),
            "pitch_stability": round(pitch_stability, 3),
            "decision": "GIỮ ✓" if decision else "BỎ ✗"
        }
        
        return decision, info