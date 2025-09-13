# ComfyUI Aliyun Drive Uploader Node

A custom node for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) that automatically uploads generated images to your Aliyun Drive.

## Features

*   Uploads images directly from your ComfyUI workflow to a specified folder on Aliyun Drive.
*   Supports batch image uploads.
*   Integrates seamlessly with ComfyUI Manager for easy installation.
*   Automatically installs required Python dependencies.

## Installation

### Method 1: Using ComfyUI Manager (Recommended)

1.  Open ComfyUI Manager within your ComfyUI interface.
2.  Search for "Aliyun Drive Uploader" or navigate to the "Install Custom Nodes" section.
3.  Find this node and click "Install".
4.  Restart ComfyUI if prompted. The node should automatically install its dependencies.

### Method 2: Manual Installation (`git clone`)

1.  Navigate to your ComfyUI custom nodes directory (usually `ComfyUI/custom_nodes`).
2.  Clone this repository:
```
bash
git clone https://github.com/your_username/comfyui_aliyundrive_uploader.git
```
3.  Navigate into the cloned directory:
```
bash
cd comfyui_aliyundrive_uploader
```
4.  Run the installation script to install dependencies:
```
bash
# Make sure you are using the same Python environment that ComfyUI uses
python install.py
```
Or, if ComfyUI is installed in a specific environment, activate it first.
5.  Restart ComfyUI. The node should be available.

## Setup
 Obtain your Aliyun Drive credentials:
  `refresh_token`: This is the long-lived token used to authenticate with Aliyun Drive. You can usually find instructions on how to get this in the `aligo` library documentation or Aliyun Drive's developer resources. Keep this secure!
  `folder_id`: The ID of the folder on your Aliyun Drive where you want the images uploaded. You can usually find this by enabling developer tools in the Aliyun Drive web interface and inspecting the folder properties.
 In your ComfyUI workflow, add the "Upload to Aliyun Drive" node.
 Connect the image output from a node (like `Save Image`) to the images input of this node.
 Fill in the folder_id and `refresh_token` fields in the node's properties with your obtained values.
 Optionally, change the `file_name_prefix` if you want a different naming scheme for uploaded files.
## Usage
Once configured in your workflow, whenever the node is executed (e.g., when you run a generation), it will attempt to upload the generated image(s) to your specified Aliyun Drive folder.

## Dependencies
This node relies on the following Python packages, which should be automatically installed:

`aligo`: For interacting with Aliyun Drive.
`requests`: HTTP library used by aligo.
`Pillow`: For basic image handling (often already present in ComfyUI environments).
These are listed in `requirements.txt`.

Example Workflow
An example workflow JSON file (workflow_example.json) can be found in the examples/ folder to demonstrate how to use the node.
