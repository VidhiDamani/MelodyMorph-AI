"""
Chromosome representation for Bollywood mashup
Each chromosome is a potential mashup solution
"""

import random
import numpy as np
import pretty_midi
import os

class BollywoodChromosome:
    """
    Represents a mashup candidate with multiple tracks
    """
    
    def __init__(self, track_data=None):
        """Initialize with optional track data"""
        self.tracks = track_data or []  # List of tracks, each track is list of notes
        self.control_genes = {
            'pitch_shifts': [0, 0, 0],      # Semitones per track
            'tempo_scales': [1.0, 1.0, 1.0], # Time stretch factors
            'track_volumes': [100, 80, 90]   # Volume levels
        }
        self.fitness = 0.0
        self.fitness_components = {}
        self.id = random.randint(1000, 9999)  # Random ID for tracking
        
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'fitness': self.fitness,
            'fitness_components': self.fitness_components,
            'control_genes': self.control_genes,
            'track_count': len(self.tracks),
            'note_counts': [len(track) for track in self.tracks]
        }
    
    def to_midi(self, output_path):
        """
        Convert chromosome to MIDI file
        """
        try:
            # Create MIDI object
            midi = pretty_midi.PrettyMIDI(initial_tempo=120)
            
            # Instrument mapping (GM standard)
            instruments = [0, 33, 40]  # Piano, Bass, Violin
            
            for track_idx, track_notes in enumerate(self.tracks):
                if not track_notes:
                    continue
                    
                # Create instrument
                instrument = pretty_midi.Instrument(
                    program=instruments[track_idx % len(instruments)],
                    name=f"Track_{track_idx}"
                )
                
                for note in track_notes:
                    # Apply pitch shift
                    pitch = note['pitch'] + self.control_genes['pitch_shifts'][track_idx]
                    
                    # Keep pitch in valid range (0-127)
                    pitch = max(0, min(127, pitch))
                    
                    # Apply tempo scaling
                    start = note['start'] * self.control_genes['tempo_scales'][track_idx]
                    end = note['end'] * self.control_genes['tempo_scales'][track_idx]
                    
                    # Apply volume
                    velocity = int(note.get('velocity', 100) * 
                                 self.control_genes['track_volumes'][track_idx] / 100)
                    velocity = max(1, min(127, velocity))
                    
                    # Create MIDI note
                    midi_note = pretty_midi.Note(
                        velocity=velocity,
                        pitch=int(pitch),
                        start=start,
                        end=end
                    )
                    instrument.notes.append(midi_note)
                
                # Sort notes by start time
                instrument.notes.sort(key=lambda x: x.start)
                midi.instruments.append(instrument)
            
            # Save MIDI file
            midi.write(output_path)
            return True
            
        except Exception as e:
            print(f"Error creating MIDI: {e}")
            return False
    
    @staticmethod
    def create_random(source_tracks, length_bars=4):
        """
        Create random chromosome from source tracks
        """
        chromosome = BollywoodChromosome()
        chromosome.tracks = []
        
        # For each track position (0=drums, 1=bass, 2=melody)
        for track_idx in range(3):
            if track_idx < len(source_tracks) and source_tracks[track_idx]:
                # Get source track
                source = source_tracks[track_idx]
                
                if len(source) > 10:  # If enough notes
                    # Select random segment
                    segment_length = min(length_bars * 8, len(source))  # ~8 notes per bar
                    max_start = max(0, len(source) - segment_length)
                    start_idx = random.randint(0, max_start)
                    segment = source[start_idx:start_idx + segment_length]
                else:
                    segment = source.copy()
                
                chromosome.tracks.append(segment)
            else:
                chromosome.tracks.append([])
        
        # Random control genes
        chromosome.control_genes['pitch_shifts'] = [
            random.randint(-3, 3) for _ in range(3)
        ]
        chromosome.control_genes['tempo_scales'] = [
            round(random.uniform(0.9, 1.1), 2) for _ in range(3)
        ]
        
        return chromosome
    
    def __str__(self):
        return f"Chromosome #{self.id} | Fitness: {self.fitness:.3f}"