# LaMa Inpainting Module

## Overview

This module contains the inpainting component of the Camelia project. It uses [LaMa (Large Mask Inpainting)](https://github.com/advimman/lama) to reconstruct censored areas in images.

## Usage

### Command Line Interface

Run the inpainting on images with:

```bash
python bin/uncen.py --input_images_dir <images_dir> --input_masks_dir <masks_dir> --output_dir <output_dir>
```

## Pre-trained Models

The inpainting models are located in:

-   `pretrained/best/`: Contains the primary inpainting model used by Camelia
