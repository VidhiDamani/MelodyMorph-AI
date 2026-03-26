"""
Genetic Algorithm for Bollywood Mashup Generation
"""

import random
import numpy as np
from typing import List, Dict
from tqdm import tqdm
import time
from .chromosome import BollywoodChromosome
from .fitness import BollywoodFitness

class BollywoodGA:
    """
    Genetic Algorithm for Bollywood Mashup Generation
    """
    
    def __init__(self, 
                 source_tracks: List[List],
                 source_features: Dict,
                 population_size: int = 50,
                 elite_size: int = 10,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.7):
        
        self.source_tracks = source_tracks
        self.source_features = source_features
        self.population_size = population_size
        self.elite_size = elite_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        
        self.fitness_calculator = BollywoodFitness(source_features)
        self.population = []
        self.generation = 0
        self.best_fitness_history = []
        self.avg_fitness_history = []
        
        self.start_time = None
        self.end_time = None
        
    def initialize_population(self):
        """Create initial random population"""
        print("🎵 Initializing population...")
        self.population = []
        for i in range(self.population_size):
            chromosome = BollywoodChromosome.create_random(self.source_tracks)
            self.population.append(chromosome)
        
        # Evaluate initial population
        self._evaluate_population()
        print(f"✅ Initialized {self.population_size} chromosomes")
        print(f"   Best fitness: {self.population[0].fitness:.3f}")
        
    def _evaluate_population(self):
        """Evaluate fitness for entire population"""
        for chromosome in self.population:
            self.fitness_calculator.evaluate(chromosome)
        
        # Sort by fitness (descending)
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        
    def _selection(self) -> List[BollywoodChromosome]:
        """
        Tournament selection
        """
        selected = []
        
        # Keep elites (best chromosomes)
        selected.extend(self.population[:self.elite_size])
        
        # Tournament selection for rest
        while len(selected) < self.population_size:
            # Pick 5 random chromosomes
            tournament = random.sample(self.population, min(5, len(self.population)))
            # Select the best from tournament
            winner = max(tournament, key=lambda x: x.fitness)
            selected.append(winner)
        
        return selected
    
    def _crossover(self, parent1, parent2):
        """
        Create children by mixing parents
        """
        if random.random() > self.crossover_rate:
            return parent1, parent2
        
        child1_tracks = []
        child2_tracks = []
        
        # Crossover point (track level)
        crossover_point = random.randint(0, len(parent1.tracks))
        
        for i in range(len(parent1.tracks)):
            if i < crossover_point:
                child1_tracks.append(parent1.tracks[i])
                child2_tracks.append(parent2.tracks[i])
            else:
                child1_tracks.append(parent2.tracks[i])
                child2_tracks.append(parent1.tracks[i])
        
        # Create children
        child1 = BollywoodChromosome(child1_tracks)
        child2 = BollywoodChromosome(child2_tracks)
        
        # Inherit control genes
        for key in parent1.control_genes:
            child1.control_genes[key] = parent1.control_genes[key].copy()
            child2.control_genes[key] = parent2.control_genes[key].copy()
            
            # Element-wise crossover for genes
            for i in range(len(parent1.control_genes[key])):
                if random.random() < 0.5:
                    child1.control_genes[key][i], child2.control_genes[key][i] = \
                        child2.control_genes[key][i], child1.control_genes[key][i]
        
        return child1, child2
    
    def _mutate(self, chromosome):
        """
        Apply random mutations
        """
        mutated = BollywoodChromosome([track[:] for track in chromosome.tracks])
        mutated.control_genes = {k: v.copy() for k, v in chromosome.control_genes.items()}
        
        # Mutate pitch shifts
        for i in range(len(mutated.control_genes['pitch_shifts'])):
            if random.random() < self.mutation_rate * 2: # Double chance
                # Change by a guaranteed offset
                mutated.control_genes['pitch_shifts'][i] += random.choice([-2, -1, 1, 2])
                # Keep in range
                mutated.control_genes['pitch_shifts'][i] = max(-5, min(5, 
                    mutated.control_genes['pitch_shifts'][i]))
        
        # Mutate tempo scales (bigger jumps)
        for i in range(len(mutated.control_genes['tempo_scales'])):
            if random.random() < self.mutation_rate * 2:
                # Change by 5-15%
                mutated.control_genes['tempo_scales'][i] *= random.choice([random.uniform(0.85, 0.95), random.uniform(1.05, 1.15)])
                # Keep in range
                mutated.control_genes['tempo_scales'][i] = max(0.8, min(1.2, 
                    mutated.control_genes['tempo_scales'][i]))
                mutated.control_genes['tempo_scales'][i] = round(
                    mutated.control_genes['tempo_scales'][i], 2)
        
        # Swap notes between tracks (rare)
        if random.random() < self.mutation_rate / 2:
            if len(mutated.tracks) >= 2:
                track1 = random.randint(0, len(mutated.tracks) - 1)
                track2 = random.randint(0, len(mutated.tracks) - 1)
                if (track1 != track2 and 
                    mutated.tracks[track1] and 
                    mutated.tracks[track2]):
                    idx1 = random.randint(0, len(mutated.tracks[track1]) - 1)
                    idx2 = random.randint(0, len(mutated.tracks[track2]) - 1)
                    (mutated.tracks[track1][idx1], 
                     mutated.tracks[track2][idx2]) = \
                        (mutated.tracks[track2][idx2], 
                         mutated.tracks[track1][idx1])
        
        return mutated
    
    def run(self, generations: int = 50):
        """
        Run the genetic algorithm
        """
        self.start_time = time.time()
        print(f"\n🎮 Starting GA with {generations} generations...")
        print("=" * 50)
        
        for gen in range(generations):
            self.generation = gen
            
            # Selection
            selected = self._selection()
            
            # Create new population through crossover
            new_population = []
            for i in range(0, len(selected) - 1, 2):
                if i + 1 < len(selected):
                    child1, child2 = self._crossover(selected[i], selected[i+1])
                    new_population.append(child1)
                    new_population.append(child2)
            
            # Mutation
            mutated_population = []
            for chromosome in new_population:
                mutated = self._mutate(chromosome)
                mutated_population.append(mutated)
            
            # Ensure population size
            while len(mutated_population) < self.population_size:
                mutated_population.append(
                    BollywoodChromosome.create_random(self.source_tracks)
                )
            
            self.population = mutated_population[:self.population_size]
            
            # Evaluate
            self._evaluate_population()
            
            # Track history
            self.best_fitness_history.append(self.population[0].fitness)
            self.avg_fitness_history.append(
                np.mean([c.fitness for c in self.population])
            )
            
            # Progress update every 5 generations
            if gen % 5 == 0 or gen == generations - 1:
                print(f"Gen {gen:3d} | Best: {self.population[0].fitness:.3f} | "
                      f"Avg: {self.avg_fitness_history[-1]:.3f}")
        
        self.end_time = time.time()
        
        # Final report
        print("=" * 50)
        print(f"✅ GA Complete!")
        print(f"   Best fitness: {self.population[0].fitness:.3f}")
        print(f"   Time taken: {self.end_time - self.start_time:.1f} seconds")
        print(f"   Generations: {generations}")
        
        return {
            'best_fitness': self.population[0].fitness,
            'best_fitness_components': self.population[0].fitness_components,
            'fitness_history': self.best_fitness_history,
            'avg_fitness_history': self.avg_fitness_history,
            'generations': generations,
            'time_taken': self.end_time - self.start_time
        }
    
    def get_best(self):
        """Return the best chromosome"""
        return self.population[0]
    
    def get_top_n(self, n):
        """Return top N chromosomes"""
        return self.population[:min(n, len(self.population))]
    
    def get_population_stats(self):
        """Get statistics about current population"""
        if not self.population:
            return {}
        
        fitnesses = [c.fitness for c in self.population]
        return {
            'best': max(fitnesses),
            'worst': min(fitnesses),
            'average': np.mean(fitnesses),
            'std': np.std(fitnesses),
            'size': len(self.population)
        }