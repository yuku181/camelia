import os
import subprocess
import argparse
import shutil

def run_segmentation(model_type, segmentation_script, input_dir, output_dir):
    """Run the segmentation step."""
    print(f"Running segmentation with model type: {model_type}")
    
    script_path = os.path.abspath(segmentation_script)
    script_dir = os.path.dirname(script_path)
    input_dir_abs = os.path.abspath(input_dir)
    output_dir_abs = os.path.abspath(output_dir)
    
    current_dir = os.getcwd()
    
    try:
        if script_dir:
            os.chdir(script_dir)
        
        script_name = os.path.basename(script_path)
        command = [
            "python", script_name,
            "--model_type", model_type,
            "--input_dir", input_dir_abs,
            "--output_dir", output_dir_abs
        ]
        # print(f"Running command: {' '.join(command)}")
        subprocess.run(command, check=True)
    finally:
        os.chdir(current_dir)
    
    print("Segmentation completed.")

def run_inpainting(in_dir, mask_dir, out_dir, checkpoint, inpainting_script, debug_dir=None):
    """Run the inpainting step."""
    print("Running inpainting...")
    
    in_dir_abs = os.path.abspath(in_dir)
    mask_dir_abs = os.path.abspath(mask_dir)
    out_dir_abs = os.path.abspath(out_dir)
    checkpoint_abs = os.path.abspath(checkpoint)
    
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
            "--checkpoint", checkpoint_abs
        ]
        
        if debug_dir:
            debug_dir_abs = os.path.abspath(debug_dir)
            command.extend(["--debug_dir", debug_dir_abs])
        
        subprocess.run(command, check=True, env=env)
    finally:
        os.chdir(current_dir)
    
    print("Inpainting completed.")

def main():
    parser = argparse.ArgumentParser(description="Pipeline to connect segmentation and inpainting.")
    parser.add_argument("--model_type", required=True, choices=["black_bars", "white_bars", "transparent_black"],
                        help="Model type for segmentation.")
    parser.add_argument("--clean_temp", action="store_true", 
                        help="Delete temporary files after processing is complete.")
    args = parser.parse_args()
    
    workspace_root = os.path.dirname(os.path.abspath(__file__))
    camelia_input = os.path.join(workspace_root, "camelia-decensor", "input")
    camelia_output = os.path.join(workspace_root, "camelia-decensor", "output")
    camelia_temp = os.path.join(workspace_root, "camelia-decensor", "temp")
    
    # Ensure temp directory exists
    os.makedirs(camelia_temp, exist_ok=True)
    
    print(f"Input directory: {camelia_input}")
    print(f"Output directory: {camelia_output}")
    print(f"Temp directory: {camelia_temp}")

    # Run segmentation
    run_segmentation(
        model_type=args.model_type,
        segmentation_script=os.path.join(workspace_root, "smp-segmentation", "run_segmentation.py"),
        input_dir=camelia_input,
        output_dir=camelia_temp
    )

    # Run inpainting
    run_inpainting(
        in_dir=os.path.join(camelia_temp, "images"),
        mask_dir=os.path.join(camelia_temp, "masks"),
        out_dir=camelia_output,
        checkpoint=os.path.join(workspace_root, "lama-inpainting", "pretrained", "best"),
        inpainting_script=os.path.join(workspace_root, "lama-inpainting", "bin", "uncen.py")
    )
    
    # Clean up temporary directory if args is set
    if args.clean_temp:
        print(f"Cleaning up temporary directory contents: {camelia_temp}")
        try:
            for root_dir, dirs, files in os.walk(camelia_temp):
                if root_dir == camelia_temp:
                    continue
                
                for file in files:
                    file_path = os.path.join(root_dir, file)
                    try:
                        os.unlink(file_path)
                    except Exception as e:
                        print(f"Error removing file {file_path}: {e}")
                        
                for dir_name in dirs:
                    dir_path = os.path.join(root_dir, dir_name)
                    try:
                        shutil.rmtree(dir_path)
                    except Exception as e:
                        print(f"Error removing directory {dir_path}: {e}")
            
            for file in os.listdir(camelia_temp):
                file_path = os.path.join(camelia_temp, file)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    
            print(f"Successfully cleaned temporary directory contents while preserving the directory structure")
        except Exception as e:
            print(f"Error cleaning temporary directory contents: {e}")
            
    print("Processing complete!")

if __name__ == "__main__":
    main()