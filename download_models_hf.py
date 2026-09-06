# -*- coding: utf-8 -*-
"""
使用 huggingface_hub 从镜像下载 SadTalker 模型
"""
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from huggingface_hub import hf_hub_download

CHECKPOINT_DIR = r"D:\digital_human\SadTalker\checkpoints"

FILES = [
    # (repo_id, filename, subfolder)
    ("OpenTalker/SadTalker", "SadTalker_V0.0.2_256.safetensors", None),
    ("OpenTalker/SadTalker", "mapping_00229-model.pth.tar", None),
    ("OpenTalker/SadTalker", "epoch_20.pth", None),
    ("OpenTalker/SadTalker", "BFM_model_front.mat", "BFM_Fitting"),
]

def main():
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    print(f"HF_ENDPOINT: {os.environ['HF_ENDPOINT']}")
    print(f"保存目录: {CHECKPOINT_DIR}\n")
    
    for repo_id, filename, subfolder in FILES:
        print(f"下载: {filename} (repo: {repo_id})")
        try:
            path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                subfolder=subfolder,
                local_dir=CHECKPOINT_DIR,
            )
            size_mb = os.path.getsize(path) / 1024 / 1024
            print(f"  ✅ 完成: {path} ({size_mb:.1f} MB)\n")
        except Exception as e:
            print(f"  ❌ 失败: {e}\n")
    
    print("下载完成！")
    print("checkpoints 目录内容:")
    for root, dirs, files in os.walk(CHECKPOINT_DIR):
        for f in files:
            fp = os.path.join(root, f)
            print(f"  {os.path.relpath(fp, CHECKPOINT_DIR)} ({os.path.getsize(fp)/1024/1024:.1f} MB)")

if __name__ == "__main__":
    main()
