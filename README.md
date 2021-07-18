# Blender QLE

**Add a basic Quick Lighting Environment to your Blender scene.**

![Blender QLE Screenshot](https://github.com/don1138/blender-qle/blob/master/blender-qle.jpg)

## Installation

Download the latest ZIP from [**Releases**](https://github.com/don1138/blender-qle/releases), or `quick_lighting_environment.py` from repository, and install addon.

## Usage

This addon creates a panel named **Quick Lighting Environment** under ``Properties > Scene``.

### 👉 Add Environement
   + Sets the ``World > Surface`` strength to ``0`` (black), and creates three positioned Area Lights. It will also create an Empty named ``Lights_Target`` that is connected to all lights with a ``Track To`` Object Constraint.
   + If you disconnect/delete a Light or the Empty, clicking **Add Environment** again adds the missing object or contraint back into your scene.

### 👉 Clear Environment
   + Deletes QLE Lights and Empty from scene, and sets the ``World > Surface`` strength back to ``1``.

<p align="center">
  <img align="center" src="https://badges.pufler.dev/created/don1138/blender-qle?style=for-the-badge&colorA=222&colorB=48684b" alt="Repo Created">
  <img align="center" src="https://badges.pufler.dev/updated/don1138/blender-qle?style=for-the-badge&colorA=222&colorB=48684b" alt="Repo Updated">
</p>
