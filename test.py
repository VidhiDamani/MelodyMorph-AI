print("🎵 Bollywood Mashup Generator")
print("Checking if everything works...")

try:
    import numpy as np
    print("✅ NumPy works!")
    
    import pretty_midi
    print("✅ pretty_midi works!")
    
    import flask
    print("✅ Flask works!")
    
    print("\n🎉 All good! Ready to build!")
    
except Exception as e:
    print(f"❌ Error: {e}")