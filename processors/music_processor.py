"""
Music Cue Processor for DocShipper
Handles Premiere XML parsing, audio metadata extraction, and cue sheet generation
Adapted from cuemaker.py for Streamlit integration
"""

import os
import xml.etree.ElementTree as ET
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Callable

import openpyxl
from pymediainfo import MediaInfo

from utils.timecode import TimecodeHandler

logger = logging.getLogger(__name__)


class MusicCueProcessor:
    """
    Music cue sheet processor for extracting audio metadata from Premiere XML
    and generating professional cue sheets in Excel format.
    """

    def __init__(self):
        self.tc_handler = TimecodeHandler(24)  # Default to 24fps

    def extract_audio_paths_from_xml(self, xml_path: str, filter_keyword: str = "alibi") -> Set[str]:
        """Extract audio file paths from Premiere XML."""
        audio_paths = set()
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            for file_elem in root.findall(".//file"):
                pathurl = file_elem.find("pathurl")
                if pathurl is not None and pathurl.text:
                    path = pathurl.text
                    clean_path = path.replace('file://localhost', '')
                    clean_path = clean_path.replace('%20', ' ')

                    filename = os.path.basename(clean_path).lower()
                    if filter_keyword.lower() in filename:
                        audio_paths.add(clean_path)

            return audio_paths
        except ET.ParseError as e:
            logger.error(f"Failed to parse XML: {e}")
            return set()

    def extract_sequence_framerate(self, xml_path: str) -> int:
        """Extract sequence framerate from XML, default to 24."""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            seq = root.find('.//sequence')
            if seq is not None:
                rate = seq.find('rate')
                if rate is not None:
                    timebase = rate.find('timebase')
                    if timebase is not None and timebase.text.isdigit():
                        return int(timebase.text)
        except Exception:
            pass
        return 24

    def extract_clip_timecodes_from_xml(self, xml_path: str) -> Dict[str, List[Dict]]:
        """Extract source in/out timecodes for each clip from XML."""
        clip_timecodes = {}
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            framerate = self.extract_sequence_framerate(xml_path)
            self.tc_handler = TimecodeHandler(framerate)

            for clipitem in root.findall(".//clipitem"):
                file_elem = clipitem.find("file")
                if file_elem is not None:
                    pathurl_elem = file_elem.find("pathurl")
                    if pathurl_elem is not None and pathurl_elem.text:
                        file_path = pathurl_elem.text.replace('file://localhost', '').replace('%20', ' ')
                        filename = os.path.basename(file_path)

                        in_elem = clipitem.find("in")
                        out_elem = clipitem.find("out")

                        if in_elem is not None and out_elem is not None:
                            try:
                                in_frames = int(in_elem.text)
                                out_frames = int(out_elem.text)

                                source_in = self.tc_handler.frames_to_timecode(in_frames)
                                source_out = self.tc_handler.frames_to_timecode(out_frames)
                                duration_frames = out_frames - in_frames
                                source_duration = self.tc_handler.frames_to_timecode(duration_frames)

                                if filename not in clip_timecodes:
                                    clip_timecodes[filename] = []

                                clip_timecodes[filename].append({
                                    'source_in': source_in,
                                    'source_out': source_out,
                                    'source_duration': source_duration
                                })
                            except (ValueError, TypeError):
                                continue

            return clip_timecodes
        except ET.ParseError as e:
            logger.error(f"Error parsing XML for timecodes: {e}")
            return {}

    def extract_metadata_row(self, file_path: str, framerate: int = 24,
                              clip_timecodes: Dict = None) -> Dict:
        """Extract metadata from an audio file."""
        filename = os.path.basename(file_path)
        cue_name = filename

        timecode_info = ""
        if clip_timecodes and filename in clip_timecodes:
            timecode_entries = []
            for tc in clip_timecodes[filename]:
                timecode_entries.append(f"In: {tc['source_in']} Out: {tc['source_out']} Duration: {tc['source_duration']}")
            timecode_info = " | ".join(timecode_entries)

        row = {
            'CUE NAME': cue_name,
            'FILE NAME': filename,
            'DURATION': '',
            'SOURCE TIMECODES': timecode_info,
            'ALBUM': '',
            'ALBUM/PERFORMER': '',
            'TRACK #': '',
            'GROUPING': '',
            'PERFORMER': '',
            'COMPOSER': '',
            'GENRE': '',
            'YEAR': '',
            'COMMENT': ''
        }

        try:
            media_info = MediaInfo.parse(file_path)
            tc_handler = TimecodeHandler(framerate)

            for track in media_info.tracks:
                if track.track_type == "General":
                    duration_ms = getattr(track, 'duration', None)
                    if duration_ms:
                        row['DURATION'] = tc_handler.ms_to_timecode(duration_ms)
                    row['ALBUM'] = getattr(track, 'album', '') or ''
                    row['ALBUM/PERFORMER'] = getattr(track, 'album_performer', '') or ''
                    row['TRACK #'] = getattr(track, 'track_name_position', '') or ''
                    row['GROUPING'] = getattr(track, 'grouping', '') or ''
                    row['PERFORMER'] = getattr(track, 'performer', '') or ''
                    row['COMPOSER'] = getattr(track, 'composer', '') or ''
                    row['GENRE'] = getattr(track, 'genre', '') or ''
                    row['YEAR'] = getattr(track, 'recorded_date', '') or ''
                    row['COMMENT'] = getattr(track, 'comment', '') or ''
        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {e}")

        return row

    def extract_project_info_from_xml(self, xml_path: str) -> Dict[str, str]:
        """Extract project information from XML for template header."""
        project_info = {
            'content_producer': '',
            'runtime': '',
            'project_title': '',
            'version': '',
            'featurette_title': '',
            'date': datetime.now().strftime("%Y-%m-%d")
        }

        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            sequence = root.find('.//sequence')
            if sequence is not None:
                name_elem = sequence.find('name')
                if name_elem is not None and name_elem.text:
                    project_info['project_title'] = name_elem.text
                    project_info['featurette_title'] = name_elem.text

                duration_elem = sequence.find('duration')
                if duration_elem is not None and duration_elem.text:
                    framerate = self.extract_sequence_framerate(xml_path)
                    frames = int(duration_elem.text)
                    tc_handler = TimecodeHandler(framerate)
                    runtime_timecode = tc_handler.frames_to_timecode(frames)
                    project_info['runtime'] = runtime_timecode

        except Exception as e:
            logger.error(f"Error extracting project info: {e}")

        return project_info

    def populate_excel_template(self, template_path: str, output_dir: str,
                                 audio_data: List[Dict], project_info: Dict) -> str:
        """Populate Excel template with extracted data."""
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template file not found: {template_path}")

        output_filename = f"CueSheet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        output_path = os.path.join(output_dir, output_filename)
        shutil.copy2(template_path, output_path)

        wb = openpyxl.load_workbook(output_path)
        ws = wb.active

        # Populate header information
        if project_info['content_producer']:
            ws['D2'] = project_info['content_producer']
        if project_info['runtime']:
            ws['H2'] = project_info['runtime']
        if project_info['project_title']:
            ws['D3'] = project_info['project_title']
        if project_info['version']:
            ws['H3'] = project_info['version']
        if project_info['featurette_title']:
            ws['D4'] = project_info['featurette_title']
        ws['H4'] = project_info['date']

        # Populate cue data starting from row 7
        for i, row_data in enumerate(audio_data):
            row_num = 7 + i

            ws[f'A{row_num}'] = f"{i + 1}.0"

            timecode_info = row_data.get('SOURCE TIMECODES', '')
            if 'In:' in timecode_info:
                try:
                    in_tc = timecode_info.split('In:')[1].split('Out:')[0].strip()
                    ws[f'B{row_num}'] = in_tc
                except:
                    ws[f'B{row_num}'] = "00:00:00"
            else:
                ws[f'B{row_num}'] = "00:00:00"

            if 'Out:' in timecode_info:
                try:
                    out_tc = timecode_info.split('Out:')[1].split('Duration:')[0].strip()
                    ws[f'C{row_num}'] = out_tc
                except:
                    ws[f'C{row_num}'] = row_data.get('DURATION', '00:00:00')
            else:
                ws[f'C{row_num}'] = row_data.get('DURATION', '00:00:00')

            ws[f'D{row_num}'] = row_data.get('CUE NAME', '')
            ws[f'E{row_num}'] = row_data.get('DURATION', '00:00:00')

            filename = row_data.get('FILE NAME', '').lower()
            if 'instrumental' in filename or 'inst' in filename:
                usage = 'BI'
            elif 'vocal' in filename or 'voice' in filename:
                usage = 'BV'
            else:
                usage = 'BV'
            ws[f'F{row_num}'] = usage

            ws[f'G{row_num}'] = 'Library'
            ws[f'H{row_num}'] = 'In Context'

            composer = row_data.get('COMPOSER', '')
            ws[f'I{row_num}'] = composer if composer else 'Unknown/Unknown'

            ws[f'J{row_num}'] = row_data.get('ALBUM', '') or 'Unknown'
            ws[f'K{row_num}'] = row_data.get('ALBUM/PERFORMER', '') or 'Library'

        wb.save(output_path)
        return output_path

    def process(self, xml_path: str, template_path: Optional[str], output_dir: str,
                filter_keyword: str = "alibi",
                progress_callback: Callable = None) -> Dict:
        """Complete music cue processing pipeline."""
        results = {
            'status': 'success',
            'message': '',
            'files': {},
            'cue_count': 0
        }

        try:
            if progress_callback:
                progress_callback(0.1, "Extracting project information...")

            project_info = self.extract_project_info_from_xml(xml_path)

            if progress_callback:
                progress_callback(0.2, "Extracting audio paths...")

            audio_paths = self.extract_audio_paths_from_xml(xml_path, filter_keyword)
            if not audio_paths:
                results['status'] = 'warning'
                results['message'] = f"No audio files found containing '{filter_keyword}'"
                return results

            if progress_callback:
                progress_callback(0.3, "Extracting clip timecodes...")

            framerate = self.extract_sequence_framerate(xml_path)
            clip_timecodes = self.extract_clip_timecodes_from_xml(xml_path)

            if progress_callback:
                progress_callback(0.4, "Processing audio metadata...")

            processed_filenames = set()
            audio_data = []
            total_files = len(audio_paths)

            for i, file_path in enumerate(audio_paths):
                if progress_callback:
                    progress = 0.4 + (0.4 * i / total_files)
                    progress_callback(progress, f"Processing file {i + 1}/{total_files}")

                if not os.path.exists(file_path):
                    logger.warning(f"File not found: {file_path}")
                    continue

                filename = os.path.basename(file_path)
                if filename in processed_filenames:
                    continue

                row_data = self.extract_metadata_row(file_path, framerate, clip_timecodes)
                audio_data.append(row_data)
                processed_filenames.add(filename)

            audio_data.sort(key=lambda x: x['CUE NAME'].lower())

            if progress_callback:
                progress_callback(0.9, "Generating Excel output...")

            if template_path and os.path.exists(template_path):
                output_path = self.populate_excel_template(template_path, output_dir, audio_data, project_info)
            else:
                output_path = self._create_basic_cue_sheet(output_dir, audio_data, project_info)

            if progress_callback:
                progress_callback(1.0, "Processing complete!")

            results['files']['excel'] = output_path
            results['cue_count'] = len(audio_data)
            results['message'] = f"Successfully processed {len(audio_data)} music cues"

            return results

        except Exception as e:
            logger.error(f"Music cue processing failed: {e}")
            results['status'] = 'error'
            results['message'] = str(e)
            return results

    def _create_basic_cue_sheet(self, output_dir: str, audio_data: List[Dict],
                                 project_info: Dict) -> str:
        """Create a basic cue sheet without a template."""
        output_filename = f"CueSheet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        output_path = os.path.join(output_dir, output_filename)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Music Cues"

        # Headers
        headers = ['Cue #', 'TC In', 'TC Out', 'Cue Name', 'Duration', 'Use',
                   'Source', 'Context', 'Composer', 'Publisher', 'Library']
        for col, header in enumerate(headers, 1):
            ws.cell(row=1, column=col, value=header)

        # Data
        for i, row_data in enumerate(audio_data):
            row_num = i + 2
            timecode_info = row_data.get('SOURCE TIMECODES', '')

            tc_in = "00:00:00"
            tc_out = row_data.get('DURATION', '00:00:00')
            if 'In:' in timecode_info:
                try:
                    tc_in = timecode_info.split('In:')[1].split('Out:')[0].strip()
                    tc_out = timecode_info.split('Out:')[1].split('Duration:')[0].strip()
                except:
                    pass

            filename = row_data.get('FILE NAME', '').lower()
            usage = 'BI' if 'instrumental' in filename or 'inst' in filename else 'BV'

            ws.cell(row=row_num, column=1, value=f"{i + 1}.0")
            ws.cell(row=row_num, column=2, value=tc_in)
            ws.cell(row=row_num, column=3, value=tc_out)
            ws.cell(row=row_num, column=4, value=row_data.get('CUE NAME', ''))
            ws.cell(row=row_num, column=5, value=row_data.get('DURATION', ''))
            ws.cell(row=row_num, column=6, value=usage)
            ws.cell(row=row_num, column=7, value='Library')
            ws.cell(row=row_num, column=8, value='In Context')
            ws.cell(row=row_num, column=9, value=row_data.get('COMPOSER', 'Unknown'))
            ws.cell(row=row_num, column=10, value=row_data.get('ALBUM', 'Unknown'))
            ws.cell(row=row_num, column=11, value=row_data.get('ALBUM/PERFORMER', 'Library'))

        wb.save(output_path)
        return output_path
