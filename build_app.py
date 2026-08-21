import os
import subprocess
import sys
import platform

def build_executable():
    print("="*50)
    print("Preparing to build Python script into a standalone executable...")
    print("="*50)

    # Make sure the user's code is saved as main.py
    if not os.path.exists("main.py"):
        print("Error: 'main.py' not found!")
        print("Please save your complete code as 'main.py' in the same folder as this script.")
        sys.exit(1)

    # Check if pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not detected, installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    os_name = platform.system()
    app_name = "MediaSorter"
    
    # Basic packaging parameters
    # --noconfirm: Overwrite existing dist folder
    # --windowed: Hide the console window (pure GUI app)
    # --name: Set the application name
    # --collect-all tkinterdnd2: Force include tkinterdnd2 dependencies (critical)
    args = [
        "pyinstaller",
        "--noconfirm",
        "--windowed",
        "--name", app_name,
        "--collect-all", "tkinterdnd2",
        "main.py"
    ]

    if os_name == "Windows":
        print("Detected OS: Windows. Generating .exe file.")
    elif os_name == "Darwin":
        print("Detected OS: macOS. Generating .app application.")
    else:
        print(f"Detected OS: {os_name}. Attempting to build for Linux.")

    print(f"\nExecuting command: {' '.join(args)}\n")
    print("Building... this may take a few minutes, please be patient...")
    
    try:
        # Run PyInstaller
        subprocess.run(args, check=True)
        print("="*50)
        print("Build successful! 🎉")
        print(f"Please find your application in the 'dist' folder: {app_name}")
        
    except subprocess.CalledProcessError:
        print("="*50)
        print("Build failed, please check the error messages above.")

if __name__ == "__main__":
    build_executable()
