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


DEFAULT_KELVIN = 5454.0
NEW_LIGHT_KELVIN = 6500.0

# The legacy lights used RGB colors rather than active temperature settings.
# These values preload the equivalent QLE Classic choices without changing the
# default RGB appearance.
LIGHT_KELVIN_DEFAULTS = {
    "Area_Right": 20000.0,
    "Area_Left": 3800.0,
    "Area_Fill": DEFAULT_KELVIN,
    "Area_Back": DEFAULT_KELVIN,
}


def kelvin_for(slot):
    return LIGHT_KELVIN_DEFAULTS.get(slot, NEW_LIGHT_KELVIN)
