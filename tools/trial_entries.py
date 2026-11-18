"""Build one library entry per Trial task: verbatim prompt.md, up to four model screenshots labelled with the model.
usage: python3 -I trial_entries.py <trial-data.json> <out.jsonl> <img_dir> <tmp_dir>
"""
import json, os, subprocess, sys, urllib.request

data_path, out_path, img_dir, tmp = sys.argv[1:5]
d = json.load(open(data_path))
origin = "https://trial-by-pyro.netlify.app"  # screenshots live on the showcase, not on artifact_origin
NAMES = {"anthropic_opus55": "Claude Opus 5.5", "anthropic_opus5": "Claude Opus 5", "gpt-6.1_sol": "GPT-6.1 Sol",
         "gpt-6_astra": "GPT-6 Astra", "google_gemini3.8_flash": "Gemini 3.8 Flash", "xai_grok4.6": "Grok 4.6",
         "zai_glm5.3_flash": "GLM-5.3 Flash", "alibaba_qwen3.8_flash": "Qwen3.8 Flash", "devin_swe2": "Devin SWE-2"}
ORDER = ["anthropic_opus55", "gpt-6.1_sol", "gpt-6_astra", "google_gemini3.8_flash", "xai_grok4.6", "zai_glm5.3_flash",
         "alibaba_qwen3.8_flash", "anthropic_opus5", "devin_swe2"]
CAT = {"01": "simulation", "02": "simulation", "03": "music", "04": "simulation", "05": "3d-scene", "06": "simulation",
       "07": "simulation", "08": "tool", "09": "toy", "10": "game", "11": "game", "12": "game", "13": "game",
       "14": "simulation", "15": "tool", "16": "game", "17": "game", "18": "simulation", "19": "tool", "20": "simulation",
       "21": "tool", "22": "tool", "23": "tool", "24": "other"}
by_task = {}
for r in d["results"]:
    if r["artifact"].get("exists"):
        by_task.setdefault(r["task_id"], []).append(r)
out = open(out_path, "w")
for task in sorted(by_task):
    rows = sorted(by_task[task], key=lambda r: ORDER.index(r["model_key"]) if r["model_key"] in ORDER else 99)
    prompt = urllib.request.urlopen(f"https://raw.githubusercontent.com/pyros-projects/Trial/main/prompts/{task}/prompt.md").read().decode()
    title = next((l[2:].strip() for l in prompt.splitlines() if l.startswith("# ")), rows[0]["task_title"])
    eid = f"trial-{task}"
    stills, labels = [], []
    for r in rows:
        if len(stills) == 4:
            break
        shot = r["artifact"].get("screenshot_url")
        if not shot:
            continue
        n = len(stills) + 1
        raw, jpg = f"{tmp}/{eid}-{n}.bin", f"{img_dir}/{eid}-{n}.jpg"
        if not os.path.exists(jpg):
            subprocess.run(["curl", "-sL", "--max-time", "60", "-o", raw, origin + shot], check=False)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-frames:v", "1", "-vf", "scale='min(960,iw)':-2", "-q:v", "4", jpg], check=False)
            if os.path.exists(raw):
                os.remove(raw)
        if os.path.exists(jpg):
            stills.append(f"img/{eid}-{n}.jpg"); labels.append(NAMES.get(r["model_key"], r["model_key"]))
    models = [NAMES.get(r["model_key"], r["model_key"]) for r in rows]
    out.write(json.dumps({
        "id": eid, "venue": "trial", "title": title, "author": "Pyro", "category": CAT.get(task[:2], "other"),
        "source_url": f"https://trial-by-pyro.netlify.app/compare/{task}/",
        "prompt_url": f"https://github.com/pyros-projects/Trial/blob/main/prompts/{task}/prompt.md",
        "demo_url": f"https://trial-by-pyro.netlify.app/compare/{task}/",
        "date": min(r["modified_at"] for r in rows)[:10], "models": models, "claim": f"Trial task {task[:2]} · {len(rows)} builds",
        "engagement": {}, "prompt": prompt, "stills": stills, "still_labels": labels,
        "notes": f"Pyro's own Trial brief. {len(rows)} models built it; the comparison page runs every build live.",
    }, ensure_ascii=False) + "\n")
    print(task, len(rows), "builds,", len(stills), "stills")
