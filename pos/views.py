"""
Backward-compatible re-export module.

We keep `pos/views.py` so existing imports keep working, while the
implementation is organized into:

- `pos/views/pages.py`
- `pos/views/api.py`
"""

from .views import *  # noqa: F403,F401

