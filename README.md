# Camelia

## Installation

### Prerequisites

-   Python 3.9
-   Conda (recommended for managing environments)
-   NVIDIA GPU with CUDA support (optional but recommended for faster processing)

### Steps

1. Clone the repository:

    ```bash
    git clone <repository_url>
    cd camelia
    ```

2. Create a Conda environment:

    ```bash
    conda create --name camelia_env python=3.9 -y
    conda activate camelia_env
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Verify PyTorch installation:
   Ensure that PyTorch is installed with CUDA support (if applicable):
    ```bash
    python -c "import torch; print(torch.cuda.is_available())"
    ```
    This should return `True` if CUDA is available.

## Usage

### CLI Mode

1. Place your input images in the correct `camelia-decensor/input` directory (`input/black_bars`, `input/white_bars`, `input/transparent_black`)
    - Subdirectories can be used

2. Run:

    ```bash
    python main.py --model_type <model_type>
    ```

    Replace `<model_type>` with one of the following options:

    - `black_bars`
    - `white_bars`
    - `transparent_black`

3. The output will be saved under `camelia-decensor/output`.

### Example

```bash
python main.py --model_type black_bars
```

## Notes

-   Ensure that the `pretrained` directory contains the required model checkpoints.
-   For debugging, additional outputs are saved in the `output_dbg` directory.

## License

This project is licensed under the MIT License.
