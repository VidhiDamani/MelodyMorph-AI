"""
Dataset Manager for handling Bollywood MIDI files
"""

import os
import json
import pickle
import random
import numpy as np
from ..feature_extraction.midi_parser import BollywoodMIDIParser

class DatasetManager:
    """
    Manage Bollywood MIDI dataset
    """
    
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.midi_dir = os.path.join(data_dir, 'midi_files')
        self.processed_dir = os.path.join(data_dir, 'processed')
        self.cache_file = os.path.join(data_dir, 'feature_cache.pkl')
        
        # Create directories
        os.makedirs(self.midi_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        
        self.parser = BollywoodMIDIParser()
        self.dataset = []
        
        # Load cache if exists
        self.load_cache()
        
    def add_sample_dataset(self):
        """Create sample dataset for testing"""
        print("📀 Creating sample dataset...")
        
        # Create 5 sample songs
        sample_songs = [
            {
                'name': 'Kal Ho Na Ho',
                'raga': 'yaman',
                'tempo': 95,
                'mood': 'emotional',
                'scale': [0, 2, 4, 5, 7, 9, 11]  # C major
            },
            {
                'name': 'Tum Hi Ho',
                'raga': 'bhairav',
                'tempo': 85,
                'mood': 'romantic',
                'scale': [0, 1, 4, 5, 7, 8, 11]  # C bhairav
            },
            {
                'name': 'Bole Chudiyan',
                'raga': 'desh',
                'tempo': 120,
                'mood': 'celebratory',
                'scale': [0, 2, 4, 5, 7, 9, 10]  # C desh
            },
            {
                'name': 'Kabira',
                'raga': 'bhimpalasi',
                'tempo': 90,
                'mood': 'soulful',
                'scale': [0, 2, 3, 5, 7, 8, 10]  # C bhimpalasi
            },
            {
                'name': 'Gerua',
                'raga': 'kafi',
                'tempo': 100,
                'mood': 'romantic',
                'scale': [0, 2, 3, 5, 7, 8, 10]  # C kafi
            }
        ]
        
        for song in sample_songs:
            # Create dummy tracks
            tracks = self._create_dummy_tracks(song)
            
            # Create song entry
            song_entry = {
                'filename': f"{song['name']}.mid",
                'tracks': tracks,
                'track_types': ['drums', 'bass', 'melody'],
                'tempo': song['tempo'],
                'features': self._extract_features(tracks),
                'raga': {
                    'name': song['raga'],
                    'confidence': 0.8,
                    'notes': song['scale'],
                    'vadi': song['scale'][2] if len(song['scale']) > 2 else 0,
                    'samvadi': song['scale'][4] if len(song['scale']) > 4 else 7
                },
                'metadata': {
                    'name': song['name'],
                    'mood': song['mood'],
                    'era': '2000s',
                    'movie': 'Bollywood'
                }
            }
            
            self.dataset.append(song_entry)
        
        # Save to cache
        self._save_cache()
        print(f"✅ Added {len(self.dataset)} sample songs")
        
    def _create_dummy_tracks(self, song_info):
        """Create dummy MIDI tracks for testing"""
        
        tracks = []
        scale = song_info['scale']
        tempo = song_info['tempo']
        
        # 1. Drum track (simplified)
        drums = []
        for i in range(0, 32):
            beat = i * (60 / tempo)  # Time in seconds
            drums.append({
                'pitch': 36 + (i % 4),  # Different drum sounds
                'start': beat,
                'end': beat + 0.1,
                'velocity': 100,
                'duration': 0.1
            })
        tracks.append(drums)
        
        # 2. Bass track (simple bassline)
        bass = []
        base_note = 40  # E2
        for i in range(0, 16):
            beat = i * (60 / tempo) * 2  # Half as many notes
            scale_note = scale[i % len(scale)]
            bass.append({
                'pitch': base_note + scale_note,
                'start': beat,
                'end': beat + 0.8,
                'velocity': 80,
                'duration': 0.8
            })
        tracks.append(bass)
        
        # 3. Melody track (main tune)
        melody = []
        base_melody = 60  # C4
        # Create a simple ascending-descending pattern
        pattern = scale + scale[::-1]
        for i in range(0, 32):
            beat = i * (60 / tempo) / 2  # Twice as many notes
            note_idx = i % len(pattern)
            melody.append({
                'pitch': base_melody + pattern[note_idx],
                'start': beat,
                'end': beat + 0.3,
                'velocity': 90,
                'duration': 0.3
            })
        tracks.append(melody)
        
        return tracks
    
    def _extract_features(self, tracks):
        """Extract basic features from tracks"""
        features = {
            'note_density': [],
            'pitch_range': [],
            'avg_pitch': []
        }
        
        for track in tracks:
            if track:
                pitches = [n['pitch'] for n in track]
                times = [n['start'] for n in track]
                
                if len(times) > 1:
                    duration = max(times) - min(times)
                    density = len(track) / duration if duration > 0 else 0
                else:
                    density = 1
                
                features['note_density'].append(density)
                features['pitch_range'].append(max(pitches) - min(pitches))
                features['avg_pitch'].append(np.mean(pitches))
            else:
                features['note_density'].append(0)
                features['pitch_range'].append(0)
                features['avg_pitch'].append(0)
        
        return features
    
    def _save_cache(self):
        """Save dataset to cache"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.dataset, f)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def load_cache(self):
        """Load dataset from cache"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    self.dataset = pickle.load(f)
                print(f"📂 Loaded {len(self.dataset)} songs from cache")
            except Exception as e:
                print(f"Error loading cache: {e}")
                self.dataset = []
    
    def get_song(self, index):
        """Get song by index"""
        if 0 <= index < len(self.dataset):
            return self.dataset[index]
        return None
    
    def get_song_names(self):
        """Get list of song names"""
        names = []
        for song in self.dataset:
            if 'metadata' in song and 'name' in song['metadata']:
                names.append(song['metadata']['name'])
            else:
                names.append(song.get('filename', 'Unknown'))
        return names
    
    def get_song_count(self):
        """Get number of songs in dataset"""
        return len(self.dataset)
    
    def prepare_for_ga(self, song1_idx, song2_idx):
        """
        Prepare two songs for GA input
        """
        song1 = self.dataset[song1_idx]
        song2 = self.dataset[song2_idx]
        
        # Combine tracks from both songs
        # We want: drums from song1, bass from song2, melody from song1
        source_tracks = [
            song1['tracks'][0],  # Drums from song1
            song2['tracks'][1],  # Bass from song2
            song1['tracks'][2]   # Melody from song1
        ]
        
        # Extract features for fitness functions
        source_features = {
            'raga1': song1.get('raga', {}),
            'raga2': song2.get('raga', {}),
            'density1': song1['features']['note_density'][2] if len(song1['features']['note_density']) > 2 else 4.0,
            'density2': song2['features']['note_density'][2] if len(song2['features']['note_density']) > 2 else 4.0,
            'tempo1': song1['tempo'],
            'tempo2': song2['tempo']
        }
        
        return {
            'source_tracks': source_tracks,
            'source_features': source_features,
            'song1_name': song1.get('metadata', {}).get('name', 'Song 1'),
            'song2_name': song2.get('metadata', {}).get('name', 'Song 2')
        }