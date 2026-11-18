"""Give every entry of a candidates JSONL up to four stills in <img_dir>.

Videos: four frames via stills.sh. Images: downloaded and re-encoded to 960px JPEG with ffmpeg.
Entries that already have stills on disk are left alone. Writes the updated JSONL to <out>.
usage: python3 -I fetch_media.py <in.jsonl> <out.jsonl> <img_dir> <tmp_dir> <stills.sh>
"""
import json, os, subprocess, sys, re

src, dst, img_dir, tmp, stills_sh = sys.argv[1:6]
os.makedirs(img_dir, exist_ok=True)
os.makedirs(tmp, exist_ok=True)
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"


def safe(s):
    return re.sub(r"[^A-Za-z0-9_-]", "-", s)[:60]


def have(eid):
    return [f"img/{eid}-{n}.jpg" for n in range(1, 5) if os.path.exists(f"{img_dir}/{eid}-{n}.jpg")]


def get_image(url, out_jpg):
    raw = f"{tmp}/dl-{os.path.basename(out_jpg)}.bin"
    r = subprocess.run(["curl", "-sL", "--max-time", "90", "-A", UA, "-o", raw, "-w", "%{http_code}", url], capture_output=True, text=True)
    if r.stdout.strip() != "200" or not os.path.exists(raw) or os.path.getsize(raw) < 2000:
        return False
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-frames:v", "1", "-vf", "scale='min(960,iw)':-2", "-q:v", "4", out_jpg], capture_output=True, text=True)
    os.remove(raw)
    return r.returncode == 0 and os.path.exists(out_jpg)


out = open(dst, "w")
for line in open(src):
    e = json.loads(line)
    eid = safe(e["id"])
    stills = have(eid)
    if not stills:
        media = e.get("media") or []
        vids = [m for m in media if m.get("type") in ("video", "animated_gif", "gif") and str(m.get("url", "")).split("?")[0].endswith((".mp4", ".webm", ".mov"))]
        if vids:
            subprocess.run(["bash", stills_sh, eid, vids[0]["url"], img_dir, tmp], capture_output=True, text=True)
            stills = have(eid)
        if not stills:
            urls = [m.get("url") for m in media if m.get("type") in ("photo", "image", "gif")]
            urls += [m.get("poster") for m in media if m.get("poster")]
            n = 0
            for u in urls:
                if not u or n >= 4:
                    continue
                if get_image(u, f"{img_dir}/{eid}-{n + 1}.jpg"):
                    n += 1
            stills = have(eid)
    e["stills"] = stills
    print(f'{e["id"]}: {len(stills)} stills', flush=True)
    out.write(json.dumps(e, ensure_ascii=False) + "\n")
