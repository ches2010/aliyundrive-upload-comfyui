# ComfyUI - 阿里云盘上传节点

将ComfyUI生成的图片自动上传到阿里云盘的自定义节点。通过本节点，用户能够方便快捷地将生成的图片存储到阿里云盘，便于后续查看与管理。

**中文** | [English](https://github.com/ches2010/comfyui_aliyundrive_uploader/blob/main/README_en.md) | [token教程](https://github.com/ches2010/comfyui_aliyundrive_uploader/blob/main/token.md)

---
## 更新历史
**v1.1.0**

1.增加新节点，只需将`folder_id`和`refresh_token`保存到`aliyundrive_config.json`，运行时可直接调用，无需在节点上输入。

2.新节点增加预览功能。


详细更新历史详见[更新历史](https://github.com/ches2010/comfyui_aliyundrive_uploader/blob/main/history.md)

---
## 安装说明
### 使用ComfyUI管理器（推荐）
1. **打开ComfyUI**：确保ComfyUI已成功启动并运行。
2. **进入管理器面板**：在ComfyUI界面中，通常可在侧边栏找到`Manager`面板。
3. **安装自定义节点**：点击`Install Custom Node`，然后选择`Install from URL`。
4. **输入仓库地址**：输入本节点的仓库地址`https://github.com/ches2010/comfyui_aliyundrive_uploader.git`，并点击安装按钮。ComfyUI管理器将自动完成以下操作：
    - 从GitHub克隆仓库到ComfyUI的`custom_nodes`目录。
    - 识别`requirements.txt`中的依赖，并自动安装所需的Python库。
5. **重启ComfyUI**：安装完成后，按照提示重启ComfyUI。重启后，即可在节点面板中找到并使用本节点。

### 手动安装 (`git clone`)

1.  导航至您的 ComfyUI 自定义节点目录（通常位于 `ComfyUI/custom_nodes`）。
2.  克隆此仓库：
```bash
    git clone https://github.com/your_username/comfyui_aliyundrive_uploader.git
```
3.  进入克隆的目录：
```bash
cd comfyui_aliyundrive_uploader
```
4.  运行安装脚本以安装依赖项：
```bash
# 请确保您使用的是 ComfyUI 所用的同一个 Python 环境
python install.py
```
或者，如果 ComfyUI 安装在特定环境中，请先激活该环境。
5.  重启 ComfyUI。该节点即可使用。

## 使用方法
1. **准备参数**：在使用本节点前，您需要准备阿里云盘的`folder_id`、`refresh_token`。
    - `folder_id`获取方式：在阿里云盘网页端打开目标文件夹，地址栏URL格式为`https://www.aliyundrive.com/s/xxxxxx`，其中`xxxxxx`即为`folder_id`。
    - `refresh_token`获取方式：可通过阿里云盘开放平台工具或第三方工具获取，有效期通常较长（30天以上），若失效需重新获取。
    - （可选）如果您希望上传的文件有不同的命名规则，可以修改 `file_name_prefix`。
2. **配置节点**：
   节点1：在ComfyUI工作流中添加本节点，将生成图片的节点（如`KSampler`等）的输出连接到本节点的`image`输入。同时，在本节点参数设置中：
    - `refresh_token`：填入获取到的`refresh_token`。
    - `folder_id`：填入目标文件夹的`folder_id`。
    - （可选）`file_prefix`：可自定义文件名前缀，方便对上传的图片进行归类。
    节点2：打开`comfyui/custom_nodes/comfyui_aliyundrive_uploader`目录下的`aliyun_drive_config.json`（windows系统可用记事本打开），将里面的`your_actual_refresh_token_here`和`your_actual_folder_id_here`分别换成你的`refresh_token`和`folder_id`
```jasn
{
    "refresh_token": "your_actual_refresh_token_here", #将your_actual_refresh_token_here换成你的refresh_token
    "folder_id": "your_actual_folder_id_here"   #将your_actual_folder_id_here换成你的folder_id
}
```
使用节点2时，系统将直接调用你的`refresh_token`和`folder_id`。
  
3. **运行工作流**：点击“Queue Prompt”运行工作流，节点将自动上传图片到指定的阿里云盘文件夹。
如果是第一次在你的机器上运行，后台将显示登录二维码，需使用阿里云盘手机app扫描登录后使用。

![扫描二维码示意图](https://github.com/ches2010/comfyui_aliyundrive_uploader/blob/main/aliyun/sacn.png)

## 获取 `folder_id`、`refresh_token` 和 `access_token` 的教程

### 获取 `folder_id`
1. **登录阿里云盘网页端**：使用您的阿里云盘账号登录[阿里云盘网页版](https://www.aliyundrive.com/)。
2. **导航到目标文件夹**：在阿里云盘网页端找到您希望上传图片的目标文件夹，并点击打开它。
3. **复制 `folder_id`**：此时，浏览器地址栏的URL应该类似于`https://www.aliyundrive.com/s/xxxxxx`，其中`xxxxxx`就是您需要的`folder_id`。请复制该字符串，后续将用于配置节点。

### 获取 `refresh_token` 和 `access_token`

#### 通过阿里云盘开放平台（需要开发者权限）
1. **注册成为开发者**：访问[阿里云盘开放平台](https://www.aliyundrive.com/developers/documents)，使用您的阿里云账号注册成为开发者。
2. **创建应用**：在开放平台控制台中，点击“创建应用”。填写应用相关信息，如应用名称、应用描述等。
3. **获取 `client_id` 和 `client_secret`**：应用创建成功后，在应用详情页面中可以找到`client_id`和`client_secret`，这两个信息在后续获取`refresh_token`和`access_token`时会用到。
4. **获取授权码（`code`）**：构造以下URL并在浏览器中打开：
```
https://openapi.aliyundrive.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=YOUR_REDIRECT_URI&scope=user:base,file:all:read,file:all:write
```
将`YOUR_CLIENT_ID`替换为您在第3步获取的`client_id`，`YOUR_REDIRECT_URI`替换为您在开放平台配置的回调地址（例如`http://localhost:8088/callback`）。用户登录阿里云盘账号并授权后，浏览器将重定向到回调地址，此时URL中会包含一个`code`参数，复制该参数的值。
5. **获取 `access_token` 和 `refresh_token`**：使用以下`curl`命令（或在代码中使用HTTP请求库）获取`access_token`和`refresh_token`：
```bash
curl -X POST \
  'https://openapi.aliyundrive.com/oauth/access_token' \
  -H 'Content-Type: application/json' \
  -d '{
        "client_id": "YOUR_CLIENT_ID",
        "client_secret": "YOUR_CLIENT_SECRET",
        "grant_type": "authorization_code",
        "code": "YOUR_CODE",
        "redirect_uri": "YOUR_REDIRECT_URI"
      }'
```
将`YOUR_CLIENT_ID`、`YOUR_CLIENT_SECRET`、`YOUR_CODE`和`YOUR_REDIRECT_URI`替换为实际的值。命令执行成功后，返回的JSON数据中将包含`access_token`和`refresh_token`。

#### 通过第三方工具（以 aliyundrive - webdav 为例，此方法可能存在风险，使用需谨慎）
1. **安装 `aliyundrive - webdav`**：在命令行中运行`pip install aliyundrive - webdav`。
2. **登录并获取 `refresh_token`**：运行`aliyundrive - webdav login`，按照提示在浏览器中完成登录流程。登录成功后，工具会在终端输出`refresh_token`。此时虽然未直接获取`access_token`，但节点在需要时会自动使用`refresh_token`刷新获取`access_token`。

#### 通过本仓库记录的教程获取
[token教程](https://github.com/ches2010/comfyui_aliyundrive_uploader/blob/main/token.md)

## 依赖项

此节点依赖于以下 Python 包，这些包应该会自动安装：

*   `aligo`：用于与阿里云盘交互。
*   `requests`：`aligo` 使用的 HTTP 库。
*   `Pillow`：用于基本的图像处理（在 ComfyUI 环境中通常已存在）。

这些依赖项已在 `requirements.txt` 文件中列出。

## 示例工作流

在 `examples/` 文件夹中可以找到一个示例工作流 JSON 文件 (`workflow_example.json`)，用于演示如何使用该节点。


## 注意事项
1. **依赖安装问题**：如果在安装依赖时遇到问题，请确保您的Python环境配置正确，且`pip`能够正常工作。若手动安装依赖，可尝试使用管理员权限运行安装命令。
2. **权限与配置**：确保提供的`refresh_token`和`folder_id`正确无误，否则可能导致上传失败。同时，若阿里云盘权限发生变化（如文件夹权限更改），可能影响上传功能。
3. **更新说明**：若节点有更新，使用ComfyUI管理器的用户可通过管理器直接更新节点。手动安装的用户需重新克隆仓库，并覆盖原有的节点文件。更新后，请确保重新启动ComfyUI以生效。

## 联系方式
如果在使用过程中遇到任何问题或有任何建议，欢迎通过以下方式联系我们：
- **邮箱**：ches2010@qq.com
- **GitHub仓库**：[仓库链接](https://github.com/ches2010/comfyui_aliyundrive_uploader)，您可在仓库中提交Issues反馈问题。

## 许可证
本项目基于[MIT license]开源协议发布，详细内容请查看`LICENSE`文件。在使用本项目时，请遵守相关开源协议规定。
