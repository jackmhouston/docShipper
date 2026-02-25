#!/usr/bin/env python3
"""
DocShipper - Video Editing Document Automation
Combines shotlist generation and music cue sheet workflows
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import tempfile
import os
import logging
from typing import Dict, Optional

# Import UI components
from ui import inject_styles
from ui.components import (
    page_header,
    section_header,
    progress_bar,
    primary_button,
    secondary_button,
    status_summary,
    section_divider,
    file_status_message,
    mapping_display,
)

# Import processors
from processors.video_processor import VideoProcessor, EDLParser, XMLParser, VideoAnalyzer
from processors.excel_analyzer import AdvancedExcelAnalyzer
from processors.music_processor import MusicCueProcessor

st.set_page_config(
    page_title="DocShipper",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inject global styles
inject_styles()


class DocShipper:
    """Main application class for DocShipper."""

    FIELD_NAMES = {
        'clip_name': 'Clip/Source File Name',
        'src_start': 'Source Start Time',
        'src_end': 'Source End Time',
        'rec_start': 'Record Start Time',
        'rec_end': 'Record End Time',
        'duration': 'Duration',
        'screenshot': 'Screenshot/Image'
    }

    FIELD_INFO = {
        'clip_name': ('Clip Name', 'Source media filename'),
        'src_start': ('Source Start', 'Start timecode from source'),
        'src_end': ('Source End', 'End timecode from source'),
        'rec_start': ('Record Start', 'Timeline start timecode'),
        'rec_end': ('Record End', 'Timeline end timecode'),
        'duration': ('Duration', 'Clip length'),
        'screenshot': ('Screenshot', 'Video thumbnail')
    }

    def __init__(self):
        self.analyzer = AdvancedExcelAnalyzer()
        self.video_processor = VideoProcessor()
        self.music_processor = MusicCueProcessor()
        self.init_session_state()

    def init_session_state(self):
        """Initialize all session state variables."""
        defaults = {
            # Workflow selection
            'active_workflow': 'shotlist',

            # Shotlist workflow state
            'shotlist_section': 1,
            'shotlist_progress': 0,
            'template_path': None,
            'edl_path': None,
            'edl_data': None,
            'edl_event_count': 0,
            'video_path': None,
            'video_fps': None,
            'output_dir': None,
            'mappings': {},
            'use_custom_template': False,
            'custom_template_mappings': {},
            'screenshot_width': 203,
            'screenshot_height': 120,
            'screenshot_quality': 2,
            'disable_screenshots': False,
            'guessed_show_name': None,
            'shotlist_complete': False,
            'shotlist_result_files': {},

            # Music cue workflow state
            'music_section': 1,
            'music_progress': 0,
            'xml_path': None,
            'cue_template_path': None,
            'cue_output_dir': None,
            'filter_keyword': 'alibi',
            'music_complete': False,
            'music_result_files': {},
            'cue_count': 0,
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def run(self):
        """Main application entry point."""
        page_header("DocShipper", "Video Editing Document Automation")

        # Workflow tabs
        tab1, tab2 = st.tabs(["Shotlist Generator", "Music Cue Sheet"])

        with tab1:
            self.shotlist_workflow()

        with tab2:
            self.music_cue_workflow()

    # ========== SHOTLIST WORKFLOW ==========

    def shotlist_workflow(self):
        """Complete shotlist generation workflow."""
        st.markdown("**Generate shotlists from EDL files with automatic screenshots**")

        # Section 1: Setup Files
        self.shotlist_section_1()

        # Section 2: Configure Mappings
        self.shotlist_section_2()

        # Section 3: Review and Adjust
        self.shotlist_section_3()

        # Section 4: Generate
        self.shotlist_section_4()

    def shotlist_section_1(self):
        """Shotlist Section 1: Setup Files."""
        with st.expander("1. Setup Files", expanded=(st.session_state.shotlist_section == 1)):
            section_header("Media Files")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**EDL/XML File**")
                edl_file = st.file_uploader(
                    "EDL/XML File",
                    type=['edl', 'xml'],
                    key="edl_upload",
                    help="Edit Decision List (.edl) or Premiere XML (.xml)"
                )

                if edl_file:
                    suffix = Path(edl_file.name).suffix.lower() or '.edl'
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                        tmp_file.write(edl_file.getvalue())
                        st.session_state.edl_path = tmp_file.name

                    try:
                        parser = XMLParser() if suffix == '.xml' else EDLParser()
                        edl_data = parser.parse(st.session_state.edl_path)
                        st.session_state.edl_event_count = len(edl_data)
                        file_status_message(edl_file.name, f"{len(edl_data)} events")
                    except Exception as e:
                        file_status_message(edl_file.name)

            with col2:
                st.markdown("**Video File**")
                video_file = st.file_uploader(
                    "Video File",
                    type=["mp4", "mov", "mxf", "m4v"],
                    key="video_upload",
                    help="Source video for screenshots"
                )

                if video_file:
                    suffix = ''.join(Path(video_file.name).suffixes) or '.mp4'
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_vid:
                        tmp_vid.write(video_file.getvalue())
                        st.session_state.video_path = tmp_vid.name

                    st.session_state.output_dir = str(Path(st.session_state.video_path).parent)

                    try:
                        analyzer = VideoAnalyzer()
                        fps = analyzer.get_video_frame_rate(st.session_state.video_path)
                        st.session_state.video_fps = fps
                        file_status_message(video_file.name, f"{fps} fps")
                    except:
                        file_status_message(video_file.name)

            section_divider()
            section_header("Excel Template")

            template_mode = st.radio(
                "Template Mode",
                ["Load Existing Template", "Create Custom Template"],
                index=1 if st.session_state.use_custom_template else 0,
                horizontal=True,
                key="template_mode"
            )

            if template_mode == "Load Existing Template":
                st.session_state.use_custom_template = False
                template_file = st.file_uploader(
                    "Excel Template",
                    type=['xlsx', 'xls'],
                    key="template_upload",
                    help="Your existing shotlist Excel template"
                )

                if template_file:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                        tmp_file.write(template_file.getvalue())
                        st.session_state.template_path = tmp_file.name
                    file_status_message(template_file.name)
            else:
                st.session_state.use_custom_template = True
                st.session_state.template_path = None
                self._custom_template_builder()

            section_divider()
            has_template = st.session_state.template_path or st.session_state.use_custom_template
            template_status = "Custom" if st.session_state.use_custom_template else ("Ready" if st.session_state.template_path else "Waiting...")

            status_summary([
                ("EDL File", "Ready" if st.session_state.edl_path else "Waiting..."),
                ("Video File", "Ready" if st.session_state.video_path else "Waiting..."),
                ("Template", template_status)
            ])

            st.markdown("")
            all_ready = all([
                has_template,
                st.session_state.edl_path,
                st.session_state.video_path
            ])

            if all_ready:
                if primary_button("Continue to Mapping", key="shotlist_continue_1"):
                    if st.session_state.use_custom_template and st.session_state.custom_template_mappings:
                        st.session_state.mappings = {
                            k: f"{v}2" for k, v in st.session_state.custom_template_mappings.items() if v
                        }
                    st.session_state.shotlist_section = 2
                    st.rerun()
            else:
                st.info("Upload EDL and Video files, and set up a template to continue")

    def _custom_template_builder(self):
        """UI for building a custom template with column mappings."""
        st.markdown("Define where each field should appear in your output Excel file.")
        st.caption("Enter column letters (A, B, C, etc.) - data starts at row 2 with headers in row 1")

        st.markdown("**Quick Presets**")
        col1, col2, col3 = st.columns(3)

        with col1:
            if secondary_button("Standard Layout", key="preset_standard", full_width=True):
                st.session_state.custom_template_mappings = {
                    'clip_name': 'A', 'src_start': 'B', 'src_end': 'C',
                    'rec_start': 'D', 'rec_end': 'E', 'duration': 'F', 'screenshot': 'G'
                }
                st.rerun()

        with col2:
            if secondary_button("Minimal", key="preset_minimal", full_width=True):
                st.session_state.custom_template_mappings = {
                    'clip_name': 'A', 'src_start': 'B', 'src_end': 'C', 'duration': 'D'
                }
                st.rerun()

        with col3:
            if secondary_button("Screenshot First", key="preset_screenshot", full_width=True):
                st.session_state.custom_template_mappings = {
                    'screenshot': 'A', 'clip_name': 'B', 'src_start': 'C',
                    'src_end': 'D', 'duration': 'E'
                }
                st.rerun()

        section_divider()
        st.markdown("**Column Assignments**")

        row1_fields = ['clip_name', 'src_start', 'src_end', 'screenshot']
        cols = st.columns(4)
        for i, field in enumerate(row1_fields):
            display_name, desc = self.FIELD_INFO[field]
            with cols[i]:
                current = st.session_state.custom_template_mappings.get(field, '')
                col_letter = st.text_input(
                    display_name,
                    value=current,
                    max_chars=2,
                    key=f"custom_col_{field}",
                    placeholder="A",
                    help=desc
                )
                if col_letter.strip():
                    st.session_state.custom_template_mappings[field] = col_letter.strip().upper()
                elif field in st.session_state.custom_template_mappings:
                    st.session_state.custom_template_mappings.pop(field, None)

    def shotlist_section_2(self):
        """Shotlist Section 2: Configure Mappings."""
        with st.expander("2. Configure Mappings", expanded=(st.session_state.shotlist_section == 2)):
            if st.session_state.shotlist_section < 2:
                st.info("Complete Section 1 first")
                return

            if st.session_state.use_custom_template:
                section_header("Custom Template Mappings")
                st.success("Using custom template - column mappings are set from Section 1")

                if st.session_state.mappings:
                    mapping_display(st.session_state.mappings, self.FIELD_NAMES)

                    section_divider()
                    if primary_button("Continue to Review", key="shotlist_continue_2"):
                        st.session_state.shotlist_section = 3
                        st.rerun()
                return

            if st.session_state.template_path:
                section_header("Template Analysis")

                # Run auto-analysis if not done yet
                if not st.session_state.mappings:
                    with st.spinner("Analyzing template..."):
                        try:
                            mappings = self.analyzer.analyze_template(st.session_state.template_path)
                            st.session_state.mappings = mappings
                        except Exception as e:
                            st.error(f"Analysis failed: {e}")
                            return

                # Show detected mappings summary
                if st.session_state.mappings:
                    st.markdown("**Auto-detected field mappings:**")
                    mapping_data = []
                    for field, cell_ref in st.session_state.mappings.items():
                        mapping_data.append({
                            "Field": self.FIELD_NAMES.get(field, field.replace('_', ' ').title()),
                            "Cell": cell_ref,
                            "Status": "Auto-detected"
                        })

                    df_mappings = pd.DataFrame(mapping_data)
                    st.dataframe(df_mappings, use_container_width=True, hide_index=True)

                    # Re-analyze button
                    if secondary_button("Re-analyze Template", key="reanalyze_template"):
                        st.session_state.mappings = {}
                        st.rerun()

                # Quick presets section
                section_divider()
                section_header("Quick Presets")
                st.caption("Apply a preset configuration for common template formats")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    if secondary_button("NGO Template", key="preset_ngo", full_width=True):
                        st.session_state.mappings = {
                            'clip_name': 'E15',
                            'src_start': 'F15',
                            'src_end': 'G15',
                            'screenshot': 'I15',
                            'duration': 'A8'
                        }
                        st.rerun()

                with col2:
                    if secondary_button("Standard Row 2", key="preset_row2", full_width=True):
                        st.session_state.mappings = {
                            'clip_name': 'A2',
                            'src_start': 'B2',
                            'src_end': 'C2',
                            'duration': 'D2',
                            'screenshot': 'E2'
                        }
                        st.rerun()

                with col3:
                    if secondary_button("Clear All", key="preset_clear", full_width=True):
                        st.session_state.mappings = {}
                        st.rerun()

                # Manual adjustments section
                section_divider()
                section_header("Manual Adjustments")
                st.caption("Review and correct any incorrectly detected mappings. Enter cell references like 'A2', 'E15', etc. Leave blank to remove a mapping.")

                # Row 1: Primary fields
                col1, col2, col3 = st.columns(3)

                with col1:
                    clip_name = st.text_input(
                        "Clip Name Cell",
                        value=st.session_state.mappings.get('clip_name', ''),
                        key="manual_clip_name",
                        placeholder="e.g. E15",
                        help="Cell where clip/source filenames will be written"
                    )
                    src_start = st.text_input(
                        "Time In Cell",
                        value=st.session_state.mappings.get('src_start', ''),
                        key="manual_src_start",
                        placeholder="e.g. F15",
                        help="Cell where source start timecodes will be written"
                    )

                with col2:
                    src_end = st.text_input(
                        "Time Out Cell",
                        value=st.session_state.mappings.get('src_end', ''),
                        key="manual_src_end",
                        placeholder="e.g. G15",
                        help="Cell where source end timecodes will be written"
                    )
                    screenshot = st.text_input(
                        "Screenshot Cell",
                        value=st.session_state.mappings.get('screenshot', ''),
                        key="manual_screenshot",
                        placeholder="e.g. I15",
                        help="Cell where screenshot images will be inserted"
                    )

                with col3:
                    duration = st.text_input(
                        "Duration Cell",
                        value=st.session_state.mappings.get('duration', ''),
                        key="manual_duration",
                        placeholder="e.g. H15",
                        help="Cell where clip duration will be written"
                    )
                    rec_start = st.text_input(
                        "Record Start Cell (Optional)",
                        value=st.session_state.mappings.get('rec_start', ''),
                        key="manual_rec_start",
                        placeholder="e.g. J15",
                        help="Cell where timeline/record start timecodes will be written"
                    )

                # Update mappings from manual inputs
                self._update_mapping_from_input('clip_name', clip_name)
                self._update_mapping_from_input('src_start', src_start)
                self._update_mapping_from_input('src_end', src_end)
                self._update_mapping_from_input('screenshot', screenshot)
                self._update_mapping_from_input('duration', duration)
                self._update_mapping_from_input('rec_start', rec_start)

                # Current mappings summary
                section_divider()
                section_header("Current Mappings")

                if st.session_state.mappings:
                    final_mapping_data = []
                    for field, cell_ref in sorted(st.session_state.mappings.items(), key=lambda x: x[1]):
                        final_mapping_data.append({
                            "Field": self.FIELD_NAMES.get(field, field.replace('_', ' ').title()),
                            "Cell": cell_ref
                        })
                    st.dataframe(pd.DataFrame(final_mapping_data), use_container_width=True, hide_index=True)
                else:
                    st.warning("No mappings configured. Use the fields above to set cell references.")

                # Template Preview
                section_divider()
                section_header("Output Preview")
                st.caption("Preview of how data will be placed in the Excel template")

                if st.session_state.mappings:
                    self._render_template_preview()
                else:
                    st.info("Configure mappings above to see a preview")

                # Validation and continue
                section_divider()
                required_fields = ['clip_name', 'src_start', 'src_end', 'screenshot']
                missing_fields = [f for f in required_fields if f not in st.session_state.mappings]

                if missing_fields:
                    missing_names = [self.FIELD_NAMES.get(f, f) for f in missing_fields]
                    st.warning(f"Required mappings missing: {', '.join(missing_names)}")
                else:
                    st.success("All required mappings configured")
                    if primary_button("Continue to Review", key="shotlist_continue_2b"):
                        st.session_state.shotlist_section = 3
                        st.rerun()

    def _update_mapping_from_input(self, field: str, value: str):
        """Update a mapping field from user input."""
        value = value.strip().upper() if value else ''
        if value:
            st.session_state.mappings[field] = value
        elif field in st.session_state.mappings:
            st.session_state.mappings.pop(field, None)

    def _render_template_preview(self):
        """Render a visual preview of the Excel template layout."""
        import re

        mappings = st.session_state.mappings
        if not mappings:
            return

        # Parse cell references to determine grid dimensions
        def parse_cell_ref(cell_ref: str):
            """Parse cell reference like 'E15' into (col_letter, row_num)."""
            match = re.match(r'^([A-Z]+)(\d+)$', cell_ref.upper())
            if match:
                return match.group(1), int(match.group(2))
            return None, None

        def col_to_num(col_letter: str) -> int:
            """Convert column letter to number (A=1, B=2, ..., Z=26, AA=27)."""
            result = 0
            for char in col_letter:
                result = result * 26 + (ord(char) - ord('A') + 1)
            return result

        def num_to_col(num: int) -> str:
            """Convert number to column letter."""
            result = ""
            while num > 0:
                num, remainder = divmod(num - 1, 26)
                result = chr(65 + remainder) + result
            return result

        # Find the range of cells we need to display
        min_col, max_col = 100, 0
        min_row, max_row = 1000, 0

        cell_data = {}
        for field, cell_ref in mappings.items():
            col_letter, row_num = parse_cell_ref(cell_ref)
            if col_letter and row_num:
                col_num = col_to_num(col_letter)
                min_col = min(min_col, col_num)
                max_col = max(max_col, col_num)
                min_row = min(min_row, row_num)
                max_row = max(max_row, row_num)
                cell_data[(col_num, row_num)] = field

        if not cell_data:
            st.info("No valid cell references to preview")
            return

        # Add some padding and show header row
        header_row = min_row - 1 if min_row > 1 else min_row
        display_rows = max(3, max_row - header_row + 2)  # Show at least 3 data rows

        # Placeholder content for preview
        placeholders = {
            'clip_name': 'MyClip_001.mov',
            'src_start': '01:00:15:12',
            'src_end': '01:00:22:08',
            'rec_start': '00:05:30:00',
            'rec_end': '00:05:37:20',
            'duration': '00:00:06:20',
            'screenshot': '[Screenshot]'
        }

        field_short_names = {
            'clip_name': 'Clip Name',
            'src_start': 'Time In',
            'src_end': 'Time Out',
            'rec_start': 'Rec In',
            'rec_end': 'Rec Out',
            'duration': 'Duration',
            'screenshot': 'Screenshot'
        }

        # Build preview data
        preview_data = {}
        columns = []

        for col_num in range(min_col, max_col + 1):
            col_letter = num_to_col(col_num)
            columns.append(col_letter)
            preview_data[col_letter] = []

            for row_offset in range(display_rows):
                row_num = header_row + row_offset
                field = cell_data.get((col_num, row_num))

                if field:
                    if row_num == header_row:
                        # This is a header row
                        preview_data[col_letter].append(f"**{field_short_names.get(field, field)}**")
                    else:
                        # This is the first data row - show placeholder
                        preview_data[col_letter].append(placeholders.get(field, '...'))
                elif row_num == header_row and any(cell_data.get((col_num, r)) for r in range(min_row, max_row + 1)):
                    # Header for a mapped column
                    for r in range(min_row, max_row + 1):
                        if (col_num, r) in cell_data:
                            preview_data[col_letter].append(f"**{field_short_names.get(cell_data[(col_num, r)], '')}**")
                            break
                else:
                    preview_data[col_letter].append('')

        # Ensure all columns have same length
        max_len = max(len(v) for v in preview_data.values()) if preview_data else 0
        for col in preview_data:
            while len(preview_data[col]) < max_len:
                preview_data[col].append('')

        # Create DataFrame for display
        if preview_data and columns:
            # Build row labels
            row_labels = [f"Row {header_row + i}" for i in range(max_len)]

            df_preview = pd.DataFrame(preview_data, index=row_labels)

            st.markdown("**Excel Layout Preview** (showing first few rows):")
            st.dataframe(df_preview, use_container_width=True)

            # Legend
            st.caption("Legend: Data will be written starting at the cell references you specified. Each subsequent EDL event fills the next row.")

    def shotlist_section_3(self):
        """Shotlist Section 3: Review and Adjust."""
        with st.expander("3. Review and Adjust", expanded=(st.session_state.shotlist_section == 3)):
            if st.session_state.shotlist_section < 3:
                st.info("Complete Section 2 first")
                return

            if st.session_state.edl_path:
                section_header("EDL Data Preview")

                if st.session_state.edl_data is None:
                    try:
                        parser = EDLParser()
                        edl_data = parser.parse(st.session_state.edl_path)
                        st.session_state.edl_data = edl_data
                    except Exception as e:
                        st.error(f"Error parsing EDL: {e}")
                        return

                if st.session_state.edl_data:
                    df = pd.DataFrame(st.session_state.edl_data)
                    st.markdown(f"**{len(df)} events** (showing first 10)")
                    st.dataframe(df.head(10), use_container_width=True, hide_index=True)

                section_divider()
                section_header("Screenshot Settings")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.session_state.screenshot_width = st.number_input(
                        "Width (px)", min_value=100, max_value=1920,
                        value=st.session_state.screenshot_width, step=1
                    )

                with col2:
                    st.session_state.screenshot_height = st.number_input(
                        "Height (px)", min_value=100, max_value=1080,
                        value=st.session_state.screenshot_height, step=1
                    )

                with col3:
                    st.session_state.screenshot_quality = st.slider(
                        "JPEG Quality", min_value=1, max_value=10,
                        value=st.session_state.screenshot_quality
                    )

                st.session_state.disable_screenshots = st.checkbox(
                    "Disable screenshot generation",
                    value=st.session_state.disable_screenshots,
                    key="disable_ss"
                )

                section_divider()
                if primary_button("Continue to Generate", key="shotlist_continue_3"):
                    st.session_state.shotlist_section = 4
                    st.rerun()

    def shotlist_section_4(self):
        """Shotlist Section 4: Generate."""
        with st.expander("4. Generate Shotlist", expanded=(st.session_state.shotlist_section == 4)):
            if st.session_state.shotlist_section < 4:
                st.info("Complete Section 3 first")
                return

            if not st.session_state.shotlist_complete:
                section_header("Processing Summary")

                event_count = st.session_state.edl_event_count or len(st.session_state.edl_data or [])
                summary_data = {
                    "Setting": ["EDL Events", "Mapped Fields", "Screenshots"],
                    "Value": [
                        str(event_count),
                        str(len(st.session_state.mappings)),
                        "Disabled" if st.session_state.disable_screenshots else "Enabled"
                    ]
                }
                st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)

                st.markdown("")
                if primary_button("Generate Shotlist", key="generate_shotlist"):
                    self._start_shotlist_processing()
            else:
                st.success("Shotlist generation complete!")

                if 'excel' in st.session_state.shotlist_result_files:
                    excel_path = st.session_state.shotlist_result_files['excel']
                    if os.path.exists(excel_path):
                        section_header("Download")
                        st.markdown(f"**File:** `{Path(excel_path).name}`")

                        with open(excel_path, 'rb') as f:
                            st.download_button(
                                label="Download Excel Shotlist",
                                data=f.read(),
                                file_name=Path(excel_path).name,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )

    def _start_shotlist_processing(self):
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

            template_path = None if st.session_state.use_custom_template else st.session_state.template_path

            results = self.video_processor.process(
                edl_path=st.session_state.edl_path,
                video_path=st.session_state.video_path,
                template_path=template_path,
                mappings=mappings,
                output_dir=st.session_state.output_dir,
                progress_callback=update_progress,
                edl_data_override=st.session_state.edl_data,
                disable_screenshots=st.session_state.disable_screenshots,
                show_name=st.session_state.guessed_show_name
            )

            if results['status'] == 'success':
                st.session_state.shotlist_result_files = results['files']
                st.session_state.shotlist_complete = True
                st.rerun()
            else:
                st.error(f"Processing failed: {results['message']}")

        except Exception as e:
            st.error(f"Processing failed: {str(e)}")
            logger.error(f"Processing error: {e}")

    # ========== MUSIC CUE WORKFLOW ==========

    def music_cue_workflow(self):
        """Complete music cue sheet workflow."""
        st.markdown("**Generate music cue sheets from Premiere Pro XML exports**")

        # Section 1: Setup Files
        self.music_section_1()

        # Section 2: Configure Options
        self.music_section_2()

        # Section 3: Generate
        self.music_section_3()

    def music_section_1(self):
        """Music Cue Section 1: Setup Files."""
        with st.expander("1. Setup Files", expanded=(st.session_state.music_section == 1)):
            section_header("Input Files")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Premiere XML File**")
                xml_file = st.file_uploader(
                    "Premiere XML",
                    type=['xml'],
                    key="xml_upload",
                    help="XML export from Adobe Premiere Pro"
                )

                if xml_file:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as tmp_file:
                        tmp_file.write(xml_file.getvalue())
                        st.session_state.xml_path = tmp_file.name
                    file_status_message(xml_file.name)

            with col2:
                st.markdown("**Excel Template (Optional)**")
                cue_template = st.file_uploader(
                    "Cue Sheet Template",
                    type=['xlsx', 'xls'],
                    key="cue_template_upload",
                    help="Optional: Your cue sheet template"
                )

                if cue_template:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                        tmp_file.write(cue_template.getvalue())
                        st.session_state.cue_template_path = tmp_file.name
                    file_status_message(cue_template.name)

            section_divider()
            status_summary([
                ("XML File", "Ready" if st.session_state.xml_path else "Waiting..."),
                ("Template", "Ready" if st.session_state.cue_template_path else "Optional")
            ])

            st.markdown("")
            if st.session_state.xml_path:
                if primary_button("Continue to Configure", key="music_continue_1"):
                    st.session_state.music_section = 2
                    st.rerun()
            else:
                st.info("Upload a Premiere XML file to continue")

    def music_section_2(self):
        """Music Cue Section 2: Configure Options."""
        with st.expander("2. Configure Options", expanded=(st.session_state.music_section == 2)):
            if st.session_state.music_section < 2:
                st.info("Complete Section 1 first")
                return

            section_header("Filtering Options")

            st.session_state.filter_keyword = st.text_input(
                "Filter Keyword",
                value=st.session_state.filter_keyword,
                help="Only include audio files containing this keyword (e.g., 'alibi' for Alibi Music library)"
            )

            st.caption("Leave empty to include all audio files from the XML")

            section_divider()
            if primary_button("Continue to Generate", key="music_continue_2"):
                st.session_state.music_section = 3
                st.rerun()

    def music_section_3(self):
        """Music Cue Section 3: Generate."""
        with st.expander("3. Generate Cue Sheet", expanded=(st.session_state.music_section == 3)):
            if st.session_state.music_section < 3:
                st.info("Complete Section 2 first")
                return

            if not st.session_state.music_complete:
                section_header("Processing Summary")

                summary_data = {
                    "Setting": ["XML File", "Template", "Filter Keyword"],
                    "Value": [
                        "Ready",
                        "Provided" if st.session_state.cue_template_path else "Basic template",
                        st.session_state.filter_keyword or "None (all files)"
                    ]
                }
                st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)

                st.markdown("")
                if primary_button("Generate Cue Sheet", key="generate_cue_sheet"):
                    self._start_music_processing()
            else:
                st.success(f"Cue sheet generation complete! ({st.session_state.cue_count} cues)")

                if 'excel' in st.session_state.music_result_files:
                    excel_path = st.session_state.music_result_files['excel']
                    if os.path.exists(excel_path):
                        section_header("Download")
                        st.markdown(f"**File:** `{Path(excel_path).name}`")

                        with open(excel_path, 'rb') as f:
                            st.download_button(
                                label="Download Cue Sheet",
                                data=f.read(),
                                file_name=Path(excel_path).name,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )

    def _start_music_processing(self):
        """Execute music cue sheet generation."""
        output_dir = tempfile.mkdtemp()
        st.session_state.cue_output_dir = output_dir

        progress_widget = st.progress(0)
        status_text = st.empty()

        try:
            def update_progress(progress: float, message: str):
                progress_widget.progress(progress)
                status_text.text(message)

            results = self.music_processor.process(
                xml_path=st.session_state.xml_path,
                template_path=st.session_state.cue_template_path,
                output_dir=output_dir,
                filter_keyword=st.session_state.filter_keyword or "",
                progress_callback=update_progress
            )

            if results['status'] == 'success':
                st.session_state.music_result_files = results['files']
                st.session_state.cue_count = results['cue_count']
                st.session_state.music_complete = True
                st.rerun()
            elif results['status'] == 'warning':
                st.warning(results['message'])
            else:
                st.error(f"Processing failed: {results['message']}")

        except Exception as e:
            st.error(f"Processing failed: {str(e)}")
            logger.error(f"Music processing error: {e}")


def main():
    """Main entry point."""
    app = DocShipper()
    app.run()


if __name__ == "__main__":
    main()
