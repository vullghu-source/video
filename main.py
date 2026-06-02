import os    
import uvicorn

if __name__ == "__main__":
    # Render က ပေးမယ့် Port နံပါတ်ကို ဖတ်ခိုင်းခြင်း၊ မရှိရင် 8000 ကို သုံးခြင်း
    port = int(os.environ.get("PORT", 8000))
    # host ကို 0.0.0.0 ထားပြီး server ကို run ခိုင်းခြင်း
    uvicorn.run(app, host="0.0.0.0", port=port)
 import requests    
import os  
os.environ["IMAGEIO_FFMPEG_EXE"] = "/opt/render/project/src/.venv/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux64-v4.2.2"  
  
from fastapi import FastAPI, HTTPException, BackgroundTasks    
from pydantic import BaseModel    
from moviepy.editor import VideoFileClip, AudioFileClip    
    
app = FastAPI()    
    
# Make.com ကနေ ပို့မယ့် Data ပုံစံကို သတ်မှတ်ခြင်း    
class VideoRequest(BaseModel):    
    video_url: str    
    audio_url: str    
    output_name: str = "final_tiktok.mp4"    
    
def download_file(url, save_path):    
    """ URL မှ ဖိုင်ကို ဒေါင်းလုဒ်ဆွဲသည့် Function """    
    response = requests.get(url, stream=True)    
    if response.status_code == 200:    
        with open(save_path, 'wb') as f:    
            for chunk in response.iter_content(chunk_size=1024):    
                if chunk:    
                    f.write(chunk)    
    else:    
        raise Exception(f"ဖိုင်ဒေါင်းလုဒ်ဆွဲ၍ မရပါ: {url}")    
    
def process_video(video_url, audio_url, output_name):    
    """ ဗီဒီယိုနှင့် အသံကို နောက်ကွယ်တွင် ပေါင်းစပ်ပေးသည့် Function """    
    video_tmp = "temp_video.mp4"    
    audio_tmp = "temp_audio.mp3"    
        
    try:    
        # ၁။ မူရင်းဖိုင်များကို ဒေါင်းလုဒ်ဆွဲခြင်း    
        download_file(video_url, video_tmp)    
        download_file(audio_url, audio_tmp)    
            
        # ၂။ MoviePy ဖြင့် ပေါင်းစပ်ခြင်း    
        video_clip = VideoFileClip(video_tmp)    
        audio_clip = AudioFileClip(audio_tmp)    
            
        final_duration = min(video_clip.duration, audio_clip.duration)    
        video_clip = video_clip.subclip(0, final_duration)    
        audio_clip = audio_clip.subclip(0, final_duration)    
            
        final_clip = video_clip.set_audio(audio_clip)    
        final_clip.write_videofile(    
            output_name,     
            codec="libx264",     
            audio_codec="aac",     
            fps=30,     
            logger=None    
        )    
            
        # ၃။ ပြီးသွားလျှင် ဖိုင်ဟောင်းများကို ဖျက်ခြင်း    
        video_clip.close()    
        audio_clip.close()    
        final_clip.close()    
        os.remove(video_tmp)    
        os.remove(audio_tmp)    
            
        print(f"✅ ဗီဒီယို ဖန်တီးမှု အောင်မြင်ပါသည်: {output_name}")    
            
        # 💡 NOTE: ဒီနေရာမှာ TikTok API သုံးပြီး Auto Post တင်တဲ့ ကုဒ်ထပ်ထည့်လို့ရပါတယ်    
            
    except Exception as e:    
        print(f"❌ Error: {str(e)}")    
    
@app.get("/")    
def home():    
    return {"status": "အလုပ်လုပ်နေပါသည်"}    
    
@app.post("/merge-video")    
async def merge_video_endpoint(request: VideoRequest, background_tasks: BackgroundTasks):    
    """ Make.com ကနေ လှမ်းခေါ်ရမယ့် Link (Endpoint) """    
    # ဗီဒီယို လုပ်ငန်းစဉ်က ကြာနိုင်တဲ့အတွက် Background မှာ အလုပ်လုပ်ခိုင်းထားခြင်း    
    background_tasks.add_task(    
        process_video,     
        request.video_url,     
        request.audio_url,     
        request.output_name    
    )    
    return {"message": "ဗီဒီယိုကို နောက်ကွယ်တွင် စတင်ပေါင်းစပ်နေပါပြီ။"}  
