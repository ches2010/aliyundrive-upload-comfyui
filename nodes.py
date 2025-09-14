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
except ImportError as e:
    print(f"Aliyun Drive Uploader Node: Critical Error - Could not import required libraries even after installation attempt: {e}")
    # We might not be able to define the node class properly without these
    # INSTALL_SUCCESS flag can be checked later

# --- 2. Configuration Handling ---
# Define the path to the config file relative to this script's directory
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_PATH = os.path.join(THIS_DIR, "aliyundrive_config.json")

def load_config():
    """
    Loads refresh_token and folder_id from the config file.
    Returns a dictionary with 'refresh_token' and 'folder_id' keys, or None if failed.
    """
    if not os.path.exists(CONFIG_FILE_PATH):
        print(f"Aliyun Drive Uploader Node Error: Configuration file not found at {CONFIG_FILE_PATH}")
        print("Please create 'aliyundrive_config.json' with 'refresh_token' and 'folder_id'.")
        return None

    try:
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        refresh_token = config_data.get("refresh_token")
        folder_id = config_data.get("folder_id")

        if not refresh_token or not folder_id:
             print("Aliyun Drive Uploader Node Error: 'refresh_token' or 'folder_id' missing in config file.")
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
         return None

# --- 3. Node Class Definition ---
class SimpleUploadToAliyunDrive:
    """
    A ComfyUI node to upload an image to Aliyun Drive using credentials from a config file.
    Also provides image preview.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", ),
                "file_name_prefix": ("STRING", {"default": "comfyui_output_", "multiline": False}),
                # refresh_token and folder_id are now loaded from file, not input
                # We can add a dummy input or a reload config button if needed, but for simplicity, we'll rely on file change + node re-run
            },
        }

    # This node outputs the image for preview and has no named return for data flow
    RETURN_TYPES = ("IMAGE",) 
    RETURN_NAMES = ("images",) # Name the output for clarity
    FUNCTION = "process_and_upload"
    CATEGORY = "image/upload"
    OUTPUT_NODE = False # This node doesn't just perform an action, it also passes data
    DESCRIPTION = "Uploads images to Aliyun Drive using settings from aliyundrive_config.json and provides a preview."

    def process_and_upload(self, images, file_name_prefix):
        """
        Uploads the input images to Aliyun Drive and passes them through for preview.
        """
        # --- Load Configuration ---
        config = load_config()
        if not config:
            # Configuration error, pass through image but don't upload
            print("Aliyun Drive Uploader Node: Upload skipped due to configuration error.")
            return (images, ) # Return images for preview even if upload fails

        refresh_token = config["refresh_token"]
        folder_id = config["folder_id"]

        # --- Initialize Aligo ---
        ali = None
        try:
            if not INSTALL_SUCCESS:
                 raise Exception("Dependencies were not successfully installed.")
            print("Aliyun Drive Uploader Node: Initializing Aligo...")
            ali = Aligo(refresh_token=refresh_token)
            print("Aliyun Drive Uploader Node: Aligo initialized.")
        except Exception as e:
            print(f"Aliyun Drive Uploader Node Error: Failed to initialize Aligo: {e}")
            traceback.print_exc()
            # Pass through image but don't upload
            return (images, )

        # --- Upload Process ---
        try:
            output_dir = folder_paths.get_output_directory()
            print(f"Aliyun Drive Uploader Node: Using ComfyUI output directory: {output_dir}")

            successful_uploads = 0
            for i, image in enumerate(images):
                # Convert tensor to numpy array
                image_np = 255. * image.cpu().numpy()
                from PIL import Image
                img = Image.fromarray(image_np.astype('uint8'), 'RGB')

                # Create a temporary file path
                filename = f"{file_name_prefix}{i:05}.png"
                temp_file_path = os.path.join(output_dir, filename)
                print(f"Aliyun Drive Uploader Node: Saving temporary image to {temp_file_path}")

                img.save(temp_file_path, format='PNG')

                # Upload the file
                print(f"Aliyun Drive Uploader Node: Uploading '{filename}' to folder ID '{folder_id}'...")
                try:
                    uploaded_file = ali.upload_file(file_path=temp_file_path, parent_file_id=folder_id)
                    if uploaded_file and hasattr(uploaded_file, 'file_id'):
                        print(f"Aliyun Drive Uploader Node: Successfully uploaded '{filename}'. File ID: {uploaded_file.file_id}")
                        successful_uploads += 1
                    else:
                        print(f"Aliyun Drive Uploader Node: Warning - Upload call for '{filename}' returned unexpected result.")
                except requests.exceptions.HTTPError as http_err:
                    print(f"Aliyun Drive Uploader Node: HTTP error during upload for '{filename}': {http_err}")
                    print(f"Response content: {getattr(http_err.response, 'text', 'N/A')}")
                except Exception as upload_err:
                    print(f"Aliyun Drive Uploader Node: Error during upload for '{filename}': {upload_err}")
                    traceback.print_exc()
                finally:
                    # Optional: Remove temp file
                    try:
                        os.remove(temp_file_path)
                        print(f"Aliyun Drive Uploader Node: Removed temporary file {temp_file_path}")
                    except OSError as remove_err:
                         print(f"Aliyun Drive Uploader Node: Warning - Could not remove temporary file {temp_file_path}: {remove_err}")

            print(f"Aliyun Drive Uploader Node: Upload process finished. {successful_uploads}/{len(images)} images uploaded successfully.")

        except Exception as e:
            print(f"Aliyun Drive Uploader Node General Error during processing: {e}")
            traceback.print_exc()
            # Even if upload fails, we still return the image for preview
        # --- Pass Image Through for Preview ---
        # The core function is to pass the image through so it can be connected to a Preview node
        return (images, )

# At the end of nodes.py, replace the import and registration part with:

# --- 4. Node Registration ---
# Import the original node from the separate file
try:
    from .nodes_original import UploadToAliyunDrive
    ORIGINAL_NODE_AVAILABLE = True
except ImportError:
    print("Aliyun Drive Uploader Node: Original node (nodes_original.py) not found or failed to import.")
    ORIGINAL_NODE_AVAILABLE = False

NODE_CLASS_MAPPINGS = {
    "SimpleUploadToAliyunDrive": SimpleUploadToAliyunDrive # New simplified node
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "SimpleUploadToAliyunDrive": "Upload to Aliyun Drive (Config File)"
}

# Add the original node mapping only if it was successfully imported
if ORIGINAL_NODE_AVAILABLE:
    NODE_CLASS_MAPPINGS["UploadToAliyunDrive"] = UploadToAliyunDrive
    NODE_DISPLAY_NAME_MAPPINGS["UploadToAliyunDrive"] = "Upload to Aliyun Drive (Manual)"
