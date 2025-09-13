@echo off
echo 开始安装阿里云盘上传节点...

:: 检查是否在 ComfyUI 的 custom_nodes 目录下（或提示用户输入 ComfyUI 路径）
if not exist "../../main.py" (
    echo 未检测到 ComfyUI 环境，请将此仓库放在 ComfyUI 的 custom_nodes 目录下，或手动运行：
    echo pip install -r requirements.txt
    pause
    exit /b 1
)

:: 安装依赖
echo 安装依赖库...
pip install -r requirements.txt

:: 提示安装完成
echo 安装成功！请重启 ComfyUI 以加载节点。
pause
