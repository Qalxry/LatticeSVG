# =========================================================================
# Demo 6：混合 fixed + fr
# =========================================================================

from latticesvg import GridContainer
from utils import heading, save, ColorBox

def demo_06_mixed_tracks():
    heading("Demo 6: 混合 fixed + fr 轨道")

    grid = GridContainer(style={
        "width": "800px",
        "padding": "10px",
        "background-color": "#f5f5f5",
        "grid-template-columns": ["200px", "1fr", "150px"],
        "gap": "10px",
    })

    items = [
        ("sidebar 200px", "#8e44ad"),
        ("main 1fr",      "#2980b9"),
        ("aside 150px",   "#27ae60"),
    ]
    for label, color in items:
        grid.add(ColorBox(
            width=50, height=80,
            **{"background-color": color}
        ))

    save(grid, "06_mixed_tracks.svg")
    
if __name__ == "__main__":
    demo_06_mixed_tracks()