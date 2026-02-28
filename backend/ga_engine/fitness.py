"""
Fitness functions for evaluating Bollywood mashups
"""

import numpy as np
from typing import Dict, List

class BollywoodFitness:
    """
    Comprehensive fitness evaluation for Bollywood mashups
    """
    
    def __init__(self, source_features):
        self.source_features = source_features
        self.weights = {
            'raga': 0.30,        # 30% - Raga compatibility
            'rhythm': 0.25,       # 25% - Rhythmic compatibility
            'melody': 0.20,       # 20% - Melodic interest
            'transition': 0.15,    # 15% - Smooth transitions
            'density': 0.10        # 10% - Note density match
        }
        
    def evaluate(self, chromosome):
        """
        Evaluate all fitness components
        Returns dictionary of scores
        """
        scores = {}
        
        # Calculate each component
        scores['raga'] = self._calculate_raga_score(chromosome)
        scores['rhythm'] = self._calculate_rhythm_score(chromosome)
        scores['melody'] = self._calculate_melody_score(chromosome)
        scores['transition'] = self._calculate_transition_score(chromosome)
        scores['density'] = self._calculate_density_score(chromosome)
        
        # Calculate weighted total
        total_fitness = sum(
            scores[key] * self.weights[key] 
            for key in scores
        )
        
        # Store in chromosome
        chromosome.fitness = total_fitness
        chromosome.fitness_components = scores
        
        return scores
    
    def _calculate_raga_score(self, chromosome):
        """
        Measure how well mashup preserves raga characteristics
        """
        try:
            # Get melody track (usually index 2)
            melody_track = chromosome.tracks[2] if len(chromosome.tracks) > 2 else []
            
            if not melody_track or len(melody_track) < 5:
                return 0.5
            
            # Extract pitch classes (0-11)
            pitch_classes = [note['pitch'] % 12 for note in melody_track]
            unique_pitches = set(pitch_classes)
            
            # Get source raga notes
            raga1_notes = set(self.source_features.get('raga1', {}).get('notes', []))
            raga2_notes = set(self.source_features.get('raga2', {}).get('notes', []))
            
            if not raga1_notes or not raga2_notes:
                return 0.5
            
            # Calculate overlap with both ragas
            overlap1 = len(unique_pitches & raga1_notes) / len(raga1_notes)
            overlap2 = len(unique_pitches & raga2_notes) / len(raga2_notes)
            
            # Take average
            score = (overlap1 + overlap2) / 2
            
            # Bonus for characteristic notes
            vadi1 = self.source_features.get('raga1', {}).get('vadi')
            vadi2 = self.source_features.get('raga2', {}).get('vadi')
            
            if vadi1 and vadi1 in unique_pitches:
                score += 0.1
            if vadi2 and vadi2 in unique_pitches:
                score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            print(f"Raga score error: {e}")
            return 0.5
    
    def _calculate_rhythm_score(self, chromosome):
        """
        Check rhythmic consistency
        """
        try:
            # Get drum track (usually index 0)
            drum_track = chromosome.tracks[0] if len(chromosome.tracks) > 0 else []
            
            if len(drum_track) < 4:
                return 0.5
            
            # Calculate time between drum hits
            hit_times = [note['start'] for note in drum_track]
            intervals = np.diff(hit_times)
            
            if len(intervals) == 0:
                return 0.5
            
            # Check regularity (low standard deviation is good)
            interval_std = np.std(intervals)
            max_std = 0.5  # Maximum expected std deviation
            
            # Convert to score (lower std = higher score)
            score = 1.0 / (1.0 + interval_std / max_std)
            
            return min(1.0, score)
            
        except Exception:
            return 0.5
    
    def _calculate_melody_score(self, chromosome):
        """
        Evaluate melodic interest (variety in intervals)
        """
        try:
            melody_track = chromosome.tracks[2] if len(chromosome.tracks) > 2 else []
            
            if len(melody_track) < 3:
                return 0.5
            
            # Calculate intervals between consecutive notes
            intervals = []
            for i in range(1, len(melody_track)):
                interval = abs(melody_track[i]['pitch'] - melody_track[i-1]['pitch'])
                intervals.append(interval)
            
            if not intervals:
                return 0.5
            
            # Good variety in intervals (not all same)
            unique_intervals = len(set(intervals))
            variety_score = min(1.0, unique_intervals / 5)  # Expect ~5 unique intervals
            
            # Not too many large jumps
            large_jumps = sum(1 for i in intervals if i > 12)
            jump_penalty = large_jumps / len(intervals) if intervals else 0
            
            score = variety_score * (1 - jump_penalty * 0.5)
            
            return min(1.0, max(0.2, score))
            
        except Exception:
            return 0.5
    
    def _calculate_transition_score(self, chromosome):
        """
        How smooth are transitions between phrases
        """
        try:
            melody_track = chromosome.tracks[2] if len(chromosome.tracks) > 2 else []
            
            if len(melody_track) < 8:
                return 0.5
            
            # Split into 4 phrases
            phrase_length = len(melody_track) // 4
            phrases = []
            for i in range(4):
                start = i * phrase_length
                end = start + phrase_length
                if start < len(melody_track):
                    phrases.append(melody_track[start:end])
            
            if len(phrases) < 2:
                return 0.5
            
            # Check transitions between phrases
            transition_scores = []
            for i in range(len(phrases) - 1):
                if phrases[i] and phrases[i+1]:
                    last_note = phrases[i][-1]['pitch']
                    first_note = phrases[i+1][0]['pitch']
                    interval = abs(last_note - first_note)
                    
                    # Small interval = smooth transition
                    transition_scores.append(1.0 / (1.0 + interval / 12))
            
            return np.mean(transition_scores) if transition_scores else 0.5
            
        except Exception:
            return 0.5
    
    def _calculate_density_score(self, chromosome):
        """
        Check if note density matches source styles
        """
        try:
            # Get source densities
            source1_density = self.source_features.get('density1', 4.0)
            source2_density = self.source_features.get('density2', 4.0)
            
            # Calculate target density (average)
            target_density = (source1_density + source2_density) / 2
            
            # Calculate actual density
            all_notes = []
            for track in chromosome.tracks:
                all_notes.extend(track)
            
            if len(all_notes) < 2:
                return 0.5
            
            # Notes per second
            time_range = all_notes[-1]['end'] - all_notes[0]['start']
            actual_density = len(all_notes) / time_range if time_range > 0 else 4.0
            
            # Score based on how close to target
            density_ratio = min(target_density, actual_density) / max(target_density, actual_density)
            
            return density_ratio
            
        except Exception:
            return 0.5