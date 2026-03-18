import numpy as np
from scipy.fftpack import fft, ifft
import matplotlib.pyplot as plt

def spectral_subtraction(noisy_signal, thres=0.1):
    fs = 8000  # Tần số lấy mẫu
    n = len(noisy_signal)
    spectrum = fft(noisy_signal)

    # Tính toán phổ tần số và xác định mức độ nhiễu
    noise_estimate = np.median(np.abs(spectrum))  # ước tính mức độ nhiễu

    # Trừ đi mức độ nhiễu từ phổ tín hiệu
    spectrum_filtered = np.copy(spectrum)
    spectrum_filtered[np.abs(spectrum) < noise_estimate * thres] = 0  # Lọc nhiễu (sử dụng ngưỡng)

    # Chuyển lại tín hiệu vào miền thời gian
    filtered_signal = ifft(spectrum_filtered).real
        # Vẽ Spectrogram của tín hiệu gốc và tín hiệu sau khi giảm nhiễu
    plt.figure(figsize=(12, 6))

    plt.subplot(3, 1, 1)
    plt.specgram(noisy_signal, Fs=fs, NFFT=1024, noverlap=512, cmap='viridis')
    plt.title('Spectrogram of Noisy Signal')
    plt.xlabel('Time [s]')
    plt.ylabel('Frequency [Hz]')

    plt.subplot(3, 1, 2)
    plt.specgram(spectrum_filtered, Fs=fs, NFFT=1024, noverlap=512, cmap='viridis')
    plt.title('Spectrogram of spectrum_filtered')
    plt.xlabel('Time [s]')
    plt.ylabel('Frequency [Hz]')

    plt.subplot(3, 1, 3)
    plt.specgram(filtered_signal, Fs=fs, NFFT=1024, noverlap=512, cmap='viridis')
    plt.title('Spectrogram of Filtered Signal (Spectral Gating)')
    plt.xlabel('Time [s]')
    plt.ylabel('Frequency [Hz]')

    plt.savefig('subtract.png')
    return filtered_signal