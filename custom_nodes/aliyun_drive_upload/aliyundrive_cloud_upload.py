import os
import io
import time
import json
import socket
import threading
import requests
from flask import Flask, request, redirect
import qrcode
from PIL import Image as PILImage
import torch
import numpy as np
from nodes import Node
import folder_paths

# 全局变量存储授权信息
auth_info = {
    "access_token": "",
    "refresh_token": "",
    "expires_at": 0
}
app = Flask(__name__)
server_thread = None
is_server_running = False
auth_code = None  # 接收OAuth授权码


# 阿里云盘应用配置（替换为你的信息）
CLIENT_ID = "你的client_id"
CLIENT_SECRET = "你的client_secret"
# 回调地址必须与开放平台配置一致（使用服务器公网IP/域名）
REDIRECT_URI = "http://你的公网IP:8088/callback"  # 例如：http://1.2.3.4:8088/callback


# Flask服务：处理授权流程
@app.route('/')
def index():
    # 生成阿里云盘授权URL（引导用户登录授权）
    auth_url = (
        f"https://openapi.aliyundrive.com/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=user:base,file:all:read,file:all:write"
    )
    return redirect(auth_url)

@app.route('/callback')
def callback():
    global auth_code
    # 接收阿里云盘回调的授权码
    auth_code = request.args.get('code')
    return "授权成功，请关闭页面"


def run_auth_server():
    global is_server_running
    is_server_running = True
    # 云服务器上启动服务，绑定0.0.0.0允许公网访问
    app.run(host='0.0.0.0', port=8088, debug=False, use_reloader=False)
    is_server_running = False


class AliyunDriveCloudUploadNode(Node):
    def __init__(self):
        super().__init__()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),  # 输入图片
                "refresh_token": ("STRING", {"default": ""}),  # 手动输入refresh_token（推荐复用）
                "target_folder": ("STRING", {"default": "ComfyUI云输出"}),  # 阿里云盘目标文件夹
                "start_auth": ("BOOLEAN", {"default": False}),  # 触发授权
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("file_id",)
    FUNCTION = "upload_to_drive"
    CATEGORY = "自定义节点/阿里云盘(云服务器)"

    def get_access_token(self, refresh_token):
        """获取或刷新access_token"""
        global auth_info
        if refresh_token:
            auth_info["refresh_token"] = refresh_token
        
        # 检查token有效性
        now = time.time()
        if auth_info["access_token"] and auth_info["expires_at"] > now + 60:
            return auth_info["access_token"]
        
        if not auth_info["refresh_token"]:
            raise Exception("请先授权或输入refresh_token")
        
        # 刷新token
        resp = requests.post(
            "https://openapi.aliyundrive.com/oauth/access_token",
            json={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "grant_type": "refresh_token",
                "refresh_token": auth_info["refresh_token"]
            }
        )
        data = resp.json()
        if "access_token" not in data:
            raise Exception(f"刷新token失败：{data}")
        
        auth_info.update({
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "expires_at": now + data["expires_in"]
        })
        return data["access_token"]

    def get_folder_id(self, access_token, folder_name):
        """获取或创建目标文件夹"""
        resp = requests.post(
            "https://openapi.aliyundrive.com/adrive/v3/file/list",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"parent_file_id": "root", "fields": "file_id,name", "limit": 100}
        )
        for item in resp.json().get("items", []):
            if item["name"] == folder_name:
                return item["file_id"]
        
        # 创建文件夹
        resp = requests.post(
            "https://openapi.aliyundrive.com/adrive/v3/file/create",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "name": folder_name,
                "parent_file_id": "root",
                "type": "folder"
            }
        )
        return resp.json()["file_id"]

    def upload_image(self, access_token, folder_id, image):
        """上传图片到阿里云盘"""
        # 处理图片
        image_np = image.cpu().numpy()
        img = PILImage.fromarray((image_np[0] * 255).astype(np.uint8))
        img_buffer = io.BytesIO()
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        file_content = img_buffer.read()

        # 生成唯一文件名
        timestamp = time.strftime("%Y%m%d_%H%M%S_%f")
        file_name = f"comfyui_cloud_{timestamp}.png"

        # 1. 创建上传任务
        create_resp = requests.post(
            "https://openapi.aliyundrive.com/adrive/v3/file/create",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "name": file_name,
                "parent_file_id": folder_id,
                "size": len(file_content),
                "type": "file"
            }
        )
        upload_url = create_resp.json()["upload_url"]
        file_id = create_resp.json()["file_id"]

        # 2. 上传文件内容
        upload_resp = requests.put(upload_url, data=file_content)
        if upload_resp.status_code != 200:
            raise Exception(f"上传失败：{upload_resp.text}")
        
        return file_id

    def upload_to_drive(self, image, refresh_token, target_folder, start_auth):
        global server_thread, auth_code, auth_info

        # 处理授权（仅首次需要）
        if start_auth:
            auth_code = None
            auth_info = {"access_token": "", "refresh_token": "", "expires_at": 0}
            
            # 启动公网可访问的授权服务
            if not is_server_running and server_thread is None:
                server_thread = threading.Thread(target=run_auth_server, daemon=True)
                server_thread.start()
                time.sleep(2)  # 等待服务启动

            # 生成包含公网地址的二维码（手机扫码后通过公网访问服务器）
            auth_url = REDIRECT_URI.replace("/callback", "")  # 去掉回调路径，得到基础地址
            qr = qrcode.make(auth_url)
            qr_path = os.path.join(folder_paths.output_directory, "aliyundrive_cloud_auth.png")
            qr.save(qr_path)
            print(f"请扫描二维码授权（公网地址）：{qr_path}")
            print(f"或手动访问：{auth_url}")

            # 等待授权完成（超时5分钟，公网可能较慢）
            timeout = 300
            start_time = time.time()
            while not auth_code and (time.time() - start_time) < timeout:
                time.sleep(1)
            
            if not auth_code:
                raise Exception("授权超时，请检查服务器端口是否开放")

            # 使用授权码获取token
            resp = requests.post(
                "https://openapi.aliyundrive.com/oauth/access_token",
                json={
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "grant_type": "authorization_code",
                    "code": auth_code,
                    "redirect_uri": REDIRECT_URI
                }
            )
            data = resp.json()
            if "access_token" not in data:
                raise Exception(f"获取token失败：{data}")
            
            auth_info.update({
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
                "expires_at": time.time() + data["expires_in"]
            })
            print("授权成功，建议保存refresh_token复用：", data["refresh_token"])

        # 执行上传
        access_token = self.get_access_token(refresh_token)
        folder_id = self.get_folder_id(access_token, target_folder)
        file_id = self.upload_image(access_token, folder_id, image)
        return (file_id,)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "AliyunDriveCloudUploadNode": AliyunDriveCloudUploadNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AliyunDriveCloudUploadNode": "阿里云盘上传(云服务器)"
}
