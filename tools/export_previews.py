"""Export the built site into three self-contained preview folders for the
claude.ai preview links (each link holds at most ~500 files, so the site is
split into main / pricing / portfolio groups that link to each other).

usage: python tools/export_previews.py OUT_DIR
Writes OUT_DIR/<group>/... plus OUT_DIR/<group>-files-N.json upload lists
(each publish takes at most 255 files, so images are chunked)."""
import json, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(sys.argv[1])
URLS = json.loads((ROOT / 'tools/preview_urls.json').read_text())
GROUPS = {
    'main': ['/', '/dc-wedding-photographer', '/reviews', '/faq', '/contact'],
    'pricing': ['/pricing', '/pricing/weddings-elopements', '/pricing/weddings-films', '/pricing/engagements-couples',
                '/pricing/tea-ceremonies', '/pricing/family-portraits', '/pricing/boudoir-self-love'],
    'portfolio': ['/portfolio', '/portfolio/weddings-elopements', '/portfolio/couples-engagements', '/portfolio/families',
                  '/portfolio/maternity-newborn', '/portfolio/headshots-seniors', '/portfolio/pet-portraits'],
}
TITLES = {'main': 'Alice Tran Photography Preview', 'pricing': 'Photography Pricing Preview', 'portfolio': 'Photography Portfolio Preview'}
BANNER = ('<div style="background:#783f04;color:#fff;text-align:center;font:14px/1.45 Georgia,serif;'
          'padding-block:.6rem;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))">'
          'Preview of the new site. Main pages, Pricing and Portfolio are three linked previews, so some menu links open a new tab.</div>')
group_of = {p: g for g, ps in GROUPS.items() for p in ps}


def fname(path, group):
    return 'index.html' if path == GROUPS[group][0] else path.strip('/').replace('/', '__') + '.html'


def src_file(path):
    return ROOT / 'index.html' if path == '/' else ROOT / path.strip('/') / 'index.html'


def pick_src(tag, used):
    """Drop srcset, keep the largest size up to 1280px, record the file used."""
    ss = re.search(r'srcset="([^"]*)"', tag)
    if ss:
        opts = [(int(w[:-1]), u) for u, w in (p.strip().split() for p in ss.group(1).split(','))]
        fit = [o for o in opts if o[0] <= 1280] or opts[:1]
        tag = re.sub(r'\s(srcset|sizes)="[^"]*"', '', tag)
        tag = re.sub(r'src="[^"]*"', f'src="{max(fit)[1]}"', tag)
    u = re.search(r'src="(/img/[^"]+)"', tag)
    if u:
        used.add(u.group(1))
    return tag


def strip_for_preview(s):
    s = re.sub(r'<script async src="https://www.googletagmanager[^<]*</script>\s*<script>window.dataLayer[^<]*</script>', '', s)
    s = re.sub(r'<link rel="icon"[^>]*>', '', s)
    # films: the preview cannot embed YouTube, link out instead
    s = re.sub(r'<button class="yt" data-id="([^"]+)"[^>]*aria-label="(?:Play )?([^"]*)"[^>]*>.*?</button>',
               lambda m: f'<a class="yt-link" href="https://www.youtube.com/watch?v={m.group(1)}" target="_blank" rel="noopener">&#9654; Watch {m.group(2) or "the film"} on YouTube</a>', s, flags=re.S)
    s = re.sub(r'<iframe[^>]*docs\.google\.com/forms.*?</iframe>',
               '<p class="center"><a class="btn" href="https://docs.google.com/forms/d/e/1FAIpQLSdAuHfk0kl7DzZuXduRZJl450rubKy3tqARX4tzfbsI2Sv6wA/viewform" target="_blank" rel="noopener">Open the contact form</a></p>'
               '<p class="center" style="font-size:.9rem">On the real site this form appears right here on the page.</p>', s, flags=re.S)
    return s


def relink_assets(s):
    return (s.replace('"/img/', '"img/').replace('url(/img/', 'url(img/')
             .replace('href="/css/site.css"', 'href="site.css"').replace('src="/js/site.js"', 'src="site.js"'))


def preview_css():
    css = (ROOT / 'css/site.css').read_text(encoding='utf-8').replace('position: sticky; top: 0;', 'position: sticky; top: env(safe-area-inset-top, 0px);')
    css += ('\n.yt-link{display:flex;align-items:center;justify-content:center;aspect-ratio:16/9;max-width:100%;background:var(--dark);color:#fff;'
            'text-decoration:none;font:400 1rem var(--display-sc);letter-spacing:.08em;border-radius:var(--radius);padding:1rem;text-align:center}\n'
            '.yt-link:hover{background:var(--brown);color:#fff}\n')
    return css


def as_fragment(s, title):
    """The artifact's own page gets a document skeleton at publish time, so strip ours."""
    head = re.search(r'<head>(.*?)</head>', s, re.S).group(1)
    head = re.sub(r'<meta (charset|name="viewport"|name="robots")[^>]*>', '', head)
    head = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', head)
    body = re.search(r'<body>(.*)</body>', s, re.S).group(1)
    return head.strip() + '\n' + body


def write_lists(out, prefix):
    files = sorted(p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file() and p.name != 'index.html')
    pages = [f for f in files if not f.startswith('img/')]
    imgs = [f for f in files if f.startswith('img/')]
    chunks = [pages + imgs[:240]] + [imgs[i:i + 250] for i in range(240, len(imgs), 250)]
    for i, c in enumerate(chunks):
        (OUT / f'{prefix}-files-{i}.json').write_text(json.dumps([{'path': f} for f in c]))
    size = sum((out / f).stat().st_size for f in files) / 1048576
    print(f'{prefix}: {len(files)} files, {size:.1f} MB, chunks {[len(c) for c in chunks]}')


def export_group(group, paths):
    out = OUT / group
    if out.exists():
        shutil.rmtree(out)
    (out / 'img').mkdir(parents=True)
    used = set()

    def link(m):
        href = m.group(1)
        path, _, frag = href.partition('#')
        path = path.rstrip('/') or '/'
        g = group_of.get(path)
        if g is None:
            return m.group(0)
        if g == group:
            return f'href="{fname(path, group)}{"#" + frag if frag else ""}"'
        return f'href="{URLS[g]}" target="_blank" rel="noopener"'

    for path in paths:
        s = src_file(path).read_text(encoding='utf-8')
        used |= set(re.findall(r'url\((/img/[^)]+)\)', s))
        s = re.sub(r'<img [^>]*>', lambda m: pick_src(m.group(0), used), s)
        s = strip_for_preview(s)
        s = re.sub(r'href="(/[^"]*)"', link, s)
        s = relink_assets(s)
        s = s.replace('<body>', '<body>\n' + BANNER, 1)
        if fname(path, group) == 'index.html':
            s = as_fragment(s, TITLES[group])
        (out / fname(path, group)).write_text(s, encoding='utf-8')
    for u in used:
        shutil.copy(ROOT / u.lstrip('/'), out / 'img')
    (out / 'site.css').write_text(preview_css(), encoding='utf-8')
    shutil.copy(ROOT / 'js/site.js', out / 'site.js')
    write_lists(out, group)


if __name__ == '__main__':
    for g, ps in GROUPS.items():
        export_group(g, ps)
