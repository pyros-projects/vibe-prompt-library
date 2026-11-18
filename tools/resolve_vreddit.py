"""Rewrite v.redd.it media URLs to a direct CMAF mp4 that answers 200. usage: resolve_vreddit.py <in.jsonl> <out.jsonl>"""
import json, subprocess, sys
out = open(sys.argv[2], "w")
for line in open(sys.argv[1]):
    e = json.loads(line)
    for m in e.get("media") or []:
        u = str(m.get("url") or "")
        if "v.redd.it" in u and not u.endswith(".mp4"):
            base = u.rstrip("/")
            for f in ("CMAF_1080.mp4", "CMAF_720.mp4", "CMAF_480.mp4", "CMAF_360.mp4"):
                code = subprocess.run(["curl", "-s", "-o", "/dev/null", "-r", "0-1023", "-w", "%{http_code}", "-A", "Mozilla/5.0", f"{base}/{f}"], capture_output=True, text=True).stdout
                if code in ("200", "206"):
                    m["page_url"] = u; m["url"] = f"{base}/{f}"; break
    out.write(json.dumps(e, ensure_ascii=False) + "\n")
