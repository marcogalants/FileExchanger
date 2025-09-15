
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash, jsonify
import os
import shutil
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg','png','pdf', 'xls', 'xlsx'}
IDP_API_URL = 'https://idp-caller-2j1ful.5sc6y6-4.usa-e2.cloudhub.io/api/idp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            # If running on Windows and file is Excel, copy to desktop
            if os.name == 'nt' and filename.rsplit('.', 1)[1].lower() in ['xls', 'xlsx']:
                try:
                    desktop_path = r'C:\Users\Administrator\Desktop'
                    shutil.copy(save_path, os.path.join(desktop_path, filename))
                    flash('File successfully uploaded and sent to desktop')
                except Exception as e:
                    flash(f'File uploaded, but failed to send to desktop: {e}')
            else:
                flash('File successfully uploaded')
            return redirect(url_for('upload_file'))
        else:
            flash('Allowed file types are pdf, jpg, png, xls, xlsx')
            return redirect(request.url)
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)



# Extraction endpoint for jpg, png, pdf (POST = refresh, GET = view cached)
@app.route('/extract/<filename>', methods=['GET', 'POST'])
def extract_data(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in ['jpg', 'png', 'pdf']:
        return jsonify({'error': 'Extraction only supported for jpg, png, pdf files.'}), 400
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    json_path = file_path + '.json'
    if request.method == 'GET':
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as jf:
                data = json.load(jf)
            return jsonify(data)
        else:
            return jsonify({'error': 'No extraction data found. Please extract first.'}), 404
    # POST: refresh extraction
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found.'}), 404
    with open(file_path, 'rb') as f:
        if ext == 'jpg':
            mime = 'image/jpeg'
        elif ext == 'png':
            mime = 'image/png'
        elif ext == 'pdf':
            mime = 'application/pdf'
        else:
            mime = 'application/octet-stream'
        files = {'file': (filename, f, mime)}
        try:
            import requests
            headers = {'Accept': 'application/json', 'filename': filename}
            response = requests.post(IDP_API_URL, files=files, headers=headers)
            response.raise_for_status()
            data = response.json()
            # Save the full extraction result to .json file
            with open(json_path, 'w', encoding='utf-8') as jf:
                json.dump(data, jf, ensure_ascii=False, indent=2)
            # Only return the 'result' property if present
            if 'result' in data:
                return jsonify({'result': data['result']})
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            flash(f'{filename} deleted successfully.')
        except Exception as e:
            flash(f'Error deleting {filename}: {e}')
    else:
        flash(f'File {filename} not found.')
    return redirect(url_for('upload_file'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', ssl_context=('cert.pem', 'key.pem'))
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash, jsonify
import os
import shutil
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg','png','pdf', 'xls', 'xlsx'}
IDP_API_URL = 'https://idp-caller-2j1ful.5sc6y6-4.usa-e2.cloudhub.io/api/idp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            # If running on Windows and file is Excel, copy to desktop
            if os.name == 'nt' and filename.rsplit('.', 1)[1].lower() in ['xls', 'xlsx']:
                try:
                    desktop_path = r'C:\Users\Administrator\Desktop'
                    shutil.copy(save_path, os.path.join(desktop_path, filename))
                    flash('File successfully uploaded and sent to desktop')
                except Exception as e:
                    flash(f'File uploaded, but failed to send to desktop: {e}')
            else:
                flash('File successfully uploaded')
            return redirect(url_for('upload_file'))
        else:
            flash('Allowed file types are pdf, jpg, png, xls, xlsx')
            return redirect(request.url)
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)


# Extraction endpoint for jpg, png, pdf
@app.route('/extract/<filename>', methods=['POST'])
def extract_data(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in ['jpg', 'png', 'pdf']:
        return jsonify({'error': 'Extraction only supported for jpg, png, pdf files.'}), 400
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found.'}), 404
    with open(file_path, 'rb') as f:
        if ext == 'jpg':
            mime = 'image/jpeg'
        elif ext == 'png':
            mime = 'image/png'
        elif ext == 'pdf':
            mime = 'application/pdf'
        else:
            mime = 'application/octet-stream'
        files = {'file': (filename, f, mime)}
        try:
            import requests
            headers = {'Accept': 'application/json', 'filename': filename}
            response = requests.post(IDP_API_URL, files=files, headers=headers)
            response.raise_for_status()
            data = response.json()
            # Only return the 'result' property if present
            if 'result' in data:
                return jsonify({'result': data['result']})
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', ssl_context=('cert.pem', 'key.pem'))
