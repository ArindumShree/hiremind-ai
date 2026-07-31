import os
import sys

# Add the backend package to the import path so `app.main` resolves
# when Vercel runs this entrypoint from the repo root.
_BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend")
sys.path.insert(0, os.path.abspath(_BACKEND_DIR))

from app.main import app  # noqa: E402

# Vercel's Python runtime discovers the ASGI app via the `app` attribute.
application = app
