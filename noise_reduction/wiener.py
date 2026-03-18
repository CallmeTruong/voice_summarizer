import numpy as np
from scipy.fftpack import fft, ifft

def wiener_filter(noisy_signal, fs=16000, noise_frames=5):
    frame_size = int(fs * 0.025)
    hop_size = int(fs * 0.010)
    
    noise_spectrum = np.zeros(frame_size)
    for i in range(noise_frames):
        start = i * hop_size
        if start + frame_size > len(noisy_signal):
            break
        frame = noisy_signal[start:start + frame_size] * np.hanning(frame_size)
        noise_spectrum += np.abs(fft(frame, n=frame_size)) ** 2
    noise_spectrum /= noise_frames

    output = np.zeros(len(noisy_signal))
    window_sum = np.zeros(len(noisy_signal))
    window = np.hanning(frame_size)

    for start in range(0, len(noisy_signal) - frame_size, hop_size):
        frame = noisy_signal[start:start + frame_size] * window
        spectrum = fft(frame, n=frame_size)
        power = np.abs(spectrum) ** 2

        alpha = 1.5   
        beta = 0.05   

        gain = np.maximum(beta, 1 - alpha * noise_spectrum / (power + 1e-10))
        gain = np.sqrt(gain)

        filtered_spectrum = spectrum * gain
        filtered_frame = ifft(filtered_spectrum).real * window

        output[start:start + frame_size] += filtered_frame
        window_sum[start:start + frame_size] += window ** 2

    output /= np.maximum(window_sum, 1e-8)
    return output.astype(np.float32)