"""Plugin registration for ErrorFile inspectors."""

from .base import InspectorCallable
from .defaults import load_default_plugins

__all__ = ["InspectorCallable", "load_default_plugins"]
