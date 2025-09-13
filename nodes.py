import os
import sys
import subprocess
import folder_paths
import traceback

# Ensure dependencies are installed before importing them
try:
    import requests
    from aligo import Aligo
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
            # Initialize Aligo with refresh token
            ali = Aligo(refresh_token=refresh_token)
            
            # Get the output directory from ComfyUI's configuration
            output_dir = folder_paths.get_output_directory()
            
            # Iterate through the batch of images
            for i, image in enumerate(images):
                # Convert tensor to PIL Image
                i = 255. * image.cpu().numpy()
                from PIL import Image
                img = Image.fromarray(i.astype('uint8'), 'RGB')
                
                # Create a temporary file path
                filename = f"{file_name_prefix}{i:05}.png"
                temp_file_path = os.path.join(output_dir, filename)
                
                # Save the image locally first (Aligo upload_file usually needs a file path)
                img.save(temp_file_path, format='PNG')
                
                # Upload the file to Aliyun Drive
                uploaded_file = ali.upload_file(file_path=temp_file_path, parent_file_id=folder_id)
                
                print(f"Aliyun Drive Uploader: Uploaded '{filename}' to folder ID '{folder_id}'. File ID: {uploaded_file.file_id}")
                
                # Optional: Remove the temporary file after upload
                # os.remove(temp_file_path)
                
        except Exception as e:
            print(f"Aliyun Drive Uploader Node Error: {e}")
            traceback.print_exc()
            # Depending on your needs, you might want to re-raise the exception
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
