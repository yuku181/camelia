import os
import cv2
import torch
import numpy as np
import argparse
import segmentation_models_pytorch as smp
from albumentations import Compose, Normalize, Resize
from albumentations.pytorch import ToTensorV2
from PIL import Image
import tempfile

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
IMAGE_SIZE = 1024
DEFAULT_OUTPUT_DIR = "output/"

MODEL_PATHS = {
    "black_bars": "pretrained/best_black_bars_model.pth",
    "white_bars": "pretrained/best_white_bars_model.pth",
    "transparent_black": "pretrained/best_transparent_black_model.pth"
}

preprocess_pipeline = Compose([
    Resize(IMAGE_SIZE, IMAGE_SIZE, interpolation=cv2.INTER_NEAREST),
    Normalize(),
    ToTensorV2()
])

def get_input_dir(model_type, base_input_dir="input"):
    """Get input directory based on model type."""
    return os.path.join(base_input_dir, model_type)

def load_model(model_path):
    """Load the trained model from the specified path."""
    checkpoint = torch.load(model_path, map_location=DEVICE)
    if "model_state_dict" in checkpoint:
        model_state_dict = checkpoint["model_state_dict"]
    else:
        model_state_dict = checkpoint

    model = smp.UnetPlusPlus(
        encoder_name="efficientnet-b6",
        encoder_weights=None,
        in_channels=3,
        classes=1
    ).to(DEVICE)

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

def save_results(original_image, predicted_mask, output_path, relative_output_path):
    """Save the original image and predicted mask to the output directory."""
    images_output_dir = os.path.join(output_path, "images", os.path.dirname(relative_output_path))
    masks_output_dir = os.path.join(output_path, "masks", os.path.dirname(relative_output_path))

    os.makedirs(images_output_dir, exist_ok=True)
    os.makedirs(masks_output_dir, exist_ok=True)

    if predicted_mask.max() > 0:
        predicted_mask = (predicted_mask / predicted_mask.max() * 255).astype(np.uint8)

    h, w = original_image.shape[:2]
    resized_mask = cv2.resize(predicted_mask, (w, h), interpolation=cv2.INTER_NEAREST)

    original_image_path = os.path.join(images_output_dir, os.path.basename(relative_output_path))
    Image.fromarray(original_image).save(original_image_path, format="PNG")

    mask_path = os.path.join(masks_output_dir, os.path.basename(relative_output_path))
    Image.fromarray(resized_mask).save(mask_path, format="PNG")

def convert_to_png(image_path):
    """
    Convert JPEG or WebP image to PNG format if needed.
    
    Args:
        image_path: Path to the input image
        
    Returns:
        Path to the PNG image (either converted temp file or original if already PNG)
        Flag indicating if this is a temp file that should be cleaned up
    """
    ext = os.path.splitext(image_path)[1].lower()
    
    if ext == '.png':
        return image_path, False
    
    try:
        print(f"Converting {ext} image to PNG: {image_path}")
        img = Image.open(image_path)
        
        fd, temp_path = tempfile.mkstemp(suffix='.png')
        os.close(fd)
        
        img.save(temp_path, format='PNG')
        return temp_path, True
    except Exception as e:
        print(f"Error converting image {image_path}: {e}")
        return image_path, False

def process_directory_recursively(input_dir, output_dir, model):
    temp_files = []
    
    try:
        for root, _, files in os.walk(input_dir):
            relative_path = os.path.relpath(root, input_dir)
            output_subdir = os.path.join(output_dir, relative_path)
            os.makedirs(output_subdir, exist_ok=True)

            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    image_path = os.path.join(root, file)
                    try:
                        # Convert to PNG if needed
                        png_path, is_temp = convert_to_png(image_path)
                        if is_temp:
                            temp_files.append(png_path)
                        
                        print(f"Processing: {image_path}")
                        original_image, tensor_image = preprocess_image(png_path)
                        predicted_mask = predict_mask(model, tensor_image)

                        opacity_mask = create_opacity_mask(predicted_mask)

                        output_filename = os.path.splitext(file)[0] + '.png'
                        save_results(original_image, opacity_mask, output_dir, 
                                    os.path.join(relative_path, output_filename))
                    except Exception as e:
                        print(f"Error processing {image_path}: {e}")
    finally:
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
            except:
                pass

def run_inference(model_path, model_type, base_input_dir, output_dir):
    """Run inference on all images in the input directory."""
    model = load_model(model_path)

    input_dir = get_input_dir(model_type, base_input_dir)
    # print(f"Using input directory: {input_dir}")

    if not os.path.exists(input_dir):
        os.makedirs(input_dir, exist_ok=True)
        print(f"Created input directory: {input_dir}")
        print(f"Please place input images in {input_dir}")
        return

    process_directory_recursively(input_dir, output_dir, model)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run segmentation inference.")
    parser.add_argument(
        "--model_type",
        type=str,
        required=True,
        choices=MODEL_PATHS.keys(),
        help="Specify the model type to use. Options: 'black_bars', 'white_bars', etc."
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        default="input",
        help="Base input directory (model_type subfolder will be appended)"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for segmentation results"
    )
    args = parser.parse_args()

    model_path = MODEL_PATHS[args.model_type]
    run_inference(model_path, args.model_type, args.input_dir, args.output_dir)