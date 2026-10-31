"""Export the homepage draft (drafts/home) as a self-contained preview that
also bundles the pricing pages, so each service card opens its own page.

usage: python tools/export_draft.py OUT_DIR   (run export_previews.py first;
it reads OUT_DIR/pricing). Writes OUT_DIR/draft and draft-files-N.json."""
import json, re, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import export_previews as ep

ROOT, OUT = ep.ROOT, Path(sys.argv[1])
out = OUT / 'draft'
if out.exists():
    shutil.rmtree(out)
(out / 'img').mkdir(parents=True)

s = (ROOT / 'drafts/home/index.html').read_text(encoding='utf-8')
used = set(re.findall(r'url\((/img/[^)]+)\)', s))
s = re.sub(r'<img [^>]*>', lambda m: ep.pick_src(m.group(0), used), s)
s = ep.strip_for_preview(s)


def link(m):
    p = m.group(1).split('#')[0].rstrip('/') or '/'
    if p.startswith(('/css', '/js', '/img')):
        return m.group(0)
    if p == '/pricing':
        return 'href="pricing.html"'
    if p.startswith('/pricing/'):
        return 'href="' + p.strip('/').replace('/', '__') + '.html"'
    g = 'portfolio' if p.startswith('/portfolio') else 'main'
    return f'href="{ep.URLS[g]}" target="_blank" rel="noopener"'


s = re.sub(r'href="(/[^"]*)"', link, s)
s = ep.relink_assets(s)
(out / 'index.html').write_text(ep.as_fragment(s, 'Homepage Draft'), encoding='utf-8')
for u in used:
    shutil.copy(ROOT / u.lstrip('/'), out / 'img')
(out / 'site.css').write_text(ep.preview_css(), encoding='utf-8')
shutil.copy(ROOT / 'js/site.js', out / 'site.js')

# bring the pricing preview pages along
PR = OUT / 'pricing'
for f in PR.iterdir():
    if f.suffix == '.html':
        t = f.read_text(encoding='utf-8').replace('href="index.html"', 'href="pricing.html"')
        if f.name == 'index.html':  # the group's front page is a fragment; give it a full skeleton again
            i = t.index('<div style="background:#783f04')
            head = '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            t = head + t[:i] + '\n</head>\n<body>\n' + t[i:] + '\n</body>\n</html>\n'
        (out / ('pricing.html' if f.name == 'index.html' else f.name)).write_text(t, encoding='utf-8')
for f in (PR / 'img').iterdir():
    if not (out / 'img' / f.name).exists():
        shutil.copy(f, out / 'img')

ep.write_lists(out, 'draft')
