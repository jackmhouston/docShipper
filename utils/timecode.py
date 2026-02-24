"""
Timecode Utilities for DocShipper
Shared timecode handling for both shotlist and music cue workflows
"""

import logging

logger = logging.getLogger(__name__)


class TimecodeHandler:
    """Advanced timecode handling with precision for various frame rates."""

    def __init__(self, frame_rate: float = 24.0):
        self.frame_rate = frame_rate

        # Handle common NTSC rates
        if abs(frame_rate - 23.976) < 0.001:
            self.drop_frame = False
            self.ntsc = True
            self.nominal_rate = 24
        elif abs(frame_rate - 29.97) < 0.001:
            self.drop_frame = True
            self.ntsc = True
            self.nominal_rate = 30
        else:
            self.drop_frame = False
            self.ntsc = False
            self.nominal_rate = round(frame_rate)

    def timecode_to_seconds(self, timecode: str) -> float:
        """Convert timecode (HH:MM:SS:FF) to seconds with high precision."""
        try:
            if not timecode or not isinstance(timecode, str):
                raise ValueError(f"Invalid timecode: {timecode}")

            parts = timecode.split(':')
            if len(parts) != 4:
                raise ValueError(f"Timecode must have 4 parts (HH:MM:SS:FF), got: {timecode}")

            for i, part in enumerate(parts):
                if not part.strip().isdigit():
                    raise ValueError(f"Non-numeric value in timecode '{timecode}' at position {i}: '{part}'")

            hours, minutes, seconds, frames = map(int, parts)

            total_frames = (
                hours * 3600 * self.frame_rate +
                minutes * 60 * self.frame_rate +
                seconds * self.frame_rate +
                frames
            )

            total_seconds = total_frames / self.frame_rate
            return round(total_seconds, 6)

        except Exception as e:
            logger.error(f"Error converting timecode {timecode} to seconds: {e}")
            raise

    def seconds_to_timecode(self, total_seconds: float) -> str:
        """Convert seconds to timecode string (HH:MM:SS:FF)."""
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        frames = round((total_seconds - int(total_seconds)) * self.frame_rate)
        return f"{hours:02}:{minutes:02}:{seconds:02}:{frames:02}"

    def calculate_duration(self, start_tc: str, end_tc: str) -> str:
        """Calculate duration between two timecodes."""
        start_seconds = self.timecode_to_seconds(start_tc)
        end_seconds = self.timecode_to_seconds(end_tc)
        duration_seconds = end_seconds - start_seconds

        if duration_seconds < 0:
            logger.error(f"Negative duration calculated between {start_tc} and {end_tc}")
            duration_seconds = 0

        return self.seconds_to_timecode(duration_seconds)

    def frames_to_timecode(self, frames: int) -> str:
        """Convert frame count to timecode format."""
        framerate = int(self.frame_rate)
        frame_remainder = frames % framerate
        seconds = (frames // framerate) % 60
        minutes = (frames // (framerate * 60)) % 60
        hours = frames // (framerate * 3600)
        return f"{hours:02}:{minutes:02}:{seconds:02}:{frame_remainder:02}"

    def ms_to_timecode(self, duration_ms: float) -> str:
        """Convert milliseconds to timecode."""
        framerate = int(self.frame_rate)
        total_frames = round((duration_ms / 1000) * framerate)
        frames = total_frames % framerate
        seconds = (total_frames // framerate) % 60
        minutes = (total_frames // (framerate * 60)) % 60
        hours = total_frames // (framerate * 3600)
        return f"{hours:02}:{minutes:02}:{seconds:02}:{frames:02}"

    @staticmethod
    def is_valid_timecode(tc: str) -> bool:
        """Check if a string looks like a valid timecode (HH:MM:SS:FF)."""
        if not tc or not isinstance(tc, str):
            return False
        parts = tc.split(':')
        if len(parts) != 4:
            return False
        return all(part.strip().isdigit() for part in parts)
