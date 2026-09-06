# -*- coding: utf-8 -*-
"""
数字人端到端流水线：中文文本 → edge-tts 语音 → SadTalker 口播视频
针对 RTX 3050 Ti 4GB 显存优化

用法：
    python run_digital_human.py "你想说的话"
    python run_digital_human.py --text "你想说的话"
    python run_digital_human.py --file input.txt
    python run_digital_human.py --text "..." --image my_photo.jpg --voice zh-CN-YunxiNeural
"""
import os
import sys
import asyncio
import subprocess
import argparse
import shutil
from datetime import datetime
from pathlib import Path

# ==================== 配置 ====================
PROJECT_ROOT = Path(r"D:\digital_human")
SADTALKER_DIR = PROJECT_ROOT / "SadTalker"
VENV_PYTHON = PROJECT_ROOT / "venv" / "Scripts" / "python.exe"
CHECKPOINT_DIR = SADTALKER_DIR / "checkpoints"
OUTPUT_DIR = PROJECT_ROOT / "output"
TEMP_DIR = PROJECT_ROOT / "temp"

# 默认数字人照片（用户提供的真实照片）
DEFAULT_IMAGE = r"D:\digital_human\LivePortrait\ref\face.jpg"

# edge-tts 默认中文语音
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"  # 女声
# 其他可选：zh-CN-YunxiNeural(男声), zh-CN-YunjianNeural(男声), zh-CN-XiaoyiNeural(女声)

# ==================== 4GB 显存优化参数 ====================
SADTALKER_PARAMS = {
    "batch_size": "1",       # 默认2，4GB显存必须设为1
    "size": "256",            # 渲染分辨率，默认256
    "still": True,            # 静止模式，减少头部运动，省显存
    "preprocess": "crop",     # 裁剪模式，只处理脸部
    "expression_scale": "1.0", # 表情强度
    "pose_style": "0",        # 姿势风格
    "enhancer": "None",       # 不使用GFPGAN增强，省显存
}


def ensure_dirs():
    """确保输出和临时目录存在"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)


def text_to_speech(text, output_path, voice=DEFAULT_VOICE):
    """用 edge-tts 将中文文本转为语音"""
    print("\n" + "=" * 60)
    print("第一步：edge-tts 中文语音合成")
    print("=" * 60)
    print(f"文本: {text[:50]}{'...' if len(text) > 50 else ''}")
    print(f"语音: {voice}")

    async def generate():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(output_path))

    try:
        import edge_tts
        asyncio.run(generate())
        if output_path.exists() and output_path.stat().st_size > 1000:
            size_kb = output_path.stat().st_size / 1024
            print(f"✅ 语音生成成功: {output_path} ({size_kb:.1f} KB)")
            return str(output_path)
        else:
            print("❌ 语音文件太小或不存在")
            return None
    except Exception as e:
        print(f"❌ 语音生成失败: {e}")
        return None


def sadtalker_infer(image_path, audio_path, output_dir, run_id):
    """用 SadTalker 生成口播视频"""
    print("\n" + "=" * 60)
    print("第二步：SadTalker 口型驱动")
    print("=" * 60)
    print(f"照片: {image_path}")
    print(f"音频: {audio_path}")
    print(f"参数: batch_size={SADTALKER_PARAMS['batch_size']}, size={SADTALKER_PARAMS['size']}, still={SADTALKER_PARAMS['still']}, preprocess={SADTALKER_PARAMS['preprocess']}")

    # 构建命令
    cmd = [
        str(VENV_PYTHON),
        str(SADTALKER_DIR / "inference.py"),
        "--driven_audio", audio_path,
        "--source_image", image_path,
        "--checkpoint_dir", str(CHECKPOINT_DIR),
        "--result_dir", str(output_dir),
        "--batch_size", SADTALKER_PARAMS["batch_size"],
        "--size", SADTALKER_PARAMS["size"],
        "--expression_scale", SADTALKER_PARAMS["expression_scale"],
        "--pose_style", SADTALKER_PARAMS["pose_style"],
        "--preprocess", SADTALKER_PARAMS["preprocess"],
    ]

    if SADTALKER_PARAMS["still"]:
        cmd.append("--still")

    # 设置环境变量（全部指向 D 盘，避免污染 C 盘）
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SADTALKER_DIR)
    env["TORCH_HOME"] = str(PROJECT_ROOT / ".torch")
    env["HF_HOME"] = str(PROJECT_ROOT / ".hf")
    env["MPLCONFIGDIR"] = str(PROJECT_ROOT / ".matplotlib")

    print("正在生成口播视频（4GB显存下可能需要几分钟）...")
    print("-" * 60)

    try:
        result = subprocess.run(
            cmd,
            cwd=str(SADTALKER_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=1800,  # 30分钟超时
        )

        # 输出 SadTalker 的日志
        if result.stdout:
            # 只打印最后30行
            lines = result.stdout.strip().split("\n")
            for line in lines[-30:]:
                print(line)

        if result.returncode != 0:
            print(f"\n❌ SadTalker 退出码: {result.returncode}")
            if result.stderr:
                print("错误信息:", result.stderr[-1000:])
            return None

        # 查找生成的视频
        video_files = []
        for root, dirs, files in os.walk(output_dir):
            for f in files:
                if f.endswith(".mp4"):
                    video_files.append(os.path.join(root, f))

        if not video_files:
            print("❌ 未找到生成的视频文件")
            return None

        # 取最新的
        video_files.sort(key=os.path.getmtime, reverse=True)
        video_path = video_files[0]
        size_mb = os.path.getsize(video_path) / 1024 / 1024
        print(f"\n✅ 口播视频生成成功: {video_path} ({size_mb:.1f} MB)")
        return video_path

    except subprocess.TimeoutExpired:
        print("❌ SadTalker 超时（30分钟）")
        return None
    except Exception as e:
        print(f"❌ SadTalker 执行失败: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="数字人端到端流水线：中文文本 → 语音 → 口播视频",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run_digital_human.py "大家好，欢迎收看今天的新闻播报"
  python run_digital_human.py --text "..." --image my_photo.jpg
  python run_digital_human.py --file script.txt --voice zh-CN-YunxiNeural
        """,
    )
    parser.add_argument("text", nargs="?", help="要让数字人说的话")
    parser.add_argument("--text", dest="text_opt", help="要让数字人说的话")
    parser.add_argument("--file", help="从文本文件读取内容")
    parser.add_argument("--image", default=DEFAULT_IMAGE, help=f"数字人照片路径（默认: {DEFAULT_IMAGE}）")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help=f"edge-tts 语音（默认: {DEFAULT_VOICE}）")
    parser.add_argument("--output", help="输出视频路径（默认自动生成）")
    args = parser.parse_args()

    # 获取文本
    text = args.text or args.text_opt
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read().strip()

    if not text:
        print("❌ 请提供要让数字人说的话！")
        print("用法: python run_digital_human.py \"你想说的话\"")
        sys.exit(1)

    # 检查照片
    if not os.path.exists(args.image):
        print(f"❌ 照片不存在: {args.image}")
        print("请用 --image 参数指定有效的照片路径")
        sys.exit(1)

    # 检查 SadTalker 模型
    if not CHECKPOINT_DIR.exists():
        print(f"❌ SadTalker 模型目录不存在: {CHECKPOINT_DIR}")
        print("请先运行 download_models_ms.py 下载模型")
        sys.exit(1)

    ensure_dirs()

    # 生成运行 ID
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("\n" + "🚀" * 30)
    print("数字人端到端流水线启动")
    print(f"运行 ID: {run_id}")
    print(f"目标文本: {text[:60]}{'...' if len(text) > 60 else ''}")
    print(f"数字人照片: {args.image}")
    print(f"语音: {args.voice}")
    print("🚀" * 30)

    # 第一步：生成语音
    audio_path = TEMP_DIR / f"{run_id}_tts.mp3"
    audio_file = text_to_speech(text, audio_path, args.voice)
    if not audio_file:
        print("\n❌ 语音生成失败，流水线终止！")
        sys.exit(1)

    # 第二步：SadTalker 口型驱动
    sadtalker_output = TEMP_DIR / f"{run_id}_sadtalker"
    sadtalker_output.mkdir(exist_ok=True)
    video_file = sadtalker_infer(args.image, audio_file, str(sadtalker_output), run_id)
    if not video_file:
        print("\n❌ 口播视频生成失败，流水线终止！")
        sys.exit(1)

    # 复制到最终输出目录
    if args.output:
        final_path = args.output
    else:
        final_path = str(OUTPUT_DIR / f"digital_human_{run_id}.mp4")

    os.makedirs(os.path.dirname(final_path), exist_ok=True)
    shutil.copy2(video_file, final_path)
    final_size = os.path.getsize(final_path) / 1024 / 1024

    # 完成
    print("\n" + "🎉" * 30)
    print("✅ 数字人口播视频生成完成！")
    print(f"📁 输出文件: {final_path}")
    print(f"📦 文件大小: {final_size:.1f} MB")
    print(f"🖼️  使用照片: {args.image}")
    print(f"🔊 使用语音: {args.voice}")
    print("🎉" * 30)
    print("\n提示：")
    print("  - 更换照片: --image 你的照片路径")
    print("  - 更换语音: --voice zh-CN-YunxiNeural (男声)")
    print("  - 4GB显存优化已启用: batch_size=1, still模式, 256分辨率")


if __name__ == "__main__":
    main()
