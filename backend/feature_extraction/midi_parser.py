"""
MIDI Parser for Bollywood songs
Extracts musical features from MIDI files
"""

import numpy as np
from typing import List, Dict, Tuple

class BollywoodMIDIParser:
    """
    Extract features from Bollywood MIDI files
    """
    
    def __init__(self):
        self.raga_database = self._load_raga_database()
    
    def _load_raga_database(self):
        """Load common Bollywood ragas"""
        return {
            'yaman': {
                'notes': [0, 2, 4, 5, 7, 9, 11],  # Sa, Re, Ga, Ma, Pa, Dha, Ni
                'vadi': 4,  # Ga
                'samvadi': 0,  # Sa
                'arohana': [0, 2, 4, 5, 7, 9, 11, 12],
                'avarohana': [12, 11, 9, 7, 5, 4, 2, 0]
            },
            'bhairav': {
                'notes': [0, 1, 4, 5, 7, 8, 11],
                'vadi': 0,  # Sa
                'samvadi': 5,  # Pa
                'arohana': [0, 1, 4, 5, 7, 8, 11, 12],
                'avarohana': [12, 11, 8, 7, 5, 4, 1, 0]
            },
            'desh': {
                'notes': [0, 2, 4, 5, 7, 9, 10],
                'vadi': 7,  # Pa
                'samvadi': 2,  # Re
                'arohana': [0, 2, 4, 5, 7, 9, 10, 12],
                'avarohana': [12, 10, 9, 7, 5, 4, 2, 0]
            },
            'bhimpalasi': {
                'notes': [0, 2, 3, 5, 7, 8, 10],
                'vadi': 5,  # Ma
                'samvadi': 0,  # Sa
                'arohana': [0, 2, 3, 5, 7, 8, 10, 12],
                'avarohana': [12, 10, 8, 7, 5, 3, 2, 0]
            },
            'kafi': {
                'notes': [0, 2, 3, 5, 7, 8, 10],
                'vadi': 5,  # Ma
                'samvadi': 0,  # Sa
                'arohana': [0, 2, 3, 5, 7, 8, 10, 12],
                'avarohana': [12, 10, 8, 7, 5, 3, 2, 0]
            }
        }
    
    def parse_midi(self, filepath: str) -> Dict:
        """
        Parse MIDI file and extract tracks and features
        For now, create dummy data since we're using samples
        """
        # Extract song name from filename
        import os
        filename = os.path.basename(filepath)
        song_name = filename.replace('.mid', '')
        
        # Create dummy tracks based on song name
        tracks = self._create_dummy_tracks(song_name)
        
        # Extract features
        features = self._extract_features(tracks)
        
        # Detect raga
        raga_info = self._detect_raga(tracks)
        
        return {
            'filename': filename,
            'tracks': tracks,
            'track_types': self._identify_track_types(tracks),
            'tempo': 100,  # Default tempo
            'features': features,
            'raga': raga_info
        }
    
    def _create_dummy_tracks(self, song_name: str) -> List:
        """Create dummy MIDI tracks for testing"""
        
        # Different scales for different songs
        scales = {
            'Kal Ho Na Ho': [0, 2, 4, 5, 7, 9, 11],  # Yaman
            'Tum Hi Ho': [0, 1, 4, 5, 7, 8, 11],      # Bhairav
            'Bole Chudiyan': [0, 2, 4, 5, 7, 9, 10],  # Desh
            'Kabira': [0, 2, 3, 5, 7, 8, 10],         # Bhimpalasi
            'Gerua': [0, 2, 3, 5, 7, 8, 10]           # Kafi
        }
        
        # Get scale for this song (default to Yaman)
        scale = scales.get(song_name, [0, 2, 4, 5, 7, 9, 11])
        
        tracks = []
        
        # 1. Drum track
        drums = []
        for i in range(0, 32):
            beat = i * 0.5
            drums.append({
                'pitch': 36 + (i % 4),
                'start': beat,
                'end': beat + 0.1,
                'velocity': 100,
                'duration': 0.1
            })
        tracks.append(drums)
        
        # 2. Bass track
        bass = []
        base_note = 40
        for i in range(0, 16):
            beat = i * 1.0
            scale_note = scale[i % len(scale)]
            bass.append({
                'pitch': base_note + scale_note,
                'start': beat,
                'end': beat + 0.8,
                'velocity': 80,
                'duration': 0.8
            })
        tracks.append(bass)
        
        # 3. Melody track
        melody = []
        base_melody = 60
        pattern = scale + scale[::-1]  # Ascending + descending
        for i in range(0, 32):
            beat = i * 0.25
            note_idx = i % len(pattern)
            melody.append({
                'pitch': base_melody + pattern[note_idx],
                'start': beat,
                'end': beat + 0.2,
                'velocity': 90,
                'duration': 0.2
            })
        tracks.append(melody)
        
        return tracks
    
    def _identify_track_types(self, tracks: List) -> List[str]:
        """Identify instrument types"""
        track_types = []
        
        for i, track in enumerate(tracks):
            if i == 0:
                track_types.append('drums')
            elif i == 1:
                track_types.append('bass')
            else:
                track_types.append('melody')
        
        return track_types
    
    def _extract_features(self, tracks: List) -> Dict:
        """Extract musical features from tracks"""
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
                    density = len(track) / duration if duration > 0 else 4.0
                else:
                    density = 4.0
                
                features['note_density'].append(density)
                features['pitch_range'].append(max(pitches) - min(pitches))
                features['avg_pitch'].append(np.mean(pitches))
            else:
                features['note_density'].append(0)
                features['pitch_range'].append(0)
                features['avg_pitch'].append(0)
        
        return features
    
    def _detect_raga(self, tracks: List) -> Dict:
        """Detect most likely raga from the melody track"""
        # Get melody track (usually last track)
        melody_track = tracks[-1] if tracks else []
        
        if not melody_track:
            return {'name': 'unknown', 'confidence': 0, 'notes': []}
        
        # Extract pitch classes
        pitch_classes = [note['pitch'] % 12 for note in melody_track]
        unique_pitches = set(pitch_classes)
        
        # Find best matching raga
        best_match = 'yaman'
        best_score = 0
        
        for raga_name, raga_info in self.raga_database.items():
            raga_notes = set(raga_info['notes'])
            
            # Calculate overlap
            overlap = len(unique_pitches & raga_notes)
            score = overlap / len(raga_notes) if raga_notes else 0
            
            if score > best_score:
                best_score = score
                best_match = raga_name
        
        return {
            'name': best_match,
            'confidence': min(1.0, best_score * 1.2),  # Boost a bit
            'notes': list(unique_pitches),
            'vadi': self.raga_database[best_match]['vadi'],
            'samvadi': self.raga_database[best_match]['samvadi']
        }