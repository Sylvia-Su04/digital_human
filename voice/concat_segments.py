# -*- coding: utf-8 -*-
import subprocess, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

FF = r'D:\conda_envs\digital_human\Library\bin\ffmpeg.exe'
VOICE = r'D:\digital_human\voice'

def concat(files, out):
    if not all(os.path.exists(f) for f in files):
        return False
    n = len(files)
    fc_parts = []
    for i, f in enumerate(files):
        fc_parts.append(f'[{i}:a]aformat=sample_rates=32000:channel_layouts=mono[a{i}]')
    fc_parts.append(''.join(f'[a{i}]' for i in range(n)) + f'concat=n={n}:v=0:a=1[a]')
    fc = ';'.join(fc_parts)
    cmd = [FF, '-y',
           '-i', files[0], '-i', files[1]] + (['-i', files[2]] if n == 3 else []) + [
        '-filter_complex', fc, '-map', '[a]', '-ar', '32000', '-ac', '1',
        out]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        print('FAIL', out, r.stderr[-600:])
        return False
    print('OK', out, f'{os.path.getsize(out)/1024:.0f}KB')
    return True

concat([os.path.join(VOICE, '2A.wav'), os.path.join(VOICE, '2B.wav'), os.path.join(VOICE, '2C.wav')], os.path.join(VOICE, '2.wav'))
concat([os.path.join(VOICE, '3A.wav'), os.path.join(VOICE, '3B.wav'), os.path.join(VOICE, '3C.wav')], os.path.join(VOICE, '3.wav'))
