import os
import stat
import uuid
import zipfile
import shutil
from flask import Flask, request, jsonify, send_from_directory, send_file, abort

app = Flask(__name__, static_folder='static')

UPLOAD_DIR = '/tmp/zipvault'
os.makedirs(UPLOAD_DIR, exist_ok=True)

sessions = {}


def extract_zip(zip_path, extract_dir):
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for member in zf.infolist():
            unix_attr = member.external_attr >> 16
            dest_path = os.path.normpath(os.path.join(extract_dir, member.filename))
            if not dest_path.startswith(os.path.normpath(extract_dir) + os.sep) and \
               dest_path != os.path.normpath(extract_dir):
                continue
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            if stat.S_ISLNK(unix_attr):
                link_target = zf.read(member.filename).decode()
                if os.path.lexists(dest_path):
                    os.remove(dest_path)
                os.symlink(link_target, dest_path)
            else:
                with zf.open(member) as src, open(dest_path, 'wb') as dst:
                    dst.write(src.read())


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400

    f = request.files['file']
    if not f.filename.lower().endswith('.zip'):
        return jsonify({'success': False, 'error': 'Only ZIP archives are supported'}), 400

    job_id = str(uuid.uuid4())
    extract_dir = os.path.join(UPLOAD_DIR, job_id)
    zip_path = extract_dir + '.zip'

    try:
        f.save(zip_path)
        os.makedirs(extract_dir)
        extract_zip(zip_path, extract_dir)

        files = []
        for root, dirs, filenames in os.walk(extract_dir):
            for name in filenames:
                full_path = os.path.join(root, name)
                disk_name = os.path.relpath(full_path, extract_dir)

                if os.path.islink(full_path):
                    display_name = os.path.basename(os.readlink(full_path))
                else:
                    display_name = disk_name

                try:
                    size = os.path.getsize(full_path)
                except OSError:
                    size = 0

                files.append({
                    'name': display_name,
                    'disk_name': disk_name,
                    'size': size,
                    'token': job_id,
                })

        sessions[job_id] = extract_dir
        return jsonify({'success': True, 'files': files, 'token': job_id})

    except zipfile.BadZipFile:
        shutil.rmtree(extract_dir, ignore_errors=True)
        return jsonify({'success': False, 'error': 'Invalid or corrupted ZIP file'}), 400
    except Exception:
        shutil.rmtree(extract_dir, ignore_errors=True)
        return jsonify({'success': False, 'error': 'Extraction failed'}), 500
    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)


@app.route('/download/<token>/<path:disk_name>')
def download(token, disk_name):
    if token not in sessions:
        abort(404)

    extract_dir = sessions[token]
    file_path = os.path.join(extract_dir, disk_name)
    norm_path = os.path.normpath(file_path)
    norm_dir = os.path.normpath(extract_dir)

    if not norm_path.startswith(norm_dir + os.sep):
        abort(403)

    if not os.path.exists(file_path):
        abort(404)

    if os.path.islink(file_path):
        download_name = os.path.basename(os.readlink(file_path))
    else:
        download_name = os.path.basename(disk_name)

    return send_file(file_path, as_attachment=True, download_name=download_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)