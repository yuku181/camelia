import os
import uuid
import shutil
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tempfile
import subprocess
import time

app = Flask(__name__, static_folder=None)
CORS(app)  # Enable CORS for all routes

# Configuration
WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))
CAMELIA_TEMP = os.path.join(WORKSPACE_ROOT, "camelia-decensor", "temp")
CAMELIA_OUTPUT = os.path.join(WORKSPACE_ROOT, "camelia-decensor", "output")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    """Check if the filename has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_directory(directory):
    """Ensure that a directory exists."""
    os.makedirs(directory, exist_ok=True)

def clean_temp_dirs():
    """Clean temporary directories while preserving the directory structure."""
    # Clean images directory
    images_dir = os.path.join(CAMELIA_TEMP, "images")
    if os.path.exists(images_dir):
        for root, dirs, files in os.walk(images_dir):
            for file in files:
                try:
                    os.unlink(os.path.join(root, file))
                except Exception as e:
                    app.logger.error(f"Error removing file {os.path.join(root, file)}: {e}")
    
    # Clean masks directory
    masks_dir = os.path.join(CAMELIA_TEMP, "masks")
    if os.path.exists(masks_dir):
        for root, dirs, files in os.walk(masks_dir):
            for file in files:
                try:
                    os.unlink(os.path.join(root, file))
                except Exception as e:
                    app.logger.error(f"Error removing file {os.path.join(root, file)}: {e}")
    
    # Clean any other files directly in the temp directory
    for item in os.listdir(CAMELIA_TEMP):
        item_path = os.path.join(CAMELIA_TEMP, item)
        if os.path.isfile(item_path):
            try:
                os.unlink(item_path)
            except Exception as e:
                app.logger.error(f"Error removing file {item_path}: {e}")
        elif os.path.isdir(item_path) and item not in ["images", "masks"]:
            try:
                shutil.rmtree(item_path)
            except Exception as e:
                app.logger.error(f"Error removing directory {item_path}: {e}")

def process_images(image_paths, model_type):
    """Process images using the existing Camelia functionality."""
    # Create session ID for this batch
    session_id = str(uuid.uuid4())
    
    # Create temporary directories
    images_dir = os.path.join(CAMELIA_TEMP, "images")
    masks_dir = os.path.join(CAMELIA_TEMP, "masks")
    output_dir = os.path.join(CAMELIA_OUTPUT, session_id)
    
    ensure_directory(images_dir)
    ensure_directory(masks_dir)
    ensure_directory(output_dir)
    
    # Clean temp directories before processing
    clean_temp_dirs()
    
    # Copy images to the input directory with the selected model type
    model_dir = os.path.join(WORKSPACE_ROOT, "camelia-decensor", "input", model_type)
    ensure_directory(model_dir)
    
    # Clean previous files
    for file in os.listdir(model_dir):
        file_path = os.path.join(model_dir, file)
        if os.path.isfile(file_path) and file != ".keep":
            os.unlink(file_path)
    
    # Copy uploaded images to the model directory
    for image_path in image_paths:
        filename = os.path.basename(image_path)
        dst_path = os.path.join(model_dir, filename)
        shutil.copyfile(image_path, dst_path)
    
    # Run the processing pipeline
    cmd = [
        "python", 
        os.path.join(WORKSPACE_ROOT, "main.py"),
        "--model_type", model_type
    ]
    
    try:
        subprocess.run(cmd, check=True)
        
        # Collect results
        results = []
        
        # Move output files to session directory
        for file in os.listdir(CAMELIA_OUTPUT):
            if os.path.isfile(os.path.join(CAMELIA_OUTPUT, file)) and file.endswith(tuple(ALLOWED_EXTENSIONS)):
                src_path = os.path.join(CAMELIA_OUTPUT, file)
                dst_path = os.path.join(output_dir, file)
                shutil.move(src_path, dst_path)
                results.append({
                    "filename": file,
                    "processed_path": dst_path
                })
        
        return session_id, results
        
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Error in processing pipeline: {e}")
        return None, []

@app.route('/api/process', methods=['POST'])
def process():
    """API endpoint to process images."""
    if 'files' not in request.files:
        return jsonify({"error": "No files provided"}), 400
    
    files = request.files.getlist('files')
    
    if not files or files[0].filename == '':
        return jsonify({"error": "No selected files"}), 400
    
    # Get model type from form data
    model_type = request.form.get('model_type', 'transparent_black')
    if model_type not in ['black_bars', 'white_bars', 'transparent_black']:
        return jsonify({"error": "Invalid model type"}), 400
    
    # Save uploaded files to temporary location
    temp_dir = tempfile.mkdtemp()
    saved_paths = []
    
    try:
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(temp_dir, filename)
                file.save(filepath)
                saved_paths.append(filepath)
        
        if not saved_paths:
            return jsonify({"error": "No valid image files provided"}), 400
        
        # Process the images
        session_id, results = process_images(saved_paths, model_type)
        
        if not session_id or not results:
            return jsonify({"error": "Processing failed"}), 500
        
        # Return results
        return jsonify({
            "success": True,
            "session_id": session_id,
            "results": [{"filename": r["filename"]} for r in results]
        })
        
    except Exception as e:
        app.logger.error(f"Error processing images: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)

@app.route('/api/results/<session_id>/<filename>', methods=['GET'])
def get_result(session_id, filename):
    """API endpoint to get a processed image."""
    # Security check to prevent directory traversal
    if '..' in session_id or '..' in filename:
        return jsonify({"error": "Invalid path"}), 400
    
    filepath = os.path.join(CAMELIA_OUTPUT, session_id, secure_filename(filename))
    
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    
    return send_file(filepath)

@app.route('/api/original/<filename>', methods=['GET'])
def get_original(filename):
    """API endpoint to get the original image (for comparison)."""
    # Security check to prevent directory traversal
    if '..' in filename:
        return jsonify({"error": "Invalid path"}), 400
    
    # Get from temp/images directory
    filepath = os.path.join(CAMELIA_TEMP, "images", secure_filename(filename))
    
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    
    return send_file(filepath)

if __name__ == '__main__':
    # Ensure the required directories exist
    ensure_directory(CAMELIA_TEMP)
    ensure_directory(os.path.join(CAMELIA_TEMP, "images"))
    ensure_directory(os.path.join(CAMELIA_TEMP, "masks"))
    ensure_directory(CAMELIA_OUTPUT)
    
    # Start the server
    app.run(debug=True, host='0.0.0.0', port=5000)