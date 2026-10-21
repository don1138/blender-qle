# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] — QLE 2.0 development

### Added

- Quick Tools N-panel with collapsed Adjustments, Add/Reset/Clear, and individual Area-light controls.
- Add/Delete/Reset Light, protection through environment resets/removal, live orbit controls, independent target following and aiming, and manual viewport movement.
- Object-following target with automatic origin snapping and editable offset.
- Exclusive RGB/Kelvin modes for lights and World, with separately remembered values and the 19 QLS temperature presets.
- C/L/Flat Background/Floor/None backdrop choices, color and surface finish controls, and position/visibility controls.
- Expanded Stage Studio Colors from 17 to 22 with matching Light, Middle, and Dark neutral, Warm, and Cool gray ranges.
- Background Blender regression checks and rendered color checks in EEVEE and Cycles.

### Changed

- Minimum Blender version is 4.5. The Scene Properties panel is replaced by the 3D Viewport sidebar panel.
- Original QLE light and backdrop colors are retained. Stage materials now use a clean Principled surface from the start, with consistently arranged material nodes.
- Removed the redundant Adjustments wrapper, added spacing between major control sections, and added a guided empty state.

### Fixed

- Prevented duplicate World Blackbody nodes when switching color modes and arranged the default World nodes for readability.
- Renamed the light orbit control from Around Subject to Around Target.
- Allowed replacement Stage meshes to inherit the current Principled material when their packaged assets contain no material.

- Persistent scene-local ownership and World restoration replace name-based deletion and transient global state. Cleanup no longer runs a broad orphan purge.
- Recognizable legacy setups can be adopted without resetting their appearance; missing original-World history is reported rather than guessed.

This development branch is packaged for owner testing but is not released. Earlier candidates passed focused runtime checks; the current QLS-style revision and latest package still require final runtime validation.

## [1.8.0] - 2025-10-30

### Removed

- Removed `Blackbody` nodes from lights
  - Light color updates introduced in version 1.6.7 for EEVEE compatibility caused incorrect results when multiplied by `Blackbody` output

## [1.7.1] - 2024-12-17

### Changed

- Refactored code

## 1.7.0 - 2024-12-16

### Changed

- Refactored code

## [1.6.7] - 2024-12-14

### Changed

- Added EEVEE compatibility by setting `data.color` of lights to approximate blackbody values
- Increased **Backdrop** width from 15 m to 30 m

### Fixed

- Fixed **QLE World** attachment to `scene.world`

## [1.6.6] - 2024-08-14

### Added

- Added `blender_manifest.toml`

### Changed

- Ported to [Blender Extensions](https://extensions.blender.org/add-ons/quick-lighting-environment/)
- Renamed **Blender QLE (Quick Lighting Environment)** to **Quick Lighting Environment**

## [1.6.5] - 2022-12-17

### Changed

- Refactored code
- Applied PEP 8 formatting

## [1.6.4] - 2022-05-27

### Fixed

- Fixed an error when opening a file with an existing **QLE** collection, deleting the collection, and then adding it again after `World` had been set to null

## [1.6.3] - 2022-05-24

### Changed

- Changed **Area_Fill** light shape to `DISK` and Z location to `8`
- Changed **Area_Left** and **Area_Right** light dimensions to `2 × 6`
- Changed **Backdrop** roughness to `1`

## [1.6.2] - 2022-05-22

### Added

- Added a new light

### Changed

- Changed **QLE World**, **Area_Fill**, and **Area_Back** blackbody from `5800` to `5454` for equal energy
- Changed **QLE World** strength from `0` to `0.25`
- Changed **Backdrop** color to `#808080` neutral gray
- Adjusted light positions

## [1.6.1] - 2021-12-29

### Fixed

- Fixed **Clear Collection**

## [1.6.0] - 2021-12-24

### Added

- Added new light `Area_Back`
- Added **Backdrop** object to the scene

### Changed

- Set **Area_Left** blackbody to `3800` for an orange tint
- Set **Area_Right** blackbody to `8800` for a blue tint
- Adjusted light positions

### Fixed

- Fixed error messages

## [1.5.6] - 2021-07-23

### Changed

- Assigned custom `data.name` values to lights

## [1.5.5] - 2021-07-18

### Added

- Added creation of a new world named **QLE World**, which is swapped with the existing world when adding or deleting the environment

### Fixed

- Fixed an error when `scene.world.name` is not named `World`

## [1.5.4] - 2020-09-20

### Added

- Added an INFO message when a button click returns no result

### Changed

- Replaced `try`/`except` blocks with `if`/`else`

### Fixed

- Fixed QLE objects failing to relink to the **QLE** collection after manual deletion and re-adding
- Fixed light tracking failing to reconnect after being disconnected

## [1.5.3] - 2020-09-12

### Changed

- Updated **Clear Environment** to deselect all objects before deleting `QLE`, then purge the scene
- Moved **Add tracking** and **Add blackbody node** into functions
- Cleaned up code

## [1.5.2] - 2020-08-30

### Added

- Added Wiki URL

### Changed

- Changed category to `Lighting`
- Renamed script to `quick_lighting_environment.py`

## 1.5.1 - 2020-08-22

### Changed

- Set light blackbody to `5800` for a more accurate Sun temperature

## [1.5] - 2020-07-19

### Changed

- Set light blackbody to `6000`
- Arranged light nodes
- Cleaned up code

## 1.4 - 2020-06-29

### Added

- Added error handling for clicking **Add Environment** multiple times
- Added error handling for clicking **Clear Environment** when no `QLE` exists in the scene

### Removed

- Removed **Clear All** button

## 1.3 - 2020-06-17

### Added

- Added temporary **Clear All Lights & Empties** option for error handling

### Changed

- Moved lights and empty into a new collection
- Refactored **Clear Environment**

## 1.2 - 2020-06-17

### Added

- Added icons to buttons

### Changed

- Refactored register/unregister

## 1.1 - 2020-03-21

### Added

- Enabled nodes on all lights
- Added a `Blackbody` node set to `5000` to **Emission** shaders

## 1.0 - 2020-02-24

### Added

- Initial add-on

[1.8.0]: https://github.com/don1138/blender-qle/releases/tag/v1.8.0
[1.7.1]: https://github.com/don1138/blender-qle/releases/tag/v1.7.1
[1.6.7]: https://github.com/don1138/blender-qle/releases/tag/v1.6.7
[1.6.6]: https://github.com/don1138/blender-qle/releases/tag/v1.6.6
[1.6.5]: https://github.com/don1138/blender-qle/releases/tag/v1.6.5
[1.6.4]: https://github.com/don1138/blender-qle/releases/tag/v1.6.4
[1.6.3]: https://github.com/don1138/blender-qle/releases/tag/v1.6.3
[1.6.2]: https://github.com/don1138/blender-qle/releases/tag/v.1.6.2
[1.6.1]: https://github.com/don1138/blender-qle/releases/tag/v1.6.1
[1.6.0]: https://github.com/don1138/blender-qle/releases/tag/v1.6.0
[1.5.6]: https://github.com/don1138/blender-qle/releases/tag/1.5.6
[1.5.5]: https://github.com/don1138/blender-qle/releases/tag/1.5.5
[1.5.4]: https://github.com/don1138/blender-qle/releases/tag/1.5.4
[1.5.3]: https://github.com/don1138/blender-qle/releases/tag/1.5.3
[1.5.2]: https://github.com/don1138/blender-qle/releases/tag/1.5.2
[1.5]: https://github.com/don1138/blender-qle/releases/tag/1.5
