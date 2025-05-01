import os
import cv2
import torch
import numpy as np
import argparse
import segmentation_models_pytorch as smp
from albumentations import Compose, Normalize, Resize
from albumentations.pytorch import ToTensorV2
from PIL import Image

# Constants
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
IMAGE_SIZE = 1024
INPUT_DIR = "input/"
OUTPUT_DIR = "output/"

MODEL_PATHS = {
    "black_bars": "pretrained/best_transparent_black_model.pth",
    "white_bars": "pretrained/best_white_bars_model.pth",
    "transparent_black": "pretrained/best_transparent_black_model.pth"
}

# Preprocessing pipeline
preprocess_pipeline = Compose([
    Resize(IMAGE_SIZE, IMAGE_SIZE, interpolation=cv2.INTER_NEAREST),
    Normalize(),
    ToTensorV2()
])

def load_model(model_path):
    """Load the trained model from the specified path."""
    checkpoint = torch.load(model_path, map_location=DEVICE)
    if "model_state_dict" in checkpoint:
        # If the checkpoint contains additional metadata, extract the model's state dictionary
        model_state_dict = checkpoint["model_state_dict"]
    else:
        # If the file is just the state dictionary, use it directly
        model_state_dict = checkpoint

    # Define the model architecture
    model = smp.UnetPlusPlus(
        encoder_name="efficientnet-b6",
        encoder_weights=None,
        in_channels=3,
        classes=1
    ).to(DEVICE)

    # Load the state dictionary into the model
    model.load_state_dict(model_state_dict)
    model.eval()
    return model

def preprocess_image(image_path):
    """Preprocess the input image for the model."""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Failed to load image: {image_path}")
    
    original_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    processed = preprocess_pipeline(image=original_image)
    tensor_image = processed["image"].unsqueeze(0).to(DEVICE)
    return original_image, tensor_image

def predict_mask(model, tensor_image):
    """Generate a mask prediction using the model."""
    with torch.no_grad():
        prediction = model(tensor_image)
        return prediction.squeeze().sigmoid().cpu().numpy()

def create_opacity_mask(predicted_mask):
    """
    Create an opacity mask based on thresholds.

    Args:
        predicted_mask: The predicted mask from the model.

    Returns:
        The opacity mask.
    """
    opacity_mask = np.zeros_like(predicted_mask, dtype=np.uint8)
    opacity_mask[predicted_mask > 0.2] = 50
    opacity_mask[predicted_mask > 0.35] = 75
    opacity_mask[predicted_mask > 0.5] = 100
    return opacity_mask

def save_results(original_image, predicted_mask, output_path, input_filename):
    """Save the original image and predicted mask to the output directory."""
    images_output_dir = os.path.join(output_path, "images")
    masks_output_dir = os.path.join(output_path, "masks")

    os.makedirs(images_output_dir, exist_ok=True)
    os.makedirs(masks_output_dir, exist_ok=True)

    # Normalize mask to 0-255 range
    if predicted_mask.max() > 0:
        predicted_mask = (predicted_mask / predicted_mask.max() * 255).astype(np.uint8)

    # Resize mask back to original image size
    h, w = original_image.shape[:2]
    resized_mask = cv2.resize(predicted_mask, (w, h), interpolation=cv2.INTER_NEAREST)

    # Save original image
    original_image_path = os.path.join(images_output_dir, input_filename)
    Image.fromarray(original_image).save(original_image_path, format="PNG")

    # Save mask
    mask_path = os.path.join(masks_output_dir, input_filename)
    Image.fromarray(resized_mask).save(mask_path, format="PNG")

def run_inference(model_path):
    """Run inference on all images in the input directory."""
    model = load_model(model_path)

    input_images = [
        os.path.join(INPUT_DIR, filename)
        for filename in os.listdir(INPUT_DIR)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg'))
    ]

    if not input_images:
        print(f"No images found in {INPUT_DIR}")
        return

    for image_path in input_images:
        try:
            print(f"Processing: {image_path}")
            original_image, tensor_image = preprocess_image(image_path)
            predicted_mask = predict_mask(model, tensor_image)

            opacity_mask = create_opacity_mask(predicted_mask)

            input_filename = os.path.basename(image_path)
            output_path = OUTPUT_DIR
            save_results(original_image, opacity_mask, output_path, input_filename)
        except Exception as e:
            print(f"Error processing {image_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run segmentation inference.")
    parser.add_argument(
        "--model_type",
        type=str,
        required=True,
        choices=MODEL_PATHS.keys(),
        help="Specify the model type to use. Options: 'black_bars', 'white_bars', etc."
    )
    args = parser.parse_args()

    model_path = MODEL_PATHS[args.model_type]
    run_inference(model_path)