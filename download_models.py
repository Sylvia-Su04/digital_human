# -*- coding: utf-8 -*-
"""
SadTalker 模型权重下载脚本
使用 HuggingFace 镜像 (hf-mirror.com) 下载所有必需模型
支持断点续传
"""
import os
import sys
import urllib.request
import ssl

# 禁用 SSL 验证（某些环境下需要）
ssl._create_default_https_context = ssl._create_unverified_context

CHECKPOINT_DIR = r"D:\digital_human\SadTalker\checkpoints"
BFM_DIR = os.path.join(CHECKPOINT_DIR, "BFM_Fitting")
HF_MIRROR = "https://hf-mirror.com"

# 需要下载的文件列表 (url, save_path)
FILES = [
    # SadTalker 主模型（safetensors 版本，256 分辨率）
    (f"{HF_MIRROR}/OpenTalker/SadTalker/resolve/main/SadTalker_V0.0.2_256.safetensors",
     os.path.join(CHECKPOINT_DIR, "SadTalker_V0.0.2_256.safetensors")),
    
    # mapping 网络（crop 模式用）
    (f"{HF_MIRROR}/OpenTalker/SadTalker/resolve/main/mapping_00229-model.pth.tar",
     os.path.join(CHECKPOINT_DIR, "mapping_00229-model.pth.tar")),
    
    # face3d 模型
    (f"{HF_MIRROR}/OpenTalker/SadTalker/resolve/main/epoch_20.pth",
     os.path.join(CHECKPOINT_DIR, "epoch_20.pth")),
    
    # BFM 3DMM 模型
    (f"{HF_MIRROR}/OpenTalker/SadTalker/resolve/main/BFM_Fitting/BFM_model_front.mat",
     os.path.join(BFM_DIR, "BFM_model_front.mat")),
    
    # GFPGAN 面部增强模型（可选，用于提升画质）
    (f"{HF_MIRROR}/TencentARC/GFPGAN/resolve/main/GFPGANv1.4.pth",
     os.path.join(CHECKPOINT_DIR, "GFPGANv1.4.pth")),
]


def download_file(url, save_path, chunk_size=8192):
    """下载文件，支持断点续传"""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # 检查已下载的大小
    downloaded = 0
    if os.path.exists(save_path):
        downloaded = os.path.getsize(save_path)
    
    # 获取文件总大小
    req = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            total_size = int(resp.headers.get("Content-Length", 0))
    except Exception as e:
        print(f"  获取文件大小失败: {e}")
        total_size = 0
    
    if downloaded > 0 and total_size > 0 and downloaded >= total_size:
        print(f"  已存在，跳过: {os.path.basename(save_path)} ({downloaded // 1024 // 1024} MB)")
        return True
    
    # 断点续传
    headers = {}
    if downloaded > 0:
        headers["Range"] = f"bytes={downloaded}-"
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            # 如果服务器不支持断点续传，从头开始
            if resp.status == 200:
                downloaded = 0
                mode = "wb"
            else:
                mode = "ab"
            
            with open(save_path, mode) as f:
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # 显示进度
                    if total_size > 0:
                        pct = downloaded / total_size * 100
                        mb = downloaded / 1024 / 1024
                        total_mb = total_size / 1024 / 1024
                        print(f"\r  进度: {pct:.1f}% ({mb:.1f}/{total_mb:.1f} MB)", end="", flush=True)
                    else:
                        mb = downloaded / 1024 / 1024
                        print(f"\r  已下载: {mb:.1f} MB", end="", flush=True)
        
        print()  # 换行
        return True
    except Exception as e:
        print(f"\n  下载失败: {e}")
        return False


def main():
    print("=" * 60)
    print("SadTalker 模型权重下载")
    print(f"保存目录: {CHECKPOINT_DIR}")
    print(f"镜像源: {HF_MIRROR}")
    print("=" * 60)
    
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    os.makedirs(BFM_DIR, exist_ok=True)
    
    success = 0
    failed = []
    
    for i, (url, save_path) in enumerate(FILES, 1):
        filename = os.path.basename(save_path)
        print(f"\n[{i}/{len(FILES)}] 下载: {filename}")
        
        if download_file(url, save_path):
            # 验证文件
            if os.path.exists(save_path) and os.path.getsize(save_path) > 1000:
                size_mb = os.path.getsize(save_path) / 1024 / 1024
                print(f"  ✅ 完成: {filename} ({size_mb:.1f} MB)")
                success += 1
            else:
                print(f"  ❌ 文件太小，可能下载失败")
                failed.append(filename)
        else:
            failed.append(filename)
    
    print("\n" + "=" * 60)
    print(f"下载完成: {success}/{len(FILES)} 成功")
    if failed:
        print(f"失败: {', '.join(failed)}")
        print("提示: 可重新运行本脚本继续断点续传")
    print("=" * 60)


if __name__ == "__main__":
    main()
