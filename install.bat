@echo off
echo 开始安装阿里云盘上传节点依赖...

# 检查是否安装了pip
where pip >nul 2>nul
if %errorlevel% neq 0 (
    echo 未找到pip，请先安装Python并配置环境变量。
    pause
    exit /b 1
)

# 安装依赖
pip install -r requirements.txt

echo 依赖安装完成！

# 提示用户将节点目录复制到ComfyUI的custom_nodes
echo.
echo 请将本仓库中的 "custom_nodes/aliyun_drive_upload" 文件夹复制到你的ComfyUI根目录下的 "custom_nodes" 中。
echo 例如：将 "ComfyUI-AliyunDrive-Upload/custom_nodes/aliyun_drive_upload" 复制到 "ComfyUI/custom_nodes/"
echo 重启ComfyUI即可使用节点。

pause
