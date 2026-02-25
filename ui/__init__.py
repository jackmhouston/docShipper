"""
UI Component Library for DocShipper
Minimal B/W design with page-based wizard components
"""

from ui.tokens import COLORS, FONTS, FONT_SIZES, SPACING, BORDERS, GRID
from ui.styles import get_global_css, inject_styles
from ui.components import (
    landing_header,
    workflow_button,
    step_indicator,
    page_title,
    section_header,
    nav_buttons,
    render_interactive_grid,
    field_checkboxes,
    field_assignment_panel,
    status_badge,
    file_status,
    status_row,
    info_box,
    divider,
    primary_button,
    secondary_button,
    data_table,
    mapping_summary,
    xml_detection_card,
)

__all__ = [
    # Tokens
    "COLORS",
    "FONTS",
    "FONT_SIZES",
    "SPACING",
    "BORDERS",
    "GRID",
    # Styles
    "get_global_css",
    "inject_styles",
    # Components
    "landing_header",
    "workflow_button",
    "step_indicator",
    "page_title",
    "section_header",
    "nav_buttons",
    "render_interactive_grid",
    "field_checkboxes",
    "field_assignment_panel",
    "status_badge",
    "file_status",
    "status_row",
    "info_box",
    "divider",
    "primary_button",
    "secondary_button",
    "data_table",
    "mapping_summary",
    "xml_detection_card",
]
