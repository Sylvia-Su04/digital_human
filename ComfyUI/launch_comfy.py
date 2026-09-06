"""
ComfyUI 启动包装器：先移除 sitecustomize 的 import hook，再启动 ComfyUI。
重启后 torch 版本变为 2.5.1，之前的 infer_schema 补丁可能不兼容导致导入卡住。
"""
import sys
import builtins
import os

# 恢复原始的 __import__（移除 sitecustomize.py 的 patch）
if 'sitecustomize' in sys.modules:
    sc = sys.modules['sitecustomize']
    if hasattr(sc, '_orig_import'):
        builtins.__import__ = sc._orig_import
        print("[launcher] Restored original __import__ from sitecustomize", flush=True)
    else:
        print("[launcher] sitecustomize found but no _orig_import attribute", flush=True)
else:
    print("[launcher] sitecustomize not in sys.modules", flush=True)

# 切换到 ComfyUI 目录并运行 main.py
comfy_dir = r"C:\Users\范籽粟\AppData\Local\Doubao\User Data\Profile 2\.doubao\agent_mode\workspace\ComfyUI"
os.chdir(comfy_dir)
sys.path.insert(0, comfy_dir)

print(f"[launcher] Starting ComfyUI from {comfy_dir}", flush=True)

# 运行 main.py
import runpy
sys.argv = ['main.py', '--listen', '127.0.0.1', '--port', '8189']
runpy.run_path('main.py', run_name='__main__')
