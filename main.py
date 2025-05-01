import os
import subprocess
import argparse

def run_segmentation(model_type, segmentation_script, input_dir, output_dir):
    """Run the segmentation step."""
    print(f"Running segmentation with model type: {model_type}")
    
    script_dir = os.path.dirname(segmentation_script)
    
    current_dir = os.getcwd()
    
    try:
        if script_dir:
            os.chdir(script_dir)
        
        script_name = os.path.basename(segmentation_script)
        command = [
            "python", script_name,
            "--model_type", model_type
        ]
        subprocess.run(command, check=True)
    finally:
        os.chdir(current_dir)
    
    print("Segmentation completed.")

def run_inpainting(in_dir, mask_dir, out_dir, debug_dir, checkpoint, inpainting_script):
    """Run the inpainting step."""
    print("Running inpainting...")
    
    in_dir_abs = os.path.abspath(in_dir)
    mask_dir_abs = os.path.abspath(mask_dir)
    out_dir_abs = os.path.abspath(out_dir)
    debug_dir_abs = os.path.abspath(debug_dir)
    checkpoint_abs = os.path.abspath(checkpoint)
    
    script_dir = os.path.dirname(inpainting_script)
    script_name = os.path.basename(inpainting_script)
    
    lama_root = os.path.dirname(os.path.dirname(os.path.abspath(inpainting_script)))
    
    current_dir = os.getcwd()
    
    env = os.environ.copy()
    env["PYTHONPATH"] = lama_root + (os.pathsep + env["PYTHONPATH"] if "PYTHONPATH" in env else "")
    
    print(f"Running from lama root: {lama_root}")
    print(f"Using checkpoint: {checkpoint_abs}")
    
    try:
        os.chdir(lama_root)
        
        command = [
            "python", os.path.join("bin", script_name),
            "--in_dir", in_dir_abs,
            "--mask_dir", mask_dir_abs,
            "--out_dir", out_dir_abs,
            "--debug_dir", debug_dir_abs,
            "--checkpoint", checkpoint_abs
        ]
        subprocess.run(command, check=True, env=env)
    finally:
        os.chdir(current_dir)
    
    print("Inpainting completed.")

def main():
    parser = argparse.ArgumentParser(description="Pipeline to connect segmentation and inpainting.")
    parser.add_argument("--model_type", required=True, choices=["black_bars", "white_bars", "transparent_black"],
                        help="Model type for segmentation.")
    args = parser.parse_args()

    # Run segmentation
    run_segmentation(
        model_type=args.model_type,
        segmentation_script="smp-segmentation/run_segmentation.py",
        input_dir="smp-segmentation/input",
        output_dir="smp-segmentation/output"
    )

    # Run inpainting
    run_inpainting(
        in_dir="smp-segmentation/output/images",
        mask_dir="smp-segmentation/output/masks",
        out_dir="lama-inpainting/output",
        debug_dir="lama-inpainting/output_dbg",
        checkpoint="lama-inpainting/pretrained/best",
        inpainting_script="lama-inpainting/bin/uncen.py"
    )

if __name__ == "__main__":
    main()