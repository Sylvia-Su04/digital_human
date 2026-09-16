# -*- coding: utf-8 -*-
import subprocess, os, io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
FFP = r'D:\conda_envs\digital_human\Library\bin\ffprobe.exe'
d = r'D:\digital_human\voice'
for f in sorted(os.listdir(d)):
    if f.endswith('.wav') and len(f) >= 4 and f[1].isdigit():
        p = os.path.join(d, f)
        r = subprocess.run([FFP, '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', p],
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        try:
            dur = float(json.loads(r.stdout)['format']['duration'])
            print(f'{f}: {dur:.1f}s')
        except Exception:
            print(f'{f}: ?')
