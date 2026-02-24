"""
UI Component Library for DocShipper
Modern, minimal design with blue/gold palette
"""

from ui.tokens import COLORS, FONTS, FONT_SIZES, SPACING, BORDERS
from ui.styles import get_global_css, inject_styles
from ui.components import (
    page_header,
    section_header,
    card,
    info_box,
    file_upload_card,
    status_badge,
    progress_bar,
    primary_button,
    secondary_button,
    status_summary,
    field_label,
    data_table,
    section_divider,
    file_status_message,
    mapping_display,
)

__all__ = [
    # Tokens
    "COLORS",
    "FONTS",
    "FONT_SIZES",
    "SPACING",
    "BORDERS",
    # Styles
    "get_global_css",
    "inject_styles",
    # Components
    "page_header",
    "section_header",
    "card",
    "info_box",
    "file_upload_card",
    "status_badge",
    "progress_bar",
    "primary_button",
    "secondary_button",
    "status_summary",
    "field_label",
    "data_table",
    "section_divider",
    "file_status_message",
    "mapping_display",
]
