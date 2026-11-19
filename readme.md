# Pixel Energy

**Pixel Energy** is a QGIS plugin that allows users to estimate the energy consumption of a display or calculate an indicator based on the pixels displayed in the map canvas.

The plugin analyses pixel colours and applies models and formulas to investigate the influence of map content on estimated energy consumption.

## Requirements

- QGIS 3.22 or later.
- Compatible with both QGIS 3 and QGIS 4.

The plugin uses the Python environment and PyQGIS libraries provided with QGIS. A separate Python installation is normally not required.

## Manual Installation

### Option 1 — Installing from the Plugin Folder

1. Download or obtain the plugin folder, which should contain files such as `__init__.py`, `metadata.txt`, and the Python source files.
2. Open QGIS.
3. Locate the plugin directory of your QGIS profile. You can usually access it through **Settings → Options → System**, or by opening your QGIS user profile directory.
4. Copy the plugin folder into the `python/plugins` directory. The folder must be named `pixel_analyse_qgis`.
5. Make sure that `metadata.txt` and `__init__.py` are located directly inside this folder, not in an additional subfolder.
6. Restart QGIS if necessary.
7. Open **Plugins → Manage and Install Plugins…**, search for **Pixel Energy**, and tick the checkbox to enable it.

### Option 2 — Installing from a ZIP Archive

1. Obtain the plugin folder.
2. Compress the `pixel_analyse_qgis` folder into a ZIP archive, preserving its directory structure.
3. Open QGIS.
4. Go to **Plugins → Manage and Install Plugins…**.
5. Select the **Install from ZIP** tab.
6. Select the ZIP archive and start the installation.
7. Enable the plugin if necessary.

## Features

- Analyse a selected rectangular area of the QGIS map canvas.
- Analyse the entire map canvas.
- Calculate pixel colour statistics, including red, green and blue (RGB) components, as well as luminance.
- Select a display model from the built-in models.
- Create, edit and delete custom models.
- Define a per-pixel calculation formula.
- Define an output formula, depending on the model type, to calculate estimated power consumption or an indicator.

## Usage

### 1. Opening Pixel Energy

Once the plugin is enabled, launch it from its entry in the QGIS menu or toolbar.

### 2. Selecting a Model

Select the model you want to use from the available list.

Models define, among other things, the display technology being considered, the formula applied to each pixel, and the type of result calculated.

The model management button allows you to create, edit or delete custom models. Built-in models are provided by the plugin and cannot be edited or deleted through this interface.

### 3. Analysing an Area or the Entire Map Canvas

The plugin offers two analysis options:

- Select a rectangular area of the map canvas to analyse.
- Analyse the entire map canvas.

Once the analysis is complete, the results and corresponding statistics are displayed in the plugin window.

The statistics describe the pixels in the analysed screenshot. Power estimates depend on the selected model and do not represent a direct measurement of the actual electrical power consumption of the computer or display.

### 4. Creating a Custom Model

In the main window, open the model management interface and select the option to create a new model.

A custom model can include:

- A name.
- A display technology.
- A per-pixel calculation formula.
- An output type: indicator or power.
- An output formula if the model produces a power estimate.

To build the per-pixel formula, you can use the following RGB variables:

- `@r`: red component of the pixel.
- `@g`: green component of the pixel.
- `@b`: blue component of the pixel.

For an output formula, additional variables are available:

- `@pixel_value`: result of the per-pixel calculation.
- `@pixel_count`: number of analysed pixels.
- `@width`: width of the analysed image.
- `@height`: height of the analysed image.

Use the formula-building and testing tools available in the editor to check the syntax





