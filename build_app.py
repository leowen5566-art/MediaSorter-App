import os
import subprocess
import sys

def build_executable():
    print("="*50)
    print("Starting build process...")
    print("="*50)

    # 1. 检查主程序是否存在
    if not os.path.exists("main.py"):
        print("Error: 'main.py' not found!")
        sys.exit(1)

    app_name = "MediaSorter"
    
    # 2. 使用 sys.executable -m PyInstaller，确保绝对不会因为环境变量找不到 PyInstaller
    args = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--windowed",
        "--name", app_name,
        "--collect-all", "tkinterdnd2",
        "main.py"
    ]

    print(f"Executing: {' '.join(args)}")
    result = subprocess.run(args)
    
    if result.returncode != 0:
        print(f"Build failed with exit code {result.returncode}")
        sys.exit(result.returncode)

    print("="*50)
    print("Build completed successfully!")

if __name__ == "__main__":
    build_executable()
