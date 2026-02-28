"""
Bollywood Mashup Generator using Genetic Algorithm
Main application file
"""

import os
from flask import Flask, render_template, jsonify, request, send_file
import numpy as np
import json
import time
from backend.ga_engine.genetic_algorithm import BollywoodGA
from backend.utils.dataset_manager import DatasetManager

app = Flask(__name__, 
            template_folder='frontend/templates',
            static_folder='frontend/static')

# Initialize dataset manager
dataset_manager = DatasetManager()

# Create sample dataset if empty
if dataset_manager.get_song_count() == 0:
    dataset_manager.add_sample_dataset()

# Store active GA runs
active_runs = {}

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
        'version': '1.0.0',
        'songs_available': dataset_manager.get_song_count()
    })

@app.route('/api/songs')
def get_songs():
    """Get list of available songs"""
    songs = dataset_manager.get_song_names()
    return jsonify({
        'songs': songs,
        'count': len(songs)
    })

@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate mashup using GA"""
    try:
        data = request.json
        song1_idx = int(data.get('song1', 0))
        song2_idx = int(data.get('song2', 1))
        generations = int(data.get('generations', 50))
        population_size = int(data.get('population_size', 50))
        
        # Prepare data for GA
        ga_input = dataset_manager.prepare_for_ga(song1_idx, song2_idx)
        
        # Create and run GA
        ga = BollywoodGA(
            source_tracks=ga_input['source_tracks'],
            source_features=ga_input['source_features'],
            population_size=population_size,
            elite_size=population_size // 5,
            mutation_rate=0.1,
            crossover_rate=0.7
        )
        
        # Initialize population
        ga.initialize_population()
        
        # Run evolution
        results = ga.run(generations=generations)
        
        # Get best chromosome
        best = ga.get_best()
        
        # Generate MIDI file
        timestamp = int(time.time())
        midi_filename = f"mashup_{timestamp}.mid"
        midi_path = os.path.join('data', 'generated', midi_filename)
        best.to_midi(midi_path)
        
        # Store run info
        run_id = str(timestamp)
        active_runs[run_id] = {
            'ga': ga,
            'best': best,
            'song1': ga_input['song1_name'],
            'song2': ga_input['song2_name'],
            'midi_file': midi_filename
        }
        
        # Prepare response
        response = {
            'success': True,
            'run_id': run_id,
            'best_fitness': best.fitness,
            'fitness_components': best.fitness_components,
            'fitness_history': results['fitness_history'],
            'avg_fitness_history': results['avg_fitness_history'],
            'generations': generations,
            'time_taken': results['time_taken'],
            'song1': ga_input['song1_name'],
            'song2': ga_input['song2_name'],
            'midi_file': midi_filename
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/download/<run_id>')
def download_midi(run_id):
    """Download generated MIDI file"""
    if run_id in active_runs:
        midi_file = active_runs[run_id]['midi_file']
        midi_path = os.path.join('data', 'generated', midi_file)
        if os.path.exists(midi_path):
            return send_file(midi_path, as_attachment=True)
    
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/run/<run_id>')
def get_run_info(run_id):
    """Get information about a specific run"""
    if run_id in active_runs:
        run = active_runs[run_id]
        best = run['best']
        return jsonify({
            'success': True,
            'song1': run['song1'],
            'song2': run['song2'],
            'best_fitness': best.fitness,
            'fitness_components': best.fitness_components,
            'midi_file': run['midi_file']
        })
    return jsonify({'error': 'Run not found'}), 404

if __name__ == '__main__':
    print("🎵 Starting Bollywood Mashup Generator...")
    print("=" * 50)
    print(f"📀 Songs available: {dataset_manager.get_song_count()}")
    print("📍 Open http://127.0.0.1:5000 in your browser")
    print("=" * 50)
    app.run(debug=True)