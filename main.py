from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string
from werkzeug.utils import secure_filename
import os
import random

os.system('cls' if os.name == 'nt' else 'clear')

# Ask for base path on startup
BASE_PATH = input("Enter the base folder path: ").strip()
if not os.path.isdir(BASE_PATH):
    print("Invalid directory. Exiting.")
    exit(1)

app = Flask(__name__)

HTML_TEMPLATE = '''
<!doctype html>
<html>
<head>
    <title>e622</title>
    <link rel="icon" href="{{ url_for('static', filename='favicon.png') }}" type="image/png">
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <a href="/"><img src="/static/images/e622.png" height="100"></a>
    <center>
    <h2>e622</h2>
    <ul>
        {% if current_path %}
            <li><a href="{{ url_for('browse', path=parent_path) }}">[..]</a></li>
        {% endif %}
        {% for name in dirs %}
            <li><a href="{{ url_for('browse', path=os.path.join(current_path, name)) }}">{{ name }}</a></li>
        {% endfor %}
    </ul>

    <div class="image-container">
        {% set has_media = true %}
        {% for name in files %}
            {% set file_url = url_for('view_file', path=os.path.join(current_path, name)) %}
            {% if name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')) %}
                <a href="{{ file_url }}"><img src="{{ file_url }}" alt="{{ name }}"></a>

            {% elif name.lower().endswith(('.mp4', '.webm', '.ogg', '.mov')) %}
                    <video 
                        src="{{ file_url }}" 
                        class="small-video autoplay-video" 
                        preload="metadata"
                        onclick="this.muted = false; this.controls = true; this.play();">
                    </video>
            {% endif %}
        {% endfor %}

        </div>
        <h2>Upload File</h2>
        <form action="{{ url_for('upload', path=current_path) }}" method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <input type="submit" value="Upload">
        </form>
    </div>
</body>
</center>
</html>
'''

HOME_TEMPLATE = '''
<!doctype html>
<html>
<head>
    <title>e622</title>
    <link rel="icon" href="{{ url_for('static', filename='favicon.png') }}" type="image/png">
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <center>
    <img src="/static/images/e622.png" height="100">
    <h1>e622</h1>
    {# MAKE THIS LINE {{ randomnumber }} on scr="/static/images/{{ randomnumber }}.png #}
    <img src="/static/images/{{ randomnumber }}.png" height="200"><br>
    <a href="/posts">Enter our site</a>
    </center>
</body>
</html>
'''

# Secure path joining
def safe_join(base, *paths):
    path = os.path.abspath(os.path.join(base, *paths))
    if not path.startswith(os.path.abspath(base)):
        raise ValueError("Access denied.")
    return path

@app.route('/')
def home():
    randomnumber = random.randint(1, 10)
    abs_path = BASE_PATH
    items = os.listdir(abs_path)
    dirs = sorted([item for item in items if os.path.isdir(os.path.join(abs_path, item))])
    files = sorted([item for item in items if os.path.isfile(os.path.join(abs_path, item))])
    parent_path = ''

    # every file needs to be png
    
    return render_template_string(
        HOME_TEMPLATE,
        randomnumber=randomnumber,
        current_path='',
        parent_path=parent_path,
        dirs=dirs,
        files=files,
        os=os
    )



@app.route('/posts', defaults={'path': ''})
@app.route('/posts/<path:path>')
def browse(path):
    abs_path = safe_join(BASE_PATH, path)
    if not os.path.isdir(abs_path):
        return "Invalid path.", 404

    items = os.listdir(abs_path)
    dirs = sorted([item for item in items if os.path.isdir(os.path.join(abs_path, item))])
    files = sorted([item for item in items if os.path.isfile(os.path.join(abs_path, item))])
    parent_path = os.path.dirname(path)

    return render_template_string(
        HTML_TEMPLATE,
        current_path=path,
        parent_path=parent_path,
        dirs=dirs,
        files=files,
        os=os 
    )

@app.route('/upload/<path:path>', methods=['POST'])
def upload(path):
    if 'file' not in request.files:
        return redirect(request.referrer)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.referrer)
    filename = secure_filename(file.filename)
    save_path = safe_join(BASE_PATH, path, filename)
    file.save(save_path)
    return redirect(url_for('browse', path=path))

@app.route('/posts/view/<path:path>')
def download_file(path):
    file_path = safe_join(BASE_PATH, path)
    directory = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    return send_from_directory(directory, filename, as_attachment=False)

@app.route('/posts/view/<path:path>')
def view_file(path):
    file_path = safe_join(BASE_PATH, path)
    if not os.path.isfile(file_path):
        return "File not found", 404
    return send_from_directory(os.path.dirname(file_path), os.path.basename(file_path))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=80)