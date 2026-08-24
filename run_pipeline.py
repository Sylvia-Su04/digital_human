"""
数字人串联脚本：输入文本 → GPT-SoVITS 生成语音 → LivePortrait 驱动人脸 → 输出 mp4

使用前必须完成：
  1. GPT-SoVITS 训练好自己的音色模型（.pth + .json）
  2. LivePortrait 准备好人脸参考素材（图片/视频）放入 ref/
  3. 修改下方 CONFIG 区域的路径为你实际的文件名

环境：D 盘 Anaconda + Python 3.10 + PyTorch CUDA 11.8
"""

import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path

# ===================== 配置区域（按实际情况修改） =====================

BASE_DIR = Path(r"D:\digital_human")
LP_DIR = BASE_DIR / "LivePortrait"
SOVITS_DIR = BASE_DIR / "GPT-SoVITS"

# 你的素材路径
REF_FACE = LP_DIR / "ref" / "my_face.mp4"          # 人脸参考素材（图片或视频）
SOVITS_MODEL = SOVITS_DIR / "outputs" / "my_voice.pth"   # 声纹模型权重
SOVITS_CONFIG = SOVITS_DIR / "outputs" / "my_config.json" # 声纹模型配置

# GPT-SoVITS 参考音频（推理时需要，5-10秒清晰人声）
SOVITS_REF_AUDIO = SOVITS_DIR / "outputs" / "ref_audio.wav"
SOVITS_REF_TEXT = "这是一段参考音频的文字内容。"  # 参考音频对应的文本

# ======================================================================


def check_env():
    """检查关键路径和依赖是否就绪"""
    errors = []

    if not LP_DIR.exists():
        errors.append(f"LivePortrait 目录不存在: {LP_DIR}")
    if not SOVITS_DIR.exists():
        errors.append(f"GPT-SoVITS 目录不存在: {SOVITS_DIR}")
    if not REF_FACE.exists():
        errors.append(f"人脸参考素材不存在: {REF_FACE}")
    if not SOVITS_MODEL.exists():
        errors.append(f"声纹模型不存在: {SOVITS_MODEL}")
    if not SOVITS_CONFIG.exists():
        errors.append(f"声纹配置不存在: {SOVITS_CONFIG}")

    # 检查 ffmpeg
    if shutil.which("ffmpeg") is None:
        errors.append("ffmpeg 未找到，请在 conda 环境中执行: conda install -y ffmpeg")

    if errors:
        print("❌ 环境检查未通过：")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print("✅ 环境检查通过")


def generate_audio(text: str, out_wav: Path):
    """
    调用 GPT-SoVITS 生成语音。

    注意：GPT-SoVITS 的推理接口可能随版本变化，
    以下参数基于常见用法，实际请以 GPT-SoVITS/docs 为准。
    推荐使用 GPT-SoVITS 的 api_v2.py 启动 API 服务后调用，
    或直接使用其 WebUI 推理。
    """
    cmd = [
        sys.executable,
        str(SOVITS_DIR / "inference.py"),
        "--text", text,
        "--model", str(SOVITS_MODEL),
        "--config", str(SOVITS_CONFIG),
        "--ref_audio_path", str(SOVITS_REF_AUDIO),
        "--prompt_text", SOVITS_REF_TEXT,
        "--output", str(out_wav),
    ]

    print(f"  执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(SOVITS_DIR), capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ GPT-SoVITS 推理失败:\n{result.stderr}")
        sys.exit(1)

    if not out_wav.exists():
        print(f"❌ 音频未生成，预期路径: {out_wav}")
        print(f"  GPT-SoVITS 输出:\n{result.stdout}")
        sys.exit(1)

    print(f"  ✅ 语音生成完成: {out_wav}")


def generate_digital_human_video(wav_path: Path, out_mp4: Path):
    """
    调用 LivePortrait 根据音频驱动人脸生成视频。

    注意：LivePortrait 原生推理脚本 inference.py 的参数
    可能与下方不同，请以 LivePortrait 仓库实际文档为准。
    音频驱动通常需要使用专门的音频到视频的推理入口。
    """
    cmd = [
        sys.executable,
        str(LP_DIR / "inference.py"),
        "--source", str(REF_FACE),
        "--audio", str(wav_path),
        "--output", str(out_mp4),
        "--device_id", "0",
    ]

    # RTX 3050 Ti 只有 4GB 显存，降低分辨率避免 OOM
    cmd.extend(["--resize", "256"])

    print(f"  执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(LP_DIR), capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ LivePortrait 推理失败:\n{result.stderr}")
        sys.exit(1)

    if not out_mp4.exists():
        print(f"❌ 视频未生成，预期路径: {out_mp4}")
        print(f"  LivePortrait 输出:\n{result.stdout}")
        sys.exit(1)

    print(f"  ✅ 数字人视频生成完成: {out_mp4}")


def main():
    parser = argparse.ArgumentParser(description="数字人串联脚本：文本 → 语音 → 数字人视频")
    parser.add_argument("--text", type=str, required=True, help="数字人要说的文字")
    parser.add_argument("--output", type=str, default="result.mp4", help="输出视频路径")
    parser.add_argument("--keep-audio", action="store_true", help="保留临时音频文件")
    parser.add_argument("--skip-check", action="store_true", help="跳过环境检查")
    args = parser.parse_args()

    if not args.skip_check:
        check_env()

    out_mp4 = Path(args.output).resolve()
    temp_wav = BASE_DIR / "temp_voice.wav"

    print("\n" + "=" * 60)
    print("[1/2] 正在克隆音色生成语音...")
    print("=" * 60)
    generate_audio(args.text, temp_wav)

    print("\n" + "=" * 60)
    print("[2/2] 正在驱动数字人生成动态视频...")
    print("=" * 60)
    generate_digital_human_video(temp_wav, out_mp4)

    # 清理临时音频
    if not args.keep_audio and temp_wav.exists():
        temp_wav.unlink()
        print("\n🧹 已清理临时音频文件")

    print(f"\n🎉 生成完成：{out_mp4}")


if __name__ == "__main__":
    main()
