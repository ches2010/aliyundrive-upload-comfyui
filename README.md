# ComfyUI - 阿里云盘上传节点

将ComfyUI生成的图片自动上传到阿里云盘的自定义节点。通过本节点，用户能够方便快捷地将生成的图片存储到阿里云盘，便于后续查看与管理。

## 安装说明

### 使用ComfyUI管理器（推荐）
1. **打开ComfyUI**：确保ComfyUI已成功启动并运行。
2. **进入管理器面板**：在ComfyUI界面中，通常可在侧边栏找到`Manager`面板。
3. **安装自定义节点**：点击`Install Custom Node`，然后选择`Install from URL`。
4. **输入仓库地址**：输入本节点的仓库地址`https://github.com/ches2010/ComfyUI_aliupload.git`，并点击安装按钮。ComfyUI管理器将自动完成以下操作：
    - 从GitHub克隆仓库到ComfyUI的`custom_nodes`目录。
    - 读取`manifest.json`文件，识别`requirements.txt`中的依赖，并自动安装所需的Python库。
5. **重启ComfyUI**：安装完成后，按照提示重启ComfyUI。重启后，即可在节点面板中找到并使用本节点。

### 手动安装
1. **克隆仓库**：在命令行中运行以下命令，将本仓库克隆到本地：
    ```bash
    git clone https://github.com/ches2010/ComfyUI_aliupload.git
    cd ComfyUI_aliupload
    ```
2. **安装依赖**：
    - **Windows系统**：双击运行仓库根目录下的`install.bat`文件。脚本将自动检测并安装所需的Python依赖。若未安装`pip`，脚本将提示先安装Python并配置环境变量。
    - **Linux或macOS系统**：在仓库根目录下的终端中运行以下命令赋予`install.sh`执行权限：
    ```bash
    chmod +x install.sh
    ```
    然后运行脚本：
    ```bash
   ./install.sh
    ```
    脚本会自动检测`pip`是否安装，并安装`requirements.txt`中列出的依赖。若未安装`pip`，将提示用户先安装Python并配置环境变量。
3. **部署节点**：将`custom_nodes/aliyun_drive_upload`文件夹复制到ComfyUI根目录下的`custom_nodes`文件夹中。例如，在Linux或macOS系统中，可使用以下命令：
    ```bash
    cp -r custom_nodes/aliyun_drive_upload ~/ComfyUI/custom_nodes/
    ```
    在Windows系统中，可手动将文件夹复制到相应路径。
4. **重启ComfyUI**：完成上述步骤后，重启ComfyUI，即可在节点面板中找到并使用本节点。

## 使用方法
1. **准备参数**：在使用本节点前，您需要准备阿里云盘的`folder_id`、`refresh_token`，如果有`access_token`也可一并准备（若不提供，节点会自动刷新获取）。
    - `folder_id`获取方式：在阿里云盘网页端打开目标文件夹，地址栏URL格式为`https://www.aliyundrive.com/s/xxxxxx`，其中`xxxxxx`即为`folder_id`。
    - `refresh_token`获取方式：可通过阿里云盘开放平台工具或第三方工具获取，有效期通常较长（30天以上），若失效需重新获取。
2. **配置节点**：在ComfyUI工作流中添加本节点，将生成图片的节点（如`KSampler`等）的输出连接到本节点的`image`输入。同时，在本节点参数设置中：
    - `refresh_token`：填入获取到的`refresh_token`。
    - `folder_id`：填入目标文件夹的`folder_id`。
    - （可选）`access_token`：若已获取，可填入；若留空，节点会在需要时自动刷新获取。
    - （可选）`file_prefix`：可自定义文件名前缀，方便对上传的图片进行归类。
3. **运行工作流**：点击“Queue Prompt”运行工作流，节点将自动上传图片到指定的阿里云盘文件夹，并返回`file_id`和阿里云盘文件链接。您可通过链接在阿里云盘中查看上传的图片。

一、准备转存阿里云盘文件夹
1.手机下载安装阿里云盘 APP
图片

参加阿里云盘达人招募计划，有机会获得50T容量，点击我立即报名参加！

2、注册登录阿里云盘


3、电脑浏览器打开阿里云盘官网
点击此处前往登录

4、使用手机上的阿里云盘 App 扫码登录


5、创建小雅缓存的文件夹
文件名可以自行定义，注意不能使用 备份盘 ，必须使用 资源库



6、获取所需的 folderId
获得转存文件夹参数 folderId，将这串数字复制保存。



二、获取 refreshToken（32 位长）
访问链接扫码登录即可获取，这是本站建立的代理地址：

点击 csb.histb.com 此处前往获取 refreshToken

将这串字符复制保存



三、获取 token（280 位长）
点击此处前往获取 token

点击按钮,生成登录二维码



手机扫码授权



授权完成后点击按钮生成 280 位 token



复制保存 token（280 位）



## 注意事项
1. **依赖安装问题**：如果在安装依赖时遇到问题，请确保您的Python环境配置正确，且`pip`能够正常工作。若手动安装依赖，可尝试使用管理员权限运行安装命令。
2. **权限与配置**：确保提供的`refresh_token`和`folder_id`正确无误，否则可能导致上传失败。同时，若阿里云盘权限发生变化（如文件夹权限更改），可能影响上传功能。
3. **更新说明**：若节点有更新，使用ComfyUI管理器的用户可通过管理器直接更新节点。手动安装的用户需重新克隆仓库，并覆盖原有的节点文件。更新后，请确保重新启动ComfyUI以生效。

## 联系方式
如果在使用过程中遇到任何问题或有任何建议，欢迎通过以下方式联系我们：
- **邮箱**：ches2010@qq.com
- **GitHub仓库**：[仓库链接](https://github.com/ches2010/ComfyUI_aliupload)，您可在仓库中提交Issues反馈问题。

## 许可证
本项目基于[具体许可证名称]开源协议发布，详细内容请查看`LICENSE`文件。在使用本项目时，请遵守相关开源协议规定。
