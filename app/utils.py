


#utils.py

from deep_translator import GoogleTranslator
from datetime import timedelta
import whisper
import re
import os
import subprocess
from threading import Lock, Thread
from queue import Queue

# ایجاد صف و قفل
task_queue = Queue(maxsize=3)  # صف با ظرفیت 3 کاربر همزمان
lock = Lock()


import os

directory_path = '/srv/subtitle_app/static/uploads'
if os.path.isdir(directory_path):
    # حذف دایرکتوری با استفاده از rmtree
    import shutil
    shutil.rmtree(directory_path)
elif os.path.exists(directory_path):
    # حذف فایل معمولی
    os.remove(directory_path)



def delete_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"File {file_path} deleted successfully.")
    except Exception as e:
        print(f"Error occurred while deleting {file_path}: {e}")



def worker():
    while True:
        args = task_queue.get()  # گرفتن کار از صف
        if args is None:
            break  # اگر صف خالی شد، متوقف می‌شود
        try:
            process_video_to_srt(*args)
        except Exception as e:
            print(f"Error occurred while processing video: {e}")
        finally:
            task_queue.task_done()  # اعلام اتمام کار

# راه‌اندازی 3 کارگر همزمان
threads = []
for _ in range(3):
    t = Thread(target=worker)
    t.daemon = True
    t.start()
    threads.append(t)

print("2")
def add_task_to_queue(*args):
    """افزودن وظیفه به صف، اگر پر است منتظر بماند."""
    print("Waiting for an available slot...")
    task_queue.put(args)  # وظیفه را به صف اضافه می‌کند
    print("Task added to the queue.")

def extract_audio_with_ffmpeg(video_path, audio_path):
    """
    استخراج صدای ویدیو با استفاده از ffmpeg.
    """
    try:
        command = [
            "ffmpeg",
            "-i", video_path,         # ورودی ویدیو
            "-vn",                    # حذف ترک ویدیویی
            "-acodec", "pcm_s16le",   # کدک صدای خروجی
            audio_path                # مسیر فایل خروجی
        ]
        subprocess.run(command, check=True)
        print(f"Audio extracted successfully to {audio_path}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error occurred while extracting audio: {e}")

def process_video_to_srt(video_path, audio_path, srt_output_path, output_path, model_name, model_save_path, target_language, delay, speed, padding_start, padding_end):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # استخراج صدا با ffmpeg
    extract_audio_with_ffmpeg(video_path, audio_path)

    # مدل Whisper
    model = whisper.load_model(model_name, download_root=model_save_path)
    result = model.transcribe(audio_path)

    # نوشتن زیرنویس
    with open(srt_output_path, "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(result['segments']):
            start = segment['start']
            end = segment['end']
            text = segment['text']
            if target_language:
                text = GoogleTranslator(source="auto", target=target_language).translate(text)

            srt_file.write(f"{i+1}\n{format_time(start)} --> {format_time(end)}\n{text}\n\n")

    # تنظیم زمان‌بندی زیرنویس
    adjust_srt_no_overlap(srt_output_path, output_path, delay, speed, padding_start, padding_end)


print("3")
def parse_srt_time(srt_time):
    hours, minutes, seconds = srt_time.split(":")
    seconds, milliseconds = seconds.split(",")
    return timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds), milliseconds=int(milliseconds))

def format_srt_time(time_delta):
    total_seconds = int(time_delta.total_seconds())
    milliseconds = int(time_delta.microseconds / 1000)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def adjust_srt_no_overlap(file_path, output_path, delay=0, speed=1.0, padding_start=0, padding_end=0):
    with open(file_path, "r", encoding="utf-8") as file:
        srt_content = file.read()

    pattern = re.compile(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})")
    timings = []
    adjusted_srt_content = srt_content.splitlines()

    for index, line in enumerate(adjusted_srt_content):
        match = pattern.match(line)
        if match:
            start_time = parse_srt_time(match.group(1))
            end_time = parse_srt_time(match.group(2))
            duration = end_time - start_time
            adjusted_duration = duration / speed
            start_time = start_time * (1 / speed) + timedelta(seconds=delay - padding_start)
            end_time = start_time + adjusted_duration + timedelta(seconds=padding_end)
            timings.append((index, start_time, end_time))

    for i in range(len(timings) - 1):
        _, start_time_next, _ = timings[i + 1]
        index_current, _, end_time_current = timings[i]
        if end_time_current > start_time_next:
            timings[i] = (index_current, timings[i][1], start_time_next - timedelta(milliseconds=1))

    for index, start_time, end_time in timings:
        adjusted_line = f"{format_srt_time(start_time)} --> {format_srt_time(end_time)}"
        adjusted_srt_content[index] = adjusted_line

    with open(output_path, "w", encoding="utf-8") as file:
        file.write("\n".join(adjusted_srt_content))
        
    print(f"Adjusted SRT with no overlaps saved as {output_path}")

def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{milliseconds:03}"

# توقف اجرای صف
def stop_workers():
    for _ in range(3):
        task_queue.put(None)
    for t in threads:
        t.join()
