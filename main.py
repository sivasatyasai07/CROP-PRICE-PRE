import os
import sys

# Ensure backend directory is in Python module search path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "cropmandi-ai", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Set working directory to backend so database, models, and data folders resolve properly
os.chdir(backend_dir)

from app.main import app
