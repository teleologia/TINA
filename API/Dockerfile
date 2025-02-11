# Use the official NVIDIA PyTorch image with CUDA support
FROM nvidia/cuda:12.6.0-cudnn-runtime-ubuntu24.04

# Install Python 3, venv, ffmpeg, and other dependencies
RUN apt-get update && apt-get install -y python3 python3-venv ffmpeg libsndfile1

# Set the working directory
WORKDIR /app

# Create a virtual environment
RUN python3 -m venv venv

# Activate the virtual environment and install Python dependencies
COPY requirements.txt .
RUN . venv/bin/activate && pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
RUN . venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

# Copy the application code
COPY . .

# Expose port
EXPOSE 8000

# Set environment variables for CUDA support
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Run the app within the virtual environment
CMD ["sh", "-c", ". venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
