


#__init__.py

import os
from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # دریافت مسیر اصلی پروژه
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # تنظیم مسیرها با استفاده از مسیر مطلق
    app.config['UPLOAD_FOLDER'] = os.path.join(project_root, "static", "uploads")
    app.config['DATA_FOLDER'] = os.path.join(project_root, "data")
    app.config['MODEL_FOLDER'] = os.path.join(project_root, "models")
    app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # افزایش محدودیت به 500 مگابایت

    # ایجاد پوشه‌های مورد نیاز
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)
    os.makedirs(app.config['MODEL_FOLDER'], exist_ok=True)

    # ثبت مسیرها
    from app.routes import main
    app.register_blueprint(main)

    return app