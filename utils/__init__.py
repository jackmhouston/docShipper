"""
Shared Utilities for DocShipper
"""

from utils.timecode import TimecodeHandler


def sanitize_filename(filename: str) -> str:
    """Consistent filename sanitization for cross-platform compatibility."""
    sanitized = ''.join(c if c.isalnum() or c in ['_', '-', '.'] else '_' for c in filename)
    while '__' in sanitized:
        sanitized = sanitized.replace('__', '_')
    sanitized = sanitized.strip('_')
    return sanitized


__all__ = ["TimecodeHandler", "sanitize_filename"]
