"""
MelodyMorph AI - Evolutionary Music Mashup
Main application file - FIXED VERSION
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

# Check if we have songs (loaded automatically in __init__)
if dataset_manager.get_song_count() == 0:
    print("📀 No songs found, creating sample dataset...")
    dataset_manager.add_sample_dataset()

print(f"📊 Total songs available: {dataset_manager.get_song_count()}")
print("=" * 50)

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
        'message': 'MelodyMorph AI is ready!',
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

@app.route('/api/preview/<int:song_idx>')
def preview_song(song_idx):
    """Generate and return a 10-second MIDI preview of a song"""
    try:
        song = dataset_manager.get_song(song_idx)
        if not song:
            return jsonify({'error': 'Song not found'}), 404
        
        import pretty_midi
        
        # Create a short MIDI from the song's tracks
        midi = pretty_midi.PrettyMIDI(initial_tempo=song.get('tempo', 120))
        
        # Use melody track (index 2) or fallback to any available track
        tracks = song.get('tracks', [])
        track_to_use = None
        for idx in [2, 1, 0]:  # Prefer melody, then bass, then drums
            if idx < len(tracks) and tracks[idx]:
                track_to_use = tracks[idx]
                break
        
        if not track_to_use:
            return jsonify({'error': 'No playable track found'}), 404
        
        # Find the starting time (first note)
        first_note_start = float('inf')
        for note in track_to_use:
            if note['start'] < first_note_start:
                first_note_start = note['start']
                
        if first_note_start == float('inf'):
            return jsonify({'error': 'Track is empty'}), 404
            
        # Filter notes to first 10 seconds after the first note
        notes_json = []
        for note in track_to_use:
            if note['start'] >= first_note_start and note['start'] < first_note_start + 10.0:
                end = min(note['end'], first_note_start + 10.0)
                notes_json.append({
                    'velocity': min(120, max(40, note.get('velocity', 90))),
                    'pitch': max(21, min(108, int(note['pitch']))),
                    'start': note['start'] - first_note_start,
                    'end': end - first_note_start
                })
                
        if not notes_json:
            return jsonify({'error': 'No notes in preview range'}), 404
        
        return jsonify({'notes': notes_json})
    except Exception as e:
        print(f"Preview error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate mashup using GA"""
    try:
        data = request.json
        song1_idx = int(data.get('song1', 0))
        song2_idx = int(data.get('song2', 1))
        generations = int(data.get('generations', 50))
        population_size = int(data.get('population_size', 50))
        
        print(f"\n🎮 Generating mashup:")
        print(f"   Song 1: {dataset_manager.get_song_names()[song1_idx]}")
        print(f"   Song 2: {dataset_manager.get_song_names()[song2_idx]}")
        print(f"   Generations: {generations}")
        print(f"   Population: {population_size}")
        
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
        
        print(f"✅ Generation complete! Best fitness: {best.fitness:.3f}")
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Error: {e}")
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
            return send_file(midi_path, as_attachment=True, 
                           download_name=f"melodymorph_{run_id}.mid")
    
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
    print("\n🎵 Starting MelodyMorph AI...")
    print(f"📀 {dataset_manager.get_song_count()} songs loaded!")
    print("📍 Open http://127.0.0.1:5000 in your browser")
    print("=" * 50)
    app.run(debug=True)