"""Download Voicebox TTS model weights directly to HuggingFace cache."""
import os, sys
from huggingface_hub import snapshot_download, hf_hub_download

CACHE_DIR = os.path.expanduser(r"C:\Users\Darks\.cache\huggingface\hub")

MODELS = {
    "kokoro":      ("hexgrad/Kokoro-82M",        "~350 MB"),
    "chatterbox":  ("ResembleAI/chatterbox",      "~3.2 GB"),
    "luxtts":      ("YatharthS/LuxTTS",           "~300 MB"),
}

def download(name, repo_id, size):
    print(f"\n{'='*50}")
    print(f"Downloading: {name}  ({repo_id})  {size}")
    print(f"Cache: {CACHE_DIR}")
    print("="*50)
    try:
        path = snapshot_download(
            repo_id=repo_id,
            cache_dir=CACHE_DIR,
            local_dir=None,
            ignore_patterns=["*.msgpack", "flax_model*", "tf_model*", "*.ot"],
        )
        print(f"SUCCESS: {path}")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "kokoro"
    if target not in MODELS:
        print(f"Available: {list(MODELS.keys())}")
        sys.exit(1)
    repo, size = MODELS[target]
    download(target, repo, size)
    print("\nDone. Restart Voicebox backend, then try loading the model in the app.")
