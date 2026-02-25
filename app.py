#!/usr/bin/env python3
"""
DocShipper - Video Editing Document Automation
Page-based wizard interface with minimal B/W aesthetic
XML-first unified workflow
"""

import atexit
import streamlit as st
import pandas as pd
from pathlib import Path
import tempfile
import os
import logging
from typing import Dict, Optional

import defusedxml.ElementTree as ET

# Import UI components
from ui import inject_styles
from ui.components import (
    _num_to_col,
    landing_header,
    workflow_button,
    step_indicator,
    page_title,
    section_header,
    nav_buttons,
    render_interactive_grid,
    field_checkboxes,
    field_assignment_panel,
    file_status,
    status_row,
    divider,
    primary_button,
    secondary_button,
    data_table,
    xml_detection_card,
)

# Import processors
from processors.video_processor import VideoProcessor, XMLParser, VideoAnalyzer
from processors.excel_analyzer import AdvancedExcelAnalyzer
from processors.music_processor import MusicCueProcessor, AUDIO_EXTENSIONS

from urllib.parse import unquote

st.set_page_config(
    page_title="DocShipper",
    page_icon="",
    layout="centered",
    initial_sidebar_state="collapsed"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inject global styles
inject_styles()


def _cleanup_temp_files():
    """Clean up temporary files created during the session."""
    if '_temp_files' in st.session_state:
        for path in st.session_state._temp_files:
            try:
                if os.path.exists(path):
                    os.unlink(path)
            except OSError:
                pass


class DocShipper:
    """Main application class for DocShipper - Page-based wizard."""

    # Field definitions
    FIELDS = {
        'clip_name': ('Clip Name', 'Source media filename'),
        'src_start': ('Source Start', 'Start timecode from source'),
        'src_end': ('Source End', 'End timecode from source'),
        'rec_start': ('Record Start', 'Timeline start timecode'),
        'rec_end': ('Record End', 'Timeline end timecode'),
        'duration': ('Duration', 'Clip length'),
        'screenshot': ('Screenshot', 'Video thumbnail image')
    }

    FIELD_NAMES = {k: v[0] for k, v in FIELDS.items()}

    # Required fields that cannot be unchecked
    REQUIRED_FIELDS = ['clip_name', 'src_start', 'src_end']

    # Shotlist / Both step labels (shared)
    SHOTLIST_STEPS = ['Template', 'Video', 'Mapping', 'Settings', 'Generate', 'Download']

    # Cue sheet step labels (simplified)
    CUESHEET_STEPS = ['Generate', 'Download']

    def __init__(self):
        self.analyzer = AdvancedExcelAnalyzer()
        self.video_processor = VideoProcessor()
        self.music_processor = MusicCueProcessor()
        self.init_session_state()

    def init_session_state(self):
        """Initialize all session state variables."""
        defaults = {
            # Navigation state
            'current_workflow': None,  # 'shotlist' | 'cuesheet' | 'both' | None
            'shotlist_step': 1,  # 1-6
            'cuesheet_step': 1,  # 1-2

            # Unified XML source
            'source_xml_path': None,
            'source_xml_name': None,
            'xml_info': None,  # {video_count, audio_count, fps, project_title}
            'xml_video_data': None,  # Parsed video clips from XML
            'xml_video_count': 0,

            # Shotlist workflow state
            'use_template': True,
            'template_path': None,
            'template_data': None,
            'video_path': None,
            'video_fps': None,
            'output_dir': None,
            'mappings': {},
            'selected_fields': ['clip_name', 'src_start', 'src_end'],
            'field_order': ['clip_name', 'src_start', 'src_end'],
            'mapping_selected_col': None,
            'mapping_swap_mode': False,
            'screenshot_width': 203,
            'screenshot_height': 120,
            'screenshot_quality': 2,
            'disable_screenshots': False,
            'shotlist_complete': False,
            'shotlist_result_files': {},

            # Music cue workflow state
            'music_complete': False,
            'music_result_files': {},
            'cue_count': 0,

            # Both mode state
            'both_complete': False,
            'both_result_files': {},

            # Temp file tracking
            '_temp_files': [],
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def _track_temp_file(self, path: str):
        """Register a temp file for cleanup when session ends."""
        if '_temp_files' not in st.session_state:
            st.session_state._temp_files = []
        st.session_state._temp_files.append(path)

    @staticmethod
    def _build_mappings_from_field_order(field_order: list) -> dict:
        """Convert ordered field list to sequential column mappings starting at row 2."""
        mappings = {}
        for i, field_key in enumerate(field_order):
            col_letter = _num_to_col(i + 1)
            mappings[field_key] = f'{col_letter}2'
        return mappings

    @staticmethod
    def _field_order_from_mappings(mappings: dict) -> list:
        """Derive field_order from a mappings dict by sorting on column index."""
        def _col_to_num(cell_ref: str) -> int:
            col_str = ''.join(c for c in cell_ref if c.isalpha())
            num = 0
            for c in col_str.upper():
                num = num * 26 + (ord(c) - ord('A') + 1)
            return num
        return sorted(mappings.keys(), key=lambda k: _col_to_num(mappings[k]))

    @staticmethod
    def _detect_xml_contents(xml_path: str) -> dict:
        """Analyze a Premiere XML file and return content summary.

        Returns dict with: video_count, audio_count, fps, project_title
        """
        info = {
            'video_count': 0,
            'audio_count': 0,
            'fps': None,
            'project_title': '',
        }

        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except Exception as e:
            logger.error(f"Failed to parse XML for detection: {e}")
            return info

        # Project title from sequence name
        sequence = root.find('.//sequence')
        if sequence is not None:
            name_elem = sequence.find('name')
            if name_elem is not None and name_elem.text:
                info['project_title'] = name_elem.text

        # Video clip count via XMLParser
        parser = XMLParser()
        video_clips = parser.parse(xml_path)
        info['video_count'] = len(video_clips)
        info['fps'] = parser.get_frame_rate()

        # Audio file count by extension
        seen_audio = set()
        for file_elem in root.findall('.//file'):
            pathurl = file_elem.find('pathurl')
            if pathurl is not None and pathurl.text:
                clean = unquote(pathurl.text.replace('file://localhost', ''))
                ext = os.path.splitext(clean)[1].lower()
                if ext in AUDIO_EXTENSIONS:
                    seen_audio.add(clean)
        info['audio_count'] = len(seen_audio)

        return info

    def run(self):
        """Main application entry point - route to correct page."""
        workflow = st.session_state.current_workflow

        if workflow is None:
            self.render_landing()
        elif workflow == 'shotlist':
            self.render_shotlist()
        elif workflow == 'cuesheet':
            self.render_cuesheet()
        elif workflow == 'both':
            self.render_both()

    # ========== LANDING PAGE ==========

    def render_landing(self):
        """Render the XML-first landing page."""
        landing_header()

        xml_info = st.session_state.xml_info

        if xml_info is None:
            # State 1: No XML uploaded yet
            st.caption("Export from Premiere Pro: File > Export > Final Cut Pro XML")

            xml_file = st.file_uploader(
                "Premiere Pro XML",
                type=['xml'],
                key="landing_xml_upload",
                help="XML export from Adobe Premiere Pro",
                label_visibility="collapsed"
            )

            if xml_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as tmp:
                    tmp.write(xml_file.getvalue())
                    st.session_state.source_xml_path = tmp.name
                    st.session_state.source_xml_name = xml_file.name
                    self._track_temp_file(tmp.name)

                with st.spinner("Analyzing XML..."):
                    info = self._detect_xml_contents(tmp.name)
                    st.session_state.xml_info = info

                    # Pre-parse video data for shotlist workflows
                    if info['video_count'] > 0:
                        parser = XMLParser()
                        st.session_state.xml_video_data = parser.parse(tmp.name)
                        st.session_state.xml_video_count = len(st.session_state.xml_video_data)

                st.rerun()
        else:
            # State 2: XML uploaded, show detection results
            xml_detection_card(
                filename=st.session_state.source_xml_name or '',
                project_title=xml_info.get('project_title', ''),
                video_count=xml_info.get('video_count', 0),
                audio_count=xml_info.get('audio_count', 0),
                fps=xml_info.get('fps'),
            )

            has_video = xml_info.get('video_count', 0) > 0
            has_audio = xml_info.get('audio_count', 0) > 0

            col1, col2, col3 = st.columns(3)

            with col1:
                if workflow_button(
                    "Shotlist",
                    "Generate shotlist with screenshots",
                    key="btn_shotlist",
                    enabled=has_video,
                ):
                    st.session_state.current_workflow = 'shotlist'
                    st.session_state.shotlist_step = 1
                    st.rerun()

            with col2:
                if workflow_button(
                    "Cue Sheet",
                    "Generate music cue sheet",
                    key="btn_cuesheet",
                    enabled=has_audio,
                ):
                    st.session_state.current_workflow = 'cuesheet'
                    st.session_state.cuesheet_step = 1
                    st.rerun()

            with col3:
                if workflow_button(
                    "Both",
                    "Shotlist and cue sheet together",
                    key="btn_both",
                    enabled=has_video and has_audio,
                ):
                    st.session_state.current_workflow = 'both'
                    st.session_state.shotlist_step = 1
                    st.rerun()

            divider()

            if secondary_button("Upload Different File", key="landing_reset"):
                self._reset_xml_state()
                st.rerun()

    def _reset_xml_state(self):
        """Clear XML-related state to allow re-upload."""
        st.session_state.source_xml_path = None
        st.session_state.source_xml_name = None
        st.session_state.xml_info = None
        st.session_state.xml_video_data = None
        st.session_state.xml_video_count = 0
        st.session_state.shotlist_step = 1
        st.session_state.shotlist_complete = False
        st.session_state.shotlist_result_files = {}
        st.session_state.music_complete = False
        st.session_state.music_result_files = {}
        st.session_state.cue_count = 0
        st.session_state.cuesheet_step = 1
        st.session_state.both_complete = False
        st.session_state.both_result_files = {}

    # ========== SHOTLIST WORKFLOW (6 steps) ==========

    def render_shotlist(self):
        """Render the current shotlist step."""
        step = st.session_state.shotlist_step

        step_indicator(step, 6, self.SHOTLIST_STEPS)

        if step == 1:
            self.shotlist_step_template()
        elif step == 2:
            self.shotlist_step_video()
        elif step == 3:
            self.shotlist_step_mapping()
        elif step == 4:
            self.shotlist_step_settings()
        elif step == 5:
            self.shotlist_step_generate()
        elif step == 6:
            self.shotlist_step_download()

    def shotlist_step_template(self):
        """Step 1: Template choice."""
        page_title("Template Choice", "Choose how to set up your Excel output")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Upload Template", key="tpl_upload", use_container_width=True,
                        type="primary" if st.session_state.use_template else "secondary"):
                st.session_state.use_template = True
                st.session_state.mappings = {}
                st.rerun()

            st.caption("Use an existing Excel template with auto-detected columns.")

        with col2:
            if st.button("Custom Layout", key="tpl_custom", use_container_width=True,
                        type="primary" if not st.session_state.use_template else "secondary"):
                st.session_state.use_template = False
                st.session_state.template_path = None
                st.session_state.template_data = None
                st.rerun()

            st.caption("Choose which fields to include and arrange columns.")

        divider()

        if st.session_state.use_template:
            section_header("Upload Excel Template")

            template_file = st.file_uploader(
                "Excel Template",
                type=['xlsx', 'xls'],
                key="template_upload",
                help="Your existing shotlist Excel template",
                label_visibility="collapsed"
            )

            if template_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                    tmp.write(template_file.getvalue())
                    st.session_state.template_path = tmp.name
                    self._track_temp_file(tmp.name)

                try:
                    df = pd.read_excel(st.session_state.template_path, header=None, nrows=10)
                    st.session_state.template_data = df
                    file_status(template_file.name)
                except Exception as e:
                    st.error(f"Failed to read template: {e}")

            can_continue = st.session_state.template_path is not None
        else:
            section_header("Select Fields")
            st.caption("Choose which fields to include in your shotlist output")

            updated_fields = field_checkboxes(
                fields=self.FIELDS,
                selected_fields=st.session_state.selected_fields,
                required_fields=self.REQUIRED_FIELDS,
            )

            if set(updated_fields) != set(st.session_state.selected_fields):
                st.session_state.selected_fields = updated_fields
                st.session_state.field_order = updated_fields
                st.session_state.mappings = self._build_mappings_from_field_order(updated_fields)

            if not st.session_state.mappings and st.session_state.selected_fields:
                st.session_state.field_order = list(st.session_state.selected_fields)
                st.session_state.mappings = self._build_mappings_from_field_order(
                    st.session_state.field_order
                )

            can_continue = True

        # Navigation
        divider()
        back_clicked, next_clicked = nav_buttons(
            back_enabled=True,
            back_label="Home",
            next_label="Next",
            next_enabled=can_continue
        )

        if back_clicked:
            st.session_state.current_workflow = None
            st.rerun()

        if next_clicked:
            if st.session_state.use_template and st.session_state.template_path and not st.session_state.mappings:
                try:
                    mappings = self.analyzer.analyze_template(st.session_state.template_path)
                    st.session_state.mappings = mappings
                    st.session_state.field_order = self._field_order_from_mappings(mappings)
                    st.session_state.selected_fields = list(mappings.keys())
                except Exception:
                    pass

            st.session_state.shotlist_step = 2
            st.rerun()

    def shotlist_step_video(self):
        """Step 2: Video upload (XML already loaded from landing page)."""
        page_title("Upload Video", "Source video file for screenshot generation")

        # Show XML info as read-only summary
        xml_info = st.session_state.xml_info
        if xml_info:
            clip_count = st.session_state.xml_video_count
            fps = xml_info.get('fps')
            fps_str = f" at {fps} fps" if fps else ""
            st.success(
                f"XML loaded: {st.session_state.source_xml_name} "
                f"({clip_count} clips{fps_str})"
            )

        divider()
        section_header("Video File")

        video_file = st.file_uploader(
            "Video File",
            type=["mp4", "mov", "mxf", "m4v"],
            key="video_upload",
            help="Source video for screenshots",
            label_visibility="collapsed"
        )

        if video_file:
            suffix = ''.join(Path(video_file.name).suffixes) or '.mp4'
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(video_file.getvalue())
                st.session_state.video_path = tmp.name
                self._track_temp_file(tmp.name)

            st.session_state.output_dir = str(Path(st.session_state.video_path).parent)

            try:
                analyzer = VideoAnalyzer()
                fps = analyzer.get_video_frame_rate(st.session_state.video_path)
                st.session_state.video_fps = fps
                file_status(video_file.name, f"{fps} fps")
            except Exception:
                file_status(video_file.name)

        # Status summary
        divider()
        status_row([
            ("XML", st.session_state.source_xml_path is not None,
             f"{st.session_state.xml_video_count} clips" if st.session_state.source_xml_path else None),
            ("Video", st.session_state.video_path is not None,
             f"{st.session_state.video_fps} fps" if st.session_state.video_fps else None),
        ])

        can_continue = st.session_state.video_path is not None

        divider()
        back_clicked, next_clicked = nav_buttons(
            back_enabled=True,
            next_label="Next",
            next_enabled=can_continue
        )

        if back_clicked:
            st.session_state.shotlist_step = 1
            st.rerun()

        if next_clicked:
            st.session_state.shotlist_step = 3
            st.rerun()

    def shotlist_step_mapping(self):
        """Step 3: Interactive Excel preview with column selection."""
        page_title("Excel Preview & Mapping",
                   "Select a column below to assign or swap fields")

        if not st.session_state.field_order and st.session_state.mappings:
            st.session_state.field_order = self._field_order_from_mappings(st.session_state.mappings)
        if not st.session_state.mappings and st.session_state.field_order:
            st.session_state.mappings = self._build_mappings_from_field_order(st.session_state.field_order)

        selected_col = st.session_state.mapping_selected_col
        swap_mode = st.session_state.mapping_swap_mode

        if swap_mode:
            st.info(f"Swap mode: select another column to swap with column {_num_to_col(selected_col + 1)}.")
        elif selected_col is not None:
            st.caption(f"Column {_num_to_col(selected_col + 1)} selected. Use the panel below to assign a field or swap.")
        else:
            st.caption("Row 1 = column headers. Row 2 = sample data. Select a column below to assign fields.")

        new_col = render_interactive_grid(
            field_order=st.session_state.field_order,
            fields=self.FIELDS,
            selected_column=selected_col,
        )

        if new_col != selected_col:
            if swap_mode and new_col is not None:
                self._swap_columns(selected_col, new_col)
                st.session_state.mapping_selected_col = None
            else:
                st.session_state.mapping_selected_col = new_col
            st.session_state.mapping_swap_mode = False
            st.rerun()

        if selected_col is not None and not swap_mode:
            divider()
            section_header(f"Assign Field to Column {_num_to_col(selected_col + 1)}")

            action = field_assignment_panel(
                selected_col=selected_col,
                field_order=st.session_state.field_order,
                all_fields=self.FIELDS,
            )

            if action == "clear":
                self._clear_column(selected_col)
                st.session_state.mapping_selected_col = None
                st.rerun()
            elif action == "swap":
                st.session_state.mapping_swap_mode = True
                st.rerun()
            elif action is not None:
                self._assign_field_to_column(action, selected_col)
                st.session_state.mapping_selected_col = None
                st.rerun()

        missing = [f for f in self.REQUIRED_FIELDS if f not in st.session_state.mappings]
        if missing:
            missing_names = [self.FIELD_NAMES[f] for f in missing]
            st.warning(f"Required: {', '.join(missing_names)}")
            can_continue = False
        else:
            can_continue = True

        divider()
        back_clicked, next_clicked = nav_buttons(
            back_enabled=True,
            next_label="Next",
            next_enabled=can_continue
        )

        if back_clicked:
            st.session_state.mapping_selected_col = None
            st.session_state.mapping_swap_mode = False
            st.session_state.shotlist_step = 2
            st.rerun()

        if next_clicked:
            st.session_state.mapping_selected_col = None
            st.session_state.mapping_swap_mode = False
            st.session_state.shotlist_step = 4
            st.rerun()

    def _swap_columns(self, col_a: int, col_b: int):
        """Swap two columns in field_order and rebuild mappings."""
        field_order = list(st.session_state.field_order)
        max_idx = max(col_a, col_b)

        while len(field_order) <= max_idx:
            field_order.append(None)

        field_order[col_a], field_order[col_b] = field_order[col_b], field_order[col_a]

        while field_order and field_order[-1] is None:
            field_order.pop()

        clean_order = [f for f in field_order if f is not None]
        st.session_state.field_order = clean_order
        st.session_state.mappings = self._build_mappings_from_field_order(clean_order)

    def _clear_column(self, col_idx: int):
        """Remove a field from the given column position."""
        field_order = list(st.session_state.field_order)
        if col_idx < len(field_order):
            field_order.pop(col_idx)
            st.session_state.field_order = field_order
            st.session_state.mappings = self._build_mappings_from_field_order(field_order)

    def _assign_field_to_column(self, field_key: str, col_idx: int):
        """Assign a field to a specific column position."""
        field_order = list(st.session_state.field_order)

        if field_key in field_order:
            field_order.remove(field_key)

        if col_idx >= len(field_order):
            field_order.append(field_key)
        else:
            field_order[col_idx] = field_key

        st.session_state.field_order = field_order
        st.session_state.mappings = self._build_mappings_from_field_order(field_order)

    def shotlist_step_settings(self):
        """Step 4: Screenshot settings."""
        page_title("Screenshot Settings", "Configure screenshot dimensions and quality")

        section_header("Dimensions")

        col1, col2 = st.columns(2)

        with col1:
            st.session_state.screenshot_width = st.number_input(
                "Width (px)",
                min_value=100,
                max_value=1920,
                value=st.session_state.screenshot_width,
                step=1,
                key="ss_width"
            )

        with col2:
            st.session_state.screenshot_height = st.number_input(
                "Height (px)",
                min_value=100,
                max_value=1080,
                value=st.session_state.screenshot_height,
                step=1,
                key="ss_height"
            )

        divider()
        section_header("Quality")

        st.session_state.screenshot_quality = st.slider(
            "JPEG Quality",
            min_value=1,
            max_value=10,
            value=st.session_state.screenshot_quality,
            key="ss_quality"
        )

        divider()
        section_header("Options")

        st.session_state.disable_screenshots = st.checkbox(
            "Disable screenshot generation",
            value=st.session_state.disable_screenshots,
            key="disable_ss",
            help="Generate shotlist without screenshots"
        )

        if not st.session_state.disable_screenshots:
            st.info(f"Screenshots will be {st.session_state.screenshot_width}x{st.session_state.screenshot_height}px")

        divider()
        back_clicked, next_clicked = nav_buttons(
            back_enabled=True,
            next_label="Generate",
            next_enabled=True
        )

        if back_clicked:
            st.session_state.shotlist_step = 3
            st.rerun()

        if next_clicked:
            st.session_state.shotlist_step = 5
            st.rerun()

    def shotlist_step_generate(self):
        """Step 5: Generate shotlist."""
        page_title("Generate Shotlist", "Processing your files")

        if st.session_state.shotlist_complete:
            st.session_state.shotlist_step = 6
            st.rerun()
            return

        section_header("Processing Summary")

        event_count = st.session_state.xml_video_count or len(st.session_state.xml_video_data or [])

        summary_data = pd.DataFrame({
            "Setting": ["Video Clips", "Mapped Fields", "Screenshots", "Dimensions"],
            "Value": [
                str(event_count),
                str(len(st.session_state.mappings)),
                "Disabled" if st.session_state.disable_screenshots else "Enabled",
                f"{st.session_state.screenshot_width}x{st.session_state.screenshot_height}px"
            ]
        })
        data_table(summary_data)

        divider()

        if primary_button("Start Processing", key="start_generate"):
            self._run_shotlist_processing()

        divider()
        if secondary_button("Back", key="gen_back"):
            st.session_state.shotlist_step = 4
            st.rerun()

    def _run_shotlist_processing(self):
        """Execute shotlist generation."""
        if not st.session_state.output_dir and st.session_state.video_path:
            st.session_state.output_dir = str(Path(st.session_state.video_path).parent)

        progress_widget = st.progress(0)
        status_text = st.empty()

        try:
            def update_progress(progress: float, message: str):
                progress_widget.progress(progress)
                status_text.text(message)

            mappings = dict(st.session_state.mappings)
            if st.session_state.disable_screenshots and 'screenshot' in mappings:
                mappings.pop('screenshot', None)

            template_path = st.session_state.template_path if st.session_state.use_template else None

            results = self.video_processor.process(
                edl_path=st.session_state.source_xml_path,
                video_path=st.session_state.video_path,
                template_path=template_path,
                mappings=mappings,
                output_dir=st.session_state.output_dir,
                progress_callback=update_progress,
                edl_data_override=st.session_state.xml_video_data,
                disable_screenshots=st.session_state.disable_screenshots,
                screenshot_width=st.session_state.screenshot_width,
                screenshot_height=st.session_state.screenshot_height,
                screenshot_quality=st.session_state.screenshot_quality,
            )

            if results['status'] == 'success':
                st.session_state.shotlist_result_files = results['files']
                st.session_state.shotlist_complete = True
                # Only auto-advance for shotlist-only mode
                if st.session_state.current_workflow == 'shotlist':
                    st.session_state.shotlist_step = 6
                    st.rerun()
            else:
                st.error(f"Processing failed: {results['message']}")

        except Exception as e:
            st.error(f"Processing failed: {str(e)}")
            logger.error(f"Processing error: {e}")

    def shotlist_step_download(self):
        """Step 6: Download results."""
        page_title("Download", "Your shotlist is ready")

        if not st.session_state.shotlist_complete:
            st.warning("Processing not complete")
            if secondary_button("Back to Generate", key="dl_back_gen"):
                st.session_state.shotlist_step = 5
                st.rerun()
            return

        st.success("Shotlist generation complete")

        divider()

        if 'excel' in st.session_state.shotlist_result_files:
            excel_path = st.session_state.shotlist_result_files['excel']
            if os.path.exists(excel_path):
                section_header("Download File")
                st.markdown(f"**File:** `{Path(excel_path).name}`")

                with open(excel_path, 'rb') as f:
                    st.download_button(
                        label="Download Excel Shotlist",
                        data=f.read(),
                        file_name=Path(excel_path).name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )

        divider()

        col1, col2 = st.columns(2)

        with col1:
            if secondary_button("Start Over", key="dl_restart", full_width=True):
                self._reset_shotlist_state()
                st.rerun()

        with col2:
            if secondary_button("Home", key="dl_home", full_width=True):
                st.session_state.current_workflow = None
                st.rerun()

    def _reset_shotlist_state(self):
        """Reset shotlist workflow state."""
        st.session_state.shotlist_step = 1
        st.session_state.shotlist_complete = False
        st.session_state.shotlist_result_files = {}
        st.session_state.video_path = None
        st.session_state.video_fps = None
        st.session_state.mappings = {}
        st.session_state.template_path = None
        st.session_state.template_data = None

    # ========== CUE SHEET WORKFLOW (2 steps) ==========

    def render_cuesheet(self):
        """Render the current cue sheet step."""
        step = st.session_state.cuesheet_step

        step_indicator(step, 2, self.CUESHEET_STEPS)

        if step == 1:
            self.cuesheet_step_generate()
        elif step == 2:
            self.cuesheet_step_download()

    def cuesheet_step_generate(self):
        """Step 1: Generate cue sheet (summary + start button)."""
        page_title("Generate Cue Sheet", "Processing audio files from your XML")

        if st.session_state.music_complete:
            st.session_state.cuesheet_step = 2
            st.rerun()
            return

        section_header("Processing Summary")

        xml_info = st.session_state.xml_info or {}
        summary_data = pd.DataFrame({
            "Setting": ["XML File", "Audio Files", "Project"],
            "Value": [
                st.session_state.source_xml_name or "Ready",
                str(xml_info.get('audio_count', 0)),
                xml_info.get('project_title', 'Unknown'),
            ]
        })
        data_table(summary_data)

        st.caption(
            "All audio files will be included. Files without metadata "
            "will be sorted to the bottom for easy removal in Excel."
        )

        divider()

        if primary_button("Start Processing", key="cue_start"):
            self._run_cuesheet_processing()

        divider()
        if secondary_button("Back", key="cue_back"):
            st.session_state.current_workflow = None
            st.rerun()

    def _run_cuesheet_processing(self):
        """Execute cue sheet generation."""
        output_dir = tempfile.mkdtemp()

        progress_widget = st.progress(0)
        status_text = st.empty()

        try:
            def update_progress(progress: float, message: str):
                progress_widget.progress(progress)
                status_text.text(message)

            results = self.music_processor.process(
                xml_path=st.session_state.source_xml_path,
                template_path=None,
                output_dir=output_dir,
                progress_callback=update_progress,
            )

            if results['status'] == 'success':
                st.session_state.music_result_files = results['files']
                st.session_state.cue_count = results['cue_count']
                st.session_state.music_complete = True
                if st.session_state.current_workflow == 'cuesheet':
                    st.session_state.cuesheet_step = 2
                    st.rerun()
            elif results['status'] == 'warning':
                st.warning(results['message'])
            else:
                st.error(f"Processing failed: {results['message']}")

        except Exception as e:
            st.error(f"Processing failed: {str(e)}")
            logger.error(f"Music processing error: {e}")

    def cuesheet_step_download(self):
        """Step 2: Download results."""
        page_title("Download", "Your cue sheet is ready")

        if not st.session_state.music_complete:
            st.warning("Processing not complete")
            if secondary_button("Back to Generate", key="cue_dl_back"):
                st.session_state.cuesheet_step = 1
                st.rerun()
            return

        st.success(f"Cue sheet complete ({st.session_state.cue_count} cues)")

        divider()

        if 'excel' in st.session_state.music_result_files:
            excel_path = st.session_state.music_result_files['excel']
            if os.path.exists(excel_path):
                section_header("Download File")
                st.markdown(f"**File:** `{Path(excel_path).name}`")

                with open(excel_path, 'rb') as f:
                    st.download_button(
                        label="Download Cue Sheet",
                        data=f.read(),
                        file_name=Path(excel_path).name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )

        divider()

        col1, col2 = st.columns(2)

        with col1:
            if secondary_button("Start Over", key="cue_restart", full_width=True):
                st.session_state.cuesheet_step = 1
                st.session_state.music_complete = False
                st.session_state.music_result_files = {}
                st.session_state.current_workflow = None
                self._reset_xml_state()
                st.rerun()

        with col2:
            if secondary_button("Home", key="cue_home", full_width=True):
                st.session_state.current_workflow = None
                st.rerun()

    # ========== BOTH WORKFLOW (6 steps) ==========

    def render_both(self):
        """Render the combined shotlist + cue sheet workflow."""
        step = st.session_state.shotlist_step

        step_indicator(step, 6, self.SHOTLIST_STEPS)

        # Steps 1-4 reuse shotlist methods
        if step == 1:
            self.shotlist_step_template()
        elif step == 2:
            self.shotlist_step_video()
        elif step == 3:
            self.shotlist_step_mapping()
        elif step == 4:
            self.shotlist_step_settings()
        elif step == 5:
            self.both_step_generate()
        elif step == 6:
            self.both_step_download()

    def both_step_generate(self):
        """Step 5: Generate both shotlist and cue sheet."""
        page_title("Generate Both", "Processing shotlist and cue sheet")

        if st.session_state.both_complete:
            st.session_state.shotlist_step = 6
            st.rerun()
            return

        section_header("Processing Summary")

        event_count = st.session_state.xml_video_count or len(st.session_state.xml_video_data or [])
        xml_info = st.session_state.xml_info or {}

        summary_data = pd.DataFrame({
            "Setting": ["Video Clips", "Audio Files", "Mapped Fields", "Screenshots"],
            "Value": [
                str(event_count),
                str(xml_info.get('audio_count', 0)),
                str(len(st.session_state.mappings)),
                "Disabled" if st.session_state.disable_screenshots else "Enabled",
            ]
        })
        data_table(summary_data)

        divider()

        if primary_button("Start Processing", key="both_start"):
            self._run_both_processing()

        divider()
        if secondary_button("Back", key="both_back"):
            st.session_state.shotlist_step = 4
            st.rerun()

    def _run_both_processing(self):
        """Execute combined shotlist + cue sheet generation."""
        if not st.session_state.output_dir and st.session_state.video_path:
            st.session_state.output_dir = str(Path(st.session_state.video_path).parent)

        progress_widget = st.progress(0)
        status_text = st.empty()

        try:
            # -- Phase 1: Shotlist (0% - 70%) --
            def shotlist_progress(progress: float, message: str):
                scaled = progress * 0.7
                progress_widget.progress(scaled)
                status_text.text(f"[Shotlist] {message}")

            mappings = dict(st.session_state.mappings)
            if st.session_state.disable_screenshots and 'screenshot' in mappings:
                mappings.pop('screenshot', None)

            template_path = st.session_state.template_path if st.session_state.use_template else None

            shotlist_results = self.video_processor.process(
                edl_path=st.session_state.source_xml_path,
                video_path=st.session_state.video_path,
                template_path=template_path,
                mappings=mappings,
                output_dir=st.session_state.output_dir,
                progress_callback=shotlist_progress,
                edl_data_override=st.session_state.xml_video_data,
                disable_screenshots=st.session_state.disable_screenshots,
                screenshot_width=st.session_state.screenshot_width,
                screenshot_height=st.session_state.screenshot_height,
                screenshot_quality=st.session_state.screenshot_quality,
            )

            if shotlist_results['status'] != 'success':
                st.error(f"Shotlist failed: {shotlist_results['message']}")
                return

            st.session_state.shotlist_result_files = shotlist_results['files']
            st.session_state.shotlist_complete = True

            # -- Phase 2: Cue Sheet (70% - 100%) --
            def cuesheet_progress(progress: float, message: str):
                scaled = 0.7 + (progress * 0.3)
                progress_widget.progress(scaled)
                status_text.text(f"[Cue Sheet] {message}")

            cue_output_dir = tempfile.mkdtemp()
            cue_results = self.music_processor.process(
                xml_path=st.session_state.source_xml_path,
                template_path=None,
                output_dir=cue_output_dir,
                progress_callback=cuesheet_progress,
            )

            if cue_results['status'] != 'success':
                st.warning(f"Cue sheet: {cue_results['message']}")
            else:
                st.session_state.music_result_files = cue_results['files']
                st.session_state.cue_count = cue_results['cue_count']
                st.session_state.music_complete = True

            # Merge results
            both_files = {}
            both_files.update(shotlist_results.get('files', {}))
            if cue_results.get('files', {}).get('excel'):
                both_files['cue_excel'] = cue_results['files']['excel']
            st.session_state.both_result_files = both_files
            st.session_state.both_complete = True

            progress_widget.progress(1.0)
            status_text.text("Processing complete!")

            st.session_state.shotlist_step = 6
            st.rerun()

        except Exception as e:
            st.error(f"Processing failed: {str(e)}")
            logger.error(f"Both processing error: {e}")

    def both_step_download(self):
        """Step 6: Download both results."""
        page_title("Download", "Your files are ready")

        if not st.session_state.both_complete:
            st.warning("Processing not complete")
            if secondary_button("Back to Generate", key="both_dl_back"):
                st.session_state.shotlist_step = 5
                st.rerun()
            return

        st.success("Generation complete")

        divider()

        # Shotlist download
        if 'excel' in st.session_state.shotlist_result_files:
            excel_path = st.session_state.shotlist_result_files['excel']
            if os.path.exists(excel_path):
                section_header("Shotlist")
                st.markdown(f"**File:** `{Path(excel_path).name}`")
                with open(excel_path, 'rb') as f:
                    st.download_button(
                        label="Download Shotlist Excel",
                        data=f.read(),
                        file_name=Path(excel_path).name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key="dl_shotlist",
                    )

        # Cue sheet download
        if 'cue_excel' in st.session_state.both_result_files:
            cue_path = st.session_state.both_result_files['cue_excel']
            if os.path.exists(cue_path):
                divider()
                section_header("Cue Sheet")
                st.markdown(f"**File:** `{Path(cue_path).name}`")
                with open(cue_path, 'rb') as f:
                    st.download_button(
                        label="Download Cue Sheet Excel",
                        data=f.read(),
                        file_name=Path(cue_path).name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key="dl_cuesheet",
                    )

        divider()

        col1, col2 = st.columns(2)

        with col1:
            if secondary_button("Start Over", key="both_restart", full_width=True):
                self._reset_shotlist_state()
                st.session_state.both_complete = False
                st.session_state.both_result_files = {}
                st.session_state.music_complete = False
                st.session_state.music_result_files = {}
                st.session_state.current_workflow = None
                self._reset_xml_state()
                st.rerun()

        with col2:
            if secondary_button("Home", key="both_home", full_width=True):
                st.session_state.current_workflow = None
                st.rerun()


def main():
    """Main entry point."""
    atexit.register(_cleanup_temp_files)
    app = DocShipper()
    app.run()


if __name__ == "__main__":
    main()
