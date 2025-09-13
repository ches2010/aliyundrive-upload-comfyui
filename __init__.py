"""
ComfyUI Aliyun Drive Uploader Node
A custom node for ComfyUI to upload generated images to Aliyun Drive.
"""

# This registers the node(s) with ComfyUI
from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# These will be available when the node is loaded
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
