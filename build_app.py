import os
import subprocess
import sys
import platform

def build_executable():
    print("="*50)
    print("准备将 Python 脚本打包为独立软件...")
    print("="*50)

    # 确保用户的代码被保存为 main.py
    if not os.path.exists("main.py"):
        print("错误: 找不到 'main.py'！")
        print("请将您的完整代码保存为 'main.py' 并放在与此脚本相同的文件夹中。")
        sys.exit(1)

    # 检查是否安装了 pyinstaller
    try:
        import PyInstaller
    except ImportError:
        print("未检测到 PyInstaller，正在为您安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    os_name = platform.system()
    app_name = "MediaSorter"
    
    # 基础打包参数
    # --noconfirm: 覆盖之前生成的 dist 文件夹
    # --windowed: 隐藏命令行控制台窗口 (纯 GUI 应用)
    # --name: 设置应用名称
    # --collect-all tkinterdnd2: 强制打包拖拽库所需的底层 tcl 文件 (非常关键)
    args = [
        "pyinstaller",
        "--noconfirm",
        "--windowed",
        "--name", app_name,
        "--collect-all", "tkinterdnd2",
        "main.py"
    ]

    if os_name == "Windows":
        print("检测到系统: Windows。将生成 .exe 文件。")
        # 如果有图标，可以取消下方注释并放入 app_icon.ico
        # args.extend(["--icon", "app_icon.ico"])
        
    elif os_name == "Darwin":
        print("检测到系统: macOS。将生成 .app 应用程序。")
        # 如果有图标，可以取消下方注释并放入 app_icon.icns
        # args.extend(["--icon", "app_icon.icns"])
        
    else:
        print(f"检测到系统: {os_name}。将尝试生成 Linux 可执行文件。")

    print(f"\n执行命令: {' '.join(args)}\n")
    print("正在打包，这可能需要几分钟时间，请耐心等待...")
    
    try:
        # 运行 PyInstaller
        subprocess.run(args, check=True)
        print("="*50)
        print("打包成功！🎉")
        print(f"请在当前目录的 'dist' 文件夹中查找您的应用: {app_name}")
        
        # 打开输出文件夹
        dist_path = os.path.abspath("dist")
        if os_name == "Windows":
            os.startfile(dist_path)
        elif os_name == "Darwin":
            subprocess.Popen(["open", dist_path])
            
    except subprocess.CalledProcessError:
        print("="*50)
        print("打包失败，请检查上方红色的错误信息。")

if __name__ == "__main__":
    build_executable()