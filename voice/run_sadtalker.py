# -*- coding: utf-8 -*-
"""通过 ComfyUI API 串行跑 workflow_manhua_lipsync.json，输出复制为 voice\\N.mp4"""
import json, os, io, sys, time, shutil, urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

API = 'http://127.0.0.1:8189'
WF = r'D:\digital_human\ComfyUI\workflow_manhua_lipsync.json'
INPUT_DIR = r'D:\digital_human\ComfyUI\input'
OUTPUT_DIR = r'D:\digital_human\ComfyUI\output'
VOICE = r'D:\digital_human\voice'

# 页码 -> 音频文件名（ComfyUI input 目录内）
MAPPING = {
    1: '1A.wav', 2: '1B.wav',
    4: '2A.wav', 5: '2B.wav', 6: '2C.wav',
    7: '3A.wav', 8: '3B.wav', 9: '3C.wav',
    10: '4A.wav', 12: '4B.wav',
    13: '5A.wav', 14: '5B.wav',
}

base_wf = json.load(open(WF, encoding='utf-8'))

def post_prompt(pageno, audio_file):
    wf = json.loads(json.dumps(base_wf))
    wf['1']['inputs']['image'] = 'digital_human.png'
    wf['2']['inputs']['audio'] = audio_file
    payload = json.dumps({'prompt': wf}).encode('utf-8')
    req = urllib.request.Request(API + '/prompt', data=payload,
                                 headers={'Content-Type': 'application/json'})
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read().decode())['prompt_id']
    except Exception as e:
        print(f'  [submit fail] page {pageno}: {e}')
        return None

def wait_done(pid, timeout=1800):
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(15)
        try:
            h = json.loads(urllib.request.urlopen(API + f'/history/{pid}', timeout=10).read().decode())
        except Exception:
            continue
        if pid not in h:
            continue
        item = h[pid]
        st = item.get('status', {})
        if st.get('completed') or st.get('status_str') == 'success':
            return item
        if st.get('status_str') == 'error':
            msgs = st.get('messages', [])
            for m in msgs:
                if isinstance(m, list) and m and m[0] == 'execution_error':
                    print('  [error]', json.dumps(m[1], ensure_ascii=False)[:800])
            return None
    print('  [timeout]')
    return None

def find_video_output(item):
    outs = item.get('outputs', {})
    for nid, o in outs.items():
        for key in ('video', 'gifs', 'images', 'audio'):
            for f in (o.get(key) or []):
                fn = f.get('filename', '')
                if fn:
                    return fn, f.get('subfolder', ''), key
    return None, '', ''

def main():
    results = []
    for pageno in sorted(MAPPING):
        audio = MAPPING[pageno]
        dst = os.path.join(VOICE, f'{pageno}.mp4')
        if os.path.exists(dst) and os.path.getsize(dst) > 10000:
            print(f'page {pageno}: already exists, skip')
            results.append((pageno, 'skip'))
            continue
        print(f'--- page {pageno} audio={audio} {time.strftime("%H:%M:%S")} ---', flush=True)
        pid = post_prompt(pageno, audio)
        if not pid:
            results.append((pageno, 'submit-fail'))
            continue
        item = wait_done(pid)
        if not item:
            results.append((pageno, 'error/timeout'))
            continue
        fn, sub, key = find_video_output(item)
        if not fn:
            print(f'  [no video output] page {pageno}, outputs keys: {list(item.get("outputs", {}).keys())}')
            results.append((pageno, 'no-output'))
            continue
        src = os.path.join(OUTPUT_DIR, sub, fn) if sub else os.path.join(OUTPUT_DIR, fn)
        if not os.path.exists(src):
            print(f'  [file missing] {src}')
            results.append((pageno, 'file-missing'))
            continue
        shutil.copy2(src, dst)
        print(f'  [OK] {src} -> {dst} ({os.path.getsize(dst)/1024:.0f}KB)', flush=True)
        results.append((pageno, 'ok'))
    print('=== DONE ===', results)

if __name__ == '__main__':
    main()
