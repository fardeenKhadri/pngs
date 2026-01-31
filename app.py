from flask import Flask, render_template, request, send_file, jsonify
from core.watermarker import Watermarker
import cv2
import numpy as np
import io
import os

app = Flask(__name__)
# Ensure templates and static are found in current directory
app.template_folder = 'templates'
app.static_folder = 'static'

wm = Watermarker()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/embed', methods=['POST'])
def embed():
    try:
        file = request.files['image']
        text = request.form['text']
        
        if not file or not text:
            return jsonify({'error': 'Missing image or text'}), 400

        image_bytes = file.read()
        
        # Embed
        encoded_bgr = wm.embed(image_bytes, text)
        
        # Convert back to PNG for download
        is_success, buffer = cv2.imencode(".png", encoded_bgr)
        if not is_success:
            return jsonify({'error': 'Failed to encode image'}), 500
            
        io_buf = io.BytesIO(buffer)
        io_buf.seek(0)
        
        return send_file(
            io_buf,
            mimetype='image/png',
            as_attachment=True,
            download_name='watermarked_image.png'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/decode', methods=['POST'])
def decode():
    try:
        file = request.files['image']
        if not file:
            return jsonify({'error': 'Missing image'}), 400
            
        image_bytes = file.read()
        
        # Decode
        payload = wm.decode(image_bytes)
        
        if payload:
            return jsonify({'status': 'success', 'payload': payload})
        else:
            return jsonify({'status': 'failure'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
