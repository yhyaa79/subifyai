


#run.py

import os
from app import create_app

# تغییر مسیر کاری به مسیر پروژه
os.chdir(os.path.dirname(os.path.abspath(__file__)))

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)


"""if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8090)
"""


"""

/project_root
  /app
    __init__.py
    routes.py
  /static
  /images
  /templates
    index.html
  requirements.txt
  run.py

"""