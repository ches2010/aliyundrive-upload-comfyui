import subprocess
import sys
import os
import platform

def is_installed(package_name):
    """Check if a package is installed."""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def install_package(package_name, version=None):
    """Install a package using pip."""
    if version:
        package = f"{package_name}=={version}"
    else:
        package = package_name
    
    check = "pip" in sys.executable # Check if we are running inside a venv or system python
    
    if check:
        # Use the same Python executable that is running this script
        cmd = [sys.executable, "-s", "-m", "pip", "install", package]
    else:
        # Fallback, might not always work correctly depending on system setup
        cmd = [sys.executable.replace("python.exe", "pip.exe"), "install", package] if platform.system() == "Windows" else ["pip", "install", package]

    print(f"Installing package: {package}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Failed to install {package}: {result.stderr}")
        return False
    else:
        print(f"Successfully installed {package}")
        return True

def main():
    """Main installation logic."""
    print("Running install.py for ComfyUI Aliyun Drive Uploader...")
    
    # Read requirements from requirements.txt
    script_dir = os.path.dirname(os.path.abspath(__file__))
    req_file = os.path.join(script_dir, 'requirements.txt')
    
    if not os.path.exists(req_file):
        print(f"Error: requirements.txt not found at {req_file}")
        return

    with open(req_file, 'r') as f:
        packages = f.readlines()

    failed_packages = []
    for package_line in packages:
        package_line = package_line.strip()
        if not package_line or package_line.startswith('#'):
            continue # Skip empty lines and comments
        
        # Simple parsing, assumes format like `package` or `package>=version` or `package==version`
        parts = package_line.split('==')
        if len(parts) > 1:
            pkg_name, pkg_version = parts[0], parts[1]
        else:
            parts = package_line.split('>=')
            if len(parts) > 1:
                pkg_name, pkg_version = parts[0], parts[1]
            else:
                pkg_name, pkg_version = package_line, None
        
        if not is_installed(pkg_name):
            success = install_package(pkg_name, pkg_version)
            if not success:
                failed_packages.append(package_line)
        else:
            print(f"Package '{pkg_name}' is already installed.")

    if failed_packages:
        print("The following packages failed to install:")
        for pkg in failed_packages:
            print(f" - {pkg}")
        print("Please install them manually.")
    else:
        print("All dependencies for ComfyUI Aliyun Drive Uploader have been successfully installed.")

if __name__ == "__main__":
    main()
