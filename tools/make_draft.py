"""Write src/pages/drafts/home.html: the homepage redesign draft, built from
the live homepage's photo sections plus new wording. Draft pages are
gitignored and never part of the live site.

usage: python tools/make_draft.py && python tools/build.py drafts/home"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
src = (ROOT / 'src/pages/index.html').read_text(encoding='utf-8')


def between(a, b):
    i = src.index(a); j = src.index(b, i); return src[i:j] + b


slideshow = between('<section class="slideshow"', '</section>')
grid1 = between('<section class="section">\n  [[grid page="home" from="31"', '</section>')
grid2 = between('<section class="section">\n  [[grid page="home" from="56"', '</section>')
reviews = between('<section class="section reviews">', '</section>')
reviews = reviews.replace(
    '<h2 class="sans-title">Kind words from my awesome clients</h2>',
    '<p class="eyebrow">Reviews</p>\n  <h2 class="sans-title">Kind words from my awesome clients</h2>')
grid1 = grid1.replace('[[grid page="home" from="31"',
    '<div class="section-head"><p class="eyebrow">Recent work</p><h2 class="sans-title">A few favorites</h2></div>\n  [[grid page="home" from="31"')
grid2 = grid2.replace('[[grid page="home" from="56"',
    '<div class="section-head"><p class="eyebrow">Portraits</p><h2 class="sans-title">Families, couples &amp; more</h2></div>\n  [[grid page="home" from="56"')

META = '<!-- {"title": "Homepage Draft | Alice Tran Photography", "description": "Draft of the redesigned Alice Tran Photography homepage for review. Not part of the live site.", "canonical": "/drafts/home", "og_image": "home_003", "head_extra": "<meta name=\\"robots\\" content=\\"noindex\\">"} -->'

STYLE = """<style>
/* Draft-only styles. If approved, these move into css/site.css. */
.draft-note { background: var(--mustard); color: var(--cocoa); text-align: center; font-size: .9rem; padding: .5rem 16px; }
.hero-actions { padding: 1.6rem 16px 1.2rem; display: flex; flex-direction: column; align-items: center; gap: 1.2rem; }
.hero-btns { display: flex; flex-wrap: wrap; gap: .8rem; justify-content: center; }
.hero-btns .btn { font-weight: 700; padding: .85em 2em; }
.hero-home .hero-tagline { text-shadow: 0 1px 12px rgba(255,255,255,.6); }
.intro-band p { max-width: 640px; margin: .9rem auto 0; font-size: 1.05rem; color: var(--cocoa); }
.services { display: grid; gap: 22px; }
@media (min-width: 600px) { .services { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 960px) { .services { grid-template-columns: repeat(3, 1fr); } }
.service { display: flex; flex-direction: column; background: var(--white); border-radius: 6px; overflow: hidden; border: 1px solid #eadfc8; text-decoration: none; color: var(--ink); transition: transform .2s, box-shadow .2s; }
.service:hover { transform: translateY(-3px); box-shadow: 0 12px 30px rgba(90,56,24,.14); color: var(--ink); }
.service img { width: 100%; aspect-ratio: 4 / 3; object-fit: cover; }
.service-body { padding: 1.1rem 1.2rem 1.3rem; display: flex; flex-direction: column; gap: .35rem; flex: 1; }
.service h3 { font: 400 1.25rem/1.2 var(--display); color: var(--cocoa); }
.service .from { font-size: .9rem; color: var(--muted); margin: 0; }
.service .from b { color: var(--mustard-dk); font-size: 1.05rem; }
.service .link { margin-top: auto; padding-top: .6rem; font: 400 .82rem/1.2 var(--display); font-variant: small-caps; letter-spacing: .14em; color: var(--brown); }
.service:hover .link { color: var(--mustard-dk); }
.welcome-text p { font-size: 1.04rem; }
.welcome-text h2 { text-align: left; margin-bottom: 1rem; }
.welcome-text .lead { font-size: 1.15rem; color: var(--cocoa); }
</style>"""

HERO = """[[header]]
<div class="draft-note">Draft for review only. The live site is unchanged. Photos are the same as today; the words, headings and buttons around them are new.</div>

<section class="hero hero-home">
  [[img src="home_003" alt="Couple kissing in front of the Washington Monument at sunset" sizes="100vw" class="hero-img" eager]]
  <div class="hero-content">
    [[img src="home_004" max="1280" alt="Alice Tran Photography" sizes="(min-width: 960px) 520px, 80vw" class="hero-logo" eager]]
    <h1 class="hero-tagline">Based in Washington DC &amp; Los Angeles<span>Serving Clients Worldwide</span></h1>
  </div>
</section>

<div class="hero-actions">
  <div class="hero-btns">
    <a class="btn" href="/portfolio">View Portfolio</a>
    <a class="btn btn-light" href="/contact">Book a Session</a>
  </div>
  [[social]]
</div>

<section class="paper banner intro-band">
  <h2 class="caps-title">Vibrant, Candid &amp; Emotion-Filled<br>Photographs &amp; Films</h2>
  <p>Weddings, engagements, families and portraits, photographed the way they felt. Honest moments first, posed photos second, and plenty of the silly in-between ones.</p>
</section>
"""

SIZES = '(min-width: 960px) 30vw, (min-width: 600px) 48vw, 100vw'
cards = [
    ('/pricing/weddings-elopements', 'pricing_010', 'Bride and groom in front of a modern glass building', 'Weddings &amp; Elopements', 'Intimate from <b>$2,000</b>, full day from <b>$5,000</b>', 'See wedding packages'),
    ('/pricing/weddings-films', 'pricing_012', 'Wedding party holding white parasols', 'Wedding Films', 'From <b>$3,500</b>, $500 off when bundled with photos', 'See film packages'),
    ('/pricing/engagements-couples', 'pricing_011', 'Couple kissing by a creek in autumn', 'Engagements &amp; Couples', 'From <b>$950</b>', 'See engagement packages'),
    ('/pricing/tea-ceremonies', 'pricing_013', 'Couple in traditional Korean wedding attire at a Paebaek ceremony', 'Tea Ceremonies &amp; Paebaek', 'From <b>$2,000</b> for up to 2 hours', 'See tea ceremony packages'),
    ('/pricing/family-portraits', 'pricing_014', 'Family portrait photograph by Alice Tran Photography', 'Family, Maternity &amp; Portraits', 'From <b>$500</b>', 'See portrait packages'),
    ('/pricing/boudoir-self-love', 'pricing_015', 'Boudoir photograph by Alice Tran Photography', 'Boudoir &amp; Self-Love', 'From <b>$950</b>', 'See boudoir packages'),
]
SERVICES = '''
<section class="paper section">
  <div class="section-head">
    <p class="eyebrow">What I photograph</p>
    <h2 class="sans-title">Sessions &amp; starting prices</h2>
    <p>Every collection can be customized. Tap a card to see full packages and what's included.</p>
  </div>
  <div class="services">
''' + '\n'.join(
    f'    <a class="service" href="{h}">[[img src="{img}" alt="{alt}" sizes="{SIZES}"]]<div class="service-body"><h3>{t}</h3><p class="from">{f}</p><span class="link">{l}</span></div></a>'
    for h, img, alt, t, f, l in cards) + '''
  </div>
</section>
'''

WELCOME = """
<section class="section welcome">
  <div class="welcome-text">
    <p class="eyebrow">Meet your photographer</p>
    <h2 class="sans-title">Hi, I'm Alice!</h2>
    <p class="lead">I'm a Washington DC and Los Angeles wedding photographer, and I am so happy you are here.</p>
    <p>To me, it has been a privilege to connect with everyone I've had a chance to photograph. My goal is to capture those raw, honest, and authentic emotions so that twenty years from now, you can look back on these photos and still remember exactly how that moment felt.</p>
    <p>I hope I'm the photographer you are looking for: someone you can trust to capture the real you, and to make you feel comfortable enough to fully express yourself, even that silly, quirky and awkward side. I can't wait to meet you and your loved ones and create incredible artworks together!</p>
    <p><a class="btn btn-outline" href="/dc-wedding-photographer">More about Alice</a></p>
  </div>
  <div class="welcome-photo">[[img src="home_043" alt="Beach portrait by Alice Tran Photography" sizes="(min-width: 960px) 40vw, 100vw"]]</div>
</section>
"""

HOW = """
<section class="paper section">
  <div class="section-head">
    <p class="eyebrow">How it works</p>
    <h2 class="sans-title">Booking is simple</h2>
    <p>Three steps from "hello" to your finished gallery.</p>
  </div>
  <ol class="how">
    <li><span class="num">1</span><h3>Say hello</h3><p>Send a quick inquiry with your date and what you have in mind. I reply within 24 to 48 hours and we hop on a phone call to make sure we're a good fit.</p></li>
    <li><span class="num">2</span><h3>Pick your collection</h3><p>Choose the package that fits, sign the contract and pay a 50% retainer to lock in your date. All packages can be customized.</p></li>
    <li><span class="num">3</span><h3>Show up and have fun</h3><p>I'll bring my camera and take care of the rest. Soon after, a sneak peek lands in your inbox, followed by your full gallery to relive it all.</p></li>
  </ol>
  <p class="center" style="margin-top:2rem"><a class="btn" href="/contact">Book a Session</a></p>
</section>
"""

page = '\n'.join([META, STYLE, HERO, slideshow, grid1, SERVICES, WELCOME, reviews, HOW, grid2, '[[portfolio-tiles]]', '[[footer]]', ''])
(ROOT / 'src/pages/drafts').mkdir(parents=True, exist_ok=True)
(ROOT / 'src/pages/drafts/home.html').write_text(page, encoding='utf-8')
print('draft written:', page.count('[[img'), 'img tokens,', page.count('[[grid'), 'grids, em dash:', '—' in page)
