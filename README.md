# Blender QLE

Add a basic Quick Lighting Environment to your Blender scene.

![Blender QLE Screenshot](https://github.com/don1138/blender-qle/blob/master/blender-qle.jpg)

## Installation

Download the latest ZIP from **Releases**, or `quick_lighting_environment.py` from repository, and install addon.

## Usage

This addon creates a panel named **QLE (Quick Lighting Environment)** under ``Properties > Scene``.

### 👉 Add Environement
   + Sets the ``World > Surface`` strength to ``0`` (black), and creates three positioned Area Lights. It will also create an Empty named ``Lights_Target`` that is connected to all lights with a ``Track To`` Object Constraint.
   + If you disconnect/delete a Light or the Empty, clicking **Add Environment** again adds the missing object or contraint back into your scene.

### 👉 Clear Environment
   + Deletes QLE Lights and Empty from scene, and sets the ``World > Surface`` strength back to ``1``.

## Version History

**1.1**
   + Enable nodes on all Lights
   + Add Blackbody Converter set to ``5000`` (daylight-ish) to Emission Shaders

**1.2**
   + Add icons to Buttons
   _ Refactor Register/Unregister

**1.3**
   + Move Lights and Empty into new Collection
   + Refactor Clear Environment
   + Add "Clear All Lights & Empties" as temp fix for Error Handling

**1.4**
   + Error handling for clicking Add Environment multple times, or Clear Environment when there is no QLE in Scene
   + Removed **Clear All** button.

**1.5**
   + Set Lights Blackbody to ``6000``
   + Arrange Lights Nodes
   + Code cleanup.

**1.5.1**
   + Set light Blackbody to ``5800``, more accurate Sun temperature.

**1.5.2**
   + Change category to ``Lighting``
   + Add Wiki URL
   + Rename script to ``quick_lighting_environment.py``.

**1.5.3**
   + Clear Environment: Deselect All before deleting QLE, Purge Scene after
   + Move Add Tracking and Add Blackbody Node into functions
   + Code cleanup

**1.5.4**
   + Bugfix: When a QLE object is manually deleted and then re-added, it doesn't link back into QLE Collection
   + Bugfix: Reconnect Light to Target if disconnected
   + Add INFO message for when button click returns no result


## Version Path

**1.6**
   + Popup to set light intensity, color and position when adding QLE. Yep, just like Tri-Lighting.

***

<p align="center">
  <img align="center" src="https://badges.pufler.dev/created/don1138/blender-qle?style=for-the-badge&colorA=222&colorB=48684b" alt="Repo Created">
  <img align="center" src="https://badges.pufler.dev/updated/don1138/blender-qle?style=for-the-badge&colorA=222&colorB=48684b" alt="Repo Updated">
</p>
