from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import uvicorn

# Voor transcription_api-sleutelbescherming
from fastapi.security.api_key import APIKeyHeader, APIKey
from starlette.status import HTTP_403_FORBIDDEN

from app.helpers.audio_utils import convert_to_supported_format, split_audio_file
from app.models.model_utils import load_model, transcribe, transcribe_with_timestamps
import os

# Laad het model bij het starten van de app
model, processor, asr_pipeline = load_model()

app = FastAPI()

# Vervang 'JOUW_VEILIGE_API_SLEUTEL' door je eigen transcription_api-sleutel
API_KEY = "JOUW_VEILIGE_API_SLEUTEL"
API_KEY_NAME = "access_token"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Depends(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Kon transcription_api-sleutel niet valideren"
        )

# Endpoint voor normale transcriptie
@app.post("/transcribe")
async def transcribe_audio_endpoint(
    file: UploadFile = File(...), api_key: APIKey = Depends(get_api_key)
):
    """Transcribeert het geüploade audiobestand en retourneert de tekst."""
    # Sla het geüploade bestand tijdelijk op
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await file.read())

    # Converteer naar ondersteund formaat
    converted_file_path = convert_to_supported_format(temp_file_path)
    if not converted_file_path:
        os.remove(temp_file_path)
        raise HTTPException(status_code=400, detail="Niet-ondersteund audioformaat.")

    # Transcribeer het bestand
    transcription = transcribe(converted_file_path, asr_pipeline)

    # Verwijder tijdelijke bestanden
    os.remove(temp_file_path)
    if converted_file_path != temp_file_path:
        os.remove(converted_file_path)

    return JSONResponse({"transcription": transcription})

# Endpoint voor transcriptie met timestamps
@app.post("/transcribe_timestamps")
async def transcribe_with_timestamps_endpoint(
    file: UploadFile = File(...), api_key: APIKey = Depends(get_api_key)
):
    """Transcribeert het geüploade audiobestand en retourneert tekst met tijdstempels."""
    # Sla het geüploade bestand tijdelijk op
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await file.read())

    # Converteer naar ondersteund formaat
    converted_file_path = convert_to_supported_format(temp_file_path)
    if not converted_file_path:
        os.remove(temp_file_path)
        raise HTTPException(status_code=400, detail="Niet-ondersteund audioformaat.")

    # Splits de audio als deze langer is dan 5 minuten
    segments = split_audio_file(converted_file_path, max_segment_length=5 * 60)  # 5 minuten

    transcription_results = []
    for segment_path in segments:
        # Transcribeer het segment met tijdstempels
        transcription = transcribe_with_timestamps(segment_path, asr_pipeline)
        transcription_results.append(transcription)
        # Verwijder segmentbestand indien dit niet het originele bestand is
        if segment_path != converted_file_path:
            os.remove(segment_path)  # Verwijder segmentbestand

    # Verwijder tijdelijke bestanden en directories
    os.remove(temp_file_path)
    if os.path.exists(converted_file_path):
        os.remove(converted_file_path)
    segments_dir = os.path.join(os.path.dirname(converted_file_path), "segments")
    if os.path.exists(segments_dir):
        os.rmdir(segments_dir)

    return JSONResponse({"transcriptions": transcription_results})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)