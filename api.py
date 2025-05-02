import os
import uuid
import shutil
import queue
import threading
from flask import Flask, request, jsonify, send_file, Response, stream_with_context
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tempfile
import subprocess

app = Flask(__name__, static_folder=None)
CORS(app)  # Enable CORS for all routes

WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))
CAMELIA_TEMP = os.path.join(WORKSPACE_ROOT, "camelia-decensor", "temp")
CAMELIA_OUTPUT = os.path.join(WORKSPACE_ROOT, "camelia-decensor", "output")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

# Global dictionary to store process logs
process_logs = {}
process_status = {}

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

def process_images(image_paths, model_type, session_id):
    """Process images using the existing Camelia functionality and capture logs."""
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
        process_logs[session_id].put(f"Prepared {filename} to input directory")
    
    # Run the processing pipeline
    cmd = [
        "python", 
        os.path.join(WORKSPACE_ROOT, "main.py"),
        "--model_type", model_type
    ]
    
    try:
        process_logs[session_id].put(f"Starting image processing with {model_type}")
        
        # Use Popen to capture output in real-time
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Read output line by line
        for line in iter(process.stdout.readline, ''):
            process_logs[session_id].put(line.strip())
        
        process.stdout.close()
        return_code = process.wait()
        
        if return_code != 0:
            process_logs[session_id].put(f"Process exited with error code {return_code}")
            process_status[session_id] = "error"
            return None, []
        
        # Collect results
        results = []
        
        process_logs[session_id].put("Processing completed. Collecting results...")
        
        # Move output files to session directory
        for file in os.listdir(CAMELIA_OUTPUT):
            file_path = os.path.join(CAMELIA_OUTPUT, file)
            if os.path.isfile(file_path) and file.endswith(tuple(ALLOWED_EXTENSIONS)):
                # Move the file to the session directory
                dst_path = os.path.join(output_dir, file)
                shutil.move(file_path, dst_path)
                results.append({
                    "filename": file,
                    "processed_path": dst_path
                })
                process_logs[session_id].put(f"Saved processed file: {file}")
        
        # Check the temp/images directory
        if not results:
            process_logs[session_id].put("No results found in output directory. Checking temporary directories...")
            # Check if there are any processed images in the temp dir
            temp_images_dir = os.path.join(CAMELIA_TEMP, "images")
            if os.path.exists(temp_images_dir):
                for file in os.listdir(temp_images_dir):
                    if file.endswith(tuple(ALLOWED_EXTENSIONS)):
                        src_path = os.path.join(temp_images_dir, file)
                        dst_path = os.path.join(output_dir, file)
                        shutil.copy(src_path, dst_path)
                        results.append({
                            "filename": file,
                            "processed_path": dst_path
                        })
                        process_logs[session_id].put(f"Copied temporary file as result: {file}")
        
        if not results:
            process_logs[session_id].put("Warning: No result files were found")
            
        process_logs[session_id].put("All results processed successfully")
        process_status[session_id] = "completed"
        return session_id, results
        
    except Exception as e:
        error_message = f"Error in processing pipeline: {str(e)}"
        app.logger.error(error_message)
        process_logs[session_id].put(error_message)
        process_status[session_id] = "error"
        return None, []

def process_images_thread(image_paths, model_type, session_id):
    """Run the image processing in a separate thread."""
    try:
        session_id, results = process_images(image_paths, model_type, session_id)
        
        if session_id and results:
            app.config[f"results_{session_id}"] = results
            
        process_logs[session_id].put("Job finished. Closing log...")
    except Exception as e:
        app.logger.error(f"Thread error: {e}")
        process_logs[session_id].put(f"Error: {str(e)}")
        process_status[session_id] = "error"
        process_logs[session_id].put("Job failed. Closing log...")

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
    
    # Generate a session ID
    session_id = str(uuid.uuid4())
    process_logs[session_id] = queue.Queue()
    process_status[session_id] = "processing"
    
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
            process_logs[session_id].put("No valid image files provided")
            process_status[session_id] = "error"
            return jsonify({"error": "No valid image files provided"}), 400
        
        # Start processing in a separate thread
        process_thread = threading.Thread(
            target=process_images_thread,
            args=(saved_paths, model_type, session_id)
        )
        process_thread.daemon = True
        process_thread.start()
        
        # Return session ID
        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "Processing started"
        })
        
    except Exception as e:
        app.logger.error(f"Error starting process: {e}")
        process_logs[session_id].put(f"Error: {str(e)}")
        process_status[session_id] = "error"
        return jsonify({"error": "Internal server error"}), 500
    finally:
        pass

@app.route('/api/status/<session_id>', methods=['GET'])
def get_status(session_id):
    """Get the current status of a processing job."""
    if session_id not in process_status:
        return jsonify({"error": "Session not found"}), 404
        
    status = process_status[session_id]
    
    # If processing is complete, include results
    if status == "completed" and f"results_{session_id}" in app.config:
        results = app.config[f"results_{session_id}"]
        return jsonify({
            "status": status,
            "session_id": session_id,
            "results": [{"filename": r["filename"]} for r in results]
        })
    
    return jsonify({
        "status": status,
        "session_id": session_id
    })

@app.route('/api/logs/<session_id>', methods=['GET'])
def stream_logs(session_id):
    """Stream logs for a given session."""
    if session_id not in process_logs:
        return jsonify({"error": "Session not found"}), 404
    
    def generate():
        log_queue = process_logs[session_id]
        
        # Send any existing logs
        while not log_queue.empty():
            yield f"data: {log_queue.get()}\n\n"
        
        # Stream new logs as they come in
        while session_id in process_status and process_status[session_id] == "processing":
            try:
                try:
                    log = log_queue.get(timeout=0.5)
                    yield f"data: {log}\n\n"
                except queue.Empty:
                    # Send a heartbeat to keep the connection alive
                    yield f"data: \n\n"
            except Exception as e:
                app.logger.error(f"Error in log streaming: {e}")
                break
        
        # Send any remaining logs
        while not log_queue.empty():
            yield f"data: {log_queue.get()}\n\n"
        
        # Send completion message
        if session_id in process_status:
            status = process_status[session_id]
            yield f"data: Processing {status}\n\n"
    
    return Response(stream_with_context(generate()), mimetype="text/event-stream")

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