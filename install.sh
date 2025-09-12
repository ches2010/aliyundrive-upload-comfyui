#!/bin/bash
echo "开始安装阿里云盘上传节点依赖..."

# 检查pip是否存在
if ! command -v pip &> /dev/null; then
    echo "未找到pip，请先安装Python并配置环境变量。"
    exit 1
fi

# 安装依赖
pip install -r requirements.txt

echo "依赖安装完成！"

# 提示复制节点目录
echo
echo "请将本仓库中的 'custom_nodes/ComfyUI_aliupload' 文件夹复制到你的ComfyUI根目录下的 'custom_nodes' 中。"
echo "例如：cp -r ComfyUI-AliyunDrive-Upload/custom_nodes/ComfyUI_aliupload ~/ComfyUI/custom_nodes/"
echo "重启ComfyUI即可使用节点。"
