# -*- coding: utf-8 -*-
"""ComfyUI workflow 提交与轮询脚本。
用法: python comfy_submit.py <workflow.json>
可选: --nodeid.field=value 逐个覆盖节点参数 (重复多次)
示例: python comfy_submit.py wf.json 2.text="masterpiece ..." 12.seed=777
"""
import json
import sys
import time
import urllib.request

BASE = "http://127.0.0.1:8189"


def post(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    return json.loads(urllib.request.urlopen(req, timeout=60).read().decode("utf-8"))


def get(url):
    return json.loads(urllib.request.urlopen(url, timeout=30).read().decode("utf-8"))


def main():
    args = sys.argv[1:]
    wf_path = args[0]
    with open(wf_path, encoding="utf-8") as f:
        wf = json.load(f)

    for arg in args[1:]:
        if "=" not in arg:
            continue
        k, _, v = arg.partition("=")
        node_id, _, field = k.partition(".")
        if node_id in wf and field in wf[node_id]["inputs"]:
            cur = wf[node_id]["inputs"][field]
            if isinstance(cur, bool):
                wf[node_id]["inputs"][field] = v.lower() in ("true", "1")
            elif isinstance(cur, (int, float)):
                try:
                    wf[node_id]["inputs"][field] = float(v) if "." in v else int(v)
                except ValueError:
                    wf[node_id]["inputs"][field] = v
            else:
                wf[node_id]["inputs"][field] = v
            print(f"set {node_id}.{field} = {v[:80]}")
        else:
            print(f"WARN: {node_id}.{field} not found in workflow")

    r = post(BASE + "/prompt", {"prompt": wf})
    pid = r.get("prompt_id")
    if not pid:
        print("ERROR:", json.dumps(r, ensure_ascii=False))
        sys.exit(1)
    print("prompt_id:", pid)

    t0 = time.time()
    while True:
        time.sleep(4)
        try:
            h = get(BASE + "/history/" + pid)
        except Exception as e:
            print("\nhistory err:", e)
            continue
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("completed") or st.get("status_str") == "success":
                print("\nDONE in %.0fs" % (time.time() - t0))
                for nid, out in h[pid].get("outputs", {}).items():
                    for kk, vv in out.items():
                        print("OUTPUT node%s %s: %s" % (nid, kk, json.dumps(vv, ensure_ascii=False)))
                break
            if st.get("status_str") in ("error", "failed"):
                print("\nFAILED:", json.dumps(st, ensure_ascii=False)[:1000])
                sys.exit(2)
        else:
            if time.time() - t0 > 900:
                print("\nTIMEOUT after 900s")
                sys.exit(3)
            print(".", end="", flush=True)


if __name__ == "__main__":
    main()
