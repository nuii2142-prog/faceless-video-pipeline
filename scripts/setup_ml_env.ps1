# Setup ML environment (ml-env) with chatterbox TTS
# Run once from project root after: uv venv ml-env --python 3.12

$mlPy = "$PSScriptRoot\..\ml-env\Scripts\python.exe"

Write-Host "Step 1: PyTorch CUDA 12.8"
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128 --python "$mlPy"

Write-Host "Step 2: chatterbox-tts (no-deps, we pin manually)"
uv pip install chatterbox-tts --no-deps --python "$mlPy"

Write-Host "Step 3: chatterbox exact-version deps"
uv pip install `
    "resemble-perth>=1.0.0" `
    "transformers==5.2.0" `
    "diffusers==0.29.0" `
    "safetensors==0.5.3" `
    "librosa==0.11.0" `
    "conformer==0.3.2" `
    "pykakasi==2.3.0" `
    pyloudnorm `
    --python "$mlPy"

Write-Host "Step 4: other deps"
uv pip install `
    s3tokenizer `
    huggingface_hub `
    einops `
    omegaconf `
    scipy `
    tqdm `
    numpy `
    soundfile `
    --python "$mlPy"

Write-Host "Verify"
& "$mlPy" -c "import torch; print('CUDA:', torch.cuda.is_available()); from chatterbox.tts import ChatterboxTTS; print('chatterbox: OK')"
