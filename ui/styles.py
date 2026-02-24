"""
CSS Styles for DocShipper
hybrid.css theme - CS16 beveled 3D + Classic Mac monochrome
"""

import streamlit as st
from ui.tokens import (
    COLORS, FONTS, FONT_SIZES, FONT_WEIGHTS, SPACING, BORDERS, SHADOWS,
    TRANSITIONS, LETTER_SPACING, BLACK, WHITE, LIGHT_GREY, DARK_GREY,
    ACCENT, ACCENT_LIGHT, ACCENT_DARK,
    COLOR_OK, COLOR_OK_LIGHT, COLOR_OK_DARK,
    COLOR_SUCCESS, COLOR_SUCCESS_LIGHT, COLOR_SUCCESS_DARK,
    COLOR_DANGER, COLOR_DANGER_LIGHT, COLOR_DANGER_DARK,
    ARIAL_PIXEL_BASE64,
)


def get_global_css() -> str:
    """Return complete CSS stylesheet using hybrid.css design system."""
    return f"""
    <style>
    /* ============================================
       FONT - ArialPixel embedded
       ============================================ */
    @font-face {{
        font-family: 'ArialPixel';
        src: url('data:font/truetype;base64,{ARIAL_PIXEL_BASE64}') format('truetype');
        font-weight: normal;
        font-style: normal;
    }}

    /* ============================================
       BASE STYLING - hybrid.css theme
       ============================================ */

    * {{
        box-sizing: border-box;
    }}

    /* Force ArialPixel font on text elements, but NOT on icon elements */
    body, .stApp, .main,
    p, label, button, input, select, textarea,
    h1, h2, h3, h4, h5, h6,
    .stMarkdown, .stMarkdown p, .stMarkdown span,
    [data-testid="stMarkdownContainer"],
    .main-header, .main-subtitle, .section-title {{
        font-family: {FONTS['primary']} !important;
    }}

    /* CRITICAL: Exclude Material Icons - they use icon font ligatures */
    [data-testid="stIconMaterial"],
    [data-testid="stIcon"],
    .material-icons,
    [translate="no"],
    span[class*="icon"],
    svg {{
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
    }}

    /* Expander title text only (not the icon) */
    [data-testid="stMarkdownContainer"],
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"],
    details summary [data-testid="stMarkdownContainer"] {{
        font-family: {FONTS['primary']} !important;
    }}

    /* Speckled grid background */
    .stApp {{
        background: linear-gradient(90deg, {WHITE} 21px, transparent 1%) center,
                    linear-gradient({WHITE} 21px, transparent 1%) center,
                    {BLACK} !important;
        background-size: 22px 22px !important;
        background-attachment: fixed !important;
    }}

    .main .block-container {{
        background-color: {WHITE};
        border: 2px solid {BLACK};
        padding: {SPACING['lg']} !important;
        max-width: 900px;
    }}

    body, .stApp, .main {{
        color: {COLORS['text']};
    }}

    /* Global link styling - monochrome */
    a, a:visited, a:hover, a:active {{
        color: {BLACK} !important;
    }}

    /* Override any blue/accent colors globally */
    .stApp *[style*="color: rgb(0,"] {{
        color: {BLACK} !important;
    }}

    /* ============================================
       HEADER
       ============================================ */

    .main-header {{
        font-size: {FONT_SIZES['2xl']};
        color: {BLACK} !important;
        text-align: center;
        margin: {SPACING['lg']} 0 {SPACING['sm']} 0;
        font-weight: {FONT_WEIGHTS['bold']};
        letter-spacing: {LETTER_SPACING['normal']};
        line-height: 1.2;
    }}

    .main-subtitle {{
        text-align: center;
        color: {DARK_GREY} !important;
        font-size: {FONT_SIZES['sm']};
        letter-spacing: {LETTER_SPACING['tight']};
        line-height: 1.5;
        margin-bottom: {SPACING['xl']};
    }}

    /* ============================================
       PROGRESS BAR - Segmented fill
       ============================================ */

    .progress-container {{
        width: 100%;
        height: 24px;
        background-color: {COLORS['secondary_bg']};
        border: 1px solid {BLACK};
        box-shadow: {SHADOWS['inset']};
        margin-bottom: {SPACING['xl']};
        padding: 3px;
    }}

    .progress-fill {{
        height: 100%;
        background-image: linear-gradient(
            to right,
            {COLOR_OK} 8px,
            transparent 2px
        );
        background-size: 12px 100%;
        transition: width 400ms ease;
    }}

    /* ============================================
       EXPANDERS / SECTIONS - Beveled borders
       ============================================ */

    .stExpander {{
        border: 1px solid {BLACK} !important;
        border-radius: 0 !important;
        margin-bottom: {SPACING['md']} !important;
        background-color: {WHITE} !important;
        box-shadow: {SHADOWS['bevel_raised']} !important;
    }}

    .stExpander:hover {{
        background-color: {COLORS['secondary_bg']} !important;
    }}

    details[open] summary {{
        border-bottom: 1px solid {BLACK} !important;
        margin-bottom: {SPACING['md']} !important;
        padding-bottom: {SPACING['sm']} !important;
    }}

    summary {{
        font-size: {FONT_SIZES['sm']} !important;
        font-weight: {FONT_WEIGHTS['bold']} !important;
        color: {BLACK} !important;
        letter-spacing: {LETTER_SPACING['normal']} !important;
        padding: {SPACING['md']} !important;
        line-height: 1.4 !important;
        background-color: {WHITE} !important;
    }}

    summary:hover {{
        background-color: {COLORS['secondary_bg']} !important;
    }}

    /* ============================================
       FILE UPLOADER - Monochrome styling
       ============================================ */

    .stFileUploader label,
    [data-testid="stFileUploader"] label {{
        color: {BLACK} !important;
        font-weight: {FONT_WEIGHTS['bold']} !important;
    }}

    .stFileUploader [data-testid="stFileUploadDropzone"],
    [data-testid="stFileUploaderDropzone"] {{
        background-color: {COLORS['secondary_bg']} !important;
        border: 1px dashed {BLACK} !important;
        border-radius: 0 !important;
        box-shadow: {SHADOWS['inset']} !important;
    }}

    .stFileUploader [data-testid="stFileUploadDropzone"]:hover,
    [data-testid="stFileUploaderDropzone"]:hover {{
        background-color: {WHITE} !important;
    }}

    /* File uploader text - make all text black */
    [data-testid="stFileUploaderDropzone"] span,
    [data-testid="stFileUploaderDropzone"] p,
    [data-testid="stFileUploaderDropzone"] small,
    .stFileUploader span,
    .stFileUploader p {{
        color: {BLACK} !important;
    }}

    /* Override blue link color in file uploader */
    [data-testid="stFileUploaderDropzone"] a,
    [data-testid="stFileUploaderDropzoneInstructions"] span {{
        color: {BLACK} !important;
        text-decoration: underline !important;
    }}

    /* File uploader icon */
    [data-testid="stFileUploaderDropzone"] svg {{
        stroke: {BLACK} !important;
        fill: none !important;
    }}

    /* ============================================
       BUTTONS - Beveled 3D style
       Using data-testid for Streamlit specificity
       ============================================ */

    /* All buttons base reset */
    button[data-testid^="stBaseButton"],
    .stButton > button,
    .stDownloadButton > button,
    [data-testid="stFileUploaderDropzone"] > button {{
        background-color: {ACCENT} !important;
        color: {BLACK} !important;
        border: 1px solid {BLACK} !important;
        border-radius: 0 !important;
        font-family: {FONTS['primary']} !important;
        font-size: {FONT_SIZES['sm']} !important;
        font-weight: {FONT_WEIGHTS['bold']} !important;
        padding: 8px 16px !important;
        text-transform: uppercase !important;
        letter-spacing: {LETTER_SPACING['normal']} !important;
        box-shadow: inset 1px 1px 0 {ACCENT_LIGHT},
                    inset -1px -1px 0 {ACCENT_DARK},
                    2px 2px 0 {BLACK} !important;
        transition: all {TRANSITIONS['fast']} !important;
        cursor: pointer !important;
    }}

    button[data-testid^="stBaseButton"]:hover,
    .stButton > button:hover,
    [data-testid="stFileUploaderDropzone"] > button:hover {{
        background-color: {ACCENT_LIGHT} !important;
    }}

    button[data-testid^="stBaseButton"]:active,
    .stButton > button:active,
    [data-testid="stFileUploaderDropzone"] > button:active {{
        background-color: {ACCENT_DARK} !important;
        box-shadow: inset -1px -1px 0 {ACCENT_LIGHT},
                    inset 1px 1px 0 {ACCENT_DARK} !important;
        transform: translate(2px, 2px) !important;
    }}

    /* Primary button (blue - OK/execute) */
    button[data-testid="stBaseButton-primary"],
    .stButton > button[kind="primary"] {{
        background-color: {COLOR_OK} !important;
        color: {WHITE} !important;
        box-shadow: inset 1px 1px 0 {COLOR_OK_LIGHT},
                    inset -1px -1px 0 {COLOR_OK_DARK},
                    2px 2px 0 {BLACK} !important;
    }}

    button[data-testid="stBaseButton-primary"]:hover,
    .stButton > button[kind="primary"]:hover {{
        background-color: {COLOR_OK_LIGHT} !important;
    }}

    button[data-testid="stBaseButton-primary"]:active,
    .stButton > button[kind="primary"]:active {{
        background-color: {COLOR_OK_DARK} !important;
        box-shadow: inset -1px -1px 0 {COLOR_OK_LIGHT},
                    inset 1px 1px 0 {COLOR_OK_DARK} !important;
    }}

    /* Download button (green - success) */
    .stDownloadButton > button {{
        background-color: {COLOR_SUCCESS} !important;
        color: {WHITE} !important;
        border: 1px solid {BLACK} !important;
        border-radius: 0 !important;
        font-weight: {FONT_WEIGHTS['bold']} !important;
        box-shadow: inset 1px 1px 0 {COLOR_SUCCESS_LIGHT},
                    inset -1px -1px 0 {COLOR_SUCCESS_DARK},
                    2px 2px 0 {BLACK} !important;
    }}

    .stDownloadButton > button:hover {{
        background-color: {COLOR_SUCCESS_LIGHT} !important;
    }}

    .stDownloadButton > button:active {{
        background-color: {COLOR_SUCCESS_DARK} !important;
        box-shadow: inset -1px -1px 0 {COLOR_SUCCESS_LIGHT},
                    inset 1px 1px 0 {COLOR_SUCCESS_DARK} !important;
    }}

    /* ============================================
       TEXT INPUTS - Inset beveled
       ============================================ */

    .stTextInput label, .stNumberInput label {{
        color: {BLACK} !important;
        font-weight: {FONT_WEIGHTS['bold']} !important;
    }}

    .stTextInput input, .stNumberInput input {{
        background-color: {COLORS['secondary_bg']} !important;
        border: 1px solid {BLACK} !important;
        border-radius: 0 !important;
        color: {BLACK} !important;
        font-family: {FONTS['primary']} !important;
        box-shadow: {SHADOWS['inset']} !important;
    }}

    .stTextInput input:focus, .stNumberInput input:focus {{
        background-color: {WHITE} !important;
        outline: none !important;
        box-shadow: {SHADOWS['inset']} !important;
    }}

    /* ============================================
       TABS - hybrid.css style
       Using data-testid for Streamlit specificity
       ============================================ */

    .stTabs [data-baseweb="tab-list"] {{
        gap: 0 !important;
        background-color: transparent !important;
        border-bottom: 1px solid {BLACK} !important;
    }}

    .stTabs [data-baseweb="tab"],
    button[data-testid="stTab"] {{
        background-color: {COLORS['secondary_bg']} !important;
        border: 1px solid {BLACK} !important;
        border-bottom: none !important;
        border-radius: 0 !important;
        color: {BLACK} !important;
        font-weight: {FONT_WEIGHTS['semibold']} !important;
        padding: 8px 16px !important;
        margin-right: -1px !important;
        margin-bottom: -1px !important;
        box-shadow: inset 1px 1px 0 {LIGHT_GREY},
                    inset -1px 0 0 {DARK_GREY} !important;
        text-transform: none !important;
    }}

    .stTabs [data-baseweb="tab"]:hover,
    button[data-testid="stTab"]:hover {{
        background-color: {WHITE} !important;
    }}

    .stTabs [aria-selected="true"],
    button[data-testid="stTab"][aria-selected="true"] {{
        background-color: {WHITE} !important;
        font-weight: {FONT_WEIGHTS['bold']} !important;
        z-index: 1 !important;
        position: relative !important;
        box-shadow: inset 1px 1px 0 {LIGHT_GREY},
                    inset -1px 0 0 {DARK_GREY} !important;
    }}

    .stTabs [data-baseweb="tab-panel"] {{
        border: 1px solid {BLACK} !important;
        border-top: none !important;
        border-radius: 0 !important;
        background: {WHITE} !important;
        padding: {SPACING['md']} !important;
    }}

    /* ============================================
       DATAFRAME / TABLE
       ============================================ */

    .stDataFrame {{
        border: 1px solid {BLACK} !important;
        border-radius: 0 !important;
        overflow: hidden !important;
    }}

    .stDataFrame td, .stDataFrame th {{
        color: {BLACK} !important;
        background-color: {WHITE} !important;
        border: 1px solid {BLACK} !important;
        font-size: {FONT_SIZES['sm']} !important;
        padding: 8px !important;
        line-height: 1.5 !important;
    }}

    .stDataFrame th {{
        background-color: {COLORS['secondary_bg']} !important;
        font-weight: {FONT_WEIGHTS['bold']} !important;
        text-transform: uppercase !important;
        font-size: {FONT_SIZES['xs']} !important;
        letter-spacing: {LETTER_SPACING['normal']} !important;
        box-shadow: inset 1px 1px 0 {LIGHT_GREY},
                    inset -1px -1px 0 {DARK_GREY} !important;
    }}

    /* ============================================
       ALERTS / STATUS BOXES - Beveled styling
       ============================================ */

    /* Base alert styling */
    .stAlert, [data-testid="stAlert"],
    [data-testid="stNotification"] {{
        background-color: {COLORS['secondary_bg']} !important;
        border: 1px solid {BLACK} !important;
        border-left: 4px solid {BLACK} !important;
        border-radius: 0 !important;
        color: {BLACK} !important;
        box-shadow: {SHADOWS['inset']} !important;
    }}

    /* Remove default colored indicators */
    .stAlert div[data-testid] > div:first-child,
    [data-testid="stAlert"] > div:first-child {{
        background-color: transparent !important;
    }}

    /* Success message (green) */
    .stSuccess, [data-testid="stSuccess"],
    [data-testid="stNotificationContentSuccess"] {{
        background-color: {COLOR_SUCCESS} !important;
        color: {WHITE} !important;
        border: 1px solid {BLACK} !important;
        border-left: 4px solid {COLOR_SUCCESS_DARK} !important;
        box-shadow: inset 1px 1px 0 {COLOR_SUCCESS_LIGHT},
                    inset -1px -1px 0 {COLOR_SUCCESS_DARK} !important;
    }}

    /* Error message (red border, white bg) */
    .stError, [data-testid="stError"],
    [data-testid="stNotificationContentError"] {{
        background-color: {WHITE} !important;
        color: {BLACK} !important;
        border: 2px solid {COLOR_DANGER} !important;
        border-left: 4px solid {COLOR_DANGER} !important;
        font-weight: {FONT_WEIGHTS['bold']} !important;
    }}

    /* Warning message (yellow) */
    .stWarning, [data-testid="stWarning"],
    [data-testid="stNotificationContentWarning"] {{
        background-color: {ACCENT} !important;
        color: {BLACK} !important;
        border: 1px solid {BLACK} !important;
        border-left: 4px solid {ACCENT_DARK} !important;
        box-shadow: inset 1px 1px 0 {ACCENT_LIGHT},
                    inset -1px -1px 0 {ACCENT_DARK} !important;
    }}

    /* Info message (grey) */
    .stInfo, [data-testid="stInfo"],
    [data-testid="stNotificationContentInfo"] {{
        background-color: {COLORS['secondary_bg']} !important;
        color: {BLACK} !important;
        border: 1px solid {BLACK} !important;
        border-left: 4px solid {DARK_GREY} !important;
        box-shadow: {SHADOWS['inset']} !important;
    }}

    /* Alert text - force black on all nested elements */
    .stAlert p, [data-testid="stAlert"] p,
    .stAlert span, [data-testid="stAlert"] span,
    .stAlert div, [data-testid="stAlert"] div,
    [role="alert"] p, [role="alert"] span, [role="alert"] div,
    [data-testid="stNotification"] p,
    [data-testid="stNotification"] span,
    [data-testid="stNotification"] div {{
        color: {BLACK} !important;
    }}

    /* ============================================
       DIVIDERS
       ============================================ */

    hr {{
        border: none !important;
        border-top: 1px solid {DARK_GREY} !important;
        border-bottom: 1px solid {LIGHT_GREY} !important;
        margin: {SPACING['md']} 0 !important;
    }}

    /* ============================================
       SECTION TITLE
       ============================================ */

    .section-title {{
        font-size: {FONT_SIZES['sm']};
        color: {BLACK} !important;
        font-weight: {FONT_WEIGHTS['bold']};
        text-transform: uppercase;
        letter-spacing: {LETTER_SPACING['normal']};
        margin: {SPACING['md']} 0 {SPACING['sm']} 0;
        padding-bottom: {SPACING['sm']};
        border-bottom: 1px solid {BLACK};
    }}

    /* ============================================
       MARKDOWN
       ============================================ */

    .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown li {{
        color: {BLACK} !important;
    }}

    .stMarkdown strong {{
        color: {BLACK} !important;
        font-weight: {FONT_WEIGHTS['bold']} !important;
    }}

    /* ============================================
       CODE BLOCKS
       ============================================ */

    code, pre, .stMarkdown code {{
        background-color: {COLORS['secondary_bg']} !important;
        color: {BLACK} !important;
        padding: 2px 6px !important;
        border-radius: 0 !important;
        border: 1px solid {BLACK} !important;
        font-family: {FONTS['mono']} !important;
        box-shadow: {SHADOWS['inset']} !important;
    }}

    /* ============================================
       SELECT / DROPDOWN
       ============================================ */

    .stSelectbox [data-baseweb="select"] {{
        background-color: {COLORS['secondary_bg']} !important;
        border: 1px solid {BLACK} !important;
        border-radius: 0 !important;
        box-shadow: {SHADOWS['inset']} !important;
    }}

    .stSelectbox [data-baseweb="select"]:hover {{
        background-color: {WHITE} !important;
    }}

    /* ============================================
       CHECKBOX / RADIO - Monochrome styling
       ============================================ */

    .stCheckbox label, .stRadio label,
    [data-testid="stCheckbox"] label,
    [data-testid="stRadio"] label {{
        color: {BLACK} !important;
    }}

    /* Radio button - outer ring */
    [data-baseweb="radio"] > div:first-child {{
        border-color: {BLACK} !important;
        background-color: {WHITE} !important;
    }}

    /* Radio button - inner dot when selected */
    [data-baseweb="radio"] > div:first-child > div {{
        background-color: {BLACK} !important;
    }}

    /* Radio input styling */
    [data-testid="stRadio"] input[type="radio"] {{
        accent-color: {BLACK} !important;
    }}

    /* Checkbox - outer box (SQUARE corners) */
    [data-baseweb="checkbox"] > div:first-child {{
        border-color: {BLACK} !important;
        background-color: {WHITE} !important;
        border-radius: 0 !important;
    }}

    /* Checkbox - checkmark when selected */
    [data-baseweb="checkbox"] > div:first-child[aria-checked="true"],
    [data-baseweb="checkbox"][aria-checked="true"] > div:first-child {{
        background-color: {BLACK} !important;
        border-color: {BLACK} !important;
        border-radius: 0 !important;
    }}

    /* Force square corners on all checkbox elements */
    [data-testid="stCheckbox"] div,
    [data-baseweb="checkbox"],
    [data-baseweb="checkbox"] * {{
        border-radius: 0 !important;
    }}

    /* Checkbox input styling */
    [data-testid="stCheckbox"] input[type="checkbox"],
    .stCheckbox input[type="checkbox"] {{
        accent-color: {BLACK} !important;
    }}

    /* Override Streamlit's custom checkbox/radio SVG icons */
    [data-testid="stCheckbox"] svg,
    [data-testid="stRadio"] svg,
    [data-baseweb="checkbox"] svg,
    [data-baseweb="radio"] svg {{
        fill: {WHITE} !important;
        stroke: {WHITE} !important;
    }}

    /* Radio/Checkbox label text - force black */
    [data-testid="stRadio"] p,
    [data-testid="stRadio"] span,
    [data-testid="stCheckbox"] p,
    [data-testid="stCheckbox"] span,
    [data-baseweb="radio"] p,
    [data-baseweb="radio"] span,
    [data-baseweb="checkbox"] p,
    [data-baseweb="checkbox"] span {{
        color: {BLACK} !important;
    }}

    /* ============================================
       SIDEBAR
       ============================================ */

    [data-testid="stSidebar"] {{
        background-color: {WHITE} !important;
        border-right: 2px solid {BLACK} !important;
    }}

    [data-testid="stSidebar"] .stMarkdown {{
        color: {BLACK} !important;
    }}
    </style>
    """


def inject_styles():
    """Inject global CSS into Streamlit app."""
    st.markdown(get_global_css(), unsafe_allow_html=True)
