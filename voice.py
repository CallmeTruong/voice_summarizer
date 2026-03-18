from datasets import load_from_disk

ds = load_from_disk("vivos_local/train")

print(ds)
print(ds[0])