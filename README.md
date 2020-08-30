# blender-qle

Add a basic Quick Lighting Environment to your Blender scene.

![Blender QLE Screenshot](https://github.com/don1138/blender-qle/blob/master/blender-qle.jpg)

## Installation

Download the latest ZIP from **Releases**, or `quick_lighting_environment.py` from repository, and install addon.

## Usage

This addon installs a new panel named **QLE (Quick Lighting Environment)** under ``Properties > Scene``.

Click **Add Environement** to set the ``World > Surface`` strength to ``0`` (black), and create three positioned Area Lights. This will also create an Empty named ``Lights_Target`` that is connected to all lights with a ``Track To`` Object Constraint.

Click **Clear Environment** to delete QLE Lights and Empty from scene, and set the ``World > Surface`` strength back to ``1``.

## Version History

**1.1** – Enable nodes on all Lights, and add Blackbody Converter set to ``5000`` (daylight-ish) to Emission Shaders

**1.2** – Add icons to Buttons, and refactor Register/Unregister

**1.3** – Move Lights and Empty into new Collection, refactor Clear Environment, and add "Clear All Lights & Empties" as temp fix for Error Handling

**1.4** – Error handling for clicking Add Environment multple times, or Clear Environment when there is no QLE in Scene. Removed **Clear All** button.

**1.5** – Set Lights Blackbody to ``6000``, arrange Lights Nodes, and code cleanup.

**1.5.1** – Set light Blackbody to ``5800``, more accurate Sun temperature.

**1.5.2** – Change category to ``Lighting``, add Wiki URL, rename script to ``quick_lighting_environment.py``.

## Version Path

**1.6** – Fix: When a QLE object is manually deleted and then re-added, it doesn't link back into QLE Collection.
