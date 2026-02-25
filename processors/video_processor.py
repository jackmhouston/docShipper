"""
Video Processing Module for DocShipper
Handles EDL parsing, video analysis, screenshot generation, and Excel updates
"""

import subprocess
import json
import logging
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Callable
import openpyxl
from openpyxl.drawing.image import Image

from utils.timecode import TimecodeHandler

logger = logging.getLogger(__name__)


class EDLParser:
    """Enhanced EDL parser for various formats."""

    def __init__(self):
        self.clip_patterns = [
            r'^\* FROM CLIP NAME:\s*(.+)$',
            r'^\* CLIP NAME:\s*(.+)$',
            r'^\*\s*(.+\.mov)$',
            r'^\*\s*(.+\.mp4)$',
        ]

    def _is_valid_timecode(self, tc: str) -> bool:
        """Check if a string looks like a valid timecode (HH:MM:SS:FF)."""
        return TimecodeHandler.is_valid_timecode(tc)

    def parse(self, edl_path: str) -> List[Dict]:
        """Parse EDL file and extract shot information."""
        try:
            with open(edl_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            with open(edl_path, 'r', encoding='latin-1') as file:
                lines = file.readlines()

        edl_data = []
        current_event = None
        line_number = 0

        logger.info(f"Parsing EDL: {edl_path}")
        logger.info(f"Total lines in EDL: {len(lines)}")

        for line in lines:
            line_number += 1
            line = line.strip()

            if not line:
                continue

            # Check for edit events (lines starting with numbers)
            if line and line[0].isdigit():
                if current_event:
                    edl_data.append(current_event)
                current_event = None

                line_parts = line.split()
                if len(line_parts) >= 8:
                    track_type = line_parts[2]

                    # Only process VIDEO tracks
                    if track_type.upper().startswith('V'):
                        reel_name = line_parts[1]

                        # Skip BL (blank/black) events
                        if reel_name.upper() == 'BL':
                            logger.debug(f"Line {line_number}: Skipping blank (BL) event")
                            continue

                        src_start = line_parts[4]
                        src_end = line_parts[5]
                        rec_start = line_parts[6]
                        rec_end = line_parts[7]

                        if not (self._is_valid_timecode(src_start) and
                                self._is_valid_timecode(src_end) and
                                self._is_valid_timecode(rec_start) and
                                self._is_valid_timecode(rec_end)):
                            logger.warning(f"Line {line_number}: Invalid timecode format, skipping")
                            continue

                        current_event = {
                            'Event': line_parts[0],
                            'Reel': reel_name,
                            'Track': track_type,
                            'Transition': line_parts[3],
                            'Src Start': src_start,
                            'Src End': src_end,
                            'Rec Start': rec_start,
                            'Rec End': rec_end,
                            'Clip Name': None
                        }
                        logger.debug(f"Line {line_number}: Parsed video track event {line_parts[0]}")
                continue

            # Look for clip names
            for pattern in self.clip_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    clip_name = match.group(1).strip()
                    if current_event:
                        current_event['Clip Name'] = clip_name
                    break

        if current_event:
            edl_data.append(current_event)

        logger.info(f"Parsed {len(edl_data)} events from EDL")
        return edl_data


class XMLParser:
    """Parser for Premiere Pro Final Cut Pro XML exports."""

    def parse(self, xml_path: str) -> List[Dict]:
        """Parse Premiere XML into shot rows compatible with EDL output."""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except ET.ParseError as e:
            logger.error(f"Failed to parse XML file {xml_path}: {e}")
            return []

        sequence = root.find('.//sequence')
        if sequence is None:
            logger.error("No sequence found in XML file")
            return []

        # Premiere XML commonly stores 24 + ntsc TRUE to represent 23.976 timelines.
        frame_rate = 24.0
        rate_elem = sequence.find('.//rate')
        if rate_elem is not None:
            timebase = rate_elem.find('timebase')
            ntsc = rate_elem.find('ntsc')
            if timebase is not None and timebase.text:
                try:
                    frame_rate = float(timebase.text)
                except ValueError:
                    frame_rate = 24.0
            if ntsc is not None and ntsc.text and ntsc.text.upper() == 'TRUE':
                if frame_rate == 24:
                    frame_rate = 23.976
                elif frame_rate == 30:
                    frame_rate = 29.97
                elif frame_rate == 60:
                    frame_rate = 59.94

        tc_handler = TimecodeHandler(frame_rate)
        xml_data: List[Dict] = []
        event_number = 0

        for track in sequence.findall('.//video/track'):
            for clipitem in track.findall('clipitem'):
                enabled = clipitem.find('enabled')
                if enabled is not None and enabled.text and enabled.text.upper() == 'FALSE':
                    continue

                name_elem = clipitem.find('name')
                clip_name = name_elem.text if name_elem is not None else None
                if clip_name and clip_name.lower() in ['black video', 'black', 'blank']:
                    continue

                start_elem = clipitem.find('start')
                end_elem = clipitem.find('end')
                in_elem = clipitem.find('in')
                out_elem = clipitem.find('out')
                if start_elem is None or end_elem is None:
                    continue

                try:
                    start_frame = int(start_elem.text) if start_elem.text != '-1' else 0
                    end_frame = int(end_elem.text) if end_elem.text != '-1' else 0
                    in_frame = int(in_elem.text) if in_elem is not None and in_elem.text else 0
                    out_frame = int(out_elem.text) if out_elem is not None and out_elem.text else 0
                except (TypeError, ValueError):
                    continue

                if end_frame <= start_frame:
                    continue

                event_number += 1
                xml_data.append({
                    'Event': str(event_number).zfill(3),
                    'Reel': 'AX',
                    'Track': 'V',
                    'Transition': 'C',
                    'Src Start': tc_handler.frames_to_timecode(in_frame),
                    'Src End': tc_handler.frames_to_timecode(out_frame),
                    'Rec Start': tc_handler.frames_to_timecode(start_frame),
                    'Rec End': tc_handler.frames_to_timecode(end_frame),
                    'Clip Name': clip_name,
                })

        logger.info(f"Parsed {len(xml_data)} clips from XML")
        return xml_data


class VideoAnalyzer:
    """Video file analysis and frame rate detection."""

    def get_video_frame_rate(self, video_file: str) -> Optional[float]:
        """Get video frame rate using ffprobe."""
        command = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=r_frame_rate,avg_frame_rate,time_base',
            '-of', 'json',
            video_file
        ]

        try:
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = json.loads(result.stdout)

            r_frame_rate = output['streams'][0].get('r_frame_rate', '')
            if r_frame_rate:
                try:
                    num, den = map(int, r_frame_rate.split('/'))
                    if num and den:
                        frame_rate = num / den
                        if abs(frame_rate - 23.976) < 0.01:
                            return 23.976
                        if abs(frame_rate - 29.97) < 0.01:
                            return 29.97
                        return frame_rate
                except (ValueError, ZeroDivisionError):
                    pass

            avg_frame_rate = output['streams'][0].get('avg_frame_rate', '')
            if avg_frame_rate:
                try:
                    num, den = map(int, avg_frame_rate.split('/'))
                    if num and den:
                        return num / den
                except (ValueError, ZeroDivisionError):
                    pass

            logger.error(f'Failed to parse frame rate for {video_file}')
            return None

        except subprocess.CalledProcessError as e:
            logger.error(f'Failed to get frame rate for {video_file}: {e}')
            return None


class ScreenshotGenerator:
    """Advanced screenshot generation with retry logic."""

    def __init__(self, video_analyzer: VideoAnalyzer):
        self.video_analyzer = video_analyzer

    def _sanitize_filename(self, filename: str) -> str:
        """Consistent filename sanitization for cross-platform compatibility."""
        sanitized = ''.join(c if c.isalnum() or c in ['_', '-', '.'] else '_' for c in filename)
        while '__' in sanitized:
            sanitized = sanitized.replace('__', '_')
        sanitized = sanitized.strip('_')
        return sanitized

    def capture_screenshot(self, video_file: str, timecode_start: str, timecode_end: str,
                           shot_number: int, clip_name: str, frame_rate: float,
                           screenshot_dir: str) -> bool:
        """Capture screenshot at specific timecode with retry logic."""
        try:
            tc_handler = TimecodeHandler(frame_rate)

            start_seconds = tc_handler.timecode_to_seconds(timecode_start)
            end_seconds = tc_handler.timecode_to_seconds(timecode_end)
            clip_duration = end_seconds - start_seconds

            one_frame = 1.0 / frame_rate
            max_offset = clip_duration * 0.1
            safe_offset = min(one_frame, max_offset) if clip_duration > 0 else 0

            time_in_seconds = start_seconds + safe_offset

            if clip_name is None or clip_name.strip() == '':
                clean_clip_name = f"Shot{str(shot_number).zfill(3)}"
            else:
                clean_clip_name = f"Shot{str(shot_number).zfill(3)}_{clip_name}"
                clean_clip_name = self._sanitize_filename(clean_clip_name)
                clean_clip_name = clean_clip_name[:200]

            output_file = os.path.join(screenshot_dir, f'{clean_clip_name}.png')
            os.makedirs(screenshot_dir, exist_ok=True)

            command = [
                'ffmpeg',
                '-y',
                '-ss', f"{time_in_seconds:.6f}",
                '-i', video_file,
                '-frames:v', '1',
                '-q:v', '2',
                '-vf', 'scale=203:120:force_original_aspect_ratio=decrease,pad=203:120:(ow-iw)/2:(oh-ih)/2',
                output_file
            ]

            logger.info(f"Processing shot {shot_number}: {clean_clip_name}")
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode != 0:
                logger.warning(f"Primary method failed for shot {shot_number}, trying alternative")
                command = [
                    'ffmpeg',
                    '-y',
                    '-i', video_file,
                    '-ss', f"{time_in_seconds:.6f}",
                    '-frames:v', '1',
                    '-q:v', '2',
                    '-vf', 'scale=203:120:force_original_aspect_ratio=decrease,pad=203:120:(ow-iw)/2:(oh-ih)/2',
                    output_file
                ]
                result = subprocess.run(command, capture_output=True, text=True)

            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                logger.info(f"Successfully created screenshot: {output_file}")
                return True
            else:
                logger.error(f"Screenshot not created or empty for shot {shot_number}")
                return False

        except Exception as e:
            logger.error(f"Error capturing screenshot for shot {shot_number}: {e}")
            return False


class ExcelUpdater:
    """Excel template updating with image insertion."""

    def _sanitize_filename(self, filename: str) -> str:
        """Consistent filename sanitization for cross-platform compatibility."""
        sanitized = ''.join(c if c.isalnum() or c in ['_', '-', '.'] else '_' for c in filename)
        while '__' in sanitized:
            sanitized = sanitized.replace('__', '_')
        sanitized = sanitized.strip('_')
        return sanitized

    def update_template(self, template_path: Optional[str], edl_data: List[Dict],
                        mappings: Dict[str, str], screenshot_dir: str,
                        output_path: str) -> str:
        """Update Excel template with EDL data and screenshots."""
        try:
            if template_path and os.path.exists(template_path):
                try:
                    wb = openpyxl.load_workbook(template_path)
                    ws = wb.active
                    logger.info(f"Successfully loaded template: {template_path}")
                except Exception as e:
                    logger.error(f"Failed to load template {template_path}: {e}")
                    wb = openpyxl.Workbook()
                    ws = wb.active
                    ws.title = "Shotlist"
                    self._add_headers(ws, mappings)
            else:
                logger.info("No template provided, creating new workbook")
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "Shotlist"
                self._add_headers(ws, mappings)

            field_mapping = {
                'clip_name': 'Clip Name',
                'src_start': 'Src Start',
                'src_end': 'Src End',
                'rec_start': 'Rec Start',
                'rec_end': 'Rec End',
                'duration': 'Duration'
            }

            for field, cell_ref in mappings.items():
                if field == 'screenshot':
                    continue

                edl_field = field_mapping.get(field)
                if not edl_field:
                    continue

                try:
                    col_letter = ''.join(filter(str.isalpha, cell_ref))
                    start_row = int(''.join(filter(str.isdigit, cell_ref)))

                    for i, shot in enumerate(edl_data):
                        value = shot.get(edl_field, '')
                        ws[f'{col_letter}{start_row + i}'] = value

                    logger.info(f"Successfully mapped {field} to column {col_letter}")

                except Exception as e:
                    logger.error(f"Error mapping {field} to cell {cell_ref}: {e}")
                    continue

            if 'screenshot' in mappings:
                self._insert_screenshots(ws, mappings['screenshot'], edl_data, screenshot_dir)

            wb.save(output_path)
            logger.info(f"Excel file saved as: {output_path}")

            return output_path

        except Exception as e:
            logger.error(f"Error updating Excel template: {e}")
            raise

    def _add_headers(self, ws, mappings: Dict[str, str]):
        """Add headers to new workbook."""
        header_names = {
            'clip_name': 'Clip Name',
            'src_start': 'Source Start',
            'src_end': 'Source End',
            'rec_start': 'Record Start',
            'rec_end': 'Record End',
            'duration': 'Duration',
            'screenshot': 'Screenshot'
        }

        for field, cell_ref in mappings.items():
            try:
                col_letter = ''.join(filter(str.isalpha, cell_ref))
                row_num = int(''.join(filter(str.isdigit, cell_ref)))
                header_row = row_num - 1

                header_name = header_names.get(field, field.replace('_', ' ').title())
                ws[f'{col_letter}{header_row}'] = header_name

            except Exception as e:
                logger.error(f"Error adding header for {field}: {e}")

    def _insert_screenshots(self, ws, screenshot_cell: str, edl_data: List[Dict], screenshot_dir: str):
        """Insert screenshots into Excel."""
        try:
            col_letter = ''.join(filter(str.isalpha, screenshot_cell))
            start_row = int(''.join(filter(str.isdigit, screenshot_cell)))

            for i, shot in enumerate(edl_data):
                clip_name = shot.get('Clip Name', '') or ''
                if clip_name:
                    clean_clip_name = f"Shot{str(i + 1).zfill(3)}_{clip_name}"
                    clean_clip_name = self._sanitize_filename(clean_clip_name)
                    screenshot_name = f"{clean_clip_name}.png"
                else:
                    screenshot_name = f"Shot{str(i + 1).zfill(3)}.png"

                screenshot_path = os.path.join(screenshot_dir, screenshot_name)

                if not os.path.exists(screenshot_path):
                    fallback_name = f"Shot{str(i + 1).zfill(3)}.png"
                    fallback_path = os.path.join(screenshot_dir, fallback_name)
                    if os.path.exists(fallback_path):
                        screenshot_path = fallback_path

                if os.path.exists(screenshot_path):
                    try:
                        img = Image(screenshot_path)
                        img.width = 203
                        img.height = 120
                        cell_position = f'{col_letter}{start_row + i}'
                        ws.add_image(img, cell_position)
                        logger.info(f"Added screenshot to {cell_position}")
                    except Exception as e:
                        logger.error(f"Error adding screenshot {screenshot_path}: {e}")
                else:
                    logger.warning(f"Screenshot not found: {screenshot_path}")

            logger.info(f"Screenshots insertion completed for column {col_letter}")

        except Exception as e:
            logger.error(f"Error inserting screenshots: {e}")


class VideoProcessor:
    """Main video processing orchestrator."""

    def __init__(self):
        self.edl_parser = EDLParser()
        self.xml_parser = XMLParser()
        self.video_analyzer = VideoAnalyzer()
        self.screenshot_generator = ScreenshotGenerator(self.video_analyzer)
        self.excel_updater = ExcelUpdater()

    def _detect_file_type(self, file_path: str) -> str:
        """Detect input list file type."""
        ext = Path(file_path).suffix.lower()
        if ext == '.xml':
            return 'xml'
        return 'edl'

    def process(self, edl_path: str, video_path: str, template_path: str,
                mappings: Dict[str, str], output_dir: str,
                progress_callback: Callable = None,
                edl_data_override: Optional[List[Dict]] = None,
                disable_screenshots: bool = False,
                show_name: Optional[str] = None) -> Dict[str, str]:
        """Complete processing pipeline."""

        results = {
            'status': 'success',
            'message': '',
            'files': {}
        }

        try:
            if progress_callback:
                progress_callback(0.1, "Preparing edit list data...")

            if edl_data_override is not None:
                edl_data = edl_data_override
                logger.info(f"Using EDL data override with {len(edl_data)} rows")
            else:
                file_type = self._detect_file_type(edl_path)
                if file_type == 'xml':
                    edl_data = self.xml_parser.parse(edl_path)
                    if not edl_data:
                        raise Exception("No data found in XML file")
                    logger.info(f"Parsed {len(edl_data)} shots from XML")
                else:
                    edl_data = self.edl_parser.parse(edl_path)
                    if not edl_data:
                        raise Exception("No data found in EDL file")
                    logger.info(f"Parsed {len(edl_data)} shots from EDL")

            if progress_callback:
                progress_callback(0.2, "Analyzing video file...")

            frame_rate = self.video_analyzer.get_video_frame_rate(video_path)
            if frame_rate is None:
                raise Exception("Failed to detect video frame rate")

            logger.info(f"Detected frame rate: {frame_rate} fps")

            if progress_callback:
                progress_callback(0.3, "Calculating durations...")

            tc_handler = TimecodeHandler(frame_rate)
            valid_shots = []
            skipped_shots = []

            for i, shot in enumerate(edl_data, 1):
                try:
                    clip_name = shot.get('Clip Name', '') or ''
                    if clip_name.lower().strip() == 'black video':
                        skipped_shots.append(i)
                        continue

                    if 'Src Start' in shot and 'Src End' in shot:
                        src_start = shot['Src Start']
                        src_end = shot['Src End']

                        if not src_start or not src_end or src_start == 'B' or src_end == 'B':
                            skipped_shots.append(i)
                            continue

                        duration = tc_handler.calculate_duration(src_start, src_end)
                        shot['Duration'] = duration
                        valid_shots.append(shot)
                    else:
                        skipped_shots.append(i)
                except Exception as e:
                    logger.error(f"Error processing shot {i}: {e}")
                    skipped_shots.append(i)
                    continue

            if not valid_shots:
                raise Exception("No valid shots found in EDL after filtering")

            edl_data = valid_shots

            successful_screenshots = 0
            screenshot_dir = os.path.join(output_dir, 'screenshots')
            total_shots = len(edl_data)

            if not disable_screenshots:
                if progress_callback:
                    progress_callback(0.4, "Generating screenshots...")
                os.makedirs(screenshot_dir, exist_ok=True)
                for i, shot in enumerate(edl_data, 1):
                    if progress_callback:
                        progress = 0.4 + (0.4 * i / total_shots)
                        progress_callback(progress, f"Generating screenshot {i}/{total_shots}")
                    success = self.screenshot_generator.capture_screenshot(
                        video_path,
                        shot.get('Rec Start', shot.get('Src Start', '00:00:00:00')),
                        shot.get('Rec End', shot.get('Src End', '00:00:00:00')),
                        i,
                        shot.get('Clip Name', ''),
                        frame_rate,
                        screenshot_dir
                    )
                    if success:
                        successful_screenshots += 1
                logger.info(f"Generated {successful_screenshots}/{total_shots} screenshots")
            else:
                logger.info("Screenshot generation disabled by user setting")

            if progress_callback:
                progress_callback(0.9, "Updating Excel template...")

            if edl_path:
                base_name = Path(edl_path).stem
            elif show_name:
                base_name = show_name.replace(' ', '_')
            else:
                base_name = Path(video_path).stem
            output_excel = os.path.join(output_dir, f'{base_name}_shotlist.xlsx')

            final_excel = self.excel_updater.update_template(
                template_path, edl_data, mappings, screenshot_dir, output_excel
            )

            if progress_callback:
                progress_callback(1.0, "Processing complete!")

            results['files'] = {
                'excel': final_excel,
            }
            if not disable_screenshots:
                results['files']['screenshots'] = screenshot_dir
            results['files']['csv'] = os.path.join(output_dir, f'{base_name}_shotlist.csv')

            screenshot_note = f" with {successful_screenshots} screenshots" if not disable_screenshots else " (screenshots disabled)"
            results['message'] = f"Successfully processed {len(edl_data)} shots{screenshot_note}"

            return results

        except Exception as e:
            logger.error(f"Processing failed: {e}")
            results['status'] = 'error'
            results['message'] = str(e)
            return results
