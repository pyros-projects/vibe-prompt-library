"""Inject the curated entries and the method notes into the page template.
usage: python3 -I build_page.py <final.jsonl> <meta.json> <template.html> <out.html>
"""
import json, sys

final, meta, tpl, out = sys.argv[1:5]
entries = [json.loads(l) for l in open(final) if l.strip()]
keep = ["id", "venue", "title", "author", "source_url", "prompt_url", "date", "models", "claim", "engagement",
        "prompt", "stills", "still_labels", "demo_url", "category", "headroom_note", "variants", "notes"]
vkeep = ["id", "title", "author", "source_url", "prompt_url", "date", "models", "caption", "engagement", "prompt", "stills", "demo_url", "notes"]
slim = lambda d, ks: {k: d.get(k) for k in ks if d.get(k) not in (None, "", [], {})}
for e in entries:
    e["variants"] = [slim(v, vkeep) for v in e.get("variants") or []]
entries = [slim(e, keep) | {"prompt": e["prompt"]} for e in entries]
dump = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")
html = open(tpl).read().replace("/*__DATA__*/null", dump(entries)).replace("/*__META__*/null", dump(json.load(open(meta))))
open(out, "w").write(html)
print(f"{len(entries)} entries, {len(html) // 1024} KB")
