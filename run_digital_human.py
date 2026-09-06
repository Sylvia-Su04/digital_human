# -*- coding: utf-8 -*-
"""
数字人自动化流水线
输入文字 → 生成语音 → 生成人脸视频 → 合并 → 输出完整数字人视频

用法：
    python run_digital_human.py "你想让数字人说的话"
    python run_digital_human.py --text "你想让数字人说的话"
    python run_digital_human.py --file input.txt  # 从文件读取文本
"""

import os
import sys
import subprocess
import configparser
import argparse
import shutil
from datetime import datetime


def load_config(config_path):
    """加载配置文件"""
    config = configparser.ConfigParser()
    config.read(config_path, encoding='utf-8')
    return config


def ensure_dirs(config):
    """确保输出目录和临时目录存在"""
    output_dir = config['paths']['output_dir']
    temp_dir = config['paths']['temp_dir']
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)
    return output_dir, temp_dir


def step1_tts(config, text, temp_dir, run_id):
    """
    第一步：用 GPT-SoVITS 生成语音
    返回生成的语音文件路径
    """
    print("\n" + "="*60)
    print("第一步：生成语音（GPT-SoVITS）")
    print("="*60)

    gpt_sovits_dir = config['paths']['gpt_sovits_dir']
    python_path = config['paths']['python_path']

    # 把参考文本和目标文本写入临时文件
    ref_text_file = os.path.join(temp_dir, f"{run_id}_ref_text.txt")
    target_text_file = os.path.join(temp_dir, f"{run_id}_target_text.txt")

    with open(ref_text_file, 'w', encoding='utf-8') as f:
        f.write(config['tts']['ref_text'])
    with open(target_text_file, 'w', encoding='utf-8') as f:
        f.write(text)

    # 输出目录
    tts_output_dir = os.path.join(temp_dir, f"{run_id}_tts")
    os.makedirs(tts_output_dir, exist_ok=True)

    # 构建命令
    cmd = [
        python_path,
        "GPT_SoVITS/inference_cli.py",
        "--gpt_model", config['tts']['gpt_model'],
        "--sovits_model", config['tts']['sovits_model'],
        "--ref_audio", config['tts']['ref_audio'],
        "--ref_text", ref_text_file,
        "--ref_language", config['tts']['ref_language'],
        "--target_text", target_text_file,
        "--target_language", config['tts']['target_language'],
        "--output_path", tts_output_dir
    ]

    print(f"目标文本: {text}")
    print("正在生成语音...")

    # 执行命令
    result = subprocess.run(
        cmd,
        cwd=gpt_sovits_dir,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    if result.returncode != 0:
        print("❌ 语音生成失败！")
        print("错误信息:", result.stderr[-500:] if result.stderr else "无")
        print("标准输出:", result.stdout[-500:] if result.stdout else "无")
        return None

    # 查找生成的语音文件
    audio_files = []
    for root, dirs, files in os.walk(tts_output_dir):
        for f in files:
            if f.endswith('.wav'):
                audio_files.append(os.path.join(root, f))

    if not audio_files:
        print("❌ 未找到生成的语音文件！")
        print("输出目录内容:", os.listdir(tts_output_dir))
        return None

    # 取最新的文件
    audio_files.sort(key=os.path.getmtime, reverse=True)
    audio_path = audio_files[0]
    print(f"✅ 语音生成成功: {audio_path}")
    return audio_path


def step2_liveportrait(config, temp_dir, run_id):
    """
    第二步：用 LivePortrait 生成人脸视频
    返回生成的视频文件路径
    """
    print("\n" + "="*60)
    print("第二步：生成人脸视频（LivePortrait）")
    print("="*60)

    liveportrait_dir = config['paths']['liveportrait_dir']
    python_path = config['paths']['python_path']

    # 输出目录
    lp_output_dir = os.path.join(temp_dir, f"{run_id}_liveportrait")
    os.makedirs(lp_output_dir, exist_ok=True)

    # 构建命令
    cmd = [
        python_path,
        "inference.py",
        "--source", config['liveportrait']['source_image'],
        "--driving", config['liveportrait']['driving_video'],
        "--output-dir", lp_output_dir,
        "--driving-option", config['liveportrait']['driving_option'],
    ]

    # 布尔参数
    if config['liveportrait'].getboolean('crop_driving'):
        cmd.append("--flag-crop-driving-video")
    if config['liveportrait'].getboolean('stitching'):
        cmd.append("--flag-stitching")
    if config['liveportrait'].getboolean('pasteback'):
        cmd.append("--flag-pasteback")

    # 设置环境变量（onnxruntime 修复）
    env = os.environ.copy()
    env['PYTHONPATH'] = "D:\\ort_fix"
    env['PATH'] = "D:\\conda_envs\\digital_human\\Library\\bin;D:\\conda_envs\\digital_human\\Scripts;D:\\conda_envs\\digital_human;" + env.get('PATH', '')

    print(f"源图片: {config['liveportrait']['source_image']}")
    print(f"驱动视频: {config['liveportrait']['driving_video']}")
    print("正在生成人脸视频...")

    # 执行命令
    result = subprocess.run(
        cmd,
        cwd=liveportrait_dir,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        env=env
    )

    if result.returncode != 0:
        print("❌ 人脸视频生成失败！")
        print("错误信息:", result.stderr[-500:] if result.stderr else "无")
        print("标准输出:", result.stdout[-500:] if result.stdout else "无")
        return None

    # 查找生成的视频文件
    video_files = []
    for root, dirs, files in os.walk(lp_output_dir):
        for f in files:
            if f.endswith('.mp4') and 'concat' not in f:
                video_files.append(os.path.join(root, f))

    if not video_files:
        # 如果没找到非 concat 的，找所有 mp4
        for root, dirs, files in os.walk(lp_output_dir):
            for f in files:
                if f.endswith('.mp4'):
                    video_files.append(os.path.join(root, f))

    if not video_files:
        print("❌ 未找到生成的视频文件！")
        print("输出目录内容:", os.listdir(lp_output_dir))
        return None

    # 取最新的文件
    video_files.sort(key=os.path.getmtime, reverse=True)
    video_path = video_files[0]
    print(f"✅ 人脸视频生成成功: {video_path}")
    return video_path


def step3_wav2lip(config, audio_path, video_path, temp_dir, run_id):
    """
    第三步：用 Wav2Lip 对口型
    返回对口型后的视频路径
    """
    print("\n" + "="*60)
    print("第三步：对口型（Wav2Lip）")
    print("="*60)

    # 检查是否启用对口型
    if not config.has_section('wav2lip') or not config['wav2lip'].getboolean('enable_lipsync', fallback=False):
        print("⏭️  对口型未启用，跳过")
        return video_path

    wav2lip_dir = config['wav2lip']['wav2lip_dir']
    checkpoint_path = config['wav2lip']['checkpoint_path']
    python_path = config['paths']['python_path']

    # 检查模型文件
    if not os.path.exists(checkpoint_path):
        print(f"⚠️  Wav2Lip 模型不存在: {checkpoint_path}")
        print("   跳过对口型，直接使用原视频")
        print("   如需对口型，请下载模型到上述路径")
        return video_path

    # 输出路径
    lipsync_output = os.path.join(temp_dir, f"{run_id}_lipsync.mp4")

    # 构建命令
    cmd = [
        python_path,
        "inference.py",
        "--checkpoint_path", checkpoint_path,
        "--face", video_path,
        "--audio", audio_path,
        "--outfile", lipsync_output,
        "--batch_size", "1",
    ]

    # 设置环境变量
    env = os.environ.copy()
    env['PYTHONPATH'] = wav2lip_dir

    print(f"输入视频: {video_path}")
    print(f"输入音频: {audio_path}")
    print("正在对口型...")

    # 执行命令
    result = subprocess.run(
        cmd,
        cwd=wav2lip_dir,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        env=env
    )

    if result.returncode != 0 or not os.path.exists(lipsync_output):
        print("❌ 对口型失败！使用原视频")
        print("错误信息:", result.stderr[-500:] if result.stderr else "无")
        return video_path

    file_size = os.path.getsize(lipsync_output) / (1024 * 1024)
    print(f"✅ 对口型成功: {lipsync_output}")
    print(f"文件大小: {file_size:.2f} MB")
    return lipsync_output


def get_duration(file_path, ffmpeg_path):
    """获取媒体文件时长（秒）"""
    import subprocess as sp
    ffprobe_path = ffmpeg_path.replace('ffmpeg.exe', 'ffprobe.exe')
    if not os.path.exists(ffprobe_path):
        ffprobe_path = 'ffprobe'
    result = sp.run([
        ffprobe_path, '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        file_path
    ], capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except:
        return 0


def step3_merge(config, audio_path, video_path, output_dir, run_id):
    """
    第三步：合并语音和视频（视频自动循环到音频长度）
    返回最终视频文件路径
    """
    print("\n" + "="*60)
    print("第三步：合并语音和视频")
    print("="*60)

    ffmpeg_path = config['paths']['ffmpeg_path']
    output_prefix = config['merge']['output_prefix']
    output_path = os.path.join(output_dir, f"{output_prefix}_{run_id}.mp4")

    print(f"语音: {audio_path}")
    print(f"视频: {video_path}")

    # 获取时长，计算需要循环多少次
    audio_duration = get_duration(audio_path, ffmpeg_path)
    video_duration = get_duration(video_path, ffmpeg_path)
    print(f"语音时长: {audio_duration:.1f} 秒，视频时长: {video_duration:.1f} 秒")

    if video_duration > 0 and audio_duration > video_duration:
        # 需要循环视频
        loop_count = int(audio_duration / video_duration) + 1
        print(f"视频需要循环 {loop_count} 次")

        # 创建 concat 列表文件
        temp_dir = os.path.dirname(video_path)
        list_file = os.path.join(temp_dir, f"loop_list_{run_id}.txt")
        looped_video = os.path.join(temp_dir, f"looped_{run_id}.mp4")

        with open(list_file, 'w', encoding='utf-8') as f:
            for _ in range(loop_count):
                f.write(f"file '{video_path}'\n")

        # 拼接循环视频
        print("正在循环拼接视频...")
        concat_cmd = [
            ffmpeg_path, "-y",
            "-f", "concat", "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            looped_video
        ]
        result = subprocess.run(concat_cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')

        if result.returncode != 0 or not os.path.exists(looped_video):
            print("⚠️  视频循环失败，使用原视频合并")
            looped_video = video_path
        else:
            print("✅ 视频循环完成")

        # 合并音频和循环后的视频
        print("正在合并...")
        merge_cmd = [
            ffmpeg_path, "-y",
            "-i", looped_video,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            output_path
        ]
        result = subprocess.run(merge_cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')

        # 清理临时文件
        for f in [list_file, looped_video]:
            if f != video_path and os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass
    else:
        # 视频比音频长，直接合并
        print("正在合并...")
        cmd = [
            ffmpeg_path, "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')

    if result.returncode != 0 or not os.path.exists(output_path):
        print("❌ 合并失败！")
        print("错误信息:", result.stderr[-500:] if result.stderr else "无")
        return None

    file_size = os.path.getsize(output_path) / (1024 * 1024)
    final_duration = get_duration(output_path, ffmpeg_path)
    print(f"✅ 合并成功: {output_path}")
    print(f"文件大小: {file_size:.2f} MB，时长: {final_duration:.1f} 秒")
    return output_path


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='数字人自动化流水线')
    parser.add_argument('text', nargs='?', help='要让数字人说的话')
    parser.add_argument('--text', dest='text_opt', help='要让数字人说的话')
    parser.add_argument('--file', help='从文件读取文本')
    parser.add_argument('--config', default='digital_human_config.ini', help='配置文件路径')
    args = parser.parse_args()

    # 获取文本
    text = args.text or args.text_opt
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            text = f.read().strip()

    if not text:
        print("❌ 请提供要让数字人说的话！")
        print("用法: python run_digital_human.py \"你想说的话\"")
        print("或:   python run_digital_human.py --file input.txt")
        sys.exit(1)

    # 加载配置
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.config)
    if not os.path.exists(config_path):
        config_path = args.config
    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在: {config_path}")
        sys.exit(1)

    config = load_config(config_path)
    output_dir, temp_dir = ensure_dirs(config)

    # 生成运行 ID
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("\n" + "🚀"*30)
    print("数字人自动化流水线启动")
    print(f"运行 ID: {run_id}")
    print(f"目标文本: {text}")
    print("🚀"*30)

    # 第一步：生成语音
    audio_path = step1_tts(config, text, temp_dir, run_id)
    if not audio_path:
        print("\n❌ 语音生成失败，流水线终止！")
        sys.exit(1)

    # 第二步：生成人脸视频
    video_path = step2_liveportrait(config, temp_dir, run_id)
    if not video_path:
        print("\n❌ 人脸视频生成失败，流水线终止！")
        sys.exit(1)

    # 第三步：合并
    final_path = step3_merge(config, audio_path, video_path, output_dir, run_id)
    if not final_path:
        print("\n❌ 合并失败，流水线终止！")
        sys.exit(1)

    # 完成
    print("\n" + "🎉"*30)
    print("✅ 数字人视频生成完成！")
    print(f"📁 输出文件: {final_path}")
    print("🎉"*30)

    # 清理临时文件（可选，默认保留以便调试）
    # shutil.rmtree(os.path.join(temp_dir, f"{run_id}_tts"), ignore_errors=True)
    # shutil.rmtree(os.path.join(temp_dir, f"{run_id}_liveportrait"), ignore_errors=True)


if __name__ == "__main__":
    main()
