#!/usr/bin/env python3
"""
Backward-compatible app entrypoint.

This file is kept for legacy scripts/tests that still run `python simple_app.py`.
The canonical backend entrypoint is `app.py`.
"""

import os

from app import app
from config import Config


if __name__ == '__main__':
    debug_env = os.getenv('FLASK_DEBUG')
    if debug_env is not None:
        debug_mode = debug_env.lower() == 'true'
    else:
        debug_mode = getattr(Config, 'DEBUG', False)

    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))

    app.run(debug=debug_mode, host=host, port=port)
