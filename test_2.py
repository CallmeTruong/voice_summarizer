import os
import io
import torch
import librosa
import jiwer
import numpy as np
import soundfile as sf
from tqdm import tqdm
from datasets import load_from_disk, Audio
from transformers import WhisperProcessor
from torch.utils.data import Dataset, DataLoader
import torch.nn.functional as F

from voicever2 import MonsterWhisperCTC   # file train của bạn

# =====================================================
# CONFIG
# =====================================================

CHECKPOINT_DIR = "checkpoints_monster"
MODEL_FILE     = "epoch_10.pt"
DATA_DIR       = "vivos_local"

AUDIO_COL = "audio"
TEXT_COL  = "sentence"

SAMPLE_RATE = 16000
MAX_SEC = 30
MAX_SAMPLES = SAMPLE_RATE * MAX_SEC

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BATCH_SIZE = 16


# =====================================================
# DATASET
# =====================================================

class VivosLocalDataset(Dataset):

    def __init__(self, hf_split, processor):
        self.dataset = hf_split
        self.processor = processor

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):

        record = self.dataset[idx]

        audio_raw = record[AUDIO_COL]
        audio, sr = sf.read(io.BytesIO(audio_raw["bytes"]), dtype="float32")

        if sr != SAMPLE_RATE:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=SAMPLE_RATE)

        if len(audio) > MAX_SAMPLES:
            audio = audio[:MAX_SAMPLES]
        else:
            audio = np.pad(audio, (0, MAX_SAMPLES - len(audio)))

        input_features = self.processor(
            audio,
            sampling_rate=SAMPLE_RATE,
            return_tensors="pt"
        ).input_features.squeeze(0)

        return {
            "input_features": input_features,
            "text": record[TEXT_COL]
        }


class Collate:

    def __init__(self, processor):
        self.processor = processor

    def __call__(self, batch):

        feats = torch.stack([b["input_features"] for b in batch])

        return {
            "input_features": feats,
            "texts": [b["text"] for b in batch]
        }


# =====================================================
# CTC DECODE
# =====================================================

def ctc_decode(pred_ids, tokenizer):

    decoded = []

    blank = tokenizer.pad_token_id

    for seq in pred_ids:

        prev = None
        tokens = []

        for t in seq:

            if t != blank and t != prev:
                tokens.append(t)

            prev = t

        text = tokenizer.decode(tokens, skip_special_tokens=True)

        decoded.append(text)

    return decoded


# =====================================================
# MAIN
# =====================================================

def main():

    print("Loading processor...")

    processor = WhisperProcessor.from_pretrained(
        os.path.join(CHECKPOINT_DIR, "processor")
    )

    print("Loading dataset...")

    ds = load_from_disk(DATA_DIR).cast_column(
        AUDIO_COL,
        Audio(decode=False)
    )

    test_loader = DataLoader(
        VivosLocalDataset(ds["test"], processor),
        batch_size=BATCH_SIZE,
        shuffle=False,
        collate_fn=Collate(processor),
        num_workers=4
    )

    print("Building model...")

    model = MonsterWhisperCTC(
        "vinai/PhoWhisper-medium",
        len(processor.tokenizer)
    ).to(DEVICE)

    weight_path = os.path.join(CHECKPOINT_DIR, MODEL_FILE)

    model.load_state_dict(torch.load(weight_path, map_location=DEVICE))
    model.eval()

    print("\nStarting evaluation...\n")

    all_preds = []
    all_refs = []

    with torch.no_grad():

        for batch in tqdm(test_loader):

            feats = batch["input_features"].to(DEVICE)
            refs = batch["texts"]

            main_logits, _ = model(feats)

            pred_ids = torch.argmax(main_logits, dim=-1).cpu().numpy()

            preds = ctc_decode(pred_ids, processor.tokenizer)

            all_preds.extend(preds)
            all_refs.extend(refs)

    transform = jiwer.Compose([
        jiwer.ToLowerCase(),
        jiwer.RemovePunctuation(),
        jiwer.RemoveMultipleSpaces(),
        jiwer.Strip(),
        jiwer.RemoveEmptyStrings(),
        jiwer.ReduceToListOfListOfWords()
    ])

    wer = jiwer.wer(
        all_refs,
        all_preds,
        reference_transform=transform,
        hypothesis_transform=transform
    )

    print("\n==============================")
    print(f"WER: {wer*100:.2f}%")
    print("==============================\n")

    with open("evaluation_results.txt", "w", encoding="utf-8") as f:

        for r, p in zip(all_refs, all_preds):

            f.write(f"REF : {r}\n")
            f.write(f"PRED: {p}\n")
            f.write("-"*40 + "\n")

    print("Saved results → evaluation_results.txt")


if __name__ == "__main__":
    main()