

#routes.py

from flask import Flask, render_template, request, send_file, jsonify, url_for, Blueprint, current_app
import os
from werkzeug.utils import secure_filename
from app.utils import process_video_to_srt, delete_file

main = Blueprint('main', __name__)

def allowed_file(filename):
    """بررسی پسوند مجاز فایل"""
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov', 'wmv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_project_root():
    """دریافت مسیر اصلی پروژه"""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

@main.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'file' not in request.files:
            return jsonify({"success": False, "message": "No file part"})
            
        video_file = request.files['file']
        if video_file.filename == '':
            return jsonify({"success": False, "message": "No selected file"})
            
        if not allowed_file(video_file.filename):
            return jsonify({"success": False, "message": "Invalid file type"})

        try:
            # دریافت مسیر اصلی پروژه
            project_root = get_project_root()
            
            # تنظیم مسیرها با استفاده از مسیر مطلق
            upload_folder = os.path.join(project_root, "static", "uploads")
            data_folder = os.path.join(project_root, "data")
            models_folder = os.path.join(project_root, "models")
            
            # اطمینان از وجود پوشه‌ها
            os.makedirs(upload_folder, exist_ok=True)
            os.makedirs(data_folder, exist_ok=True)
            os.makedirs(models_folder, exist_ok=True)
            
            # پاکسازی نام فایل
            filename = secure_filename(video_file.filename)
            
            # تنظیم مسیر کامل فایل‌ها
            video_path = os.path.join(upload_folder, filename)
            audio_path = os.path.join(data_folder, "extracted_audio.wav")
            srt_output_path = os.path.join(data_folder, "subtitle.srt")
            output_path = os.path.join(data_folder, "adjusted_subtitle.srt")
            
            # ذخیره فایل ویدیو
            video_file.save(video_path)
            
            # دریافت پارامترها
            target_language = request.form.get("dest_lang") if request.form.get("enableTranslation") else None
            delay = float(request.form.get("subtitleDelay", 0))
            speed = float(request.form.get("subtitleSpeed", 1))
            padding_start = float(request.form.get("PaddingStart", 0))
            padding_end = float(request.form.get("PaddingEnd", 2))
            model_name = request.form.get('model', 'base')
            
            # پردازش ویدیو و ایجاد زیرنویس
            process_video_to_srt(
                video_path, audio_path, srt_output_path, output_path,
                model_name, models_folder, target_language,
                delay, speed, padding_start, padding_end
            )
            
            # پاکسازی فایل‌های موقت
            delete_file(video_path)
            delete_file(audio_path)
            delete_file(srt_output_path)
            delete_file(upload_folder)
            
            if os.path.exists(output_path):
                print(f"File exists at: {output_path}")  # برای دیباگ
                download_url = url_for("main.download_file", filename="adjusted_subtitle.srt")
                return jsonify({"success": True, "download_url": download_url})
            else:
                print(f"File does not exist at: {output_path}")  # برای دیباگ
                return jsonify({"success": False, "message": "Subtitle generation failed"})
                
        except Exception as e:
            print(f"Error occurred: {str(e)}")  # برای دیباگ
            return jsonify({"success": False, "message": str(e)})

    return render_template('index.html')

@main.route("/download/<filename>")
def download_file(filename):
    try:
        # استفاده از مسیر مطلق
        project_root = get_project_root()
        file_path = os.path.join(project_root, "data", filename)
        
        print(f"Attempting to download file from: {file_path}")  # برای دیباگ
        
        if not os.path.exists(file_path):
            print(f"File not found at: {file_path}")  # برای دیباگ
            return "File not found", 404
            
        # ارسال فایل با تنظیمات مناسب
        response = send_file(
            file_path,
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=filename
        )
        
        # تنظیم هدرهای ضروری
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        response.headers["Content-Type"] = "application/octet-stream"
        
        return response
        
    except Exception as e:
        print(f"Error in download_file: {str(e)}")  # برای دیباگ
        return str(e), 500