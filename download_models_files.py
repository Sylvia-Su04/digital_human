# -*- coding: utf-8 -*-
"""
从 ModelScope 逐个下载 SadTalker 关键模型文件
"""
import os
from modelscope.hub.file_download import model_file_download

MODEL_ID = "wwd123/sadtalker"
CACHE_DIR = r"D:\digital_human\SadTalker\checkpoints"

# 需要下载的文件（相对模型仓库根目录）
FILES = [
    "checkpoints/SadTalker_V0.0.2_256.safetensors",
    "checkpoints/mapping_00229-model.pth.tar",
    "checkpoints/mapping_00109-model.pth.tar",
]

def main():
    os.makedirs(CACHE_DIR, exist_ok=True)
    print(f"从 ModelScope 下载模型: {MODEL_ID}")
    print(f"缓存目录: {CACHE_DIR}\n")
    
    for file_path in FILES:
        filename = os.path.basename(file_path)
        print(f"下载: {filename}")
        try:
            local_path = model_file_download(
                model_id=MODEL_ID,
                file_path=file_path,
                cache_dir=CACHE_DIR,
            )
            size_mb = os.path.getsize(local_path) / 1024 / 1024
            print(f"  ✅ {local_path} ({size_mb:.1f} MB)\n")
        except Exception as e:
            print(f"  ❌ 失败: {e}\n")
    
    # 列出下载的文件
    print("下载完成！checkpoints 目录:")
    for root, dirs, files in os.walk(CACHE_DIR):
        for f in files:
            fp = os.path.join(root, f)
            if not f.startswith(".") and os.path.getsize(fp) > 1000:
                print(f"  {os.path.relpath(fp, CACHE_DIR)} ({os.path.getsize(fp)/1024/1024:.1f} MB)")

if __name__ == "__main__":
    main()
