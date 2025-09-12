import os
import io
import time
import requests
from PIL import Image as PILImage
import torch
import numpy as np
from nodes import Node
import folder_paths

class AliyunDriveOptimizedUploadNode(Node):
    def __init__(self):
        super().__init__()
        # 缓存token信息，避免重复刷新
        self.token_cache = {
            "access_token": "",
            "refresh_token": "",
            "expires_at": 0  # 过期时间戳（秒）
        }

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),  # 输入图片
                "refresh_token": ("STRING", {"default": ""}),  # 用户提供的32位refresh_token
                "folder_id": ("STRING", {"default": ""}),  # 目标文件夹ID
            },
            "optional": {
                "access_token": ("STRING", {"default": ""}),  # 用户提供的280位access_token（可选，会自动刷新）
                "file_prefix": ("STRING", {"default": "comfyui_"}),  # 文件名前缀
            }
        }

    RETURN_TYPES = ("STRING", "STRING")  # 返回文件ID和阿里云盘文件链接
    RETURN_NAMES = ("file_id", "file_url")
    FUNCTION = "upload_image"
    CATEGORY = "自定义节点/阿里云盘(优化版)"

    def _refresh_access_token(self, refresh_token):
        """用refresh_token刷新access_token"""
        resp = requests.post(
            "https://openapi.aliyundrive.com/oauth/access_token",
            json={
                "client_id": "25dzX3vbYqktVxyX",  # 阿里云盘默认个人应用client_id（通用）
                "client_secret": "c75875c386847175f5859e734b506a",  # 对应默认client_secret
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }
        )
        data = resp.json()
        if "access_token" not in data:
            raise Exception(f"刷新token失败：{data.get('message', '未知错误')}")
        
        # 更新缓存
        self.token_cache = {
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],  # 可能返回新的refresh_token，同步更新
            "expires_at": time.time() + data["expires_in"]
        }
        return data["access_token"]

    def _get_valid_access_token(self, refresh_token, access_token):
        """获取有效的access_token（优先用缓存，过期则刷新）"""
        # 若用户提供了access_token，先检查是否有效
        if access_token and not self.token_cache["access_token"]:
            self.token_cache["access_token"] = access_token
            # 简单假设access_token有效期为3600秒（实际以刷新结果为准）
            self.token_cache["expires_at"] = time.time() + 3600
            self.token_cache["refresh_token"] = refresh_token

        # 检查缓存是否有效
        now = time.time()
        if self.token_cache["access_token"] and self.token_cache["expires_at"] > now + 60:
            return self.token_cache["access_token"]
        
        # 缓存无效，用refresh_token刷新
        if not refresh_token:
            raise Exception("请输入refresh_token")
        return self._refresh_access_token(refresh_token)

    def upload_image(self, image, refresh_token, folder_id, access_token="", file_prefix="comfyui_"):
        # 校验必要参数
        if not folder_id:
            raise Exception("请输入folder_id")
        if not refresh_token:
            raise Exception("请输入refresh_token")

        # 获取有效access_token
        access_token = self._get_valid_access_token(refresh_token, access_token)

        # 处理图片：转换为PNG并保存到内存
        image_np = image.cpu().numpy()
        img = PILImage.fromarray((image_np[0] * 255).astype(np.uint8))
        img_buffer = io.BytesIO()
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        file_content = img_buffer.read()
        file_size = len(file_content)

        # 生成唯一文件名（前缀+时间戳）
        timestamp = time.strftime("%Y%m%d_%H%M%S_%f")
        file_name = f"{file_prefix}{timestamp}.png"

        # 1. 创建上传任务（指定目标folder_id）
        create_resp = requests.post(
            "https://openapi.aliyundrive.com/adrive/v3/file/create",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "name": file_name,
                "parent_file_id": folder_id,  # 直接使用用户提供的folder_id
                "size": file_size,
                "type": "file"
            }
        )
        create_data = create_resp.json()
        if "upload_url" not in create_data:
            raise Exception(f"创建上传任务失败：{create_data.get('message', '未知错误')}")

        # 2. 上传图片内容
        upload_resp = requests.put(create_data["upload_url"], data=file_content)
        if upload_resp.status_code != 200:
            raise Exception(f"文件上传失败：{upload_resp.text}")

        # 3. 生成文件访问链接（需要权限）
        file_id = create_data["file_id"]
        file_url = f"https://www.aliyundrive.com/s/{file_id}"  # 阿里云盘分享链接格式
        return (file_id, file_url)

# 注册节点
NODE_CLASS_MAPPINGS = {
    "AliyunDriveOptimizedUploadNode": AliyunDriveOptimizedUploadNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AliyunDriveOptimizedUploadNode": "阿里云盘上传(优化版)"
}
