# -*- coding: utf-8 -*-
"""
用 requests 从 hf-mirror.com 下载 SadTalker 模型
支持断点续传和进度显示
"""
import os
import requests

CHECKPOINT_DIR = r"D:\digital_human\SadTalker\checkpoints"
HF_MIRROR = "https://hf-mirror.com"

FILES = [
    (f"{HF_MIRROR}/OpenTalker/SadTalker/resolve/main/SadTalker_V0.0.2_256.safetensors",
     os.path.join(CHECKPOINT_DIR, "SadTalker_V0.0.2_256.safetensors")),
    (f"{HF_MIRROR}/OpenTalker/SadTalker/resolve/main/mapping_00229-model.pth.tar",
     os.path.join(CHECKPOINT_DIR, "mapping_00229-model.pth.tar")),
    (f"{HF_MIRROR}/OpenTalker/SadTalker/resolve/main/epoch_20.pth",
     os.path.join(CHECKPOINT_DIR, "epoch_20.pth")),
    (f"{HF_MIRROR}/OpenTalker/SadTalker/resolve/main/BFM_Fitting/BFM_model_front.mat",
     os.path.join(CHECKPOINT_DIR, "BFM_Fitting", "BFM_model_front.mat")),
]


def download_file(url, save_path):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    downloaded = os.path.getsize(save_path) if os.path.exists(save_path) else 0
    
    headers = {}
    if downloaded > 0:
        headers["Range"] = f"bytes={downloaded}-"
    
    try:
        resp = requests.get(url, headers=headers, stream=True, timeout=60, allow_redirects=True)
        
        if resp.status_code == 200:
            downloaded = 0
            mode = "wb"
        elif resp.status_code == 206:
            mode = "ab"
        else:
            print(f"  HTTP {resp.status_code}")
            return False
        
        total_size = int(resp.headers.get("Content-Length", 0))
        if total_size == 0 and downloaded > 0:
            total_size = downloaded  # 无法获取总大小
        
        with open(save_path, mode) as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        pct = downloaded / total_size * 100
                        print(f"\r  {pct:.1f}% ({downloaded//1024//1024}/{total_size//1024//1024} MB)", end="", flush=True)
        
        print()
        return True
    except Exception as e:
        print(f"\n  错误: {e}")
        return False


def main():
    print(f"从 {HF_MIRROR} 下载模型\n")
    for url, path in FILES:
        name = os.path.basename(path)
        print(f"[{name}]")
        if download_file(url, path):
            mb = os.path.getsize(path) / 1024 / 1024
            print(f"  ✅ {mb:.1f} MB\n")
        else:
            print(f"  ❌ 失败\n")
    
    print("完成！目录内容：")
    for root, _, files in os.walk(CHECKPOINT_DIR):
        for f in files:
            if not f.startswith("."):
                fp = os.path.join(root, f)
                print(f"  {os.path.relpath(fp, CHECKPOINT_DIR)} ({os.path.getsize(fp)/1024/1024:.1f} MB)")


if __name__ == "__main__":
    main()
