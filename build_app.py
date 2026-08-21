import os
import subprocess
import sys
import platform

def build_executable():
    print("="*50)
    print("Preparing to build...")
    print("="*50)

    if not os.path.exists("main.py"):
        print("Error: 'main.py' not found!")
        sys.exit(1)

    try:
        import PyInstaller
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    app_name = "MediaSorter"
    
    args = [
        "pyinstaller",
        "--noconfirm",
        "--windowed",
        "--name", app_name,
        "--collect-all", "tkinterdnd2",
        "main.py"
    ]

    subprocess.run(args, check=True)
    print("Build successful!")

if __name__ == "__main__":
    build_executable()
