#!/bin/bash
echo "开始安装阿里云盘上传节点..."

# 检查pip是否存在
if ! command -v pip &> /dev/null; then
    echo "未找到pip，请先安装Python并配置环境变量。"
    exit 1
fi

# 检查是否在 ComfyUI 的 custom_nodes 目录下
if [ ! -f "../../main.py" ]; then
    echo "未检测到 ComfyUI 环境，请将此仓库放在 ComfyUI 的 custom_nodes 目录下，或手动运行："
    echo "pip install -r requirements.txt"
    exit 1
fi

# 安装依赖
echo "安装依赖库..."
pip install -r requirements.txt

# 提示安装完成
echo "安装成功！请重启 ComfyUI 以加载节点。"

# 提示复制节点目录
echo
echo "请将本仓库中的 'comfyui_aliyundrive_uploader' 文件夹复制到你的ComfyUI根目录下的 'custom_nodes' 中。"
echo "例如：cp -r comfyui_aliyundrive_uploader ~/ComfyUI/custom_nodes/"
echo "重启ComfyUI即可使用节点。"
