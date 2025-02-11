# app/helpers/audio_utils.py

import os
from pydub import AudioSegment
import subprocess

def convert_to_supported_format(audio_file_path):
    """
    Converts the given audio file to a supported format (MP3, WAV, or FLAC) if it's not already in one.
    The converted file will be saved in the same directory as the original.
    """
    supported_formats = ('.mp3', '.wav', '.flac')
    file_ext = os.path.splitext(audio_file_path)[1].lower()

    if file_ext in supported_formats:
        print(f"✅ The file '{audio_file_path}' is already in a supported format.")
        return audio_file_path

    # Define the new file path with .mp3 extension
    new_file_path = os.path.splitext(audio_file_path)[0] + '.mp3'

    try:
        # Load the audio file
        print(f"🔄 Converting '{audio_file_path}' to MP3 format...")
        audio = AudioSegment.from_file(audio_file_path)
        # Export as MP3
        audio.export(new_file_path, format='mp3')
        print(f"✅ Conversion successful! New file: '{new_file_path}'")
        return new_file_path
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        return None

def get_audio_duration(audio_file_path):
    try:
        audio = AudioSegment.from_file(audio_file_path)
        duration = len(audio) / 1000.0  # Duration in seconds
        return duration
    except Exception as e:
        print(f"❌ Error getting duration: {e}")
        return 0

def split_audio_file(audio_file_path, max_segment_length):
    """
    Splits the audio file into segments of maximum length specified.
    Returns a list of file paths to the segments.
    """
    duration = get_audio_duration(audio_file_path)
    if duration <= max_segment_length:
        # No need to split
        return [audio_file_path]

    print(f"🔄 Splitting '{audio_file_path}' into segments...")
    segments_dir = os.path.join(os.path.dirname(audio_file_path), "segments")
    os.makedirs(segments_dir, exist_ok=True)

    segment_paths = []
    try:
        # Use ffmpeg to split the audio into segments
        command = [
            "ffmpeg",
            "-i", audio_file_path,
            "-f", "segment",
            "-segment_time", str(max_segment_length),
            "-c", "copy",
            os.path.join(segments_dir, "segment_%03d" + os.path.splitext(audio_file_path)[1])
        ]
        subprocess.check_call(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        # Get list of segment files
        segment_files = sorted(os.listdir(segments_dir))
        segment_paths = [os.path.join(segments_dir, f) for f in segment_files if f.startswith("segment_")]

        print(f"✅ Splitting successful! Created {len(segment_paths)} segments.")
        return segment_paths
    except Exception as e:
        print(f"❌ Error during splitting: {e}")
        return []