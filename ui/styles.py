"""
CSS Styles for DocShipper
Black/White minimal aesthetic with sharp corners and no shadows
"""

import streamlit as st
import streamlit.components.v1 as components
from ui.tokens import COLORS, FONTS, FONT_SIZES, FONT_WEIGHTS, SPACING, BORDERS, SHADOWS, TRANSITIONS, LETTER_SPACING, GRID


def get_global_css() -> str:
    """Return complete CSS stylesheet using design tokens."""
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Base styling */
    * {{
        font-family: {FONTS['primary']};
    }}

    .stApp {{
        background-color: {COLORS['background']};
    }}

    body, .stApp, .main {{
        color: {COLORS['text']};
    }}

    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* Main container max-width */
    .main .block-container {{
        max-width: 900px;
        padding-top: {SPACING['xl']};
        padding-bottom: {SPACING['xl']};
    }}

    /* Landing page header */
    .landing-header {{
        font-size: {FONT_SIZES['3xl']};
        font-weight: {FONT_WEIGHTS['bold']};
        color: {COLORS['text']};
        text-align: center;
        margin-bottom: {SPACING['sm']};
        letter-spacing: -1px;
    }}

    .landing-subtitle {{
        font-size: {FONT_SIZES['base']};
        color: {COLORS['text_muted']};
        text-align: center;
        margin-bottom: {SPACING['3xl']};
    }}

    /* Workflow buttons (landing page) */
    .workflow-btn {{
        display: block;
        width: 100%;
        padding: {SPACING['2xl']} {SPACING['xl']};
        background-color: {COLORS['surface']};
        border: {BORDERS['width']} solid {COLORS['border']};
        border-radius: {BORDERS['radius']};
        cursor: pointer;
        text-align: left;
        transition: background-color {TRANSITIONS['fast']};
        margin-bottom: {SPACING['md']};
    }}

    .workflow-btn:hover {{
        background-color: {COLORS['hover_bg']};
    }}

    .workflow-btn-title {{
        font-size: {FONT_SIZES['xl']};
        font-weight: {FONT_WEIGHTS['semibold']};
        color: {COLORS['text']};
        margin-bottom: {SPACING['xs']};
    }}

    .workflow-btn-desc {{
        font-size: {FONT_SIZES['sm']};
        color: {COLORS['text_muted']};
    }}

    /* Step indicator / breadcrumb */
    .step-indicator {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: {SPACING['sm']};
        margin-bottom: {SPACING['xl']};
        padding: {SPACING['md']} 0;
        border-bottom: {BORDERS['width']} solid {COLORS['border_light']};
    }}

    .step-item {{
        display: flex;
        align-items: center;
        gap: {SPACING['xs']};
    }}

    .step-number {{
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: {FONT_SIZES['xs']};
        font-weight: {FONT_WEIGHTS['semibold']};
        border: {BORDERS['width']} solid {COLORS['border_light']};
        border-radius: {BORDERS['radius']};
    }}

    .step-number.active {{
        background-color: {COLORS['primary']};
        color: {COLORS['text_light']};
        border-color: {COLORS['primary']};
    }}

    .step-number.complete {{
        background-color: {COLORS['primary']};
        color: {COLORS['text_light']};
        border-color: {COLORS['primary']};
    }}

    .step-label {{
        font-size: {FONT_SIZES['xs']};
        color: {COLORS['text_muted']};
    }}

    .step-label.active {{
        color: {COLORS['text']};
        font-weight: {FONT_WEIGHTS['medium']};
    }}

    .step-separator {{
        width: 24px;
        height: 1px;
        background-color: {COLORS['border_light']};
    }}

    /* Page title */
    .page-title {{
        font-size: {FONT_SIZES['2xl']};
        font-weight: {FONT_WEIGHTS['semibold']};
        color: {COLORS['text']};
        margin-bottom: {SPACING['xs']};
        text-align: center;
    }}

    .page-subtitle {{
        font-size: {FONT_SIZES['sm']};
        color: {COLORS['text_muted']};
        margin-bottom: {SPACING['xl']};
        text-align: center;
    }}

    /* Section headers */
    .section-title {{
        font-size: {FONT_SIZES['sm']};
        font-weight: {FONT_WEIGHTS['semibold']};
        color: {COLORS['text']};
        text-transform: uppercase;
        letter-spacing: {LETTER_SPACING['wide']};
        margin: {SPACING['lg']} 0 {SPACING['md']} 0;
        padding-bottom: {SPACING['sm']};
        border-bottom: {BORDERS['width']} solid {COLORS['border_light']};
        text-align: center;
    }}

    /* All buttons - minimal style */
    .stButton button {{
        background-color: {COLORS['surface']} !important;
        color: {COLORS['text']} !important;
        border: {BORDERS['width']} solid {COLORS['border']} !important;
        border-radius: {BORDERS['radius']} !important;
        font-family: {FONTS['primary']} !important;
        font-size: {FONT_SIZES['sm']} !important;
        font-weight: {FONT_WEIGHTS['medium']} !important;
        padding: 10px 20px !important;
        text-transform: none !important;
        letter-spacing: {LETTER_SPACING['normal']} !important;
        transition: all {TRANSITIONS['fast']} !important;
        box-shadow: none !important;
    }}

    .stButton button:hover {{
        background-color: {COLORS['hover_bg']} !important;
        color: {COLORS['text']} !important;
        border-color: {COLORS['border']} !important;
    }}

    .stButton button[kind="primary"] {{
        background-color: {COLORS['primary']} !important;
        color: {COLORS['text_light']} !important;
        border: {BORDERS['width']} solid {COLORS['primary']} !important;
    }}

    .stButton button[kind="primary"]:hover {{
        background-color: #333333 !important;
        border-color: #333333 !important;
    }}

    .stButton button:disabled {{
        opacity: 0.4 !important;
        cursor: not-allowed !important;
    }}

    /* Download button */
    .stDownloadButton button {{
        background-color: {COLORS['primary']} !important;
        color: {COLORS['text_light']} !important;
        border: {BORDERS['width']} solid {COLORS['primary']} !important;
        border-radius: {BORDERS['radius']} !important;
    }}

    .stDownloadButton button:hover {{
        background-color: #333333 !important;
        border-color: #333333 !important;
    }}

    /* File uploader - unified drop zone */
    [data-testid="stFileUploader"] {{
        max-width: 480px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }}

    [data-testid="stFileUploader"] label {{
        color: {COLORS['text']} !important;
        font-weight: {FONT_WEIGHTS['medium']} !important;
        font-size: {FONT_SIZES['sm']} !important;
    }}

    /* Dropzone: force vertical centered layout */
    section[data-testid="stFileUploaderDropzone"] {{
        background-color: {COLORS['surface']} !important;
        border: 2px dashed {COLORS['border_light']} !important;
        border-radius: {BORDERS['radius']} !important;
        padding: {SPACING['2xl']} {SPACING['xl']} !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        gap: {SPACING['md']} !important;
        cursor: pointer !important;
        transition: border-color 0.15s ease, background-color 0.15s ease !important;
        min-height: 180px !important;
    }}

    /* Dropzone hover */
    section[data-testid="stFileUploaderDropzone"]:hover {{
        border-color: {COLORS['border']} !important;
        background-color: {COLORS['hover_bg']} !important;
    }}

    /* Instructions container (icon + text) - full width centered */
    [data-testid="stFileUploaderDropzoneInstructions"] {{
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        text-align: center !important;
        gap: {SPACING['sm']} !important;
        width: 100% !important;
    }}

    /* The icon container */
    [data-testid="stFileUploaderDropzoneInstructions"] > span {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    /* Upload icon SVG */
    [data-testid="stFileUploaderDropzoneInstructions"] svg {{
        width: 40px !important;
        height: 40px !important;
        color: {COLORS['text_muted']} !important;
    }}

    /* Text container inside instructions */
    [data-testid="stFileUploaderDropzoneInstructions"] > div {{
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        text-align: center !important;
    }}

    /* "Drag and drop" text */
    [data-testid="stFileUploaderDropzoneInstructions"] > div > span:first-child {{
        font-size: {FONT_SIZES['base']} !important;
        font-weight: {FONT_WEIGHTS['medium']} !important;
        color: {COLORS['text']} !important;
        text-align: center !important;
    }}

    /* "Limit 5GB..." subtext */
    [data-testid="stFileUploaderDropzoneInstructions"] > div > span:last-child {{
        font-size: {FONT_SIZES['xs']} !important;
        color: {COLORS['text_muted']} !important;
        text-align: center !important;
    }}

    /* Browse files button - catch ALL buttons inside dropzone */
    section[data-testid="stFileUploaderDropzone"] button {{
        background-color: transparent !important;
        color: {COLORS['text']} !important;
        border: {BORDERS['width']} solid {COLORS['border']} !important;
        border-radius: 0px !important;
        font-size: {FONT_SIZES['xs']} !important;
        font-weight: {FONT_WEIGHTS['medium']} !important;
        padding: 8px 24px !important;
        cursor: pointer !important;
        transition: background-color 0.15s ease !important;
        margin: 0 !important;
        box-shadow: none !important;
    }}

    section[data-testid="stFileUploaderDropzone"] button:hover {{
        background-color: {COLORS['hover_bg']} !important;
        color: {COLORS['text']} !important;
    }}

    /* Text inputs */
    .stTextInput label, .stNumberInput label, .stSelectbox label {{
        color: {COLORS['text']} !important;
        font-weight: {FONT_WEIGHTS['medium']} !important;
        font-size: {FONT_SIZES['sm']} !important;
    }}

    .stTextInput input, .stNumberInput input {{
        background-color: {COLORS['surface']} !important;
        border: {BORDERS['width']} solid {COLORS['border']} !important;
        border-radius: {BORDERS['radius']} !important;
        color: {COLORS['text']} !important;
        font-family: {FONTS['primary']} !important;
    }}

    .stTextInput input:focus, .stNumberInput input:focus {{
        border-color: {COLORS['text_muted']} !important;
        box-shadow: none !important;
    }}

    /* Select box */
    .stSelectbox [data-baseweb="select"] {{
        border: {BORDERS['width']} solid {COLORS['border']} !important;
        border-radius: {BORDERS['radius']} !important;
    }}

    /* Checkbox */
    .stCheckbox label {{
        color: {COLORS['text']} !important;
        font-size: {FONT_SIZES['sm']} !important;
    }}

    /* Slider */
    .stSlider label {{
        color: {COLORS['text']} !important;
        font-weight: {FONT_WEIGHTS['medium']} !important;
        font-size: {FONT_SIZES['sm']} !important;
    }}

    /* Dataframe styling */
    .stDataFrame {{
        border: {BORDERS['width']} solid {COLORS['border']} !important;
        border-radius: {BORDERS['radius']} !important;
    }}

    .stDataFrame td, .stDataFrame th {{
        color: {COLORS['text']} !important;
        background-color: {COLORS['surface']} !important;
        border-color: {COLORS['border_light']} !important;
        font-size: {FONT_SIZES['sm']} !important;
        padding: 8px 12px !important;
    }}

    .stDataFrame th {{
        background-color: {COLORS['grid_header']} !important;
        font-weight: {FONT_WEIGHTS['semibold']} !important;
        text-transform: uppercase !important;
        font-size: {FONT_SIZES['xs']} !important;
        letter-spacing: {LETTER_SPACING['normal']} !important;
    }}

    /* Alert/Info boxes */
    .stAlert, [data-testid="stAlert"] {{
        background-color: {COLORS['surface']} !important;
        border: {BORDERS['width']} solid {COLORS['border']} !important;
        border-radius: {BORDERS['radius']} !important;
        color: {COLORS['text']} !important;
        text-align: center !important;
        max-width: 480px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }}

    /* Success message */
    .stSuccess, [data-testid="stSuccess"] {{
        background-color: {COLORS['surface']} !important;
        border: {BORDERS['width']} solid {COLORS['primary']} !important;
    }}

    /* Error message */
    .stError, [data-testid="stError"] {{
        background-color: {COLORS['surface']} !important;
        border-color: {COLORS['error']} !important;
    }}

    /* Progress bar */
    .stProgress > div > div {{
        background-color: {COLORS['primary']} !important;
    }}

    /* Markdown text */
    .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown li {{
        color: {COLORS['text']} !important;
    }}

    .stMarkdown strong {{
        color: {COLORS['text']} !important;
        font-weight: {FONT_WEIGHTS['semibold']} !important;
    }}

    /* Caption text - center all captions */
    [data-testid="stCaptionContainer"] {{
        text-align: center !important;
        width: 100% !important;
    }}

    [data-testid="stCaptionContainer"] p {{
        color: {COLORS['text_muted']} !important;
        font-size: {FONT_SIZES['xs']} !important;
        text-align: center !important;
    }}

    .stCaption, .stMarkdown small {{
        color: {COLORS['text_muted']} !important;
        font-size: {FONT_SIZES['xs']} !important;
        text-align: center !important;
    }}

    /* Code blocks */
    code, pre {{
        background-color: {COLORS['surface_alt']} !important;
        color: {COLORS['text']} !important;
        padding: {SPACING['xs']} {SPACING['sm']} !important;
        border-radius: {BORDERS['radius']} !important;
        border: {BORDERS['width']} solid {COLORS['border_light']} !important;
        font-family: {FONTS['mono']} !important;
        font-size: {FONT_SIZES['sm']} !important;
    }}

    /* Dividers */
    hr {{
        border-color: {COLORS['border_light']} !important;
        border-width: {BORDERS['width']} !important;
        margin: {SPACING['lg']} 0 !important;
    }}

    /* Navigation buttons container */
    .nav-buttons {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: {SPACING['xl']};
        margin-top: {SPACING['xl']};
        border-top: {BORDERS['width']} solid {COLORS['border_light']};
    }}

    /* Excel grid preview */
    .excel-grid {{
        overflow-x: auto;
        margin-bottom: 8px;
    }}

    .excel-grid table {{
        border-collapse: collapse;
        width: 100%;
        font-family: {FONTS['mono']};
        font-size: 13px;
    }}

    .excel-grid th,
    .excel-grid td {{
        border: 1px solid #e5e7eb;
        padding: 6px 10px;
        text-align: center;
        min-width: 64px;
        height: {GRID['cell_height']};
        white-space: nowrap;
    }}

    .excel-grid .corner {{
        background-color: #f3f4f6;
        min-width: {GRID['row_header_width']};
        width: {GRID['row_header_width']};
        border-color: #d1d5db;
    }}

    .excel-grid .col-header {{
        background-color: #f3f4f6;
        color: #6b7280;
        font-weight: 600;
        font-size: 13px;
        border-color: #d1d5db;
    }}

    .excel-grid .row-header {{
        background-color: #f3f4f6;
        color: #9ca3af;
        font-weight: 600;
        min-width: {GRID['row_header_width']};
        width: {GRID['row_header_width']};
        border-color: #d1d5db;
    }}

    .excel-grid .cell.field-header {{
        background-color: #eff6ff;
        border-color: #93c5fd;
        color: #1e3a5f;
        font-weight: 500;
    }}

    .excel-grid .cell.field-data {{
        background-color: #f0fdf4;
        border-color: #86efac;
        color: #6b7280;
        font-style: italic;
        font-size: 12px;
    }}

    .excel-grid .cell.empty {{
        background-color: #ffffff;
        border-color: #e5e7eb;
    }}

    .excel-grid td.selected,
    .excel-grid th.selected {{
        background-color: #fef9c3;
        border-color: #fde047;
        color: #713f12;
    }}

    /* Field assignment panel */
    .assign-panel-title {{
        font-size: {FONT_SIZES['base']};
        font-weight: {FONT_WEIGHTS['semibold']};
        margin-bottom: {SPACING['md']};
    }}

    /* Mapping grid legend */
    .mapping-legend {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        margin-top: 12px;
        margin-bottom: 8px;
        font-size: {FONT_SIZES['sm']};
    }}

    .mapping-legend .legend-item {{
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    .mapping-legend .legend-swatch {{
        width: 16px;
        height: 16px;
        border-radius: 2px;
        border: 2px solid;
    }}

    .mapping-legend .legend-swatch.header {{
        background-color: #eff6ff;
        border-color: #93c5fd;
    }}

    .mapping-legend .legend-swatch.data {{
        background-color: #f0fdf4;
        border-color: #86efac;
    }}

    .mapping-legend .legend-swatch.selected {{
        background-color: #fef9c3;
        border-color: #fde047;
    }}

    .mapping-legend .legend-label {{
        color: {COLORS['text_muted']};
    }}

    /* Field list styles */
    .field-list {{
        border: {BORDERS['width']} solid {COLORS['border']};
    }}

    .field-item {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: {SPACING['sm']} {SPACING['md']};
        border-bottom: {BORDERS['width']} solid {COLORS['border_light']};
    }}

    .field-item:last-child {{
        border-bottom: none;
    }}

    .field-item:hover {{
        background-color: {COLORS['hover_bg']};
    }}

    .field-name {{
        font-size: {FONT_SIZES['sm']};
        font-weight: {FONT_WEIGHTS['medium']};
    }}

    .field-assigned {{
        font-size: {FONT_SIZES['xs']};
        color: {COLORS['text_muted']};
        font-family: {FONTS['mono']};
    }}

    /* Remove tab styling as we're using page-based nav */
    .stTabs {{
        display: none !important;
    }}

    /* Hide expanders - we're using pages now */
    .stExpander {{
        display: none !important;
    }}

    /* Status badges */
    .status-ready {{
        color: {COLORS['text']};
        font-weight: {FONT_WEIGHTS['medium']};
    }}

    .status-waiting {{
        color: {COLORS['text_muted']};
    }}

    /* Center status rows */
    .status-row {{
        text-align: center;
    }}

    /* XML detection card */
    .detection-card {{
        border: {BORDERS['width']} solid {COLORS['border']};
        border-radius: {BORDERS['radius']};
        padding: {SPACING['xl']};
        margin: {SPACING['lg']} 0;
        text-align: center;
    }}

    .detection-filename {{
        font-size: {FONT_SIZES['base']};
        font-weight: {FONT_WEIGHTS['semibold']};
        color: {COLORS['text']};
        margin-bottom: {SPACING['xs']};
        font-family: {FONTS['mono']};
    }}

    .detection-project {{
        font-size: {FONT_SIZES['sm']};
        color: {COLORS['text_muted']};
        margin-bottom: {SPACING['lg']};
    }}

    .detection-counts {{
        display: flex;
        justify-content: center;
        gap: {SPACING['3xl']};
        margin-bottom: {SPACING['sm']};
    }}

    .detection-item {{
        text-align: center;
    }}

    .detection-count {{
        font-size: {FONT_SIZES['2xl']};
        font-weight: {FONT_WEIGHTS['bold']};
        color: {COLORS['text']};
        line-height: 1;
    }}

    .detection-label {{
        font-size: {FONT_SIZES['xs']};
        color: {COLORS['text_muted']};
        text-transform: uppercase;
        letter-spacing: {LETTER_SPACING['wide']};
        margin-top: {SPACING['xs']};
    }}

    .detection-fps {{
        font-size: {FONT_SIZES['xs']};
        color: {COLORS['text_muted']};
    }}
    </style>
    """


def get_drag_hover_js() -> str:
    """Return JavaScript for file upload drag-hover visual feedback."""
    return """
    <script>
    (function() {
        var doc = window.parent.document || document;
        function setupDragHover() {
            var dropzones = doc.querySelectorAll('section[data-testid="stFileUploaderDropzone"]');
            dropzones.forEach(function(zone) {
                if (zone.dataset.dragBound) return;
                zone.dataset.dragBound = '1';
                var counter = 0;
                zone.addEventListener('dragenter', function(e) {
                    e.preventDefault();
                    counter++;
                    zone.style.setProperty('border-color', '#000000', 'important');
                    zone.style.setProperty('border-style', 'solid', 'important');
                    zone.style.setProperty('background-color', '#f0f0f0', 'important');
                });
                zone.addEventListener('dragover', function(e) {
                    e.preventDefault();
                });
                zone.addEventListener('dragleave', function(e) {
                    counter--;
                    if (counter <= 0) {
                        counter = 0;
                        zone.style.removeProperty('border-color');
                        zone.style.removeProperty('border-style');
                        zone.style.removeProperty('background-color');
                    }
                });
                zone.addEventListener('drop', function(e) {
                    counter = 0;
                    zone.style.removeProperty('border-color');
                    zone.style.removeProperty('border-style');
                    zone.style.removeProperty('background-color');
                });
            });
        }
        // Run immediately and poll for new dropzones
        function trySetup() {
            try { setupDragHover(); } catch(e) {}
        }
        trySetup();
        setInterval(trySetup, 1000);
        // Also watch for DOM changes in parent document
        try {
            new MutationObserver(function() { trySetup(); }).observe(
                doc.body, { childList: true, subtree: true }
            );
        } catch(e) {}
    })();
    </script>
    """


def inject_styles():
    """Inject global CSS and drag-hover JS into Streamlit app."""
    st.markdown(get_global_css(), unsafe_allow_html=True)
    # Use components.html() for JS - st.markdown doesn't execute <script> tags
    components.html(get_drag_hover_js(), height=0, scrolling=False)
