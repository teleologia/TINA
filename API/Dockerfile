# Gebruik de officiële NVIDIA PyTorch-afbeelding met CUDA-ondersteuning
FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04

# Installeer Python 3, venv, ffmpeg en andere dependencies
RUN apt-get update && apt-get install -y python3 python3-venv ffmpeg libsndfile1

# Stel de werkdirectory in
WORKDIR /app

# Maak een virtuele omgeving
RUN python3 -m venv venv

# Activeer de virtuele omgeving en installeer Python-dependencies
COPY requirements.txt .
RUN . venv/bin/activate && pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
RUN . venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

# Kopieer de applicatiecode
COPY . .

# Exposeer poort
EXPOSE 8000

# Stel omgevingsvariabelen in voor CUDA-ondersteuning
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Start de app binnen de virtuele omgeving
CMD ["sh", "-c", ". venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000"]