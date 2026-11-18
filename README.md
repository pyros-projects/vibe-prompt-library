# Vibe Prompt Library

Prompts that people published together with what their model built: a single-file game, a soft-body
toy, a shader, a simulation. Each entry shows stills from the result, the prompt word for word and a
link to the source. Live: https://vibe-prompt-library.netlify.app

It exists to find prompts that still separate models. Some prompts saturate: there are only so many
ways to build a better black-hole simulator, so the ceiling is the prompt, not the model. Most entries
say where the room is.

## What is in it

- 113 entries from X, Reddit, the web, GitHub and the 24 briefs of [Trial](https://github.com/pyros-projects/Trial).
- 97 sub-entries: other runs of the same series, each with its own prompt and stills, so the library
  keeps working when an original post is deleted.
- Only posts that show the result and publish the full prompt. Results without a prompt are left out.

Prompts, stills and builds belong to their authors. Every entry links to its source.

## Layout

```text
data/library.jsonl   one entry per line: prompt, stills, source links, sub-entries ("variants")
data/meta.json       collection date and the method notes shown in the page footer
src/template.html    the page; build_page.py injects the data
site/                what gets deployed: index.html and img/
tools/               build and media scripts
```

## Rebuild the page

```bash
uv run --no-project python tools/build_page.py data/library.jsonl data/meta.json src/template.html site/index.html
```

## Add an entry

1. Append a line to `data/library.jsonl` with at least `id`, `venue` (`x`, `reddit`, `web`, `github`
   or `trial`), `title`, `author`, `source_url`, `prompt`, `category` and `media`.
2. Fetch stills (videos give four frames, images are re-encoded to 960 px):

   ```bash
   uv run --no-project python tools/fetch_media.py new.jsonl new-with-stills.jsonl site/img /tmp/stills tools/stills.sh
   ```

   For Reddit videos run `tools/resolve_vreddit.py` first; it swaps `v.redd.it` links for a direct file.
3. Rebuild the page and deploy `site/`.

## Deploy

```bash
netlify deploy --prod --no-build --dir site --site vibe-prompt-library
```
