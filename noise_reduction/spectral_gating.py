import numpy as np
from scipy.fftpack import fft, ifft
import matplotlib.pyplot as plt

def adaptive_spectral_gating(noisy_signal, thres=0.1, fs=8000):
    n = len(noisy_signal)
    
    # Chuyển tín hiệu vào miền tần số (FFT)
    spectrum = fft(noisy_signal)

    # Tính toán mức độ nhiễu và xác định ngưỡng động cho từng tần số
    abs_spectrum = np.abs(spectrum)
    mean_amplitude = np.mean(abs_spectrum)  # Tính toán biên độ trung bình

    # Tự động điều chỉnh ngưỡng động: giảm ngưỡng cho những tần số có biên độ nhỏ hơn mức trung bình
    dynamic_threshold = mean_amplitude * thres  # Ngưỡng động, điều chỉnh theo biên độ trung bình

    # Lọc tín hiệu: Giữ lại tần số có biên độ lớn hơn ngưỡng động
    spectrum_filtered = np.copy(spectrum)
    spectrum_filtered[np.abs(spectrum) < dynamic_threshold] = 0

    # Chuyển tín hiệu đã lọc trở lại miền thời gian
    filtered_signal = ifft(spectrum_filtered).real

    # Vẽ Spectrogram
    plt.figure(figsize=(12, 6))

    plt.subplot(3, 1, 1)
    plt.specgram(noisy_signal, Fs=fs, NFFT=1024, noverlap=512, cmap='viridis')
    plt.title('Spectrogram of Noisy Signal')
    plt.xlabel('Time [s]')
    plt.ylabel('Frequency [Hz]')

    plt.subplot(3, 1, 2)
    plt.specgram(filtered_signal, Fs=fs, NFFT=1024, noverlap=512, cmap='viridis')
    plt.title('Spectrogram of Filtered Signal')
    plt.xlabel('Time [s]')
    plt.ylabel('Frequency [Hz]')

    # Phổ tần của tín hiệu sau khi lọc
    plt.subplot(3, 1, 3)
    positive_freqs = np.fft.fftfreq(n, d=1/fs)[:n//2]
    positive_spectrum_filtered = np.abs(spectrum_filtered[:n//2])

    plt.plot(positive_freqs, positive_spectrum_filtered)
    plt.title('Filtered Spectrum')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Amplitude')

    plt.tight_layout()
    plt.savefig('spectral_gating.png')

    return filtered_signal