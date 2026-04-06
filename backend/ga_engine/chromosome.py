"""
Chromosome representation for Bollywood mashup
Each chromosome is a potential mashup solution
UPDATED VERSION - VERTICAL MASHUP (tracks play simultaneously)
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
    Represents a mashup candidate with multiple tracks playing simultaneously
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
        
    def copy(self):
        """Create a deep copy of this chromosome"""
        new_c = BollywoodChromosome([track[:] for track in self.tracks])
        new_c.control_genes = {k: v.copy() for k, v in self.control_genes.items()}
        new_c.fitness = self.fitness
        new_c.fitness_components = self.fitness_components.copy()
        new_c.creation_generation = self.creation_generation
        return new_c
    
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
        Convert chromosome to MIDI file with MULTI-TRACK mixing (vertical mashup)
        All tracks play SIMULTANEOUSLY
        """
        if not HAS_PRETTY_MIDI:
            print("⚠️ pretty_midi not installed, cannot create MIDI")
            return False
        
        try:
            # Create MIDI object
            midi = pretty_midi.PrettyMIDI(initial_tempo=120)
            
            # Instrument mapping for different tracks
            instrument_programs = {
                'drums': [0, 16, 24, 25, 26],      # Piano, Organ, Guitar, Nylon Guitar, Steel Guitar
                'bass': [32, 33, 34, 35, 43],       # Bass, Bass, Bass, Bass, Contrabass
                'melody': [40, 41, 42, 48, 56]      # Violin, Viola, Cello, Strings, Trumpet
            }
            
            # TRACK 0: Drums/Percussion (plays simultaneously with others)
            if len(self.tracks) > 0 and self.tracks[0]:
                # Choose instrument
                instrument_idx = self.control_genes['instrument_choices'][0] % len(instrument_programs['drums'])
                program = instrument_programs['drums'][instrument_idx]
                
                # Use normal instrument for track 0 (forcing it to drums causes silence for melody)
                drum_instrument = pretty_midi.Instrument(program=program, name='Rhythm')
                
                for note in self.tracks[0]:
                    # Apply tempo scaling only (drums don't pitch shift)
                    tempo_scale = self.control_genes['tempo_scales'][0]
                    start = note['start'] * tempo_scale
                    end = note['end'] * tempo_scale
                    
                    # Ensure valid note duration
                    if end <= start:
                        end = start + 0.1
                    
                    # Apply volume
                    velocity = int(note.get('velocity', 100) * self.control_genes['track_volumes'][0] / 100)
                    velocity = max(60, min(120, velocity)) # Increased minimum volume
                    
                    midi_note = pretty_midi.Note(
                        velocity=velocity,
                        pitch=note['pitch'],
                        start=start,
                        end=end
                    )
                    drum_instrument.notes.append(midi_note)
                
                if drum_instrument.notes:
                    midi.instruments.append(drum_instrument)
            
            # TRACK 1: Bass/Harmony (plays simultaneously with others)
            if len(self.tracks) > 1 and self.tracks[1]:
                # Choose instrument
                instrument_idx = self.control_genes['instrument_choices'][1] % len(instrument_programs['bass'])
                program = instrument_programs['bass'][instrument_idx]
                
                bass_instrument = pretty_midi.Instrument(program=program, name='Bass')
                
                for note in self.tracks[1]:
                    # Apply pitch shift
                    pitch_shift = self.control_genes['pitch_shifts'][1]
                    # Limit extreme shifts
                    if abs(pitch_shift) > 5:
                        pitch_shift = 5 if pitch_shift > 0 else -5
                    
                    pitch = note['pitch'] + pitch_shift
                    pitch = max(30, min(100, int(pitch)))
                    
                    # Apply tempo scaling
                    tempo_scale = self.control_genes['tempo_scales'][1]
                    start = note['start'] * tempo_scale
                    end = note['end'] * tempo_scale
                    
                    # Ensure valid note duration
                    if end <= start:
                        end = start + 0.1
                    
                    # Apply volume
                    velocity = int(note.get('velocity', 80) * self.control_genes['track_volumes'][1] / 100)
                    velocity = max(50, min(120, velocity))
                    
                    midi_note = pretty_midi.Note(
                        velocity=velocity,
                        pitch=pitch,
                        start=start,
                        end=end
                    )
                    bass_instrument.notes.append(midi_note)
                
                if bass_instrument.notes:
                    midi.instruments.append(bass_instrument)
            
            # TRACK 2: Melody (plays simultaneously with others)
            if len(self.tracks) > 2 and self.tracks[2]:
                # Choose instrument
                instrument_idx = self.control_genes['instrument_choices'][2] % len(instrument_programs['melody'])
                program = instrument_programs['melody'][instrument_idx]
                
                melody_instrument = pretty_midi.Instrument(program=program, name='Melody')
                
                for note in self.tracks[2]:
                    # Apply pitch shift
                    pitch_shift = self.control_genes['pitch_shifts'][2]
                    if abs(pitch_shift) > 5:
                        pitch_shift = 5 if pitch_shift > 0 else -5
                    
                    pitch = note['pitch'] + pitch_shift
                    pitch = max(40, min(90, int(pitch)))
                    
                    # Apply tempo scaling
                    tempo_scale = self.control_genes['tempo_scales'][2]
                    start = note['start'] * tempo_scale
                    end = note['end'] * tempo_scale
                    
                    # Ensure valid note duration
                    if end <= start:
                        end = start + 0.1
                    
                    # Apply volume
                    velocity = int(note.get('velocity', 90) * self.control_genes['track_volumes'][2] / 100)
                    velocity = max(50, min(120, velocity))
                    
                    midi_note = pretty_midi.Note(
                        velocity=velocity,
                        pitch=pitch,
                        start=start,
                        end=end
                    )
                    melody_instrument.notes.append(midi_note)
                
                if melody_instrument.notes:
                    midi.instruments.append(melody_instrument)
            
            # Save MIDI file
            if midi.instruments:
                total_notes = sum(len(inst.notes) for inst in midi.instruments)
                if total_notes == 0:
                    print("⚠️ WARNING: MIDI object has instruments but ZERO notes!")
                    return False
                
                midi.write(output_path)
                print(f"✅ Created vertical mashup with {len(midi.instruments)} tracks and {total_notes} notes")
                return True
            else:
                print("⚠️ No instruments with notes to save")
                return False
            
        except Exception as e:
            print(f"Error creating MIDI: {e}")
            return False
    
    @staticmethod
    def _normalize_track(track):
        """Shift all notes so the track starts at time 0"""
        if not track:
            return []
        t = sorted(track, key=lambda n: n['start'])
        offset = t[0]['start']
        return [{**n, 'start': n['start'] - offset, 'end': n['end'] - offset} for n in t]

    @staticmethod
    def _blend_two_tracks(track1, track2, segment_sec=6.0):
        """
        Interleave two tracks by alternating segments of ~segment_sec seconds.
        This ensures BOTH songs are heard throughout the mashup.
        """
        if not track1 and not track2:
            return []
        if not track1:
            return [n.copy() for n in track2]
        if not track2:
            return [n.copy() for n in track1]

        t1 = BollywoodChromosome._normalize_track(track1)
        t2 = BollywoodChromosome._normalize_track(track2)

        dur1 = max((n['end'] for n in t1), default=segment_sec)
        dur2 = max((n['end'] for n in t2), default=segment_sec)
        total_dur = max(dur1, dur2)

        result = []
        seg_idx = 0
        cursor = 0.0

        while cursor < total_dur:
            seg_end = min(cursor + segment_sec, total_dur)
            src = t1 if seg_idx % 2 == 0 else t2
            src_dur = dur1 if seg_idx % 2 == 0 else dur2

            # How far into the source track this segment starts (with looping)
            src_cursor = cursor % src_dur if src_dur > 0 else 0.0
            src_seg_end = src_cursor + segment_sec

            for note in src:
                ns = note['start']
                ne = note['end']
                # Accept notes that start within [src_cursor, src_seg_end)
                if ns >= src_cursor and ns < src_seg_end:
                    new_start = cursor + (ns - src_cursor)
                    new_end   = cursor + min(ne - src_cursor, segment_sec)
                    if new_end > new_start:
                        result.append({
                            'pitch':    note['pitch'],
                            'start':    round(new_start, 4),
                            'end':      round(min(new_end, seg_end), 4),
                            'velocity': note.get('velocity', 80),
                            'duration': round(min(new_end, seg_end) - new_start, 4)
                        })

            cursor = seg_end
            seg_idx += 1

        return result

    @staticmethod
    def create_random(source_tracks):
        """
        Create random chromosome by BLENDING both songs track-by-track.
        Each slot (drums / bass / melody) is a per-slot interleave of song1 + song2,
        so both songs are genuinely heard throughout the mashup.
        """
        chromosome = BollywoodChromosome()
        chromosome.tracks = []

        # Separate the two songs' track lists
        song_track_lists = []
        for item in source_tracks:
            if item and isinstance(item[0], list):
                song_track_lists.append(item)   # Already a list of tracks
            elif item:
                song_track_lists.append([item]) # Single track — wrap

        # Ensure we have at least 2 songs; pad if needed
        while len(song_track_lists) < 2:
            song_track_lists.append([[], [], []])

        tracks1 = song_track_lists[0]
        tracks2 = song_track_lists[1]

        # Pad to 3 tracks each
        while len(tracks1) < 3: tracks1.append([])
        while len(tracks2) < 3: tracks2.append([])

        # For each slot, blend the two songs' corresponding tracks
        for i in range(3):
            t1 = tracks1[i] if tracks1[i] else []
            t2 = tracks2[i] if tracks2[i] else []

            blend_prob = random.random()
            if blend_prob < 0.7:
                # Proper interleave — both songs contribute
                seg = random.uniform(4.0, 8.0)   # Vary segment length for diversity
                blended = BollywoodChromosome._blend_two_tracks(t1, t2, segment_sec=seg)
                chromosome.tracks.append(blended)
            elif blend_prob < 0.85:
                # Mostly song1 with song2's notes scattered in
                chromosome.tracks.append([n.copy() for n in t1] if t1 else [n.copy() for n in t2])
            else:
                # Mostly song2
                chromosome.tracks.append([n.copy() for n in t2] if t2 else [n.copy() for n in t1])

        # Control genes
        chromosome.control_genes['pitch_shifts'] = [0, 0, 0]
        chromosome.control_genes['tempo_scales'] = [1.0, 1.0, 1.0]
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
                child1_tracks.append([note.copy() for note in self.tracks[i]] if self.tracks[i] else [])
                child2_tracks.append([note.copy() for note in other.tracks[i]] if other.tracks[i] else [])
            else:
                child1_tracks.append([note.copy() for note in other.tracks[i]] if other.tracks[i] else [])
                child2_tracks.append([note.copy() for note in self.tracks[i]] if self.tracks[i] else [])
        
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
        mutated = BollywoodChromosome()
        mutated.tracks = []
        
        # Deep copy tracks
        for track in self.tracks:
            if track:
                mutated.tracks.append([note.copy() for note in track])
            else:
                mutated.tracks.append([])
        
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
        
        return mutated
    
    def __str__(self):
        return f"Chromosome #{self.id} | Fitness: {self.fitness:.3f}"