# QLE 2.0 — Controls Checkpoint

Date: 2026-10-18. Repository: `blender-qle`. Branch: `qle-2.0`.

## Implemented in chunk 3

- Replaced the Scene Properties panel with Quick Tools > Quick Lighting Environment in the 3D Viewport Sidebar. Add/Reset/Clear share the top row. Adjustments starts closed and uses Blender's remembered collapsible sections.
- Individual light headers provide editable name, Select, Protect, and Enabled. Bodies provide Power, RGB/Kelvin, orbit Position, Follow Target, Target/Manual Aim, Shape/Size, Reset Light, and Delete Light. The default order is Left, Right, Fill, Back, then extras.
- Orbit fields read the actual evaluated light position relative to its target. Normal viewport grabbing and native location animation remain available. Native translation-follow constraints use a hidden reference helper so initial transform values are preserved. No QLS orbit-parent hierarchy is exposed as the user workflow.
- Follow Target controls translation independently of Aim. Switching Follow on/off preserves world position. Switching to Manual Aim preserves the evaluated direction before allowing native rotation.
- Target Free/Object following snaps to the selected origin, permits offsets, ignores source rotation/scale, preserves position when freed, and falls back to Free when its source is deleted.
- RGB and Kelvin are exclusive for Lights and World; each remembers its own value. Kelvin uses white RGB, with no Tint field. Copied QLS's verified 19 presets and descriptions; the earlier count of 20 was corrected.
- Exported only L, Flat Background, and Floor geometry from QLS into `_backdrops.blend` using Blender 4.5. C still uses the unchanged legacy `_backdrop.blend`. No Tabletop, Dome, or Reflector assets were included.
- Backdrop selection preserves surface and Enabled state through type changes and None. Add repairs the selected geometry; Clear followed by Add restores C defaults. Finish, Roughness, Color, and Position are live controls.
- Inspected the legacy material: Diffuse shader, Roughness 1.0. Preserve this default. Explicit Finish/Roughness edits create a Principled surface to support reflection; Reset restores the legacy Diffuse material.
- Protected lights keep private targets and translation references through Reset/Clear. Add repairs missing protected targets without duplicating the original slot. Deleting one light cleans up its own private helpers.
- Panel drawing is read-only and hides adjustment controls for shared/linked QLE content that cannot safely be edited. Reset and Clear retain their confirmation operators.
- Updated README and Unreleased changelog. QLS and `master` were not modified.

## Functional checks

| Blender / engine | Foundation scenarios | Control scenarios |
| --- | --- | --- |
| 4.5.14 / EEVEE | 27 passed | 28 passed |
| 4.5.14 / Cycles | 27 passed | 28 passed |
| 5.2.2 / EEVEE | 27 passed | 28 passed |
| 5.2.2 / Cycles | 27 passed | 28 passed |

**220 checks passed.** All four processes exited zero, with the expected success markers (`QLE_FOUNDATION_TESTS_OK count=54` or `QLE_CONTROLS_TESTS_OK count=56`).

New checks cover native global Grab, manual movement followed by Distance edits, independent Follow/Aim, pole/coincident controls, object snapping and offsets, source deletion, reselecting Object mode after a deleted source, added/original light resets, protection while following an object, private-target repair, deletion/helper cleanup, color memory, all presets, every backdrop choice, missing asset preservation, legacy shader restoration, save/reopen, registration cleanup, and native location animation.

The panel drawing probe traverses collapsed/open, RGB/Kelvin, Manual, None-backdrop, protected-only, and empty states using real registered RNA objects. It validates property/operator paths and that drawing does not change object transforms or constraints. It enforces the installed Blender API's full-width rule for collapsible panels: no panels inside boxes/columns. This is a Python drawing-path check, not a rendered UI inspection.

## Actual rendered color checks

`tests/test_color_render.py` renders 32 × 32 temporary EXR images, reads their scene-linear center pixels, and removes the temporary files afterward. It isolates direct World backgrounds and illumination from one Area light on white Diffuse geometry.

For each Blender/engine combination, both World and Light are set to blue RGB, then switched to 5600 K. Every blue render has a dominant blue channel; every Kelvin render has nonzero red/green and a balanced blue/red ratio instead of retaining the blue tint.

**8 rendered comparisons passed (16 renders):** Light and World in both engines and both versions. Both processes exited zero and emitted `QLE_COLOR_RENDER_TESTS_OK count=4`. This establishes the specific color-mode behavior, not full-scene visual equivalence between engines.

## Reproduce

With the appropriate separately approved Blender background mission, run these from the repo root using either installed Blender executable:

```sh
PYTHONDONTWRITEBYTECODE=1 /Applications/Blender-4.5.14.app/Contents/MacOS/Blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python tests/test_foundation.py
PYTHONDONTWRITEBYTECODE=1 /Applications/Blender-4.5.14.app/Contents/MacOS/Blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python tests/test_controls.py
PYTHONDONTWRITEBYTECODE=1 /Applications/Blender-4.5.14.app/Contents/MacOS/Blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python tests/test_color_render.py
```

The additional `_backdrops.blend` library can be regenerated with `tools/export_backdrops.py` and the approved sibling QLS source. The original `_backdrop.blend` remains unchanged. The installed extension has no dependency on that checkout.

## Remaining chunk 4 checks

- Actual N-panel appearance, width/spacing, and interaction in Blender, including menu context and collapse-state persistence.
- Interactive Reset/Clear confirmation and Undo behavior.
- Packaged extension build, installation, disable/re-enable, and package inventory.
- Representative scene/default renders beyond the isolated color checks.

No existing Blender window or user project was controlled. No commit, package build, push, or release was performed in chunk 3.
