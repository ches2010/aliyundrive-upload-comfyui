# ComfyUI 阿里云盘上传节点 (ComfyUI Aliyun Drive Uploader Node)

[English](./README.md) | **中文**

一个用于 [ComfyUI](https://github.com/comfyanonymous/ComfyUI) 的自定义节点，可将生成的图片自动上传到您的阿里云盘。

## 功能特性

*   直接从您的 ComfyUI 工作流中将图片上传到阿里云盘的指定文件夹。
*   支持批量图片上传。
*   与 ComfyUI Manager 无缝集成，便于安装。
*   自动安装所需的 Python 依赖项。

## 安装方法

### 方法一：使用 ComfyUI Manager (推荐)

1.  在 ComfyUI 界面中打开 ComfyUI Manager。
2.  搜索 "Aliyun Drive Uploader" 或导航到 "Install Custom Nodes" (安装自定义节点) 部分。
3.  找到此节点并点击 "Install" (安装)。
4.  如果提示，请重启 ComfyUI。节点应会自动安装其依赖项。

### 方法二：手动安装 (`git clone`)

1.  导航至您的 ComfyUI 自定义节点目录（通常位于 `ComfyUI/custom_nodes`）。
2.  克隆此仓库：
```
bash
    git clone https://github.com/your_username/comfyui_aliyundrive_uploader.git
```
3.  进入克隆的目录：
```
bash
cd comfyui_aliyundrive_uploader
```
4.  运行安装脚本以安装依赖项：
```
bash
# 请确保您使用的是 ComfyUI 所用的同一个 Python 环境
python install.py
```
或者，如果 ComfyUI 安装在特定环境中，请先激活该环境。
5.  重启 ComfyUI。该节点即可使用。

## 配置与设置

1.  获取您的阿里云盘凭证：
    *   `refresh_token`：这是用于与阿里云盘进行身份验证的长效令牌。您通常可以在 `aligo` 库的文档或阿里云盘的开发者资源中找到获取此令牌的说明。**请妥善保管此令牌！**
    *   `folder_id`：您希望图片上传到的阿里云盘上的文件夹 ID。您通常可以通过在阿里云盘网页版中启用开发者工具并检查文件夹属性来找到此 ID。
2.  在您的 ComfyUI 工作流中，添加 "Upload to Aliyun Drive" (上传到阿里云盘) 节点。
3.  将图片输出节点（如 `Save Image`）的输出连接到此节点的 `images` 输入。
4.  在节点属性中填入您获得的 `folder_id` 和 `refresh_token`。
5.  （可选）如果您希望上传的文件有不同的命名规则，可以修改 `file_name_prefix`。

## 使用方法

在工作流中配置好节点后，每当执行该节点时（例如，当您运行一次图像生成时），它将尝试将生成的图片上传到您指定的阿里云盘文件夹中。

## 依赖项

此节点依赖于以下 Python 包，这些包应该会自动安装：

*   `aligo`：用于与阿里云盘交互。
*   `requests`：`aligo` 使用的 HTTP 库。
*   `Pillow`：用于基本的图像处理（在 ComfyUI 环境中通常已存在）。

这些依赖项已在 `requirements.txt` 文件中列出。

## 示例工作流

在 `examples/` 文件夹中可以找到一个示例工作流 JSON 文件 (`workflow_example.json`)，用于演示如何使用该节点。
