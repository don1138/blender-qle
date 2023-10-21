# Blender QLE

**Adds a Basic Lighting Setup to Your Blender Scene.**

![Blender QLE Screenshot](https://github.com/don1138/blender-qle/blob/master/blender-qle.jpg)

## Installation

Download the latest ZIP from [**Releases**](https://github.com/don1138/blender-qle/releases), and install addon via `Edit > Preferences… > Add-ons > Install…`.

## Usage

This addon creates a panel named **Quick Lighting Environment** under `Properties > Scene`.

**!! IMPORTANT !!** Make sure you have an active **World** in your scene, or the add-on will error out.

### + Add Environement
   + Creates a **World** named **"QLE World"** with **Background > Strength** set to `0.25` and a **Blackbody** value of `5454`.
   + Creates four positioned **Area Lights** with **Blackbody** values of `3800` (Left, orange tint), `5454` (Fill and Back, equal energy), and `20,000` (Right, blue tint -- or at least as blue as a blackbody light gets). 
   + Creates an **Empty** named `Lights_Target` and connects all **Lights** to it with ``Track To`` **Object Constraints**.
   + Adds an **Mesh Object** named `Backdrop`.
   + If you disconnect/delete a **Light**, the **Backdrop**, or the **Empty**, clicking **Add Environment** re-inserts the missing object or constraint back into your scene.

### - Clear Environment
   + Purges **QLE Lights**, **Backdrop**, and **Empty** from scene, and resets the **World** from **"QLE World"** back to the original.

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

<br><br>

<p align="center">
  <img alt="GitHub latest commit" src="https://img.shields.io/github/last-commit/don1138/blender-qle">
  <img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/don1138/blender-qle">
  <img alt="Github all releases" src="https://img.shields.io/github/downloads/don1138/blender-qle/total.svg"><br>
  <img src="https://repobeats.axiom.co/api/embed/e7313fc8115e168686e43e209cb5138dbb64f20a.svg" alt="Repobeats analytics image">
</p>

