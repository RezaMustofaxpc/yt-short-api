from fastapi import FastAPI
from pydantic import BaseModel
import yt_dlp
import moviepy.editor as mp
from faster_whisper import WhisperModel
import uuid
import os
import random


app = FastAPI()

class VideoInput(BaseModel):
    youtube_url: str

@app.post("/api/generate")
def generate_short(data: VideoInput):
    uid = str(uuid.uuid4())
    input_file = f"{uid}.mp4"
    output_file = f"short_{uid}.mp4"

    ydl_opts = {
        'outtmpl': input_file,
        'format': 'bestvideo+bestaudio',
        'cookiefile': 'youtube_cookies.txt',
        'quiet': False,
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([data.youtube_url])

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Download failed. File '{input_file}' not found.")

    clip = mp.VideoFileClip(input_file)
    start = random.uniform(0, max(1, clip.duration - 80))
    end = min(start + random.uniform(5, 80), clip.duration)
    short_clip = clip.subclip(start, end)

    model = WhisperModel("base")
    segments, _ = model.transcribe(input_file)
    caption_text = " ".join([seg.text for seg in segments])
    print("Caption:", caption_text)

    short_clip.write_videofile(output_file)

    return {"message": "Video processed successfully!", "output_file": output_file}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
