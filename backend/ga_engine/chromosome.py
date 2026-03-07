"""
Chromosome representation for Bollywood mashup
Each chromosome is a potential mashup solution
UPDATED VERSION - with better MIDI generation
"""

import random
import numpy as np
import os

# Try to import pretty_midi
try:
    import pretty_midi
    HAS_PRETTY_MIDI = True
except ImportError:
    print("⚠️ pretty_midi not installed. Install with: pip install pretty_midi")
    HAS_PRETTY_MIDI = False

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
            'track_volumes': [100, 80, 90],  # Volume levels
            'instrument_choices': [0, 0, 0]  # Instrument variations
        }
        self.fitness = 0.0
        self.fitness_components = {}
        self.id = random.randint(1000, 9999)  # Random ID for tracking
        self.creation_generation = 0
        
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
        Convert chromosome to MIDI file with better instrument choices
        """
        if not HAS_PRETTY_MIDI:
            print("⚠️ pretty_midi not installed, cannot create MIDI")
            return False
        
        try:
            # Create MIDI object
            midi = pretty_midi.PrettyMIDI(initial_tempo=120)
            
            # Better instrument mapping for Bollywood sound
            # Program numbers from General MIDI standard
            instrument_families = {
                'drums': [0, 16, 24, 25, 26],      # Piano, Organ, Guitar, Nylon Guitar, Steel Guitar
                'bass': [32, 33, 34, 35, 43],       # Bass, Bass, Bass, Bass, Contrabass
                'melody': [40, 41, 42, 48, 56]      # Violin, Viola, Cello, Strings, Trumpet
            }
            
            # Nice instrument combinations for good mashups
            good_combinations = [
                [0, 33, 40],    # Piano, Bass, Violin
                [24, 35, 48],    # Guitar, Contrabass, Strings
                [16, 32, 41],    # Organ, Bass, Viola
                [25, 34, 56],    # Nylon Guitar, Bass, Trumpet
                [26, 43, 42]     # Steel Guitar, Contrabass, Cello
            ]
            
            for track_idx, track_notes in enumerate(self.tracks):
                if not track_notes:
                    continue
                
                # Choose instrument based on fitness and track type
                if track_idx == 0:
                    # Drum/rhythm track
                    if self.fitness > 0.7:
                        program = instrument_families['drums'][2]  # Guitar for good mashups
                    elif self.fitness > 0.4:
                        program = instrument_families['drums'][1]  # Organ
                    else:
                        program = instrument_families['drums'][0]  # Piano
                        
                elif track_idx == 1:
                    # Bass track
                    if self.fitness > 0.7:
                        program = instrument_families['bass'][3]  # Contrabass
                    elif self.fitness > 0.4:
                        program = instrument_families['bass'][1]  # Bass
                    else:
                        program = instrument_families['bass'][0]  # Bass
                        
                else:
                    # Melody track
                    if self.fitness > 0.7:
                        program = instrument_families['melody'][3]  # Strings
                    elif self.fitness > 0.4:
                        program = instrument_families['melody'][0]  # Violin
                    else:
                        program = instrument_families['melody'][1]  # Viola
                
                # Override with instrument choice from genes if available
                if 'instrument_choices' in self.control_genes:
                    choice_idx = self.control_genes['instrument_choices'][track_idx % 3]
                    if track_idx == 0:
                        program = instrument_families['drums'][choice_idx % len(instrument_families['drums'])]
                    elif track_idx == 1:
                        program = instrument_families['bass'][choice_idx % len(instrument_families['bass'])]
                    else:
                        program = instrument_families['melody'][choice_idx % len(instrument_families['melody'])]
                
                # Create instrument
                instrument = pretty_midi.Instrument(
                    program=program,
                    name=f"Track_{track_idx}"
                )
                
                for note in track_notes:
                    # Apply pitch shift (limited to avoid chipmunk sounds)
                    pitch_shift = self.control_genes['pitch_shifts'][track_idx % 3]
                    # Limit extreme shifts
                    if abs(pitch_shift) > 5:
                        pitch_shift = 5 if pitch_shift > 0 else -5
                    
                    pitch = note['pitch'] + pitch_shift
                    pitch = max(30, min(100, int(pitch)))  # Keep in reasonable range
                    
                    # Apply tempo scaling
                    tempo_scale = self.control_genes['tempo_scales'][track_idx % 3]
                    # Limit extreme tempo changes
                    if tempo_scale < 0.8:
                        tempo_scale = 0.8
                    if tempo_scale > 1.2:
                        tempo_scale = 1.2
                    
                    start = note['start'] * tempo_scale
                    end = note['end'] * tempo_scale
                    
                    # Apply volume with some natural variation
                    base_volume = note.get('velocity', 80)
                    volume_factor = self.control_genes['track_volumes'][track_idx % 3] / 100
                    velocity = int(base_volume * volume_factor)
                    
                    # Add slight variation to make it sound more human
                    velocity = int(velocity * random.uniform(0.9, 1.1))
                    velocity = max(40, min(110, velocity))  # Keep in good range
                    
                    # Create MIDI note
                    midi_note = pretty_midi.Note(
                        velocity=velocity,
                        pitch=pitch,
                        start=start,
                        end=end
                    )
                    instrument.notes.append(midi_note)
                
                # Sort notes by start time
                if instrument.notes:
                    instrument.notes.sort(key=lambda x: x.start)
                    midi.instruments.append(instrument)
            
            # Add some reverb/tempo info (optional)
            if midi.instruments:
                # Set a reasonable tempo
                tempo = 100
                if hasattr(midi, 'tick_scales'):
                    pass  # Keep default
                
                # Save MIDI file
                midi.write(output_path)
                return True
            else:
                print("⚠️ No instruments with notes to save")
                return False
            
        except Exception as e:
            print(f"Error creating MIDI: {e}")
            return False
    
    @staticmethod
    def create_random(source_tracks, length_bars=4):
        """
        Create random chromosome from source tracks with more variety
        """
        chromosome = BollywoodChromosome()
        chromosome.tracks = []
        
        # For each track position (0=drums, 1=bass, 2=melody)
        for track_idx in range(3):
            if track_idx < len(source_tracks) and source_tracks[track_idx]:
                # Get source track
                source = source_tracks[track_idx]
                
                if len(source) > 8:  # If enough notes
                    # Select random segment with some variety in length
                    segment_length = min(random.randint(6, 12) * 2, len(source))
                    max_start = max(0, len(source) - segment_length)
                    start_idx = random.randint(0, max_start)
                    
                    # Sometimes take multiple segments and combine
                    if random.random() > 0.7 and max_start > segment_length:
                        # Take two segments and splice them
                        start2 = random.randint(0, max_start)
                        segment1 = source[start_idx:start_idx + segment_length//2]
                        segment2 = source[start2:start2 + segment_length//2]
                        segment = segment1 + segment2
                    else:
                        segment = source[start_idx:start_idx + segment_length]
                else:
                    segment = source.copy()
                
                chromosome.tracks.append(segment)
            else:
                chromosome.tracks.append([])
        
        # Random control genes with more variety
        chromosome.control_genes['pitch_shifts'] = [
            random.randint(-3, 3) for _ in range(3)
        ]
        
        chromosome.control_genes['tempo_scales'] = [
            round(random.uniform(0.85, 1.15), 2) for _ in range(3)
        ]
        
        chromosome.control_genes['track_volumes'] = [
            random.randint(70, 100) for _ in range(3)
        ]
        
        chromosome.control_genes['instrument_choices'] = [
            random.randint(0, 4) for _ in range(3)
        ]
        
        return chromosome
    
    def crossover(self, other, point=None):
        """
        Create two children by mixing with another chromosome
        """
        if point is None:
            point = random.randint(0, len(self.tracks))
        
        child1_tracks = []
        child2_tracks = []
        
        for i in range(len(self.tracks)):
            if i < point:
                child1_tracks.append(self.tracks[i])
                child2_tracks.append(other.tracks[i])
            else:
                child1_tracks.append(other.tracks[i])
                child2_tracks.append(self.tracks[i])
        
        child1 = BollywoodChromosome(child1_tracks)
        child2 = BollywoodChromosome(child2_tracks)
        
        # Mix control genes
        for key in self.control_genes:
            # 50% chance to take from either parent
            if random.random() > 0.5:
                child1.control_genes[key] = self.control_genes[key].copy()
                child2.control_genes[key] = other.control_genes[key].copy()
            else:
                child1.control_genes[key] = other.control_genes[key].copy()
                child2.control_genes[key] = self.control_genes[key].copy()
            
            # Sometimes swap individual values
            if isinstance(child1.control_genes[key], list):
                for j in range(len(child1.control_genes[key])):
                    if random.random() < 0.3:
                        temp = child1.control_genes[key][j]
                        child1.control_genes[key][j] = child2.control_genes[key][j]
                        child2.control_genes[key][j] = temp
        
        return child1, child2
    
    def mutate(self, mutation_rate=0.1):
        """
        Apply random mutations to create a variant
        """
        mutated = BollywoodChromosome([track[:] for track in self.tracks])
        mutated.control_genes = {k: v.copy() for k, v in self.control_genes.items()}
        
        # Mutate pitch shifts
        for i in range(len(mutated.control_genes['pitch_shifts'])):
            if random.random() < mutation_rate:
                # Change by -1, 0, or +1
                mutated.control_genes['pitch_shifts'][i] += random.randint(-1, 1)
                # Keep in range
                mutated.control_genes['pitch_shifts'][i] = max(-3, min(3, 
                    mutated.control_genes['pitch_shifts'][i]))
        
        # Mutate tempo scales
        for i in range(len(mutated.control_genes['tempo_scales'])):
            if random.random() < mutation_rate:
                # Change by 2-5%
                mutated.control_genes['tempo_scales'][i] *= random.uniform(0.95, 1.05)
                # Keep in range
                mutated.control_genes['tempo_scales'][i] = max(0.85, min(1.15, 
                    mutated.control_genes['tempo_scales'][i]))
                mutated.control_genes['tempo_scales'][i] = round(
                    mutated.control_genes['tempo_scales'][i], 2)
        
        # Mutate volumes
        for i in range(len(mutated.control_genes['track_volumes'])):
            if random.random() < mutation_rate:
                mutated.control_genes['track_volumes'][i] += random.randint(-10, 10)
                mutated.control_genes['track_volumes'][i] = max(50, min(120, 
                    mutated.control_genes['track_volumes'][i]))
        
        # Mutate instrument choices
        for i in range(len(mutated.control_genes.get('instrument_choices', [0,0,0]))):
            if random.random() < mutation_rate:
                mutated.control_genes['instrument_choices'][i] = random.randint(0, 4)
        
        # Sometimes swap a few notes between tracks for variety
        if random.random() < mutation_rate / 2:
            if len(mutated.tracks) >= 2:
                track1 = random.randint(0, len(mutated.tracks) - 1)
                track2 = random.randint(0, len(mutated.tracks) - 1)
                if (track1 != track2 and 
                    mutated.tracks[track1] and 
                    mutated.tracks[track2] and
                    len(mutated.tracks[track1]) > 0 and 
                    len(mutated.tracks[track2]) > 0):
                    
                    idx1 = random.randint(0, len(mutated.tracks[track1]) - 1)
                    idx2 = random.randint(0, len(mutated.tracks[track2]) - 1)
                    
                    # Swap notes
                    (mutated.tracks[track1][idx1], 
                     mutated.tracks[track2][idx2]) = \
                        (mutated.tracks[track2][idx2], 
                         mutated.tracks[track1][idx1])
        
        return mutated
    
    def __str__(self):
        return f"Chromosome #{self.id} | Fitness: {self.fitness:.3f}"