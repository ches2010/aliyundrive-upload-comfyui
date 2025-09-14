import os
import sys
import subprocess
import folder_paths
import traceback

# Ensure dependencies are installed before importing them
try:
    import requests
    from aligo import Aligo
    # Import specific exceptions if available (check aligo docs)
    # from aligo.core import *
except ImportError:
    # If running inside ComfyUI, try to install dependencies silently
    # This is a fallback, primary installation should happen via install.py or requirements.txt
    print("Aliyun Drive Uploader Node: Required packages not found. Attempting to install...")
    try:
        subprocess.check_call([sys.executable, '-s', '-m', 'pip', 'install', 'aligo', 'requests'])
        import requests
        from aligo import Aligo
        print("Aliyun Drive Uploader Node: Dependencies installed successfully.")
    except Exception as e:
        print(f"Aliyun Drive Uploader Node: Failed to install dependencies: {e}")
        raise e

# Define the node class
class UploadToAliyunDrive:
    """
    A ComfyUI node to upload an image to Aliyun Drive.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", ),
                "folder_id": ("STRING", {"default": "your_folder_id_here", "multiline": False}),
                "refresh_token": ("STRING", {"default": "your_refresh_token_here", "multiline": False}),
                "file_name_prefix": ("STRING", {"default": "comfyui_output_", "multiline": False}),
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "upload"
    CATEGORY = "image/upload"
    OUTPUT_NODE = True # Indicates this node has output actions

    def upload(self, images, folder_id, refresh_token, file_name_prefix):
        """
        Uploads the input images to Aliyun Drive.
        """
        try:
            print(f"Aliyun Drive Uploader: Attempting to initialize Aligo with provided refresh_token...")
            # Initialize Aligo with refresh token
            ali = Aligo(refresh_token=refresh_token)
            print(f"Aliyun Drive Uploader: Aligo initialized successfully.")
            
            # --- Optional: Verify folder exists (requires listing capability) ---
            # This is a more advanced check and might require pagination for large drives.
            # Uncomment and adapt if needed.
            # try:
            #     folder_info = ali.get_file(file_id=folder_id)
            #     if not folder_info or not getattr(folder_info, 'type', None) == 'folder':
            #          print(f"Aliyun Drive Uploader Warning: folder_id '{folder_id}' might not be a valid folder or could not be retrieved for verification.")
            #     else:
            #          print(f"Aliyun Drive Uploader: Verified folder name: {getattr(folder_info, 'name', 'Unknown')}")
            # except Exception as verify_err:
            #     print(f"Aliyun Drive Uploader: Warning - Could not verify folder existence: {verify_err}")
            # --- End Optional Check ---

            # Get the output directory from ComfyUI's configuration
            output_dir = folder_paths.get_output_directory()
            print(f"Aliyun Drive Uploader: Using ComfyUI output directory: {output_dir}")
            
            # Iterate through the batch of images
            for i, image in enumerate(images):
                # Convert tensor to numpy array
                # Use a different variable name, e.g., 'image_np'
                image_np = 255. * image.cpu().numpy()
                from PIL import Image
                # Create PIL Image from the numpy array
                img = Image.fromarray(image_np.astype('uint8'), 'RGB')
                
                # Create a temporary file path using the loop index 'i'
                filename = f"{file_name_prefix}{i:05}.png"
                temp_file_path = os.path.join(output_dir, filename)
                print(f"Aliyun Drive Uploader: Saving temporary image to {temp_file_path}")
                
                # Save the image locally first (Aligo upload_file usually needs a file path)
                img.save(temp_file_path, format='PNG')
                
                # Upload the file to Aliyun Drive
                print(f"Aliyun Drive Uploader: Uploading '{filename}' to folder ID '{folder_id}'...")
                try:
                    # Wrap the upload call in its own try-except to isolate potential aligo issues
                    uploaded_file = ali.upload_file(file_path=temp_file_path, parent_file_id=folder_id)
                    
                    if uploaded_file and hasattr(uploaded_file, 'file_id'):
                        print(f"Aliyun Drive Uploader: Successfully uploaded '{filename}'. File ID: {uploaded_file.file_id}")
                    else:
                        # Handle case where upload_file might return None or unexpected object without raising
                        print(f"Aliyun Drive Uploader: Warning - Upload call for '{filename}' returned unexpected result or None.")
                        
                except AttributeError as attr_err:
                    # Specifically catch the 'Null' object error from aligo
                    print(f"Aliyun Drive Uploader: AttributeError during upload (likely from aligo library): {attr_err}")
                    print(f"Aliyun Drive Uploader: This often indicates an API error (like 404 for folder_id) was not handled correctly by aligo.")
                    # Re-raise or handle as needed. Raising might stop the whole workflow.
                    # raise attr_err # Re-raise if you want the node to fail visibly
                    # Or just log and continue with other images
                    print(f"Aliyun Drive Uploader: Skipping upload for '{filename}' due to library error.")
                    
                except requests.exceptions.HTTPError as http_err:
                    # Catch HTTP errors returned by the API (like the 404 we saw)
                    print(f"Aliyun Drive Uploader: HTTP error during upload for '{filename}': {http_err}")
                    print(f"Aliyun Drive Uploader: Response content: {getattr(http_err.response, 'text', 'N/A')}")
                    # Re-raise or handle
                    # raise http_err
                    print(f"Aliyun Drive Uploader: Skipping upload for '{filename}' due to HTTP error.")
                    
                except Exception as upload_err:
                    # Catch any other exceptions during the upload process
                    print(f"Aliyun Drive Uploader: Unexpected error during upload for '{filename}': {upload_err}")
                    traceback.print_exc()
                    # Re-raise or handle
                    # raise upload_err
                    print(f"Aliyun Drive Uploader: Skipping upload for '{filename}' due to unexpected error.")

                # Optional: Remove the temporary file after upload attempt (success or failure)
                # Consider if you want to keep files locally if upload fails
                # try:
                #     os.remove(temp_file_path)
                #     print(f"Aliyun Drive Uploader: Removed temporary file {temp_file_path}")
                # except OSError as remove_err:
                #     print(f"Aliyun Drive Uploader: Warning - Could not remove temporary file {temp_file_path}: {remove_err}")

        except Exception as e:
            print(f"Aliyun Drive Uploader Node General Error: {e}")
            traceback.print_exc()
            # Depending on your needs, you might want to re-raise the exception
            # to halt the workflow or make the node show an error state in ComfyUI
            # raise e 

        # This node doesn't return any data to other nodes, it just performs an action
        return ()

# A dictionary that contains all nodes you want to export with their names
NODE_CLASS_MAPPINGS = {
    "UploadToAliyunDrive": UploadToAliyunDrive
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "UploadToAliyunDrive": "Upload to Aliyun Drive"
}
