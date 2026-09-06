"""
分段生成语音并拼接，避免长文本漏字
用命令行调用 GPT-SoVITS/inference_cli.py
"""
import sys
import os
import subprocess
import shutil

# 配置
gpt_sovits_dir = r'D:\digital_human\GPT-SoVITS'
python_path = r'D:\conda_envs\digital_human\python.exe'
gpt_model = r'GPT_weights_v2Pro/Su_emotional-e15.ckpt'
sovits_model = r'SoVITS_weights_v2Pro/Su_e4_s148.pth'
ref_audio = r'D:\digital_human\ref_clip.wav'
ref_text = '加油呀，你已经很棒了，真的。'
ref_language = '中文'
target_language = '中文'
ffmpeg_path = r'D:\conda_envs\digital_human\Library\bin\ffmpeg.exe'

# 分段文件
segments = [
    r'D:\digital_human\汇报_第1段.txt',
    r'D:\digital_human\汇报_第2段.txt',
    r'D:\digital_human\汇报_第3段.txt',
]

output_dir = r'D:\digital_human\temp\segmented_tts'
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir, exist_ok=True)

# 写入参考文本文件
ref_text_file = os.path.join(output_dir, 'ref_text.txt')
with open(ref_text_file, 'w', encoding='utf-8') as f:
    f.write(ref_text)

audio_files = []

# 分段生成语音
for i, seg_file in enumerate(segments):
    print(f"\n{'='*60}")
    print(f"生成第 {i+1} 段语音...")
    print(f"{'='*60}")

    with open(seg_file, 'r', encoding='utf-8') as f:
        text = f.read().strip()
    print(f"文本: {text[:60]}...")

    # 目标文本文件
    target_text_file = os.path.join(output_dir, f'target_{i+1}.txt')
    with open(target_text_file, 'w', encoding='utf-8') as f:
        f.write(text)

    # 输出目录
    seg_output_dir = os.path.join(output_dir, f'segment_{i+1}')
    os.makedirs(seg_output_dir, exist_ok=True)

    # 构建命令
    cmd = [
        python_path,
        "GPT_SoVITS/inference_cli.py",
        "--gpt_model", gpt_model,
        "--sovits_model", sovits_model,
        "--ref_audio", ref_audio,
        "--ref_text", ref_text_file,
        "--ref_language", ref_language,
        "--target_text", target_text_file,
        "--target_language", target_language,
        "--output_path", seg_output_dir
    ]

    # 环境变量
    env = os.environ.copy()
    env['PYTHONPATH'] = r'D:\ort_fix;' + gpt_sovits_dir
    env['PATH'] = r'D:\conda_envs\digital_human\Library\bin;D:\conda_envs\digital_human\Scripts;D:\conda_envs\digital_human;' + env.get('PATH', '')

    # 执行命令
    result = subprocess.run(
        cmd,
        cwd=gpt_sovits_dir,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        env=env
    )

    if result.returncode != 0:
        print(f"❌ 第 {i+1} 段语音生成失败！")
        print("错误信息:", result.stderr[-500:] if result.stderr else "无")
        print("标准输出:", result.stdout[-500:] if result.stdout else "无")
        sys.exit(1)

    # 查找生成的语音文件
    seg_audio_files = []
    for root, dirs, files in os.walk(seg_output_dir):
        for f in files:
            if f.endswith('.wav'):
                seg_audio_files.append(os.path.join(root, f))

    if not seg_audio_files:
        print(f"❌ 第 {i+1} 段未找到生成的语音文件！")
        sys.exit(1)

    seg_audio_files.sort(key=os.path.getmtime, reverse=True)
    audio_file = seg_audio_files[0]
    audio_files.append(audio_file)
    file_size = os.path.getsize(audio_file) / 1024
    print(f"✅ 第 {i+1} 段完成: {audio_file} ({file_size:.1f} KB)")

# 拼接语音
print(f"\n{'='*60}")
print("拼接三段语音...")
print(f"{'='*60}")

# 创建 concat 列表
list_file = os.path.join(output_dir, 'concat_list.txt')
with open(list_file, 'w', encoding='utf-8') as f:
    for audio_file in audio_files:
        f.write(f"file '{audio_file}'\n")

final_audio = os.path.join(output_dir, 'final_combined.wav')
concat_cmd = [
    ffmpeg_path, '-y',
    '-f', 'concat', '-safe', '0',
    '-i', list_file,
    '-c', 'copy',
    final_audio
]
result = subprocess.run(concat_cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')

if result.returncode == 0 and os.path.exists(final_audio):
    file_size = os.path.getsize(final_audio) / 1024
    print(f"✅ 语音拼接完成: {final_audio} ({file_size:.1f} KB)")

    # 获取时长
    ffprobe_path = ffmpeg_path.replace('ffmpeg.exe', 'ffprobe.exe')
    duration_result = subprocess.run([
        ffprobe_path, '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        final_audio
    ], capture_output=True, text=True)
    try:
        duration = float(duration_result.stdout.strip())
        print(f"⏱️  总时长: {duration:.1f} 秒 ({duration/60:.2f} 分钟)")
    except:
        pass

    # 复制到最终位置
    final_output = r'D:\digital_human\temp\final_combined_voice.wav'
    shutil.copy2(final_audio, final_output)
    print(f"\n📁 最终语音文件: {final_output}")
else:
    print("❌ 语音拼接失败")
    print(result.stderr[-500:] if result.stderr else "无错误信息")
    sys.exit(1)

print("\n🎉 分段语音生成完成！")
