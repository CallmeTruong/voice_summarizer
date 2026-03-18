import torch
import numpy as np

class VADGate:
    def __init__(self, fs=8000, threshold=0.25):
        self.model, self.utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False
        )
        self.fs = fs
        self.threshold = threshold
        (self.get_speech_ts, _, _, _, _) = self.utils

    def filter_signal(self, signal):
        tensor = torch.FloatTensor(signal)
        speech_timestamps = self.get_speech_ts(
            tensor, 
            self.model,
            threshold=self.threshold,
            sampling_rate=self.fs
        )
        
        segments = []
        for ts in speech_timestamps:
            segments.append(signal[ts['start']:ts['end']])
        
        print(f"Tìm thấy {len(segments)} đoạn có giọng nói")
        return segments
    