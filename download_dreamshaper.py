import urllib.request, os, sys, time

url = "https://hf-mirror.com/digiplay/DreamShaper_8/resolve/main/dreamshaper_8.safetensors"
dest = r"D:\digital_human\ComfyUI\models\checkpoints\dreamshaper_8.safetensors"
tmp = dest + ".part"
total = 2132625894


def download():
    existing = os.path.getsize(tmp) if os.path.exists(tmp) else 0
    if existing >= total:
        os.replace(tmp, dest)
        print("\nAlready complete.")
        return
    print("\nResuming from {} MB".format(existing / 1048576))
    req = urllib.request.Request(url, headers={"Range": "bytes={}-".format(existing)})
    mode = "ab" if existing > 0 else "wb"
    with urllib.request.urlopen(req, timeout=60) as resp, open(tmp, mode) as f:
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
            done = f.tell()
            pct = done * 100.0 / total
            sys.stdout.write("\r{:.1f}%  {:.0f}/{:.0f} MB".format(pct, done / 1048576, total / 1048576))
            sys.stdout.flush()
    os.replace(tmp, dest)
    print("\nDone: {} bytes ({:.2f} GB)".format(os.path.getsize(dest), os.path.getsize(dest) / 1073741824))


for attempt in range(15):
    try:
        download()
        break
    except Exception as e:
        print("\n[retry {}] {}".format(attempt + 1, e))
        time.sleep(3)
