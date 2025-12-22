import os

def check_project_structure():
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # لیست مسیرهای مورد نیاز
    required_paths = [
        os.path.join(project_root, 'app'),
        os.path.join(project_root, 'static'),
        os.path.join(project_root, 'static', 'uploads'),
        os.path.join(project_root, 'templates'),
        os.path.join(project_root, 'data'),
        os.path.join(project_root, 'models'),
    ]
    
    # بررسی وجود فایل index.html
    template_file = os.path.join(project_root, 'templates', 'index.html')
    
    print("Checking project structure...")
    print(f"Project root: {project_root}")
    
    for path in required_paths:
        if os.path.exists(path):
            print(f"✓ Found: {path}")
        else:
            print(f"✗ Missing: {path}")
            os.makedirs(path, exist_ok=True)
            print(f"  Created directory: {path}")
    
    if os.path.exists(template_file):
        print(f"✓ Found template: {template_file}")
    else:
        print(f"✗ Missing template: {template_file}")

if __name__ == "__main__":
    check_project_structure()
