# -*- coding: utf-8 -*-
"""单段测试：提交页1（1A.wav），轮询直到完成，输出到 voice\\1.mp4。"""
import json, os, io, sys, time, shutil, urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

API = 'http://127.0.0.1:8189'
WF = r'D:\digital_human\ComfyUI\workflow_manhua_lipsync.json'
OUTPUT_DIR = r'D:\digital_human\ComfyUI\output'
SAD_OUT = r'D:\digital_human\ComfyUI\custom_nodes\Comfyui-SadTalker\SadTalker\output'
VOICE = r'D:\digital_human\voice'
PAGE = 1
AUDIO = '1A.wav'

base_wf = json.load(open(WF, encoding='utf-8'))
base_wf['1']['inputs']['image'] = 'digital_human.png'
base_wf['2']['inputs']['audio'] = AUDIO

payload = json.dumps({'prompt': base_wf}).encode('utf-8')
req = urllib.request.Request(API + '/prompt', data=payload, headers={'Content-Type': 'application/json'})
pid = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())['prompt_id']
print('submitted prompt_id:', pid, flush=True)

t0 = time.time()
while time.time() - t0 < 600:
    time.sleep(15)
    el = int(time.time() - t0)
    try:
        h = json.loads(urllib.request.urlopen(API + f'/history/{pid}', timeout=10).read().decode())
    except Exception:
        print(f'[{el}s] history query failed', flush=True)
        continue
    if pid in h:
        st = h[pid].get('status', {})
        if st.get('status_str') == 'success' or st.get('completed'):
            print(f'[{el}s] SUCCESS', flush=True)
            outs = h[pid].get('outputs', {})
            found = []
            for nid, o in outs.items():
                for k in o:
                    if k == 'ui':
                        continue
                    found.append((nid, k, o[k]))
            print('outputs:', json.dumps(found, ensure_ascii=False)[:600], flush=True)
            break
        if st.get('status_str') == 'error':
            print(f'[{el}s] ERROR', flush=True)
            for m in st.get('messages', []):
                if isinstance(m, list) and m and m[0] == 'execution_error':
                    print(json.dumps(m[1], ensure_ascii=False)[:1200], flush=True)
            break
    else:
        print(f'[{el}s] still running...', flush=True)
else:
    print('TIMEOUT after 600s', flush=True)

# 检查 SadTalker 输出目录有没有新 mp4
print('--- recent files in SadTalker output ---', flush=True)
for d in sorted(os.listdir(SAD_OUT), key=lambda x: os.path.getmtime(os.path.join(SAD_OUT, x)), reverse=True)[:3]:
    p = os.path.join(SAD_OUT, d)
    print(time.strftime('%H:%M:%S', time.localtime(os.path.getmtime(p))), d, flush=True)
    for dp, dn, fn in os.walk(p):
        for f in fn:
            fp = os.path.join(dp, f)
            print('   ', time.strftime('%H:%M:%S', time.localtime(os.path.getmtime(fp))), f'{os.path.getsize(fp)/1024:.0f}KB', f, flush=True)
