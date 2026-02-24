"""
Reusable UI Components for DocShipper
Styled components using design tokens
"""

import streamlit as st
import pandas as pd
from typing import Callable, List, Tuple, Optional, Any
from ui.tokens import COLORS, FONTS, FONT_SIZES, SPACING, BORDERS


def page_header(title: str, subtitle: str = None):
    """Render main page header with optional subtitle."""
    st.markdown(f'<div class="main-header">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="main-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def section_header(title: str, badge: str = None):
    """Render section header with optional badge."""
    if badge:
        st.markdown(f'<div class="section-title">{badge} {title}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def card(title: str = None):
    """Create a styled card container context."""
    container = st.container()
    if title:
        container.markdown(f'<div class="card-header">{title}</div>', unsafe_allow_html=True)
    return container


def info_box(message: str, variant: str = "info"):
    """Render styled info/success/warning/error box."""
    variant_class = {
        "info": "",
        "success": " info-box-success",
        "warning": " info-box-warning",
        "error": " info-box-error"
    }.get(variant, "")

    st.markdown(
        f'<div class="info-box{variant_class}">{message}</div>',
        unsafe_allow_html=True
    )


def file_upload_card(
    label: str,
    file_types: List[str],
    key: str,
    help_text: str = None
) -> Any:
    """Styled file uploader with consistent styling."""
    st.markdown(f"**{label}**")
    return st.file_uploader(
        label,
        type=file_types,
        key=key,
        help=help_text,
        label_visibility="collapsed"
    )


def status_badge(status: str, label: str = None) -> str:
    """Return HTML for a status badge."""
    badge_class = {
        "complete": "status-badge-complete",
        "active": "status-badge-active",
        "pending": "status-badge-pending"
    }.get(status, "status-badge-pending")

    display_label = label or status.capitalize()
    return f'<span class="status-badge {badge_class}">{display_label}</span>'


def progress_bar(percent: int):
    """Render custom styled progress bar."""
    percent = max(0, min(100, percent))
    html = f"""
    <div class="progress-container">
        <div class="progress-fill" style="width: {percent}%;"></div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


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


def status_summary(items: List[Tuple[str, str]]):
    """Render a status summary as columns."""
    cols = st.columns(len(items))
    for i, (name, status) in enumerate(items):
        with cols[i]:
            st.markdown(f"**{name}**: {status}")


def field_label(text: str):
    """Render a styled field label."""
    st.markdown(f'<div class="field-label">{text}</div>', unsafe_allow_html=True)


def data_table(
    df: pd.DataFrame,
    editable: bool = False,
    hide_index: bool = True,
    num_rows: str = "fixed"
) -> pd.DataFrame:
    """Render a styled data table."""
    if editable:
        return st.data_editor(
            df,
            use_container_width=True,
            hide_index=hide_index,
            num_rows=num_rows
        )
    else:
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=hide_index
        )
        return df


def section_divider():
    """Render a styled horizontal divider."""
    st.markdown("---")


def file_status_message(filename: str, details: str = None, success: bool = True):
    """Display a file status message."""
    if success:
        if details:
            st.success(f"Loaded: {filename} ({details})")
        else:
            st.success(f"Loaded: {filename}")
    else:
        st.error(f"Failed: {filename}")


def mapping_display(mappings: dict, field_names: dict):
    """Display mapping configuration as a table."""
    if not mappings:
        st.info("No mappings configured")
        return

    mapping_data = []
    for field, cell_ref in sorted(mappings.items(), key=lambda x: x[1]):
        col_letter = ''.join(filter(str.isalpha, cell_ref))
        mapping_data.append({
            "Column": col_letter,
            "Field": field_names.get(field, field.replace('_', ' ').title()),
            "Cell": cell_ref
        })

    df_mappings = pd.DataFrame(mapping_data)
    st.dataframe(df_mappings, use_container_width=True, hide_index=True)


def workflow_card(title: str, description: str, icon: str = None):
    """Display a workflow selection card."""
    with st.container():
        if icon:
            st.markdown(f"### {icon} {title}")
        else:
            st.markdown(f"### {title}")
        st.caption(description)
