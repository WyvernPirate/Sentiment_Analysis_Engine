"""Shared Flask extension instances.

Kept in their own module (rather than instantiated in app.py or models.py)
so both can import `db` without a circular-import.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
