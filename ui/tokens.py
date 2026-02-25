"""
Design Tokens for DocShipper
Single source of truth for all design values - Black/White minimal aesthetic
"""

# Colors - Pure Black/White palette
COLORS = {
    "primary": "#000000",           # Black
    "background": "#ffffff",        # White
    "surface": "#ffffff",           # White
    "surface_alt": "#f8f8f8",       # Off-white for alternating
    "text": "#000000",              # Black text
    "text_muted": "#666666",        # Gray text
    "text_light": "#ffffff",        # White text (on dark)
    "border": "#000000",            # Black border
    "border_light": "#e0e0e0",      # Light gray border
    "grid_header": "#f0f0f0",       # Grid header background
    "grid_border": "#d0d0d0",       # Grid cell borders
    "grid_selected": "#e8e8e8",     # Selected cell
    "success": "#000000",           # Success uses black
    "error": "#cc0000",             # Only color: errors
    "hover_bg": "#f5f5f5",          # Subtle hover
}

# Typography - Clean sans-serif
FONTS = {
    "primary": "'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    "mono": "'SF Mono', 'Monaco', 'Consolas', monospace",
}

FONT_SIZES = {
    "xs": "11px",
    "sm": "13px",
    "base": "15px",
    "lg": "18px",
    "xl": "24px",
    "2xl": "32px",
    "3xl": "48px",
}

FONT_WEIGHTS = {
    "normal": "400",
    "medium": "500",
    "semibold": "600",
    "bold": "700",
}

# Spacing scale
SPACING = {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px",
    "2xl": "48px",
    "3xl": "64px",
}

# Borders - Sharp, no rounding
BORDERS = {
    "width": "1px",
    "radius": "0px",
}

# Shadows - None for minimal aesthetic
SHADOWS = {
    "sm": "none",
    "md": "none",
    "lg": "none",
}

# Transitions
TRANSITIONS = {
    "fast": "0.1s ease",
    "normal": "0.15s ease",
    "slow": "0.2s ease",
}

# Letter spacing
LETTER_SPACING = {
    "tight": "0px",
    "normal": "0.5px",
    "wide": "1px",
}

# Grid editor specific tokens
GRID = {
    "cell_width": "80px",
    "cell_height": "32px",
    "header_bg": "#f0f0f0",
    "row_header_width": "40px",
}
