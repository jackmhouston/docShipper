"""
Reusable UI Components for DocShipper
Page-based wizard components with B/W minimal aesthetic
"""

import re
import streamlit as st
import pandas as pd
from typing import List, Tuple, Optional, Dict
from ui.tokens import COLORS


# Example data for the mapping grid preview
EXAMPLE_DATA = {
    'clip_name': 'clip001.mov',
    'src_start': '01:00:02:15',
    'src_end': '01:00:15:22',
    'rec_start': '00:00:00:00',
    'rec_end': '00:00:13:07',
    'duration': '00:00:13:07',
    'screenshot': '[image]',
}


def _num_to_col(n: int) -> str:
    """Convert 1-based column number to Excel letter (1=A, 2=B, ..., 27=AA)."""
    result = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result


def landing_header():
    """Render the landing page header."""
    st.markdown('<div class="landing-header">DocShipper</div>', unsafe_allow_html=True)
    st.markdown('<div class="landing-subtitle">Video Editing Document Automation</div>', unsafe_allow_html=True)


def workflow_button(title: str, description: str, key: str, enabled: bool = True) -> bool:
    """Large workflow selection button for landing page. Returns True if clicked."""
    clicked = st.button(
        f"{title}",
        key=key,
        use_container_width=True,
        help=description,
        disabled=not enabled,
    )
    if enabled:
        st.caption(description)
    else:
        st.caption(f"~~{description}~~")
    return clicked


def step_indicator(current: int, total: int, labels: List[str]):
    """Render a step indicator / breadcrumb. current is 1-indexed."""
    items_html = []

    for i in range(1, total + 1):
        if i < current:
            num_class = "step-number complete"
            label_class = "step-label"
            display_num = "+"
        elif i == current:
            num_class = "step-number active"
            label_class = "step-label active"
            display_num = str(i)
        else:
            num_class = "step-number"
            label_class = "step-label"
            display_num = str(i)

        label = labels[i-1] if i-1 < len(labels) else f"Step {i}"
        items_html.append(f'<div class="step-item"><div class="{num_class}">{display_num}</div><span class="{label_class}">{label}</span></div>')

        if i < total:
            items_html.append('<div class="step-separator"></div>')

    html = f'<div class="step-indicator">{"".join(items_html)}</div>'
    st.markdown(html, unsafe_allow_html=True)


def page_title(title: str, subtitle: str = None):
    """Render page title with optional subtitle."""
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def section_header(title: str):
    """Render section header."""
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def nav_buttons(
    back_enabled: bool = True,
    next_label: str = "Next",
    next_enabled: bool = True,
    back_label: str = "Back",
    show_back: bool = True
) -> Tuple[bool, bool]:
    """Render navigation buttons (Back / Next). Returns (back_clicked, next_clicked)."""
    col1, col2, col3 = st.columns([1, 2, 1])

    back_clicked = False
    next_clicked = False

    with col1:
        if show_back:
            back_clicked = st.button(
                back_label,
                key=f"nav_back_{next_label}",
                disabled=not back_enabled,
                use_container_width=True
            )

    with col3:
        next_clicked = st.button(
            next_label,
            key=f"nav_next_{next_label}",
            type="primary",
            disabled=not next_enabled,
            use_container_width=True
        )

    return back_clicked, next_clicked


# ========== NEW: Mapping Grid Components ==========


def render_interactive_grid(
    field_order: List[str],
    fields: Dict[str, Tuple[str, str]],
    selected_column: Optional[int] = None,
    total_columns: int = 10,
    total_rows: int = 5,
) -> Optional[int]:
    """Render Excel-like grid preview with column selection.

    Displays an HTML table for the visual grid and a selectbox for
    column selection. Returns the selected column index (0-based) or None.
    """
    num_mapped = len(field_order)
    num_cols = max(num_mapped, total_columns)

    # Build HTML table
    rows_html = []

    # Column header row (A, B, C, ...)
    header_cells = ['<th class="corner"></th>']
    for col_idx in range(num_cols):
        col_letter = _num_to_col(col_idx + 1)
        cls = "col-header selected" if col_idx == selected_column else "col-header"
        header_cells.append(f'<th class="{cls}">{col_letter}</th>')
    rows_html.append(f'<tr>{"".join(header_cells)}</tr>')

    # Data rows (1 through total_rows)
    for row_num in range(1, total_rows + 1):
        cells = [f'<td class="row-header">{row_num}</td>']
        for col_idx in range(num_cols):
            is_selected = col_idx == selected_column
            has_field = col_idx < num_mapped

            if is_selected:
                cls = "cell selected"
            elif has_field and row_num == 1:
                cls = "cell field-header"
            elif has_field and row_num == 2:
                cls = "cell field-data"
            else:
                cls = "cell empty"

            if has_field:
                field_key = field_order[col_idx]
                if row_num == 1:
                    content = fields[field_key][0] if field_key in fields else field_key
                elif row_num == 2:
                    content = EXAMPLE_DATA.get(field_key, '')
                else:
                    content = ''
            else:
                content = ''

            cells.append(f'<td class="{cls}">{content}</td>')
        rows_html.append(f'<tr>{"".join(cells)}</tr>')

    table_html = f'<div class="excel-grid"><table>{"".join(rows_html)}</table></div>'
    st.markdown(table_html, unsafe_allow_html=True)

    # Color legend
    legend_html = """
    <div class="mapping-legend">
        <div class="legend-item">
            <div class="legend-swatch header"></div>
            <span class="legend-label">Header Row</span>
        </div>
        <div class="legend-item">
            <div class="legend-swatch data"></div>
            <span class="legend-label">Data Row</span>
        </div>
        <div class="legend-item">
            <div class="legend-swatch selected"></div>
            <span class="legend-label">Selected</span>
        </div>
    </div>
    """
    st.markdown(legend_html, unsafe_allow_html=True)

    # Column selection dropdown
    options = ["-- Select a column --"]
    for i in range(num_cols):
        col_letter = _num_to_col(i + 1)
        if i < num_mapped:
            field_key = field_order[i]
            display = fields[field_key][0] if field_key in fields else field_key
            options.append(f"{col_letter} - {display}")
        else:
            options.append(f"{col_letter} - (empty)")

    default_idx = (selected_column + 1) if selected_column is not None else 0

    selected = st.selectbox(
        "Select column to edit",
        options,
        index=default_idx,
        key=f"grid_col_{selected_column}",
        label_visibility="collapsed",
    )

    if selected == options[0]:
        return None
    return options.index(selected) - 1


def field_checkboxes(
    fields: Dict[str, Tuple[str, str]],
    selected_fields: List[str],
    required_fields: List[str],
) -> List[str]:
    """Render field selection checkboxes in 2-column layout.

    Required fields are always checked and disabled.
    Returns updated list of selected field keys.
    """
    updated = list(required_fields)

    optional_fields = [k for k in fields if k not in required_fields]

    col1, col2 = st.columns(2)

    # Required fields first (disabled, always checked)
    for i, field_key in enumerate(required_fields):
        display_name = fields[field_key][0]
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            st.checkbox(
                f"{display_name} (required)",
                value=True,
                disabled=True,
                key=f"fchk_{field_key}",
            )

    # Optional fields (toggleable)
    for i, field_key in enumerate(optional_fields):
        display_name = fields[field_key][0]
        target_col = col1 if (len(required_fields) + i) % 2 == 0 else col2
        is_selected = field_key in selected_fields
        with target_col:
            checked = st.checkbox(
                display_name,
                value=is_selected,
                key=f"fchk_{field_key}",
            )
            if checked:
                updated.append(field_key)

    return updated


def field_assignment_panel(
    selected_col: int,
    field_order: List[str],
    all_fields: Dict[str, Tuple[str, str]],
) -> Optional[str]:
    """Render field assignment panel for the selected column.

    Shows buttons for each available (unassigned) field, plus the currently
    assigned field, a Clear button, and a Swap button.

    Returns:
        - field key string: assign this field to the column
        - "clear": clear the column
        - "swap": enter swap mode
        - None: no action taken
    """
    col_letter = _num_to_col(selected_col + 1)
    current_field = field_order[selected_col] if selected_col < len(field_order) else None

    st.markdown(
        f'<div class="assign-panel-title">Assign Field to Column {col_letter}</div>',
        unsafe_allow_html=True,
    )

    # Determine which fields are already assigned to OTHER columns
    assigned_fields = set(field_order)

    # Available fields = all fields not assigned elsewhere (but include current)
    available = []
    for field_key in all_fields:
        if field_key not in assigned_fields or field_key == current_field:
            available.append(field_key)

    # Render field buttons in a grid (3 columns)
    num_btns = len(available) + 2  # +clear +swap
    btn_cols = st.columns(3)

    result = None

    for i, field_key in enumerate(available):
        display_name = all_fields[field_key][0]
        is_current = field_key == current_field
        with btn_cols[i % 3]:
            btn_label = f"{display_name}" if not is_current else f"{display_name} (current)"
            if st.button(
                btn_label,
                key=f"assign_{field_key}_{selected_col}",
                use_container_width=True,
                type="primary" if is_current else "secondary",
            ):
                if not is_current:
                    result = field_key

    # Action buttons row
    act_col1, act_col2, act_col3 = st.columns(3)

    with act_col1:
        if current_field and st.button(
            "Clear Cell",
            key=f"clear_{selected_col}",
            use_container_width=True,
        ):
            result = "clear"

    with act_col2:
        if current_field and st.button(
            "Swap with...",
            key=f"swap_{selected_col}",
            use_container_width=True,
        ):
            result = "swap"

    return result


# ========== Status & Feedback Components ==========


def status_badge(ready: bool, ready_text: str = "Ready", waiting_text: str = "Waiting...") -> str:
    """Return HTML for a status badge."""
    if ready:
        return f'<span class="status-ready">{ready_text}</span>'
    else:
        return f'<span class="status-waiting">{waiting_text}</span>'


def file_status(filename: str, details: str = None, success: bool = True):
    """Display file upload status."""
    if success:
        if details:
            st.success(f"{filename} ({details})")
        else:
            st.success(f"{filename}")
    else:
        st.error(f"Failed: {filename}")


def status_row(items: List[Tuple[str, bool, str]]):
    """Render a row of status items. items: List of (label, is_ready, detail_text)."""
    cols = st.columns(len(items))
    for i, (label, is_ready, detail) in enumerate(items):
        with cols[i]:
            status = "Ready" if is_ready else "Waiting..."
            status_class = "status-ready" if is_ready else "status-waiting"
            st.markdown(f"**{label}**: <span class='{status_class}'>{detail or status}</span>", unsafe_allow_html=True)


def info_box(message: str, variant: str = "info"):
    """Render styled info box."""
    if variant == "success":
        st.success(message)
    elif variant == "error":
        st.error(message)
    elif variant == "warning":
        st.warning(message)
    else:
        st.info(message)


def divider():
    """Render a horizontal divider."""
    st.markdown("---")


def primary_button(label: str, key: str, full_width: bool = True, disabled: bool = False) -> bool:
    """Primary action button."""
    return st.button(
        label,
        type="primary",
        use_container_width=full_width,
        key=key,
        disabled=disabled
    )


def secondary_button(label: str, key: str, full_width: bool = False, disabled: bool = False) -> bool:
    """Secondary action button."""
    return st.button(
        label,
        type="secondary",
        use_container_width=full_width,
        key=key,
        disabled=disabled
    )


def data_table(df: pd.DataFrame, hide_index: bool = True):
    """Render a styled data table."""
    st.dataframe(df, use_container_width=True, hide_index=hide_index)


def mapping_summary(mappings: Dict[str, str], field_names: Dict[str, str]):
    """Display a summary of current mappings."""
    if not mappings:
        st.info("No mappings configured")
        return

    data = []
    for field, cell in sorted(mappings.items(), key=lambda x: x[1]):
        data.append({
            "Field": field_names.get(field, field.replace('_', ' ').title()),
            "Cell": cell
        })

    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)


def xml_detection_card(filename: str, project_title: str,
                       video_count: int, audio_count: int, fps: Optional[float] = None):
    """Render an XML content detection summary card."""
    fps_text = f" at {fps} fps" if fps else ""
    html = f'''
    <div class="detection-card">
        <div class="detection-filename">{filename}</div>
        <div class="detection-project">{project_title}</div>
        <div class="detection-counts">
            <div class="detection-item">
                <div class="detection-count">{video_count}</div>
                <div class="detection-label">Video Clips</div>
            </div>
            <div class="detection-item">
                <div class="detection-count">{audio_count}</div>
                <div class="detection-label">Audio Files</div>
            </div>
        </div>
        <div class="detection-fps">{fps_text}</div>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)
