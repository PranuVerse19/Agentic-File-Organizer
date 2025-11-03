from flask import Flask, render_template, request, send_from_directory
import os
import shutil

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ORG_FOLDER'] = 'organized'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['ORG_FOLDER'], exist_ok=True)

def classify_file(filename):
    ext = filename.lower().split('.')[-1]
    if ext in ['jpg', 'jpeg', 'png', 'gif']:
        return 'Images', f"I detected the extension '.{ext}', which is an image format."
    elif ext in ['pdf', 'doc', 'docx', 'txt']:
        return 'Documents', f"The file extension '.{ext}' indicates it's a document file."
    elif ext in ['mp4', 'mkv', 'avi']:
        return 'Videos', f"The '.{ext}' format is typically a video file."
    elif ext in ['mp3', 'wav']:
        return 'Audio', f"The '.{ext}' extension represents an audio file."
    elif ext in ['zip', 'rar']:
        return 'Archives', f"'.{ext}' files are compressed archives."
    else:
        return 'Others', f"The extension '.{ext}' is unknown, so I categorized it as 'Others'."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    files = request.files.getlist('files')
    agent_report = []

    for file in files:
        if file.filename != '':
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(upload_path)
            category, reason = classify_file(file.filename)
            target_dir = os.path.join(app.config['ORG_FOLDER'], category)
            os.makedirs(target_dir, exist_ok=True)
            shutil.move(upload_path, os.path.join(target_dir, file.filename))
            agent_report.append({
                'filename': file.filename,
                'category': category,
                'reason': reason
            })
    return render_template('success.html', report=agent_report)

# 🆕 Route to display organized files
@app.route('/organized')
def view_organized():
    organized_data = {}
    base_dir = app.config['ORG_FOLDER']

    for category in os.listdir(base_dir):
        category_path = os.path.join(base_dir, category)
        if os.path.isdir(category_path):
            organized_data[category] = os.listdir(category_path)

    return render_template('organized.html', data=organized_data)

# 🆕 Route to serve the actual files (for viewing or download)
@app.route('/organized/<category>/<filename>')
def serve_file(category, filename):
    directory = os.path.join(app.config['ORG_FOLDER'], category)
    return send_from_directory(directory, filename)

if __name__ == '__main__':
    app.run(debug=True)
