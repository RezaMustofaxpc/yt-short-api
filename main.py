from fastapi import FastAPI
from pydantic import BaseModel
import yt_dlp
import moviepy.editor as mp
import whisper
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

    ydl_opts = {'outtmpl': input_file, 'format': 'bestvideo+bestaudio'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([data.youtube_url])

    clip = mp.VideoFileClip(input_file)
    start = random.uniform(0, max(1, clip.duration - 80))
    end = min(start + random.uniform(5, 80), clip.duration)
    short_clip = clip.subclip(start, end)

    model = whisper.load_model("base")
    result = model.transcribe(input_file)
    print("Caption:", result["text"])

    short_clip.write_videofile(output_file)

    return {"video_url": f"https://your-cdn.com/videos/{output_file}"}
