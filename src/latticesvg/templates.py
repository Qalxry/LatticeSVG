"""Built-in style templates and helper builders for common report elements.

Each template is a plain ``dict`` suitable for passing to a node's ``style``
parameter.  Templates can be merged::

    from latticesvg.templates import TITLE, PARAGRAPH
    merged = {**PARAGRAPH, "color": "#222"}

The module also provides builder functions (e.g. ``build_table``) that return
ready-to-use node trees.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Union

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
    "line-height": "1.3",
}

SUBTITLE = {
    "font-size": "20px",
    "font-weight": "bold",
    "color": "#333333",
    "line-height": "1.4",
}

H1 = {
    "font-size": "24px",
    "font-weight": "bold",
    "color": "#222222",
    "line-height": "1.3",
}

H2 = {
    "font-size": "20px",
    "font-weight": "bold",
    "color": "#333333",
    "line-height": "1.4",
}

H3 = {
    "font-size": "16px",
    "font-weight": "bold",
    "color": "#444444",
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


# --------------------------------------------------------------------------
# Table builder
# --------------------------------------------------------------------------

# Default style presets used by build_table when no overrides are given.

TABLE_DEFAULT: Dict[str, Any] = {
    "background-color": "#ffffff",
    "border": "1px solid #dee2e6",
}

TABLE_HEADER_DEFAULT: Dict[str, Any] = {
    "background-color": "#f1f3f5",
    "padding": "8px 12px",
    "border-bottom": "2px solid #dee2e6",
    "font-size": "13px",
    "font-weight": "bold",
    "color": "#212529",
    "text-align": "left",
}

TABLE_CELL_DEFAULT: Dict[str, Any] = {
    "padding": "6px 12px",
    "border-bottom": "1px solid #dee2e6",
    "font-size": "13px",
    "color": "#495057",
    "text-align": "left",
}


def build_table(
    headers: Sequence[str],
    rows: Sequence[Sequence[Any]],
    *,
    style: Optional[Dict[str, Any]] = None,
    header_style: Optional[Dict[str, Any]] = None,
    cell_style: Optional[Dict[str, Any]] = None,
    col_widths: Optional[List[str]] = None,
    stripe_color: Optional[str] = "#f8f9fa",
) -> "GridContainer":
    """Build a table as a :class:`GridContainer` node tree.

    Parameters
    ----------
    headers : sequence of str
        Column header labels.
    rows : sequence of sequences
        Each inner sequence is one data row. Values are converted to ``str``.
    style : dict, optional
        Override styles for the outer table container.  Merged on top of
        :data:`TABLE_DEFAULT`.
    header_style : dict, optional
        Override styles for every header cell.  Merged on top of
        :data:`TABLE_HEADER_DEFAULT`.
    cell_style : dict, optional
        Override styles for every body cell.  Merged on top of
        :data:`TABLE_CELL_DEFAULT`.
    col_widths : list of str, optional
        Explicit column widths (e.g. ``["200px", "1fr", "1fr"]``).
        Defaults to equal ``1fr`` for all columns.
    stripe_color : str or None, optional
        Background colour for alternating (even) rows.  Set to ``None``
        to disable striping.  Default ``"#f8f9fa"``.

    Returns
    -------
    GridContainer
        A fully-constructed node tree ready for ``layout()`` and rendering.

    Examples
    --------
    >>> from latticesvg.templates import build_table
    >>> tbl = build_table(
    ...     headers=["Name", "Value"],
    ...     rows=[["alpha", "1.0"], ["beta", "2.5"]],
    ... )
    """
    # Lazy import to avoid circular dependency at module level
    from .nodes.grid import GridContainer
    from .nodes.text import TextNode

    num_cols = len(headers)
    if col_widths is None:
        col_widths = ["1fr"] * num_cols

    # --- Outer table container ---
    table_style: Dict[str, Any] = {
        **TABLE_DEFAULT,
        "grid-template-columns": col_widths,
        "gap": "0px",
    }
    if style:
        table_style.update(style)

    table = GridContainer(style=table_style)

    # --- Header row (grid row 1) ---
    h_style = {**TABLE_HEADER_DEFAULT}
    if header_style:
        h_style.update(header_style)

    for c_idx, label in enumerate(headers):
        cell = GridContainer(style={
            **h_style,
            "grid-template-columns": ["1fr"],
        })
        cell.add(
            TextNode(str(label), style={
                "font-size": h_style.get("font-size", "13px"),
                "font-weight": h_style.get("font-weight", "bold"),
                "color": h_style.get("color", "#212529"),
                "text-align": h_style.get("text-align", "left"),
            }),
            row=1, col=1,
        )
        table.add(cell, row=1, col=c_idx + 1)

    # --- Body rows (grid rows 2 …) ---
    b_style = {**TABLE_CELL_DEFAULT}
    if cell_style:
        b_style.update(cell_style)

    for r_idx, row_data in enumerate(rows):
        grid_row = r_idx + 2  # header occupies row 1
        is_even = r_idx % 2 == 1  # 0-based: rows 1,3,5… are "even" visually

        for c_idx in range(num_cols):
            value = str(row_data[c_idx]) if c_idx < len(row_data) else ""

            row_bg: Dict[str, Any] = {}
            if stripe_color and is_even:
                row_bg["background-color"] = stripe_color

            # Last body row: no border-bottom (the table already has one)
            last_row_override: Dict[str, Any] = {}
            if r_idx == len(rows) - 1:
                last_row_override["border-bottom"] = "0px solid transparent"

            cell = GridContainer(style={
                **b_style,
                **row_bg,
                **last_row_override,
                "grid-template-columns": ["1fr"],
            })
            cell.add(
                TextNode(value, style={
                    "font-size": b_style.get("font-size", "13px"),
                    "color": b_style.get("color", "#495057"),
                    "text-align": b_style.get("text-align", "left"),
                }),
                row=1, col=1,
            )
            table.add(cell, row=grid_row, col=c_idx + 1)

    return table
