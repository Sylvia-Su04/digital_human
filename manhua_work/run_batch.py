# -*- coding: utf-8 -*-
"""串行提交多个ComfyUI workflow并逐个轮询完成"""
import json, sys, time, urllib.request

BASE = "http://127.0.0.1:8189"

def post(url, data):
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read().decode("utf-8"))

def get(url):
    return json.loads(urllib.request.urlopen(url, timeout=30).read().decode("utf-8"))

def run_one(wf_path):
    wf = json.load(open(wf_path, encoding="utf-8"))
    r = post(BASE + "/prompt", {"prompt": wf})
    pid = r["prompt_id"]
    print(f"[{wf_path}] submitted pid={pid[:12]}", flush=True)
    start = time.time()
    while True:
        time.sleep(20)
        q = get(BASE + "/queue")
        running = [x[1] for x in q["queue_running"]]
        pending = [x[1] for x in q["queue_pending"]]
        if pid not in running and pid not in pending:
            break
        if time.time() - start > 2400:
            print(f"[{wf_path}] TIMEOUT 40min", flush=True)
            return False
    h = get(BASE + f"/history/{pid}")
    if pid in h:
        st = h[pid].get("status", {})
        ok = st.get("status_str") == "success"
        print(f"[{wf_path}] done in {time.time()-start:.0f}s status={st.get('status_str')}", flush=True)
        return ok
    print(f"[{wf_path}] no history entry", flush=True)
    return False

if __name__ == "__main__":
    paths = sys.argv[1:]
    results = {}
    for p in paths:
        results[p] = run_one(p)
    print("SUMMARY:", json.dumps(results, ensure_ascii=False), flush=True)
    sys.exit(0 if all(results.values()) else 1)
