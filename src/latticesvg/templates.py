"""Built-in style templates for common report elements.

Each template is a plain ``dict`` suitable for passing to a node's ``style``
parameter.  Templates can be merged::

    from latticesvg.templates import TITLE, PARAGRAPH
    merged = {**PARAGRAPH, "color": "#222"}
"""

# --------------------------------------------------------------------------
# Page / container templates
# --------------------------------------------------------------------------

REPORT_PAGE = {
    "width": "800px",
    "padding": "30px",
    "background-color": "#ffffff",
    "grid-template-columns": ["1fr"],
    "gap": "20px",
}

TWO_COLUMN = {
    "grid-template-columns": ["1fr", "1fr"],
    "gap": "20px",
}

THREE_COLUMN = {
    "grid-template-columns": ["1fr", "1fr", "1fr"],
    "gap": "20px",
}

SIDEBAR_LAYOUT = {
    "grid-template-columns": ["240px", "1fr"],
    "gap": "24px",
}

CHART_CONTAINER = {
    "grid-template-columns": ["1fr", "1fr"],
    "grid-template-rows": ["1fr", "1fr"],
    "gap": "10px",
}

# --------------------------------------------------------------------------
# Header / footer
# --------------------------------------------------------------------------

HEADER = {
    "padding": "16px 24px",
    "background-color": "#2c3e50",
    "color": "#ffffff",
    "font-size": "18px",
    "font-weight": "bold",
}

FOOTER = {
    "padding": "12px 24px",
    "background-color": "#34495e",
    "color": "#ecf0f1",
    "font-size": "12px",
    "text-align": "center",
}

# --------------------------------------------------------------------------
# Typography templates
# --------------------------------------------------------------------------

TITLE = {
    "font-size": "28px",
    "font-weight": "bold",
    "color": "#1a1a1a",
    "text-align": "center",
    "margin": "0 0 12px 0",
    "line-height": "1.3",
}

SUBTITLE = {
    "font-size": "20px",
    "font-weight": "bold",
    "color": "#333333",
    "margin": "0 0 8px 0",
    "line-height": "1.4",
}

H1 = {
    "font-size": "24px",
    "font-weight": "bold",
    "color": "#222222",
    "margin": "16px 0 8px 0",
    "line-height": "1.3",
}

H2 = {
    "font-size": "20px",
    "font-weight": "bold",
    "color": "#333333",
    "margin": "12px 0 6px 0",
    "line-height": "1.4",
}

H3 = {
    "font-size": "16px",
    "font-weight": "bold",
    "color": "#444444",
    "margin": "8px 0 4px 0",
    "line-height": "1.4",
}

PARAGRAPH = {
    "font-size": "14px",
    "color": "#333333",
    "line-height": "1.6",
    "text-align": "left",
}

CAPTION = {
    "font-size": "12px",
    "color": "#888888",
    "text-align": "center",
    "line-height": "1.4",
    "margin": "4px 0 0 0",
}

CODE = {
    "font-family": "monospace",
    "font-size": "13px",
    "color": "#d63384",
    "background-color": "#f8f9fa",
    "padding": "2px 6px",
    "line-height": "1.5",
    "white-space": "pre",
}

# --------------------------------------------------------------------------
# Visual elements
# --------------------------------------------------------------------------

CARD = {
    "padding": "16px",
    "background-color": "#ffffff",
    "border": "1px solid #e0e0e0",
}

HIGHLIGHT_BOX = {
    "padding": "12px 16px",
    "background-color": "#fff3cd",
    "border": "1px solid #ffc107",
    "color": "#856404",
}

# --------------------------------------------------------------------------
# All templates as a dict for programmatic access
# --------------------------------------------------------------------------

ALL_TEMPLATES = {
    "report-page": REPORT_PAGE,
    "two-column": TWO_COLUMN,
    "three-column": THREE_COLUMN,
    "sidebar-layout": SIDEBAR_LAYOUT,
    "chart-container": CHART_CONTAINER,
    "header": HEADER,
    "footer": FOOTER,
    "title": TITLE,
    "subtitle": SUBTITLE,
    "h1": H1,
    "h2": H2,
    "h3": H3,
    "paragraph": PARAGRAPH,
    "caption": CAPTION,
    "code": CODE,
    "card": CARD,
    "highlight-box": HIGHLIGHT_BOX,
}
