from fastapi import FastAPI, UploadFile, File, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import librosa
import httpx
import tempfile
import wave
import asyncio

import sys
sys.path.append("C:/Users/repakaha/Desktop/ASR Project Group/EnglishASR/ASR-Wav2vec-Finetune-main")

from inference import Inferencer

#from pydub import AudioSegment
#import mimetypes


import torch

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Replace "*" with ["http://localhost:8000"] for stricter security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize model
device = "cuda:0" if torch.cuda.is_available() else "cpu"
huggingface_folder = ("Model_0.114\Model_0.114") # Update as needed
model_path = None # Or provide your .tar file path

inferencer = Inferencer(device=device, huggingface_folder=huggingface_folder, model_path=model_path)

# Folder to store uploaded files
UPLOAD_DIR = os.path.join(os.getcwd(), "uploaded_audio")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/infer-uploaded-audio/")
async def infer_uploaded_audio(file: UploadFile = File(...)):
    try:
        # Save uploaded file to project folder
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    
    
        # print(f"Saved file: {file_path}")
        # print(f"Guessed MIME type: {mimetypes.guess_type(file_path)}")


        # # Convert to proper WAV format
        # wav_path = os.path.splitext(file_path)[0] + "_converted.wav"
        # audio = AudioSegment.from_file(file_path)
        # audio = audio.set_frame_rate(16000).set_channels(1)
        # audio.export(wav_path, format="wav")

        # Load and transcribe
        wav, _ = librosa.load(file_path, sr=16000)
        transcript = inferencer.transcribe(wav)
        print(transcript)
        return {"filename": file.filename, "transcription": transcript}

    except Exception as e: 
        # import traceback
        # traceback.print_exc()  # Add this to print full error in terminal
        return {"error": str(e)}

INFERENCE_URL = "http://127.0.0.1:8000/infer-uploaded-audio/"

@app.websocket("/ws/asr")
async def websocket_asr(websocket: WebSocket):
    await websocket.accept()
    audio_buffer = bytearray()

    try:
        while True:
            data = await websocket.receive_bytes()
            audio_buffer.extend(data)

            # Optional: stream in chunks or wait for a trigger
            if len(audio_buffer) > 32000:  # ~1 second of 16kHz 16-bit mono audio
                # Save to temp .wav file
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
                    with wave.open(tmpfile, 'wb') as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)  # 16-bit
                        wf.setframerate(16000)
                        wf.writeframes(audio_buffer)

                    tmpfile_path = tmpfile.name

                # Send to inference endpoint
                async with httpx.AsyncClient() as client:
                    with open(tmpfile_path, "rb") as f:
                        files = {"file": ("audio.wav", f, "audio/wav")}
                        response = await client.post(INFERENCE_URL, files=files)

                if response.status_code == 200:
                    await websocket.send_text(response.text.strip())
                else:
                    await websocket.send_text(f"Error: {response.status_code}")

                audio_buffer.clear()

    except Exception as e:
        await websocket.send_text(f"Exception: {str(e)}")
        await websocket.close()

