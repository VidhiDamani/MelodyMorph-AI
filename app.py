"""
Bollywood Mashup Generator using Genetic Algorithm
Main application file
"""

import os
from flask import Flask, render_template, jsonify, request
import numpy as np
import json

app = Flask(__name__, 
            template_folder='frontend/templates',
            static_folder='frontend/static')

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/api/status')
def status():
    """API endpoint to check if server is running"""
    return jsonify({
        'status': 'online',
        'message': 'Bollywood Mashup GA is ready!',
        'version': '1.0.0'
    })

@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate mashup (will implement later)"""
    data = request.json
    return jsonify({
        'status': 'processing',
        'message': 'Mashup generation started',
        'song1': data.get('song1'),
        'song2': data.get('song2')
    })

if __name__ == '__main__':
    print("🎵 Starting Bollywood Mashup Generator...")
    print("📍 Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True)