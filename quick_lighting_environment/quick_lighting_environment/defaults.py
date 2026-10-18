# SPDX-License-Identifier: GPL-3.0-or-later
"""Original QLE light defaults, retained without color or power conversion."""

LIGHT_SETTINGS = {
    "Area_Right": {
        "loc": (5, -5, 5),
        "shape": "RECTANGLE",
        "energy": 100,
        "size_x": 2,
        "size_y": 6,
        "color": (0.407237, 0.564712, 1), #3800
        "temperature": None
    },
    "Area_Left": {
        "loc": (-5, -5, 5),
        "shape": "RECTANGLE",
        "energy": 100,
        "size_x": 2,
        "size_y": 6,
        "color": (1, 0.584079, 0.337164), #20,000
        "temperature": None
    },
    "Area_Fill": {
        "loc": (0, 0, 8),
        "shape": "DISK",
        "energy": 800,
        "size_x": 8,
        "size_y": 8,
        "color": (1, 0.846874, 0.723055), #5454
        "temperature": None
    },
    "Area_Back": {
        "loc": (0, 5, 5),
        "shape": "RECTANGLE",
        "energy": 100,
        "size_x": 8,
        "size_y": 1,
        "color": (1, 0.846874, 0.723055), #5454
        "temperature": None
    },
}
