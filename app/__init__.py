# MadCo HR Agent API package
import importlib.util
from pathlib import Path

# Expose Flask app from root app.py so `gunicorn app:app` resolves properly
_app_file = Path(__file__).resolve().parent.parent / "app.py"
if _app_file.exists():
    _spec = importlib.util.spec_from_file_location("root_flask_app", _app_file)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    app = getattr(_mod, "app", None)
