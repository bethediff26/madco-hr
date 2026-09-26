"""WSGI entry point for production servers (Gunicorn, Render, etc.)."""
import importlib.util
from pathlib import Path
import os

_app_file = Path(__file__).resolve().parent / "app.py"
_spec = importlib.util.spec_from_file_location("root_flask_app", _app_file)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

app = _mod.app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
