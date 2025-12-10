import os
from flask import Flask, request, jsonify, send_from_directory, abort
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, Document
from config import Config
from dotenv import load_dotenv

load_dotenv()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

db.init_app(app)
migrate = Migrate(app, db)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/documents/upload', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        import uuid
        uid = uuid.uuid4().hex[:8]
        final_filename = f"{uid}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], final_filename)
        file.save(filepath)
        filesize = os.path.getsize(filepath)

        doc = Document(filename=filename, filepath=filepath, filesize=filesize)
        db.session.add(doc)
        db.session.commit()

        return jsonify({
            "id": doc.id,
            "filename": doc.filename,
            "filesize": doc.filesize,
            "created_at": doc.created_at.isoformat()
        }), 201
    else:
        return jsonify({"error": "Invalid file type. Only PDFs allowed."}), 400

@app.route('/documents', methods=['GET'])
def list_documents():
    docs = Document.query.order_by(Document.created_at.desc()).all()
    data = []
    for d in docs:
        data.append({
            "id": d.id,
            "filename": d.filename,
            "filesize": d.filesize,
            "created_at": d.created_at.isoformat()
        })
    return jsonify(data), 200

@app.route('/documents/<int:doc_id>', methods=['GET'])
def download_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    directory = os.path.dirname(doc.filepath)
    filename = os.path.basename(doc.filepath)
    if not os.path.commonpath([directory, app.config['UPLOAD_FOLDER']]) == app.config['UPLOAD_FOLDER']:
        abort(403)
    return send_from_directory(directory, filename, as_attachment=True, download_name=doc.filename)

@app.route('/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    try:
        if os.path.exists(doc.filepath):
            os.remove(doc.filepath)
    except Exception as e:
        return jsonify({"error": "File delete failed", "details": str(e)}), 500
    db.session.delete(doc)
    db.session.commit()
    return jsonify({"message": "Document deleted"}), 200

if __name__ == '__main__':
    app.run(debug=True)
