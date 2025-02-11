# app/models/model_utils.py

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

def load_model():
    # Controleer of er een GPU beschikbaar is en stel het apparaat in
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    # Laad het Whisper Large v3 Turbo-model en de processor
    model_id = "openai/whisper-large-v3-turbo"
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)
    processor = AutoProcessor.from_pretrained(model_id)

    # Initialiseer de ASR-pipeline met het model en de processor
    asr_pipeline = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=torch_dtype,
        device=0 if torch.cuda.is_available() else -1,
    )
    return model, processor, asr_pipeline

def transcribe(audio_file_path, asr_pipeline):
    print("🎙️ Bezig met transcriberen van audio... Een moment geduld alstublieft.")
    result = asr_pipeline(audio_file_path)
    return result["text"]

def transcribe_with_timestamps(audio_file_path, asr_pipeline):
    print("🎙️ Bezig met transcriberen van audio met tijdstempels... Een moment geduld alstublieft.")
    result = asr_pipeline(audio_file_path, return_timestamps=True)
    return result