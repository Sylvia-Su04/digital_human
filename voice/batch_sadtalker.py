# -*- coding: utf-8 -*-
"""批量跑 14 页数字人口播：ComfyUI API 提交 -> 轮询 -> 从 SadTalker output 目录取最新 mp4 -> voice\\N.mp4"""
import json, os, io, sys, time, shutil, urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

API = 'http://127.0.0.1:8189'
WF = r'D:\digital_human\ComfyUI\workflow_manhua_lipsync.json'
SAD_OUT = r'D:\digital_human\ComfyUI\custom_nodes\Comfyui-SadTalker\SadTalker\output'
VOICE = r'D:\digital_human\voice'
LOG = os.path.join(VOICE, 'batch_log.txt')

MAPPING = {
    1: '1A.wav',
    13: '5B.wav',
}

base_wf = json.load(open(WF, encoding='utf-8'))

def log(msg):
    line = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def snapshot():
    s = set()
    for d in os.listdir(SAD_OUT):
        for dp, dn, fn in os.walk(os.path.join(SAD_OUT, d)):
            for f in fn:
                s.add(os.path.join(dp, f))
    return s

def submit(audio):
    wf = json.loads(json.dumps(base_wf))
    wf['1']['inputs']['image'] = 'digital_human.png'
    wf['2']['inputs']['audio'] = audio
    req = urllib.request.Request(API + '/prompt', data=json.dumps({'prompt': wf}).encode('utf-8'),
                                 headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode())['prompt_id']

def wait_done(pid, timeout=900):
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(15)
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
    return None  # timeout

def run_page(pageno, audio):
    dst = os.path.join(VOICE, f'{pageno}.mp4')
    if os.path.exists(dst) and os.path.getsize(dst) > 10000:
        log(f'page {pageno}: already exists, skip')
        return 'skip'
    before = snapshot()
    log(f'--- page {pageno} audio={audio} ---')
    pid = submit(audio)
    log(f'  submitted {pid}')
    ok = wait_done(pid)
    if not ok:
        log(f'  page {pageno}: failed (ok={ok})')
        return 'fail'
    # 找快照后新增的 mp4
    cands = []
    for f in snapshot() - before:
        if f.lower().endswith('.mp4'):
            cands.append(f)
    cands.sort(key=os.path.getmtime, reverse=True)
    if not cands:
        log(f'  page {pageno}: no new mp4 found in SadTalker output')
        return 'no-output'
    src = cands[0]
    shutil.copy2(src, dst)
    log(f'  OK {os.path.basename(src)} -> {dst} ({os.path.getsize(dst)/1024:.0f}KB)')
    return 'ok'

def main():
    results = []
    for pageno in sorted(MAPPING):
        r = run_page(pageno, MAPPING[pageno])
        results.append((pageno, r))
    log('=== ALL DONE === ' + str(results))

if __name__ == '__main__':
    main()
