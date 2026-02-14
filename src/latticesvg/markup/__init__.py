"""Markup parsing — HTML subset and Markdown to rich text spans."""

from .parser import TextSpan, parse_markup, parse_html, parse_markdown

__all__ = [
    "TextSpan",
    "parse_markup",
    "parse_html",
    "parse_markdown",
]
