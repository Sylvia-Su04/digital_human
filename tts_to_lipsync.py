"""
tts_to_lipsync.py — 漫剧平台配音集成脚本
=========================================
文案 -> GPT-SoVITS 配音 -> ComfyUI/input/role_voice.wav -> SadTalker 口播

功能：
  1. CLI 模式（默认）：调用 inference_cli.py，一次性加载模型生成 wav
  2. API 模式：调用已启动的 GPT-SoVITS API（端口 9880），适合批量配音
  3. --start-api：后台启动 API 服务（模型常驻，避免重复加载）

模型：
  Su          — 基础音色（默认）
  Su_emotional — 情感版音色

用法：
  python tts_to_lipsync.py --text "大家好，欢迎来到漫剧平台。"
  python tts_to_lipsync.py --text-file script.txt
  python tts_to_lipsync.py --text "测试" --voice Su_emotional
  python tts_to_lipsync.py --start-api
  python tts_to_lipsync.py --text "测试" --mode api
"""

import argparse
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
import urllib.error
import json
import shutil

# ============================================================
# 配置
# ============================================================
GPT_SOVITS_DIR = r"D:\digital_human\GPT-SoVITS"
PYTHON_EXE = r"D:\conda_envs\digital_human\python.exe"
COMFYUI_INPUT = r"D:\digital_human\ComfyUI\input"
DEFAULT_OUTPUT = os.path.join(COMFYUI_INPUT, "role_voice.wav")
API_HOST = "127.0.0.1"
API_PORT = 9880

# 音色配置
VOICES = {
    "Su": {
        "gpt": r"GPT_weights_v2Pro\Su_e15_s135.ckpt",
        "sovits": r"SoVITS_weights_v2Pro\Su_e8_s296.pth",
        "ref_audio": r"D:\digital_human\ref_clip.wav",
        "ref_text": "加油呀，你已经很棒了，真的。",
    },
    "Su_emotional": {
        "gpt": r"GPT_weights_v2Pro\Su_emotional-e15.ckpt",
        "sovits": r"SoVITS_weights_v2Pro\Su_emotional_e5_s215.pth",
        "ref_audio": r"D:\digital_human\ref_clip.wav",
        "ref_text": "加油呀，你已经很棒了，真的。",
    },
}


def build_env():
    env = os.environ.copy()
    env["PYTHONPATH"] = r"D:\ort_fix;" + GPT_SOVITS_DIR
    env["PATH"] = (
        r"D:\conda_envs\digital_human\Library\bin;"
        r"D:\conda_envs\digital_human\Scripts;"
        r"D:\conda_envs\digital_human;"
        + env.get("PATH", "")
    )
    return env


def tts_cli(text, voice_name, output_path):
    voice = VOICES[voice_name]
    tmp_dir = tempfile.mkdtemp(prefix="gpt_sovits_")
    ref_text_file = os.path.join(tmp_dir, "ref_text.txt")
    target_text_file = os.path.join(tmp_dir, "target_text.txt")
    seg_output_dir = os.path.join(tmp_dir, "output")
    os.makedirs(seg_output_dir, exist_ok=True)

    with open(ref_text_file, "w", encoding="utf-8") as f:
        f.write(voice["ref_text"])
    with open(target_text_file, "w", encoding="utf-8") as f:
        f.write(text)

    cmd = [
        PYTHON_EXE,
        "GPT_SoVITS/inference_cli.py",
        "--gpt_model", voice["gpt"],
        "--sovits_model", voice["sovits"],
        "--ref_audio", voice["ref_audio"],
        "--ref_text", ref_text_file,
        "--ref_language", "中文",
        "--target_text", target_text_file,
        "--target_language", "中文",
        "--output_path", seg_output_dir,
    ]

    print(f"[CLI] 音色: {voice_name}")
    print(f"[CLI] GPT:  {voice['gpt']}")
    print(f"[CLI] SoVITS: {voice['sovits']}")
    print(f"[CLI] 文案 ({len(text)} 字): {text[:80]}{'...' if len(text) > 80 else ''}")
    print("[CLI] 正在推理（首次加载模型约 30-60 秒）...")

    result = subprocess.run(
        cmd, cwd=GPT_SOVITS_DIR, capture_output=True,
        text=True, encoding="utf-8", errors="replace", env=build_env(),
    )

    if result.returncode != 0:
        print(f"[CLI] 推理失败 (exit code {result.returncode})")
        print("--- stderr (最后 800 字) ---")
        print(result.stderr[-800:] if result.stderr else "(无)")
        print("--- stdout (最后 800 字) ---")
        print(result.stdout[-800:] if result.stdout else "(无)")
        return False

    generated = None
    for f in os.listdir(seg_output_dir):
        if f.endswith(".wav"):
            generated = os.path.join(seg_output_dir, f)
            break

    if not generated:
        print("[CLI] 未找到生成的 wav 文件")
        print("stdout:", result.stdout[-500:])
        return False

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    shutil.copy2(generated, output_path)
    size_kb = os.path.getsize(output_path) / 1024
    print(f"[CLI] 配音完成: {output_path} ({size_kb:.1f} KB)")
    return True


def api_running():
    try:
        req = urllib.request.Request(f"http://{API_HOST}:{API_PORT}/", method="GET")
        urllib.request.urlopen(req, timeout=3)
        return True
    except urllib.error.HTTPError:
        return True
    except Exception:
        return False


def tts_api(text, voice_name, output_path):
    voice = VOICES[voice_name]
    payload = {
        "refer_wav_path": voice["ref_audio"],
        "prompt_text": voice["ref_text"],
        "prompt_language": "zh",
        "text": text,
        "text_language": "zh",
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"http://{API_HOST}:{API_PORT}/",
        data=data, headers={"Content-Type": "application/json"}, method="POST",
    )
    print(f"[API] 音色: {voice_name}")
    print(f"[API] 文案 ({len(text)} 字): {text[:80]}{'...' if len(text) > 80 else ''}")
    print(f"[API] 正在请求 http://{API_HOST}:{API_PORT}/ ...")
    try:
        resp = urllib.request.urlopen(req, timeout=120)
        audio_data = resp.read()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"[API] HTTP {e.code}: {body[:500]}")
        return False
    except Exception as e:
        print(f"[API] 请求失败: {e}")
        return False

    if len(audio_data) < 1000:
        print(f"[API] 返回数据过小 ({len(audio_data)} bytes)")
        print(audio_data[:500])
        return False

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(audio_data)
    size_kb = len(audio_data) / 1024
    print(f"[API] 配音完成: {output_path} ({size_kb:.1f} KB)")
    return True


def start_api(voice_name="Su"):
    if api_running():
        print(f"[API] 服务已在运行 (http://{API_HOST}:{API_PORT}/)")
        return None
    voice = VOICES[voice_name]
    cmd = [
        PYTHON_EXE, "api.py",
        "-g", voice["gpt"], "-s", voice["sovits"],
        "-dr", voice["ref_audio"], "-dt", voice["ref_text"],
        "-dl", "zh", "-a", API_HOST, "-p", str(API_PORT),
    ]
    print(f"[API] 启动服务，音色: {voice_name}")
    print(f"[API] GPT: {voice['gpt']}")
    print(f"[API] SoVITS: {voice['sovits']}")
    print("[API] 模型加载中（约 30-60 秒）...")
    proc = subprocess.Popen(
        cmd, cwd=GPT_SOVITS_DIR, env=build_env(),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace",
    )
    for i in range(90):
        time.sleep(2)
        if api_running():
            print(f"[API] 服务已就绪: http://{API_HOST}:{API_PORT}/ (PID: {proc.pid})")
            return proc
        if proc.poll() is not None:
            print(f"[API] 进程已退出 (code {proc.returncode})")
            out = proc.stdout.read() if proc.stdout else ""
            print(out[-1500:])
            return None
    print(f"[API] 等待超时，PID: {proc.pid}，可手动检查 http://{API_HOST}:{API_PORT}/")
    return proc


def main():
    parser = argparse.ArgumentParser(
        description="漫剧平台配音集成：文案 -> GPT-SoVITS -> role_voice.wav",
    )
    parser.add_argument("--text", type=str, help="待配音的文案")
    parser.add_argument("--text-file", type=str, help="从文件读取文案（UTF-8）")
    parser.add_argument("--voice", type=str, default="Su", choices=list(VOICES.keys()), help="角色音色")
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT, help="输出 wav 路径")
    parser.add_argument("--mode", type=str, default="auto", choices=["auto", "cli", "api"], help="推理模式")
    parser.add_argument("--start-api", action="store_true", help="后台启动 API 服务")
    args = parser.parse_args()

    if args.start_api:
        start_api(args.voice)
        return

    text = None
    if args.text:
        text = args.text.strip()
    elif args.text_file:
        if not os.path.exists(args.text_file):
            print(f"文件不存在: {args.text_file}")
            sys.exit(1)
        with open(args.text_file, "r", encoding="utf-8") as f:
            text = f.read().strip()

    if not text:
        print("请通过 --text 或 --text-file 提供文案")
        parser.print_help()
        sys.exit(1)

    mode = args.mode
    if mode == "auto":
        mode = "api" if api_running() else "cli"
        print(f"[auto] 使用 {mode} 模式")

    if mode == "api":
        ok = tts_api(text, args.voice, args.output)
    else:
        ok = tts_cli(text, args.voice, args.output)

    if not ok:
        sys.exit(1)
    print(f"\n配音文件已就绪: {args.output}")
    print("可在 ComfyUI 中加载 workflow_manhua_lipsync.json 使用")


if __name__ == "__main__":
    main()