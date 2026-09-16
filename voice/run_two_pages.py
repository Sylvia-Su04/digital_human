# -*- coding: utf-8 -*-
"""等现有页1任务完成 -> 复制为 voice\\1.mp4 -> 提交页13(5B.wav) -> 复制为 voice\\13.mp4"""
import json, os, io, sys, time, shutil, urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

API = 'http://127.0.0.1:8189'
WF = r'D:\digital_human\ComfyUI\workflow_manhua_lipsync.json'
SAD_OUT = r'D:\digital_human\ComfyUI\custom_nodes\Comfyui-SadTalker\SadTalker\output'
VOICE = r'D:\digital_human\voice'
PAGE1_PID = '4fbb3930-2853-4ed7-950b-000d28d2e20b'

base_wf = json.load(open(WF, encoding='utf-8'))

def log(msg):
    print(f'[{time.strftime("%H:%M:%S")}] {msg}', flush=True)
    with open(os.path.join(VOICE, 'batch_log.txt'), 'a', encoding='utf-8') as f:
        f.write(f'[{time.strftime("%H:%M:%S")}] {msg}\n')

def snapshot():
    s = set()
    for d in os.listdir(SAD_OUT):
        for dp, dn, fn in os.walk(os.path.join(SAD_OUT, d)):
            for f in fn:
                s.add(os.path.join(dp, f))
    return s

def wait_done(pid, timeout=1800):
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(20)
        try:
            h = json.loads(urllib.request.urlopen(API + f'/history/{pid}', timeout=10).read().decode())
        except Exception:
            continue
        if pid not in h:
            continue
        st = h[pid].get('status', {})
        if st.get('status_str') == 'success' or st.get('completed'):
            return True
        if st.get('status_str') == 'error':
            for m in st.get('messages', []):
                if isinstance(m, list) and m and m[0] == 'execution_error':
                    log('  ERROR: ' + json.dumps(m[1], ensure_ascii=False)[:600])
            return False
    return None

def submit(audio):
    wf = json.loads(json.dumps(base_wf))
    wf['1']['inputs']['image'] = 'digital_human.png'
    wf['2']['inputs']['audio'] = audio
    req = urllib.request.Request(API + '/prompt', data=json.dumps({'prompt': wf}).encode('utf-8'),
                                 headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode())['prompt_id']

def grab_new_mp4(before, dst):
    cands = []
    for f in snapshot() - before:
        if f.lower().endswith('.mp4'):
            cands.append(f)
    cands.sort(key=os.path.getmtime, reverse=True)
    if not cands:
        log(f'  no new mp4 for {os.path.basename(dst)}')
        return False
    shutil.copy2(cands[0], dst)
    log(f'  OK -> {dst} ({os.path.getsize(dst)/1024:.0f}KB)')
    return True

# --- 段1：等页1任务完成 ---
log('waiting page-1 task 4fbb3930...')
ok1 = wait_done(PAGE1_PID)
log(f'page-1 done: {ok1}')
before = snapshot()
if ok1:
    grab_new_mp4(before, os.path.join(VOICE, '1.mp4'))

# --- 段2：提交页6 (3A.wav) ---
log('submitting page-6 (3A.wav)...')
before = snapshot()
pid13 = submit('3A.wav')
log(f'  submitted {pid13}')
ok13 = wait_done(pid13, timeout=1800)
log(f'page-6 done: {ok13}')
if ok13:
    grab_new_mp4(before, os.path.join(VOICE, '6.mp4'))
log('=== FINISHED ===')
