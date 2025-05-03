# SMP Segmentation Module

## Overview

This module contains the segmentation component of the Camelia project. It uses [Segmentation Models PyTorch (SMP)](https://github.com/qubvel/segmentation_models.pytorch) to detect and create masks of censored areas in images

## Usage

### Command Line Interface

Run the segmentation on images with:

```bash
python run_segmentation.py --model_type <model_type> [--input_dir <input_dir>] [--output_dir <output_dir>]
```

Arguments:

-   `--model_type`: Type of censorship to detect (Required)
    -   Options: `black_bars`, `white_bars`, `transparent_black`
-   `--input_dir`: Base input directory (Optional, default: "input")
-   `--output_dir`: Output directory for segmentation results (Optional, default: "output/")

### Input/Output Structure

-   **Input**: Place images in the corresponding subdirectory under the input directory:

    -   `input/black_bars/`
    -   `input/white_bars/`
    -   `input/transparent_black/`

-   **Output**: Results are saved in the output directory with the following structure:
    -   `output/images/`: Original images
    -   `output/masks/`: Generated masks showing detected censored areas

## Pre-trained Models

The module includes pre-trained models for each censorship type:

-   `pretrained/best_black_bars_model.pth`
-   `pretrained/best_white_bars_model.pth`
-   `pretrained/best_transparent_black_model.pth`

## Training

To train a new segmentation model, use the Jupyter notebook:

```bash
jupyter notebook train_segmentation.ipynb
```
