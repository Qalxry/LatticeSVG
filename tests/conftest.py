"""Shared fixtures for LatticeSVG tests."""
import pytest


@pytest.fixture
def sample_grid_style():
    """A basic grid container style for testing."""
    return {
        "width": "800px",
        "padding": "20px",
        "background-color": "#ffffff",
        "grid-template-columns": ["200px", "1fr"],
        "gap": "20px",
    }


@pytest.fixture
def sample_text_style():
    """A basic text style for testing."""
    return {
        "font-size": "16px",
        "font-family": "sans-serif",
        "color": "#333333",
        "line-height": "1.5",
    }
