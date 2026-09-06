# -*- coding: utf-8 -*-
"""
从 ModelScope 下载 SadTalker 模型
"""
import os
from modelscope.hub.snapshot_download import snapshot_download
from modelscope.hub.api import HubApi

CHECKPOINT_DIR = r"D:\digital_human\SadTalker\checkpoints"

def search_models():
    """搜索 SadTalker 相关模型"""
    api = HubApi()
    try:
        models = api.list_models(filter="SadTalker", page_size=10)
        print("搜索结果:")
        for m in models.get("Models", []):
            print(f"  - {m.get('Name', '?')} (ID: {m.get('ModelId', '?')})")
        return models
    except Exception as e:
        print(f"搜索失败: {e}")
        return None

def download_model(model_id):
    """下载模型到指定目录"""
    print(f"\n下载模型: {model_id}")
    try:
        path = snapshot_download(
            model_id,
            cache_dir=CHECKPOINT_DIR,
        )
        print(f"下载完成: {path}")
        # 列出下载的文件
        for root, dirs, files in os.walk(path):
            for f in files:
                fp = os.path.join(root, f)
                print(f"  {os.path.relpath(fp, path)} ({os.path.getsize(fp)/1024/1024:.1f} MB)")
        return path
    except Exception as e:
        print(f"下载失败: {e}")
        return None

if __name__ == "__main__":
    # 先搜索
    search_models()
    
    # 尝试常见的模型 ID
    candidates = [
        "AI-ModelScope/SadTalker",
        "iic/SadTalker",
        "damo/SadTalker",
    ]
    
    for mid in candidates:
        print(f"\n尝试: {mid}")
        path = download_model(mid)
        if path:
            break
