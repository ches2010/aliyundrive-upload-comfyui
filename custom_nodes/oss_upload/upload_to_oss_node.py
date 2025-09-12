import os
import io
import base64
import numpy as np
from PIL import Image
import oss2  # 阿里云OSS SDK
import torch

# 导入ComfyUI必要的模块
from nodes import Node
import folder_paths

class UploadToOSSNode(Node):
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # 阿里云OSS配置（实际使用时建议通过环境变量或配置文件传入，避免硬编码）
                "access_key_id": ("STRING", {"default": "你的AccessKeyId"}),
                "access_key_secret": ("STRING", {"default": "你的AccessKeySecret"}),
                "endpoint": ("STRING", {"default": "oss-cn-beijing.aliyuncs.com"}),  # OSS地域节点
                "bucket_name": ("STRING", {"default": "你的Bucket名称"}),
                "object_prefix": ("STRING", {"default": "comfyui-output/"}),  # 网盘存储路径前缀
                # 输入图片（ComfyUI生成的图片通常是torch.Tensor格式）
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("STRING",)  # 返回上传后的图片URL
    RETURN_NAMES = ("image_url",)
    FUNCTION = "upload_image"
    CATEGORY = "自定义节点/网盘上传"

    def upload_image(self, access_key_id, access_key_secret, endpoint, bucket_name, object_prefix, image):
        try:
            # 1. 处理输入图片：将torch.Tensor转换为PIL Image
            # ComfyUI的IMAGE类型是 (batch_size, height, width, channels) 的tensor，取值范围[0,1]
            image_np = image.cpu().numpy()
            # 取batch中的第一张图，转换为0-255的uint8
            img = Image.fromarray((image_np[0] * 255).astype(np.uint8))

            # 2. 将图片存入内存缓冲区（避免本地临时文件）
            img_buffer = io.BytesIO()
            img.save(img_buffer, format="PNG")  # 保存为PNG格式
            img_buffer.seek(0)  # 回到缓冲区起始位置

            # 3. 上传到阿里云OSS
            # 初始化OSS客户端
            auth = oss2.Auth(access_key_id, access_key_secret)
            bucket = oss2.Bucket(auth, endpoint, bucket_name)

            # 生成唯一文件名（例如：comfyui-output/20231001_123456.png）
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            object_name = f"{object_prefix}{timestamp}.png"

            # 上传文件
            result = bucket.put_object(object_name, img_buffer)
            if result.status == 200:
                # 生成可访问的URL（需确保Bucket设置了公共读或合适的访问权限）
                image_url = f"https://{bucket_name}.{endpoint}/{object_name}"
                return (image_url,)
            else:
                raise Exception(f"上传失败，状态码：{result.status}")

        except Exception as e:
            raise Exception(f"上传过程出错：{str(e)}")

# 注册节点
NODE_CLASS_MAPPINGS = {
    "UploadToOSSNode": UploadToOSSNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "UploadToOSSNode": "上传图片到阿里云OSS"
}
