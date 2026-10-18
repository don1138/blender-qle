# Blender QLE

**Adds a Basic Lighting Setup to Your Blender Scene.**

![Blender QLE Screenshot](https://github.com/don1138/blender-qle/blob/master/imx/blender-qle.jpg)

## QLE 2.0 development branch

Requires **Blender 4.5 or newer**. The new panel is under **3D Viewport > Sidebar > Quick Tools > Quick Lighting Environment**. The screenshots below show the legacy release. This branch has not yet been packaged or released; see [the plan](docs/QLE_2.0_PLAN.md) and validation notes under `docs/`.

## Installation

Published ZIPs are available from [Releases](https://github.com/don1138/blender-qle/releases). Install the appropriate extension ZIP through Blender Preferences. The published release and this development branch may differ.

## Usage

- **Add:** creates the original four-light environment, target, C backdrop, and 5454 K World at Strength 0.25. Click again to restore missing default parts without resetting adjustments. Protected original lights count as present.
- **Reset:** restores default unprotected lights, target, backdrop, and World, removing added unprotected lights and adjustments. Requires confirmation. Protected lights remain.
- **Clear:** removes unprotected QLE content and restores the previous World. Requires confirmation. Protected lights remain editable.

Open **Adjustments** for more controls:

- **Lights:** add, rename, select, enable/disable, protect, reset, or delete an Area light. Each light has Power, exclusive RGB/Kelvin color modes, Shape, and Size controls.
- **Position:** Around Subject, Elevation, and Distance describe placement around the light's target. Users can still grab the actual light normally; these fields reflect the resulting position.
- **Follow Target** controls whether target movement carries the light. **Aim > Target/Manual** independently chooses automatic pointing or manual rotation.
- **Target:** choose Free or Object following. Selecting an object snaps to its origin; Position allows an offset. Following inherits translation only.
- **Backdrop:** choose C, L, Flat Background, Floor, or None. Color, Finish, Roughness, Position, and visibility remain editable. Switching shapes preserves the surface settings and enabled state.
- **World:** Strength plus the same exclusive RGB/Kelvin modes. Each mode remembers its own value; Kelvin is never multiplied by the saved RGB color.

**Protect** moves a light and its required helpers into `QLE Protected`. It retains its own target through Reset/Clear. **Reset Light** restores one light's settings and position while preserving its name and protection.

Existing recognizable QLE setups can be adopted by clicking Add. Legacy QLE did not save the previous World in `.blend` files; if that history is missing, QLE reports it and creates a fallback World on Clear rather than guessing.

The original backdrop's Diffuse material remains unchanged by default. An explicit Finish or Roughness edit converts its surface to Principled so reflective finishes can work. Reset restores the original material.

## Lights

### All Lights
![QLE - All Lights](https://github.com/don1138/blender-qle/blob/master/imx/QLE-00.jpg)
### QLE World
![QLE - QLE World](https://github.com/don1138/blender-qle/blob/master/imx/QLE-01.jpg)
### Area Right
![QLE - Area Right](https://github.com/don1138/blender-qle/blob/master/imx/QLE-02.jpg)
### Area Left
![QLE - Area Left](https://github.com/don1138/blender-qle/blob/master/imx/QLE-03.jpg)
### Area Back
![QLE - Area Back](https://github.com/don1138/blender-qle/blob/master/imx/QLE-04.jpg)
### Area Fill
![QLE - Area Fill](https://github.com/don1138/blender-qle/blob/master/imx/QLE-05.jpg)

## Notes
- Using World light is a bit of a cheat, but I like how it evens out the backdrop.
- If you want a true "Studio" setup, turn the **QLE World** strength to `0` and increase the power of the **Area Fill** light.
- You may also want to angle some bounce cards on the ground in front of your model to lessen the bottom shadows. I use a basic mesh plane with `Properties > Object Properties > Visibility > Ray Visibility > Camera` and `Glossy` turned off.

## Mentions
- [Architecture Topics: 10 Best Free Blender ADD-ONS!](https://www.youtube.com/watch?v=QJnB6LRtpxA&t=173s)
- [Architecture Topics: Best Glass Material in Blender (Tutorial)](https://www.youtube.com/watch?v=MzIreMJRhqk)
- [Jinxxy.com](https://jinxxy.com/market/browse?search_query=Quick+Metal+Materials&listing=3449245791745476435)
- [Architecture Topics: BEST Free Lighting Addons for Blender 2024](https://youtu.be/nojuev0F1_w)
- [Quick Lighting Environment (QLE) Addon for Blender | Free Studio Light Just ONE CLICK | Graphskill](https://www.youtube.com/watch?v=8RnYfONirUQ)

<br><br>

<p align="center">
  <img alt="GitHub latest commit" src="https://img.shields.io/github/last-commit/don1138/blender-qle">
  <img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/don1138/blender-qle">
  <img alt="Github all releases" src="https://img.shields.io/github/downloads/don1138/blender-qle/total.svg"><br>
  <img src="https://repobeats.axiom.co/api/embed/e7313fc8115e168686e43e209cb5138dbb64f20a.svg" alt="Repobeats analytics image">
</p>
