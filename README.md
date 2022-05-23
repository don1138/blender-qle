# Blender QLE

**Adds a Basic Lighting Setup to Your Blender Scene.**

![Blender QLE Screenshot](https://github.com/don1138/blender-qle/blob/master/blender-qle.jpg)

## Installation

Download the latest ZIP from [**Releases**](https://github.com/don1138/blender-qle/releases), and install addon via `Edit > Preferences… > Add-ons > Install…`.

## Usage

This addon creates a panel named **Quick Lighting Environment** under ``Properties > Scene``.

### + Add Environement
   + Creates a **World** named **"QLE World"** with **Background > Strength** set to `0.25` and a **Blackbody** value of `5454`.
   + Creates four positioned **Area Lights** with **Blackbody** values of `3800` (Left, orange tint), `5454` (Front and Back, equal energy), and `20,000` (Right, blue tint -- or at least as blue as a blackbody light gets). 
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

<br><br>

<p align="center">
  <img align="center" src="https://badges.pufler.dev/created/don1138/blender-qle?style=for-the-badge&colorA=222&colorB=48684b" alt="Repo Created">
  <img align="center" src="https://badges.pufler.dev/updated/don1138/blender-qle?style=for-the-badge&colorA=222&colorB=48684b" alt="Repo Updated">
</p>

![Alt](https://repobeats.axiom.co/api/embed/e7313fc8115e168686e43e209cb5138dbb64f20a.svg "Repobeats analytics image")
