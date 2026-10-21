# SPDX-License-Identifier: GPL-3.0-or-later
"""QLE Studio Colors, shared values and swatches."""
from pathlib import Path
import bpy.utils.previews
from . import backdrops

PRESETS = {
    'PURE_WHITE': ('Pure White', '#FFFFFF'),
    'REAL_WHITE': ('Real White', '#E9E9E2'),
    'LIGHT_GRAY': ('Light Gray', '#999999'),
    'MIDDLE_GRAY': ('Middle Gray', '#666666'),
    'DARK_GRAY': ('Dark Gray', '#333333'),
    'CHARCOAL': ('Charcoal', '#1D2024'),
    'REAL_BLACK': ('Real Black', '#16161D'),
    'PURE_BLACK': ('Pure Black', '#000000'),
    'WARM_WHITE': ('Warm White', '#FFFAF3'),
    'WARM_LIGHT_GRAY': ('Warm Light Gray', '#A1988A'),
    'WARM_MIDDLE_GRAY': ('Warm Middle Gray', '#6C655C'),
    'WARM_DARK_GRAY': ('Warm Dark Gray', '#36332E'),
    'SAND': ('Sand', '#CBB99F'),
    'COOL_WHITE': ('Cool White', '#E7F1FF'),
    'COOL_LIGHT_GRAY': ('Cool Light Gray', '#939BA0'),
    'COOL_MIDDLE_GRAY': ('Cool Middle Gray', '#5F686E'),
    'COOL_DARK_GRAY': ('Cool Dark Gray', '#2F3437'),
    'SLATE_BLUE': ('Slate Blue', '#596C7C'),
    'SAGE': ('Sage', '#8E9B87'),
    'DUSTY_ROSE': ('Dusty Rose', '#B98F91'),
    'CHROMA_GREEN': ('Chroma Green', '#00B140'),
    'CHROMA_BLUE': ('Chroma Blue', '#0047BB'),
}
GROUPS = (
    ('Neutral', ('PURE_WHITE', 'REAL_WHITE', 'LIGHT_GRAY', 'MIDDLE_GRAY',
                 'DARK_GRAY', 'CHARCOAL', 'REAL_BLACK', 'PURE_BLACK')),
    ('Warm', ('WARM_WHITE', 'WARM_LIGHT_GRAY', 'WARM_MIDDLE_GRAY',
              'WARM_DARK_GRAY', 'SAND')),
    ('Cool', ('COOL_WHITE', 'COOL_LIGHT_GRAY', 'COOL_MIDDLE_GRAY',
              'COOL_DARK_GRAY', 'SLATE_BLUE')),
    ('Color', ('SAGE', 'DUSTY_ROSE')),
    ('Utility', ('CHROMA_GREEN', 'CHROMA_BLUE')),
)
_previews = None


def value(preset):
    hex_value = PRESETS[preset][1].lstrip('#')

    def linear(channel):
        x = int(channel, 16) / 255
        return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
    return (*[linear(hex_value[i:i+2]) for i in (0, 2, 4)], 1.0)


def active(scene):
    current = backdrops.color(scene)
    return next((name for name in PRESETS if all(abs(a-b) < 0.0001
                 for a, b in zip(current, value(name)))), '')


def label(scene):
    preset = active(scene)
    return PRESETS[preset][0] if preset else 'Custom'


def icon(preset):
    return _previews[preset].icon_id if _previews is not None and preset in _previews else 0


def load():
    global _previews
    unload()
    _previews = bpy.utils.previews.new()
    try:
        for preset in PRESETS:
            path = Path(__file__).with_name('icons') / 'stage_colors' / (preset.lower().replace('_', '-') + '.png')
            _previews.load(preset, str(path), 'IMAGE')
    except Exception:
        unload()
        raise


def unload():
    global _previews
    if _previews is not None:
        try:
            bpy.utils.previews.remove(_previews)
        except KeyError:
            pass
        finally:
            _previews = None
