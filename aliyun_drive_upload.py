import os
import requests
from aliyundrive_openapi import AliyunDriveOpenAPI
from comfyui import ComfyNode, Image

class AliyunDriveUploadNode(ComfyNode):
    def __init__(self):
        super().__init__()
        self.FOLDER_ID = 'your_folder_id'
        self.REFRESH_TOKEN = 'your_refresh_token'
        self.ACCESS_TOKEN = 'your_access_token'

    @staticmethod
    def name():
        return "Aliyun Drive Upload"

    @staticmethod
    def category():
        return "Image"

    @staticmethod
    def inputs():
        return {
            "image": ("IMAGE",),
        }

    @staticmethod
    def outputs():
        return {}

    def run(self, image: Image):
        # Save the image to a temporary file
        temp_file_path = "temp_image.png"
        image.save(temp_file_path)

        # Initialize Aliyun Drive API
        api = AliyunDriveOpenAPI()
        api.refresh_token = self.REFRESH_TOKEN
        api.access_token = self.ACCESS_TOKEN

        # Upload the image to Aliyun Drive
        with open(temp_file_path, 'rb') as f:
            response = api.upload_file(f, self.FOLDER_ID, 'uploaded_image.png')

        if response.status_code == 200:
            print("Image uploaded successfully to Aliyun Drive")
        else:
            print(f"Failed to upload image: {response.text}")

        # Clean up the temporary file
        os.remove(temp_file_path)

# Register the node
ComfyNode.register_node(AliyunDriveUploadNode)
