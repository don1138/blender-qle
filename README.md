# Blender QLE

**Adds a Basic Lighting Setup to Your Blender Scene.**

![Blender QLE Screenshot](https://github.com/don1138/blender-qle/blob/master/blender-qle.jpg)

## Installation

Download the latest ZIP from [**Releases**](https://github.com/don1138/blender-qle/releases), and install addon via `Edit > Preferences… > Add-ons > Install…`.

## Usage

This addon creates a panel named **Quick Lighting Environment** under ``Properties > Scene``.

### + Add Environement
   + Creates a **World** named **"QLE World"** with ``World > Surface`` strength set to ``0`` (black)
   + Creates four positioned **Area Lights** with **Blackbody** values of `3800` (Left, orange tint), `5800` (Front and Back, neutral tint), and `8800` (Right, blue tint). 
   + Creates an **Empty** named `Lights_Target` and connects all **Lights** to it with ``Track To`` **Object Constraints**.
   + Adds an **Mesh Object** named `Backdrop`
   + If you disconnect/delete a **Light**, the **Backdrop**, or the **Empty**, clicking **Add Environment** re-inserts the missing object or contraint back into your scene.

### - Clear Environment
   + Purges **QLE Lights**, **Backdrop**, and **Empty** from scene, and resets the **World** from **"QLE World"** back to the original.

<p align="center">
  <img align="center" src="https://badges.pufler.dev/created/don1138/blender-qle?style=for-the-badge&colorA=222&colorB=48684b" alt="Repo Created">
  <img align="center" src="https://badges.pufler.dev/updated/don1138/blender-qle?style=for-the-badge&colorA=222&colorB=48684b" alt="Repo Updated">
</p>
