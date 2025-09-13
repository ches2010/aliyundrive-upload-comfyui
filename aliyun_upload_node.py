import os
import io
from PIL import Image
from aligo import AliyunDrive  # 假设的SDK，需根据实际调整
import torch
from nodes import Node  # ComfyUI节点基类

# 阿里云盘上传类
class AliyunDriveUploader:
    def __init__(self, refresh_token, folder_id):
        self.drive = AliyunDrive(refresh_token=refresh_token)
        self.folder_id = folder_id  # 目标文件夹ID

    def upload_image(self, image_data, filename):
        """上传图片到阿里云盘指定文件夹"""
        # 将图片数据（torch tensor）转换为PIL Image
        if isinstance(image_data, torch.Tensor):
            image_data = image_data.cpu().numpy()
            image = Image.fromarray((image_data * 255).astype('uint8'))
        else:
            image = Image.open(io.BytesIO(image_data))
        
        # 保存为临时文件（或直接用字节流上传，取决于SDK支持）
        temp_path = f"temp_{filename}"
        image.save(temp_path)
        
        # 上传到阿里云盘
        try:
            self.drive.upload_file(
                file_path=temp_path,
                parent_file_id=self.folder_id,
                new_file_name=filename
            )
            print(f"上传成功: {filename}")
        except Exception as e:
            print(f"上传失败: {str(e)}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

# ComfyUI节点定义
class AliyunDriveUploadNode(Node):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),  # 接收ComfyUI生成的图片
                "refresh_token": ("STRING", {"default": ""}),  # 用户输入refresh_token
                "folder_id": ("STRING", {"default": ""}),  # 用户输入目标文件夹ID
                "filename": ("STRING", {"default": "output.png"}),  # 上传的文件名
            }
        }

    RETURN_TYPES = ()  # 无输出（仅上传）
    FUNCTION = "upload"
    CATEGORY = "Custom/Upload"  # 节点分类

    def upload(self, image, refresh_token, folder_id, filename):
        if not refresh_token or not folder_id:
            raise ValueError("请填写refresh_token和folder_id")
        
        # 初始化上传器
        uploader = AliyunDriveUploader(refresh_token, folder_id)
        # 处理图片并上传（假设image是单张，批量可循环）
        uploader.upload_image(image[0], filename)  # image通常是(batch, h, w, c)格式
        return ()
