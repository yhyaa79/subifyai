# routes.py

from flask import Flask, render_template, request, send_file, jsonify, url_for, Blueprint, current_app
import os
from werkzeug.utils import secure_filename
from app.utils import process_video_to_srt, delete_file

import json
from datetime import datetime, timedelta

main = Blueprint('main', __name__)

# ==================== اول این تابع را تعریف کنید ====================
def get_project_root():
    """دریافت مسیر اصلی پروژه"""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# =====================================================================

# حالا می‌توانیم از get_project_root استفاده کنیم
RATE_LIMIT_FILE = os.path.join(get_project_root(), "rate_limit.json")
RATE_LIMIT_SECONDS = 24 * 60 * 60  # 24 ساعت

def load_rate_limits():
    """بارگذاری داده‌های rate limit از فایل JSON"""
    if os.path.exists(RATE_LIMIT_FILE):
        try:
            with open(RATE_LIMIT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_rate_limits(data):
    """ذخیره داده‌های rate limit در فایل JSON"""
    with open(RATE_LIMIT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def is_rate_limited(ip):
    """بررسی اینکه آیا کاربر در ۲۴ ساعت گذشته درخواست داده یا نه"""
    limits = load_rate_limits()
    if ip in limits:
        last_time = datetime.fromisoformat(limits[ip])
        if datetime.now() < last_time + timedelta(seconds=RATE_LIMIT_SECONDS):
            return True, last_time + timedelta(seconds=RATE_LIMIT_SECONDS)
    return False, None

def update_rate_limit(ip):
    """به‌روزرسانی زمان آخرین درخواست کاربر"""
    limits = load_rate_limits()
    limits[ip] = datetime.now().isoformat()
    save_rate_limits(limits)

def allowed_file(filename):
    """بررسی پسوند مجاز فایل"""
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov', 'wmv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_ip = request.remote_addr

        # بررسی محدودیت
        limited, until = is_rate_limited(user_ip)
        if limited:
            remaining = int((until - datetime.now()).total_seconds())
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            return jsonify({
                "success": False,
                "message": f"شما قبلاً در ۲۴ ساعت گذشته درخواست داده‌اید. لطفاً {hours} ساعت و {minutes} دقیقه دیگر تلاش کنید."
            })

        if 'file' not in request.files:
            return jsonify({"success": False, "message": "No file part"})
            
        video_file = request.files['file']
        if video_file.filename == '':
            return jsonify({"success": False, "message": "No selected file"})
            
        if not allowed_file(video_file.filename):
            return jsonify({"success": False, "message": "Invalid file type"})

        try:
            project_root = get_project_root()
            
            upload_folder = os.path.join(project_root, "static", "uploads")
            data_folder = os.path.join(project_root, "data")
            models_folder = os.path.join(project_root, "models")
            
            os.makedirs(upload_folder, exist_ok=True)
            os.makedirs(data_folder, exist_ok=True)
            os.makedirs(models_folder, exist_ok=True)
            
            filename = secure_filename(video_file.filename)
            video_path = os.path.join(upload_folder, filename)
            audio_path = os.path.join(data_folder, "extracted_audio.wav")
            srt_output_path = os.path.join(data_folder, "subtitle.srt")
            output_path = os.path.join(data_folder, "adjusted_subtitle.srt")
            
            video_file.save(video_path)
            
            target_language = request.form.get("dest_lang") if request.form.get("enableTranslation") else None
            delay = float(request.form.get("subtitleDelay", 0))
            speed = float(request.form.get("subtitleSpeed", 1))
            padding_start = float(request.form.get("PaddingStart", 0))
            padding_end = float(request.form.get("PaddingEnd", 2))
            model_name = request.form.get('model', 'base')
            
            process_video_to_srt(
                video_path, audio_path, srt_output_path, output_path,
                model_name, models_folder, target_language,
                delay, speed, padding_start, padding_end
            )
            
            # پاکسازی فایل‌های موقت (حذف نکنید upload_folder را!)
            delete_file(video_path)
            delete_file(audio_path)
            delete_file(srt_output_path)

            if os.path.exists(output_path):
                # فقط در صورت موفقیت، محدودیت را اعمال کن
                update_rate_limit(user_ip)

                download_url = url_for("main.download_file", filename="adjusted_subtitle.srt")
                return jsonify({"success": True, "download_url": download_url})
            else:
                return jsonify({"success": False, "message": "Subtitle generation failed"})
                
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return jsonify({"success": False, "message": str(e)})

    return render_template('index.html')

@main.route("/download/<filename>")
def download_file(filename):
    try:
        project_root = get_project_root()
        file_path = os.path.join(project_root, "data", filename)
        
        if not os.path.exists(file_path):
            return "File not found", 404
            
        return send_file(
            file_path,
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"Error in download_file: {str(e)}")
        return str(e), 500