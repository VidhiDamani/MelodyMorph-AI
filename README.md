# 🎵 Bollywood Mashup Generator using Genetic Algorithm

A genetic algorithm-based system that creates unique mashups by combining melodies from Bollywood songs. Select any two songs, and watch as the AI evolves them over generations to create something completely new!

## ✨ Features

- 🎼 **Genetic Algorithm Core**: Evolves melodies over 50+ generations to find optimal combinations
- 🎬 **Bollywood Focused**: Specifically designed for Hindi film music with raga-aware fitness functions
- 🎧 **15-Second Preview**: Listen to any song before generating (click the ▶️ button)
- 📊 **Real-time Visualization**: Watch fitness improve generation by generation
- 🎹 **MIDI Output**: Download and play generated mashups in any MIDI player
- 🌐 **Web Interface**: Beautiful, easy-to-use interface built with Flask

## 📋 Requirements

- Python 3.8+
- 4GB+ RAM (for dataset loading)
- 10GB+ free space (for MIDI dataset, optional)

## 🛠️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/bollywood-mashup-ga.git
cd bollywood-mashup-ga

# 2. Create virtual environment
python -m venv venv

# 3. Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt