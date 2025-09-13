import os
import sys
import subprocess

def install():
    # 可选：检查Python版本
    if sys.version_info < (3, 8):
        print("错误：需要Python 3.8及以上版本", file=sys.stderr)
        sys.exit(1)
    
    # 可选：安装依赖（管理器会自动处理requirements.txt，但可在此补充）
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败：{e}", file=sys.stderr)
        sys.exit(1)
    
    # 可选：创建默认配置文件（如示例配置模板）
    config_path = os.path.join(os.path.dirname(__file__), "config_example.json")
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            f.write('{"refresh_token": "在此填入你的token", "folder_id": "在此填入文件夹ID"}')
        print("已创建配置示例文件，请修改后使用")

if __name__ == "__main__":
    install()
