# SPDX-License-Identifier: GPL-3.0-or-later
"""QLS Studio Colors, shared values and swatches; no QLS runtime dependency."""
from pathlib import Path
import bpy.utils.previews
from . import backdrops

PRESETS = {'PURE_WHITE': ('Pure White', '#FFFFFF'), 'REAL_WHITE': ('Real White', '#E9E9E2'), 'WARM_WHITE': ('Warm White', '#F1E9DC'), 'LIGHT_GRAY': ('Light Gray', '#B8B8B5'), 'MIDDLE_GRAY': ('Middle Gray', '#808080'), 'DARK_GRAY': ('Dark Gray', '#3A3B3D'), 'CHARCOAL': ('Charcoal', '#1D2024'), 'REAL_BLACK': ('Real Black', '#16161D'), 'PURE_BLACK': ('Pure Black', '#000000'), 'WARM_GRAY': ('Warm Gray', '#9D9388'), 'SAND': ('Sand', '#CBB99F'), 'COOL_GRAY': ('Cool Gray', '#89949D'), 'SLATE_BLUE': ('Slate Blue', '#596C7C'), 'SAGE': ('Sage', '#8E9B87'), 'DUSTY_ROSE': ('Dusty Rose', '#B98F91'), 'CHROMA_GREEN': ('Chroma Green', '#00B140'), 'CHROMA_BLUE': ('Chroma Blue', '#0047BB')}
GROUPS = (('Neutral', ('PURE_WHITE', 'REAL_WHITE', 'WARM_WHITE', 'LIGHT_GRAY', 'MIDDLE_GRAY', 'DARK_GRAY', 'CHARCOAL', 'REAL_BLACK', 'PURE_BLACK')), ('Warm', ('WARM_GRAY', 'SAND')), ('Cool', ('COOL_GRAY', 'SLATE_BLUE')), ('Color', ('SAGE', 'DUSTY_ROSE')), ('Utility', ('CHROMA_GREEN', 'CHROMA_BLUE')))
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
                 for a,b in zip(current, value(name)))), '')


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
