# blender-qle

Add a basic Quick Lighting Environment to your Blender scene.

![Blender QLE Screenshot](https://github.com/don1138/blender-qle/blob/master/blender-qle.jpg)

## Installation

Download `quick_environment.py` and install addon.

## Usage

This addon installs a new panel named **Add Quick Environment** under ``Properties > Scene``.

Click **Add Environement** to set the world surface to black, and create three positioned Area Lights. This will also create an Empty named ``Lights_Target`` that is connected to all lights with a "Track To" Object Constraint.

Click **Clear Environment** to deleta ALL Lights and Empties in your scene.

## Version History

**1.1** – Enable nodes on all lights, and add Blackbody Converter set to 5000 (daylight-ish) to Emission Shaders

## Version Path

**1.2** – Move lights and empty to a new Collection
