import os
import sys
import json
import subprocess
import folder_paths
import traceback
import hashlib # For potential future use or hashing

# --- 1. Dependency Management ---
# Ensure dependencies are installed before importing them
DEPENDENCIES = ['aligo', 'requests'] # Add other deps if needed in the future

def is_dependency_installed(dep_name):
    try:
        __import__(dep_name)
        return True
    except ImportError:
        return False

def install_dependencies():
    missing_deps = [dep for dep in DEPENDENCIES if not is_dependency_installed(dep)]
    if missing_deps:
        print(f"Aliyun Drive Uploader Node: Missing dependencies: {missing_deps}. Attempting to install...")
        try:
            # Use '-s' flag to isolate installation if needed
            subprocess.check_call([sys.executable, '-s', '-m', 'pip', 'install'] + missing_deps)
            print("Aliyun Drive Uploader Node: Dependencies installed successfully.")
            return True
        except Exception as e:
            print(f"Aliyun Drive Uploader Node: Failed to install dependencies {missing_deps}: {e}")
            return False
    return True

# Attempt to install dependencies on import
INSTALL_SUCCESS = install_dependencies()

# Import dependencies after attempting installation
try:
    import requests
    from aligo import Aligo
    DEPS_AVAILABLE = True
except ImportError as e:
    print(f"Aliyun Drive Uploader Node: Critical Error - Could not import required libraries even after installation attempt: {e}")
    DEPS_AVAILABLE = False

# --- 2. Configuration Handling ---
# Define the path to the config file relative to this script's directory
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_PATH = os.path.join(THIS_DIR, "aliyundrive_config.json")

def load_config():
    """
    Loads refresh_token and folder_id from the config file.
    Returns a dictionary with 'refresh_token' and 'folder_id' keys, or None if failed.
    """
    print(f"Aliyun Drive Uploader Node: Attempting to load config from {CONFIG_FILE_PATH}")
    if not os.path.exists(CONFIG_FILE_PATH):
        print(f"Aliyun Drive Uploader Node Error: Configuration file not found at {CONFIG_FILE_PATH}")
        print("Please create 'aliyundrive_config.json' with 'refresh_token' and 'folder_id'.")
        return None

    try:
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        refresh_token = config_data.get("refresh_token")
        folder_id = config_data.get("folder_id")

        if not refresh_token:
             print("Aliyun Drive Uploader Node Error: 'refresh_token' is missing or empty in config file.")
             return None
        if not folder_id:
             print("Aliyun Drive Uploader Node Error: 'folder_id' is missing or empty in config file.")
             return None
        
        print("Aliyun Drive Uploader Node: Configuration loaded successfully.")
        return {
            "refresh_token": refresh_token.strip(), # Remove potential whitespace
            "folder_id": folder_id.strip()
        }
    except json.JSONDecodeError as e:
        print(f"Aliyun Drive Uploader Node Error: Failed to parse config file JSON: {e}")
        return None
    except Exception as e:
         print(f"Aliyun Drive Uploader Node Error: Unexpected error loading config: {e}")
         traceback.print_exc()
         return None

# --- 3. Node Class Definition ---
class SimpleUploadToAliyunDrive:
    """
    A ComfyUI node to upload an image to Aliyun Drive using credentials from a config file.
    This node acts as an output node for preview but does not pass the image data forward.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", ),
                "file_name_prefix": ("STRING", {"default": "comfyui_output_", "multiline": False}),
            },
        }

    # --- Modified: No data output ---
    RETURN_TYPES = () # Empty tuple means no outputs
    RETURN_NAMES = () # Empty tuple for names
    # --- Modified: Mark as output node for preview ---
    OUTPUT_NODE = True # This enables preview without needing to connect to another node
    FUNCTION = "process_and_upload"
    CATEGORY = "image/upload"
    DESCRIPTION = "Uploads images to Aliyun Drive using settings from aliyundrive_config.json. Acts as a preview node."

    def process_and_upload(self, images, file_name_prefix):
        """
        Uploads the input images to Aliyun Drive.
        Does not return the images, just triggers the upload and enables preview.
        """
        print("Aliyun Drive Uploader Node: process_and_upload called.")
        
        # --- Check if any images are received ---
        if images is None:
            print("Aliyun Drive Uploader Node Warning: No images received on input.")
            # Return empty dict for OUTPUT_NODE
            return {} 
        
        # Handle single image tensor or batch
        # ComfyUI usually sends a batch as [B, H, W, C] tensor
        # len(images) gives the batch size (B)
        try:
            image_count = len(images) if hasattr(images, '__len__') else (1 if images is not None else 0)
        except:
             # Fallback if len fails for any reason
             image_count = 1 if images is not None else 0
             
        print(f"Aliyun Drive Uploader Node: Received {image_count} image(s).")

        if image_count == 0:
             print("Aliyun Drive Uploader Node: Image list is empty. Nothing to upload.")
             return {}

        # --- Load Configuration ---
        config = load_config()
        if not config:
            print("Aliyun Drive Uploader Node: Upload process aborted due to configuration error.")
            return {} # Return empty dict for OUTPUT_NODE

        refresh_token = config["refresh_token"]
        folder_id = config["folder_id"]

        # --- Initialize Aligo ---
        ali = None
        if not DEPS_AVAILABLE:
             print("Aliyun Drive Uploader Node: Upload process aborted due to missing dependencies.")
             return {}

        try:
            print("Aliyun Drive Uploader Node: Initializing Aligo client...")
            ali = Aligo(refresh_token=refresh_token)
            print("Aliyun Drive Uploader Node: Aligo client initialized successfully.")
        except Exception as e:
            print(f"Aliyun Drive Uploader Node Error: Failed to initialize Aligo client: {e}")
            traceback.print_exc()
            return {}

        # --- Upload Process ---
        try:
            output_dir = folder_paths.get_output_directory()
            print(f"Aliyun Drive Uploader Node: Using ComfyUI output directory: {output_dir}")

            successful_uploads = 0
            from PIL import Image # Import here as it's used inside the loop
            
            # --- Main Upload Loop ---
            print("Aliyun Drive Uploader Node: Starting upload loop...")
            # Iterate over the batch dimension
            for i in range(image_count): 
                try:
                    print(f"Aliyun Drive Uploader Node: Processing image {i+1}/{image_count}...")
                    
                    # Get the i-th image from the batch tensor [B, H, W, C]
                    # images[i] will be a tensor of shape [H, W, C]
                    single_image_tensor = images[i] 
                    
                    # Convert tensor [H, W, C] to numpy array
                    # Assuming tensor values are in 0-1 range, scale to 0-255
                    image_np = 255. * single_image_tensor.cpu().numpy()
                    # Create PIL Image from numpy array (H, W, C) in RGB format
                    img = Image.fromarray(image_np.astype('uint8'), 'RGB')

                    # Create a temporary file path
                    filename = f"{file_name_prefix}{i:05}.png"
                    temp_file_path = os.path.join(output_dir, filename)
                    print(f"Aliyun Drive Uploader Node: Saving temporary image to {temp_file_path}")

                    img.save(temp_file_path, format='PNG')
                    print(f"Aliyun Drive Uploader Node: Temporary image saved.")

                    # Upload the file
                    print(f"Aliyun Drive Uploader Node: Uploading '{filename}' to folder ID '{folder_id}'...")
                    uploaded_file = ali.upload_file(file_path=temp_file_path, parent_file_id=folder_id)
                    
                    if uploaded_file and hasattr(uploaded_file, 'file_id'):
                        print(f"Aliyun Drive Uploader Node: Successfully uploaded '{filename}'. File ID: {uploaded_file.file_id}")
                        successful_uploads += 1
                    else:
                        print(f"Aliyun Drive Uploader Node: Warning - Upload call for '{filename}' did not return a valid file object.")
                        
                except Exception as img_err:
                    print(f"Aliyun Drive Uploader Node Error processing image {i+1}: {img_err}")
                    traceback.print_exc()
                finally:
                     # Optional: Remove temp file
                     try:
                         if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                             os.remove(temp_file_path)
                             print(f"Aliyun Drive Uploader Node: Removed temporary file {temp_file_path}")
                     except OSError as remove_err:
                         print(f"Aliyun Drive Uploader Node: Warning - Could not remove temporary file {temp_file_path}: {remove_err}")

            print(f"Aliyun Drive Uploader Node: Upload process finished. {successful_uploads}/{image_count} images uploaded successfully.")

        except Exception as e:
            print(f"Aliyun Drive Uploader Node General Error during upload process: {e}")
            traceback.print_exc()
            
        # --- No data returned, just enable preview via OUTPUT_NODE ---
        print("Aliyun Drive Uploader Node: Upload complete. Enabling preview.")
        # For OUTPUT_NODE, returning an empty dict {} is standard
        return {} 

# --- 4. Node Registration ---
# Assuming you have the original node in nodes_original.py
try:
    from .nodes_original import UploadToAliyunDrive
    ORIGINAL_NODE_AVAILABLE = True
except ImportError:
    print("Aliyun Drive Uploader Node: Original node (nodes_original.py) not found or failed to import.")
    ORIGINAL_NODE_AVAILABLE = False

NODE_CLASS_MAPPINGS = {
    "SimpleUploadToAliyunDrive": SimpleUploadToAliyunDrive
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SimpleUploadToAliyunDrive": "Upload to Aliyun Drive (Config File - Preview)"
}

if ORIGINAL_NODE_AVAILABLE:
    NODE_CLASS_MAPPINGS["UploadToAliyunDrive"] = UploadToAliyunDrive
    NODE_DISPLAY_NAME_MAPPINGS["UploadToAliyunDrive"] = "Upload to Aliyun Drive (Manual)"
