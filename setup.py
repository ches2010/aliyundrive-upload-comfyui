from setuptools import setup, find_packages

setup(
    name='comfyui-aliyun-drive-node',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'aliyundrive-openapi',
    ],
    entry_points={
        'comfyui.nodes': [
            'aliyun_drive_upload = custom_nodes.aliyun_drive_upload:AliyunDriveUploadNode',
        ],
    },
)
