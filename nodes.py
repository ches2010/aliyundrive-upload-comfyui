import os
import sys
import json
import subprocess
import folder_paths
import traceback
import hashlib # For potential future use or hashing

# --- 1. Dependency Management ---
# Ensure dependencies are installed before importing them
# Updated to include py115 for 115 Pan support
DEPENDENCIES = ['aligo', 'requests', 'py115']

def is_dependency_installed(dep_name):
    try:
        __import__(dep_name)
        return True
    except ImportError:
        return False

def install_dependencies():
    missing_deps = [dep for dep in DEPENDENCIES if not is_dependency_installed(dep)]
    if missing_deps:
        print(f"Custom Uploader Node: Missing dependencies: {missing_deps}. Attempting to install...")
        try:
            # Use '-s' flag to isolate installation if needed
            subprocess.check_call([sys.executable, '-s', '-m', 'pip', 'install'] + missing_deps)
            print("Custom Uploader Node: Dependencies installed successfully.")
            return True
        except Exception as e:
            print(f"Custom Uploader Node: Failed to install dependencies {missing_deps}: {e}")
            return False
    return True

# Attempt to install dependencies on import
INSTALL_SUCCESS = install_dependencies()

# Import dependencies after attempting installation
try:
    import requests
    from aligo import Aligo
    try:
        from py115 import Cloud
    except ImportError:
        from py115.cloud import Cloud  # 尝试从子模块导入
    DEPS_AVAILABLE = True
    print("Uploader Nodes: All dependencies imported successfully.")
except ImportError as e:
    print(f"Custom Uploader Node: Critical Error - Could not import required libraries: {e}")
    traceback.print_exc()
    DEPS_AVAILABLE = False

# --- 2. Configuration Handling ---
# Define the path to the config files relative to this script's directory
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
MERGED_CONFIG_FILE_PATH = os.path.join(THIS_DIR, "uploader_configs.json") # 新增

def load_configs():
    """
    Loads configurations for all services from the merged config file.
    Returns a dictionary with service names as keys and their configs as values, or None if failed.
    """
    print(f"Uploader Nodes: Attempting to load merged config from {MERGED_CONFIG_FILE_PATH}")
    if not os.path.exists(MERGED_CONFIG_FILE_PATH):
        print(f"Uploader Nodes Error: Merged configuration file not found at {MERGED_CONFIG_FILE_PATH}")
        print("Please create 'uploader_configs.json' with 'aliyundrive' and 'pan115' sections.")
        return None

    try:
        with open(MERGED_CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
            full_config_data = json.load(f)
        
        aliyun_config = full_config_data.get("aliyundrive", {})
        pan115_config = full_config_data.get("pan115", {})

        # Basic validation for Aliyun
        if not aliyun_config.get("refresh_token"):
             print("Uploader Nodes Error: 'aliyundrive.refresh_token' is missing or empty in config file.")
             return None
        if not aliyun_config.get("folder_id"):
             print("Uploader Nodes Error: 'aliyundrive.folder_id' is missing or empty in config file.")
             return None

        # Basic validation for 115 (cookie is mandatory)
        if not pan115_config.get("cookie"):
             print("Uploader Nodes Error: 'pan115.cookie' is missing or empty in config file.")
             return None

        print("Uploader Nodes: Merged configuration loaded successfully.")
        return {
            "aliyundrive": {
                "refresh_token": aliyun_config["refresh_token"].strip(),
                "folder_id": aliyun_config["folder_id"].strip()
            },
            "pan115": {
                "cookie": pan115_config["cookie"].strip(),
                "target_cid": pan115_config.get("target_cid", "").strip() # Handle missing or empty
            }
        }
    except json.JSONDecodeError as e:
        print(f"Uploader Nodes Error: Failed to parse merged config file JSON: {e}")
        return None
    except Exception as e:
         print(f"Uploader Nodes Error: Unexpected error loading merged config: {e}")
         traceback.print_exc()
         return None

# --- 3. Node Class Definitions ---

# --- Existing Aliyun Node (Unchanged) ---
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

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    OUTPUT_NODE = True
    FUNCTION = "process_and_upload"
    CATEGORY = "image/upload"
    DESCRIPTION = "Uploads images to Aliyun Drive using settings from aliyundrive_config.json. Acts as a preview node."

    def process_and_upload(self, images, file_name_prefix):
        """
        Uploads the input images to Aliyun Drive.
        Does not return the images, just triggers the upload and enables preview.
        """
        print("Aliyun Drive Uploader Node: process_and_upload called.")
        
        if images is None:
            print("Aliyun Drive Uploader Node Warning: No images received on input.")
            return {"ui": {"images": []}} 
        
        try:
            image_count = len(images) if hasattr(images, '__len__') else (1 if images is not None else 0)
        except:
             image_count = 1 if images is not None else 0
             
        print(f"Aliyun Drive Uploader Node: Received {image_count} image(s).")

        if image_count == 0:
             print("Aliyun Drive Uploader Node: Image list is empty. Nothing to upload.")
             return {"ui": {"images": []}}

        configs = load_configs()
        if not configs:
            print("Aliyun Drive Uploader Node: Upload process aborted due to configuration error.")
            return {"ui": {"images": []}}
        config = configs.get("aliyundrive")
        if not config:
            print("Aliyun Drive Uploader Node: Aliyun Drive configuration section missing in merged config.")
            return {"ui": {"images": []}}

        refresh_token = config["refresh_token"]
        folder_id = config["folder_id"]

        ali = None
        if not DEPS_AVAILABLE:
             print("Aliyun Drive Uploader Node: Upload process aborted due to missing dependencies.")
             return {"ui": {"images": []}}

        try:
            print("Aliyun Drive Uploader Node: Initializing Aligo client...")
            ali = Aligo(refresh_token=refresh_token)
            print("Aliyun Drive Uploader Node: Aligo client initialized successfully.")
        except Exception as e:
            print(f"Aliyun Drive Uploader Node Error: Failed to initialize Aligo client: {e}")
            traceback.print_exc()
            return {"ui": {"images": []}}

        try:
            output_dir = folder_paths.get_output_directory()
            print(f"Aliyun Drive Uploader Node: Using ComfyUI output directory: {output_dir}")

            successful_uploads = 0
            from PIL import Image
            
            print("Aliyun Drive Uploader Node: Starting upload loop...")
            for i in range(image_count): 
                try:
                    print(f"Aliyun Drive Uploader Node: Processing image {i+1}/{image_count}...")
                    single_image_tensor = images[i] 
                    
                    image_np = 255. * single_image_tensor.cpu().numpy()
                    img = Image.fromarray(image_np.astype('uint8'), 'RGB')

                    filename = f"{file_name_prefix}{i:05}.png"
                    temp_file_path = os.path.join(output_dir, filename)
                    print(f"Aliyun Drive Uploader Node: Saving temporary image to {temp_file_path}")

                    img.save(temp_file_path, format='PNG')
                    print(f"Aliyun Drive Uploader Node: Temporary image saved.")

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
            
        preview_images = []
        if image_count > 0 and images is not None:
            try:
                first_image = images[0]
                preview_filename = f"{file_name_prefix}preview.png"
                preview_file_path = os.path.join(output_dir, preview_filename)
                
                image_np = 255. * first_image.cpu().numpy()
                img = Image.fromarray(image_np.astype('uint8'), 'RGB')
                img.save(preview_file_path, format='PNG')
                print(f"Aliyun Drive Uploader Node: Preview image saved for UI: {preview_filename}")

                preview_images.append({
                    "filename": preview_filename,
                    "type": "output",
                    "subfolder": ""
                })
            except Exception as preview_err:
                print(f"Aliyun Drive Uploader Node: Failed to generate preview: {preview_err}")
                traceback.print_exc()

        print("Aliyun Drive Uploader Node: Upload complete. Enabling preview.")
        return {
            "ui": {
                "images": preview_images
            }
        } 

# --- New 115 Node (MODIFIED) ---
class UploadTo115:
    """
    A ComfyUI node to upload an image to 115 Cloud using credentials from a config file.
    This node acts as an output node for preview but does not pass the image data forward.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", ),
                "file_name_prefix": ("STRING", {"default": "comfyui_output_115_", "multiline": False}),
            },
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    OUTPUT_NODE = True
    FUNCTION = "process_and_upload"
    CATEGORY = "image/upload"
    DESCRIPTION = "Uploads images to 115 Cloud using settings from uploader_configs.json. Acts as a preview node."

    def process_and_upload(self, images, file_name_prefix):
        """
        Uploads the input images to 115 Cloud.
        Does not return the images, just triggers the upload and enables preview.
        """
        print("115 Uploader Node: process_and_upload called.")
        
        if images is None:
            print("115 Uploader Node Warning: No images received on input.")
            return {"ui": {"images": []}} 
        
        try:
            image_count = len(images) if hasattr(images, '__len__') else (1 if images is not None else 0)
        except:
             image_count = 1 if images is not None else 0
             
        print(f"115 Uploader Node: Received {image_count} image(s).")

        if image_count == 0:
             print("115 Uploader Node: Image list is empty. Nothing to upload.")
             return {"ui": {"images": []}}

        configs = load_configs()
        if not configs:
            print("115 Uploader Node: Upload process aborted due to configuration error.")
            return {"ui": {"images": []}}
        config = configs.get("pan115")
        if not config:
            print("115 Uploader Node: 115 configuration section missing in merged config.")
            return {"ui": {"images": []}}

        cookie_str = config["cookie"]  # <-- 保持为字符串
        target_cid = config["target_cid"] # Can be None

        cloud_115 = None
        if not DEPS_AVAILABLE:
             print("115 Uploader Node: Upload process aborted due to missing dependencies.")
             return {"ui": {"images": []}}

        try:
            print("115 Uploader Node: Initializing py115 client...")
            cloud_115 = Cloud()  # <-- 1. 创建空实例
            print("115 Uploader Node: Attempting to log in...")

            # 2. 登录
            login_success = cloud_115.login(cookie_str)
            if not login_success:
                raise Exception("Login failed. Please check your cookie.")

            print("115 Uploader Node: Login successful.")
            
        except Exception as e:
            print(f"115 Uploader Node Error: Failed to initialize py115 client or login: {e}")
            traceback.print_exc()
            return {"ui": {"images": []}}

        try:
            output_dir = folder_paths.get_output_directory()
            print(f"115 Uploader Node: Using ComfyUI output directory: {output_dir}")

            successful_uploads = 0
            from PIL import Image
            
            print("115 Uploader Node: Starting upload loop...")
            for i in range(image_count): 
                try:
                    print(f"115 Uploader Node: Processing image {i+1}/{image_count}...")
                    single_image_tensor = images[i] 
                    
                    image_np = 255. * single_image_tensor.cpu().numpy()
                    img = Image.fromarray(image_np.astype('uint8'), 'RGB')

                    filename = f"{file_name_prefix}{i:05}.png"
                    temp_file_path = os.path.join(output_dir, filename)
                    print(f"115 Uploader Node: Saving temporary image to {temp_file_path}")

                    img.save(temp_file_path, format='PNG')
                    print(f"115 Uploader Node: Temporary image saved.")

                    print(f"115 Uploader Node: Uploading '{filename}' to folder CID '{target_cid if target_cid else 'Root'}'...")

                    # --- 上传文件 ---
                    # py115 0.1.1 中上传方法是 .put(local_path, remote_path=None, pid=None)
                    # 或者 .upload_file(local_path, pid=None)
                    # 我们使用 .put()，因为它更通用
                    upload_result = cloud_115.put(temp_file_path, pid=target_cid)

                    # 检查上传结果
                    if upload_result and isinstance(upload_result, dict) and upload_result.get('state', False):
                        print(f"115 Uploader Node: Successfully uploaded '{filename}'.")
                        successful_uploads += 1
                    else:
                        print(f"115 Uploader Node: Upload may have failed for '{filename}'. Result: {upload_result}")

                except Exception as img_err:
                    print(f"115 Uploader Node Error processing image {i+1}: {img_err}")
                    traceback.print_exc()
                finally:
                    try:
                        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                            os.remove(temp_file_path)
                            print(f"115 Uploader Node: Removed temporary file {temp_file_path}")
                    except OSError as remove_err:
                        print(f"115 Uploader Node: Warning - Could not remove temporary file {temp_file_path}: {remove_err}")

            print(f"115 Uploader Node: Upload process finished. {successful_uploads}/{image_count} images uploaded successfully.")

        except Exception as e:
            print(f"115 Uploader Node General Error during upload process: {e}")
            traceback.print_exc()
            
        preview_images = []
        if image_count > 0 and images is not None:
            try:
                first_image = images[0]
                preview_filename = f"{file_name_prefix}preview.png"
                preview_file_path = os.path.join(output_dir, preview_filename)
                
                image_np = 255. * first_image.cpu().numpy()
                img = Image.fromarray(image_np.astype('uint8'), 'RGB')
                img.save(preview_file_path, format='PNG')
                print(f"115 Uploader Node: Preview image saved for UI: {preview_filename}")

                preview_images.append({
                    "filename": preview_filename,
                    "type": "output",
                    "subfolder": ""
                })
            except Exception as preview_err:
                print(f"115 Uploader Node: Failed to generate preview: {preview_err}")
                traceback.print_exc()

        print("115 Uploader Node: Upload complete. Enabling preview.")
        return {
            "ui": {
                "images": preview_images
            }
        } 

# --- 4. Node Registration ---
# Assuming you have the original node in nodes_original.py
try:
    from .nodes_original import UploadToAliyunDrive
    ORIGINAL_NODE_AVAILABLE = True
except ImportError:
    print("Custom Uploader Node: Original node (nodes_original.py) not found or failed to import.")
    ORIGINAL_NODE_AVAILABLE = False

NODE_CLASS_MAPPINGS = {
    "SimpleUploadToAliyunDrive": SimpleUploadToAliyunDrive,
    "UploadTo115": UploadTo115 # Register the new node
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SimpleUploadToAliyunDrive": "Upload to Aliyun Drive (Config File - Preview)",
    "UploadTo115": "Upload to 115 Cloud (Config File - Preview)" # Display name for the new node
}

if ORIGINAL_NODE_AVAILABLE:
    NODE_CLASS_MAPPINGS["UploadToAliyunDrive"] = UploadToAliyunDrive
    NODE_DISPLAY_NAME_MAPPINGS["UploadToAliyunDrive"] = "Upload to Aliyun Drive (Manual)"
