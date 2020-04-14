# blender-qle

Add a basic Quick Lighting Environment to your Blender scene.

![Blender QLE Screenshot](https://github.com/don1138/blender-qle/blob/master/blender-qle.jpg)

## Installation

Download `quick_environment.py` and install addon.

## Usage

This addon installs a new panel named **Add Quick Environment** under ``Properties > Scene``.

Click **Add Environement** to set the ``World > Surface`` strength to ``0`` (black), and create three positioned Area Lights. This will also create an Empty named ``Lights_Target`` that is connected to all lights with a ``Track To`` Object Constraint.

Click **Clear Environment** to delete ALL Lights and Empties in your scene, and set the ``World > Surface`` strength back to ``1``.

## Version History

**1.1** – Enable nodes on all Lights, and add Blackbody Converter set to ``5000`` (daylight-ish) to Emission Shaders

## Version Path

**1.2** – Move Lights and Empty into a new Collection
