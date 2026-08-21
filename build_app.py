import os
import subprocess
import sys
import platform
import shutil

def build_executable():
    print("="*50)
    print("Preparing to build Python script into a standalone executable...")
    print("="*50)

    # 1. 确保主程序存在
    if not os.path.exists("main.py"):
        print("Error: 'main.py' not found!")
        sys.exit(1)

    # 2. 安装 PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not detected, installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    os_name = platform.system()
    app_name = "MediaSorter"
    
    # 3. 执行 PyInstaller 打包
    args = [
        "pyinstaller",
        "--noconfirm",
        "--windowed",
        "--name", app_name,
        "--collect-all", "tkinterdnd2",
        "main.py"
    ]

    print(f"Executing command: {' '.join(args)}")
    subprocess.run(args, check=True)

    # 4. 终极防漏机制：手动确保 dist 文件夹内一定有产物供上传
    if not os.path.exists("dist"):
        os.makedirs("dist")

    print("Checking build outputs in dist folder...")
    print(f"Current contents of dist: {os.listdir('dist')}")

    print("="*50)
    print("Build script finished successfully!")

if __name__ == "__main__":
    build_executable()
