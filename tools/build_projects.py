#!/usr/bin/env python3
"""Generate /work/<slug>/index.html project pages and the homepage carousel.

Edit PROJECTS below, then run:  python3 tools/build_projects.py
Carousel order = PROJECTS order (max 9). Icons: tools/icons.json (Simple Icons, CC0).
"""
import json, html, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS = json.load(open(os.path.join(ROOT, 'tools', 'icons.json')))

LAUREL_SEL = '<img class="laurel" src="/assets/img/laurel-nyciff-2026.png" alt="Official Selection, New York City Independent Film Festival 2026" width="800" height="518">'
LAUREL_RH = '<img class="laurel laurel-rh" src="/assets/img/laurel-ravenheart-2022.png" alt="Official Selection, Ravenheart International Film Festival 2022" width="600" height="351">'
LAUREL_FM = '<img class="laurel" src="/assets/img/laurel-filmocracy-2020.png" alt="Official Selection, Filmocracy Fest 2020" width="600" height="389">'
LAUREL_LF10 = '<img class="laurel" src="/assets/img/laurel-litchfield-2010.png" alt="Official Selection, Litchfield Hills Film Festival 2010" width="600" height="480">'
LAUREL_ACT = '<img class="laurel laurel-award" src="/assets/img/laurel-nyciff-2026-best-actress.png" alt="Winner, Best Actress — Leah Eckardt, New York City Independent Film Festival 2026" width="401" height="348">'

# watch: (label, icon key, url, note)
PROJECTS = [
    dict(slug='golden', title='Golden', kind='Feature', year='2026',
         still='golden-doorway.jpg', pos='50% 80%', laurel='sel',
         alt='Golden — a couple talks in sunlight, framed by tall open doors',
         logline='Suddenly stranded in Rome, an American filmmaker meets a heartbroken young woman and invites her to join him on a trip through the Italian countryside.',
         credit='Directed by Mehran C. Torgoley',
         honors=['Official Selection — NYC Independent Film Festival 2026',
                 'Winner — Best Actress in a Narrative Feature, Leah Eckardt'],
         video=('yt', 'GkRgk2qgmxU'), video_label='Official trailer',
         status='Now on the festival circuit. Distribution to be announced.',
         gallery=[('golden-leah.jpg', 'Leah Eckardt in Golden', 'act')],
         watch=[]),
    dict(slug='curse-of-aurore', title='Curse of Aurore', kind='Feature', year='2020',
         still='curse-of-aurore.jpg', pos='50% 60%', laurel='rh',
         alt='Curse of Aurore — two filmmakers hold a candlelit séance in a stone cellar',
         logline='A thumb drive from the dark web holds the last footage of three American filmmakers who went to rural Quebec to research a century-old child murder.',
         credit='Directed by Mehran C. Torgoley · Found-footage horror · Freestyle Digital Media',
         honors=['Official Selection — Ravenheart International Film Festival 2022',
                 'Winner — Best Actress, Llana Barron — Ravenheart 2022',
                 'Opened #1 at Cinémas Guzzo, Quebec'],
         video=('yt', '_koawiiqMwI'), video_label='Official trailer',
         watch=[('Prime Video', 'generic', 'https://watch.amazon.com/detail?gti=amzn1.dv.gti.42bb2662-0fc9-f78a-24e5-07cf8e0f9942', 'Included with Prime · rent or buy'),
                ('Tubi', 'tubi', 'https://tubitv.com/movies/618715', 'Free with ads'),
                ('The Roku Channel', 'roku', 'https://app.roku.com/details/b43a2c778a9e50c995a51dc7a1165583/curse-of-aurore', 'Free with ads'),
                ('Apple TV', 'appletv', 'https://tv.apple.com/us/movie/curse-of-aurore/umc.cmc.tgxvy3ig9ki8vc4di2a1at9r', 'Rent or buy'),
                ('Fandango at Home', 'fandango', 'https://athome.fandango.com/content/browse/details/Curse-of-Aurore/1546925', 'Free with ads · rent or buy'),
                ('Hoopla', 'generic', 'https://www.hoopladigital.com/title/13903883', 'Free with a library card')]),
    dict(slug='izzy-lyon', title='Izzy Lyon: The Unspun Truth', short='Izzy Lyon', kind='Feature', year='2022',
         still='izzy-lyon.jpg', pos='50% 40%', laurel='fm',
         alt='Izzy Lyon — Phil LaMarr and his puppet in matching pink shirts',
         logline='Twenty years after the world’s greatest sign spinner vanished, his most devoted fans band together to restore his legacy.',
         credit='Directed by Mehran C. Torgoley & Dan Lanigan · Mockumentary · With Phil LaMarr, David Koechner, Greg Proops · Octane Multimedia',
         honors=['Official Selection — Filmocracy Fest 2020'],
         video=('yt', '8bKuW3BRQKg'), video_label='Official trailer',
         watch=[('Prime Video', 'generic', 'https://watch.amazon.com/detail?gti=amzn1.dv.gti.017d2ef2-9e5a-4c53-93f0-a27403da2dc5', 'Included with Prime · rent or buy'),
                ('Tubi', 'tubi', 'https://tubitv.com/movies/100003313', 'Free with ads'),
                ('YouTube', 'youtube', 'https://www.youtube.com/watch?v=UyVYUc5WLoI', 'Rent or buy'),
                ('Apple TV', 'appletv', 'https://tv.apple.com/us/movie/izzy-lyon-the-unspun-truth/umc.cmc.5bk9pyod30xia7fzj1pc4k3rn', 'Rent or buy'),
                ('Google Play', 'googleplay', 'https://play.google.com/store/movies/details/Izzy_Lyon_The_Unspun_Truth?id=9gRKfwoQwcA.P', 'Rent or buy'),
                ('Fandango at Home', 'fandango', 'https://athome.fandango.com/content/browse/details/Izzy-Lyon-The-Unspun-Truth/2129462', 'Free with ads · rent or buy')]),
    dict(slug='room-enough', title='Room Enough', kind='Short film', year='2010',
         still='room-enough.jpg', pos='30% 50%', laurel='lf10',
         alt='Room Enough — a bare bulb on a pull chain in a dark room',
         logline='Watching a clone with his exact memories—and none of his baggage—publish his book and live his life better than he ever could, a burnt-out diner worker confronts the quiet sting of becoming obsolete in his own skin.',
         credit='Written, directed and edited by Mehran C. Torgoley · Inspired by a story by Isaac Marion',
         honors=['Official Selection — Litchfield Hills Film Festival 2010'], video=('yt', 'cFR2GDF-agg'), video_label='Full film',
         watch=[('YouTube', 'youtube', 'https://www.youtube.com/watch?v=cFR2GDF-agg', 'Free')]),
    dict(slug='dirty-laundry', title='Dirty Laundry', kind='Short film', year='2013',
         still='dirty-laundry.jpg', pos='50% 50%',
         alt='Dirty Laundry — a woman smokes beside a dryer’s round window',
         logline='Beneath the sterile hum of a laundry room, a sharp-dressed woman cleans away evidence of…something, and methodically crosses another name off a hit list.',
         credit='Directed by Mehran C. Torgoley',
         honors=[], video=('yt', 'Zje8UmMOOXU'), video_label='Full film',
         watch=[('YouTube', 'youtube', 'https://www.youtube.com/watch?v=Zje8UmMOOXU', 'Free')]),
    dict(slug='broken-arrow', title='Broken Arrow', kind='Music video', year='', artist='Llana Barron',
         still='broken-arrow.jpg', pos='50% 40%',
         alt='Broken Arrow — singer drawing a bow in front of a target',
         logline=None, credit='Directed by Mehran C. Torgoley',
         honors=[], video=('yt', 'yQFaheUgMhA'), video_label='Music video',
         watch=[('YouTube', 'youtube', 'https://www.youtube.com/watch?v=yQFaheUgMhA', 'Free')]),
    dict(slug='the-queen', title='The Queen', kind='Music video', year='', artist='Kai Elle',
         still='the-queen.jpg', pos='50% 50%',
         alt='The Queen — singer in a red jacket in an empty subway car',
         logline=None, credit='Directed by Mehran C. Torgoley',
         honors=[], video=('yt', 'cNxJkNInNvM'), video_label='Music video',
         watch=[('YouTube', 'youtube', 'https://www.youtube.com/watch?v=cNxJkNInNvM', 'Free')]),
    dict(slug='raise-hell', title='Raise Hell', kind='Music video', year='', artist='Caiikie',
         still='raise-hell.jpg', pos='50% 50%',
         alt='Raise Hell — singer screaming behind the wheel at night',
         logline=None, credit='Directed by Mehran C. Torgoley',
         honors=[], video=('yt', '9PFCAwCi3kw'), video_label='Music video',
         watch=[('YouTube', 'youtube', 'https://www.youtube.com/watch?v=9PFCAwCi3kw', 'Free')]),
    dict(slug='already-gone', title='Already Gone', kind='Music video', year='', artist='MCKNY ft. Bizzy Bone',
         still='already-gone.jpg', pos='50% 50%',
         alt='Already Gone — a woman outside a white building with a blue door',
         logline=None, credit='Directed by Mehran C. Torgoley',
         honors=[], video=('vimeo', 'https://vimeo.com/numbir9/alreadygonev2'), video_label='Music video',
         watch=[('Vimeo', 'vimeo', 'https://vimeo.com/numbir9/alreadygonev2', 'Free')]),
]

E = html.escape
PLAY = '<span class="play"><svg viewBox="0 0 12 14" aria-hidden="true"><path d="M1 1l10 6-10 6z" fill="currentColor"/></svg></span>'


def icon(key):
    return f'<svg class="wicon" viewBox="0 0 24 24" aria-hidden="true"><path d="{ICONS[key]}" fill="currentColor"/></svg>'


SECTION = {'Feature': '/features/', 'Short film': '/shorts/', 'Music video': '/music-videos/'}


def nav(p=None, current=None):
    cur = current or (SECTION.get(p['kind']) if p else None)
    links = [('/#work', 'Work'), ('/features/', 'Features'), ('/shorts/', 'Shorts'), ('/music-videos/', 'Music videos'), ('/#about', 'About'), ('/contact/', 'Contact')]
    return ''.join(f'<a href="{h}"{" aria-current=\"page\"" if h == cur else ""}>{t}</a>' for h, t in links)


TAGS = {'Feature': 'Feature Film', 'Short film': 'Short Film', 'Music video': 'Music Video'}


def tag(p):
    return f'<span class="ptag">{TAGS.get(p["kind"], p["kind"])}</span>'


def meta_line(p):
    bits = [p['kind']]
    if p.get('artist'): bits.append(p['artist'])
    if p.get('year'): bits.append(p['year'])
    return ' — '.join(bits)


LAURELS = {'sel': LAUREL_SEL, 'act': LAUREL_ACT, 'rh': LAUREL_RH, 'fm': LAUREL_FM, 'lf10': LAUREL_LF10}


def laurel_for(p):
    # one key -> single laurel; a list of keys -> stacked top to bottom, never overlapping
    k = p.get('laurel')
    if isinstance(k, (list, tuple)):
        return '<div class="lstack">' + ''.join(LAURELS[x] for x in k) + '</div>'
    return LAURELS.get(k, '')


def page(p, nxt):
    t = E(p['title'])
    player = ''
    if p['video']:
        kind, ref = p['video']
        attr = f'data-yt="{ref}"' if kind == 'yt' else f'data-vimeo="{ref}"'
        player = (f'<div class="player project-player" {attr} data-title="{t}">'
                  f'<button aria-label="Play {t} — {E(p["video_label"])}">'
                  f'<img src="/assets/img/{p["still"]}" alt="" style="object-position:{p["pos"]}">{laurel_for(p)}{tag(p)}{PLAY}</button></div>'
                  f'<p class="mono vlabel">{E(p["video_label"])}</p>')
    else:
        player = (f'<div class="project-still"><img src="/assets/img/{p["still"]}" alt="{E(p["alt"])}" style="object-position:{p["pos"]}">'
                  f'{laurel_for(p)}{tag(p)}</div>')
    gallery = ''
    for img, alt, lau in p.get('gallery', []):
        lt = LAUREL_ACT if lau == 'act' else LAUREL_SEL if lau == 'sel' else ''
        gallery += f'<figure class="project-gallery"><img src="/assets/img/{img}" alt="{E(alt)}" loading="lazy">{lt}</figure>'
    honors = ''.join(f'<li>{E(h)}</li>' for h in p['honors'])
    honors = f'<ul class="laurels mono">{honors}</ul>' if honors else ''
    log = f'<p class="logline">{E(p["logline"])}</p>' if p.get('logline') else ''
    status = f'<p class="status mono">{E(p["status"])}</p>' if p.get('status') else ''
    if p['watch']:
        items = ''.join(
            f'<li><a href="{E(u)}" target="_blank" rel="noopener">{icon(ic)}<span class="wname">{E(n)}</span>'
            f'<span class="wnote mono">{E(note)}</span><span class="warr" aria-hidden="true">↗</span></a></li>'
            for n, ic, u, note in p['watch'])
        watch = f'<aside class="watch"><h2 class="mono">Where to watch</h2><ul>{items}</ul></aside>'
    else:
        watch = '<aside class="watch"><h2 class="mono">Where to watch</h2><p class="mono empty">Coming soon.</p></aside>'
    title_html = t if len(p['title']) < 14 else t.replace(': ', ':<br>')
    og = f'https://mehrantorgoley.com/assets/img/{"golden-doorway-og.jpg" if p["slug"] == "golden" else p["still"]}'
    desc = p.get('logline') or f'{p["title"]} — {meta_line(p)}, directed by Mehran C. Torgoley.'
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t} — Mehran C. Torgoley</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="https://mehrantorgoley.com/work/{p['slug']}/">
<meta property="og:title" content="{t} — Mehran C. Torgoley">
<meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0B0B0B">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/anton-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/site.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>

<header class="site-header">
  <a class="brand" href="/">MEHRAN C. TORGOLEY</a>
  <button class="menu-btn" aria-label="Menu" aria-expanded="false" aria-controls="nav"><span></span><span></span></button>
  <nav class="nav" id="nav">
    {nav(p)}
  </nav>
</header>

<main id="main">
  <section class="page-head project-head">
    <h1 class="display"><span class="mask"><span>{title_html}</span></span></h1>
    <span class="mono">{E(meta_line(p))}</span>
  </section>

  <section class="wrap">
    {player}
  </section>

  <section class="wrap project-body">
    <div class="project-info">
      {log}
      <p class="credit mono">{E(p['credit'])}</p>
      {honors}
      {status}
    </div>
    {watch}
  </section>
  {f'<section class="wrap">{gallery}</section>' if gallery else ''}

  <section class="wrap next-project">
    <a href="/work/{nxt['slug']}/"><span class="mono">Next project</span><span class="display">{E(nxt.get('short', nxt['title']))} <span class="arrow">→</span></span></a>
  </section>
</main>

<footer class="contact" id="contact">
  <a class="big display" href="/contact/" style="font-size:clamp(56px,6.6vw,96px)">Let’s make<br>something <span class="arrow">→</span></a>
  <div class="foot">
    <a class="mail" href="mailto:hello@mehrantorgoley.com">hello@mehrantorgoley.com</a>
    <span class="mono" data-clock>California</span>
    <span class="links"><a href="https://www.imdb.com/name/nm1977604/" rel="noopener">IMDb</a><a href="https://vimeo.com/numbir9" rel="noopener">Vimeo</a></span>
  </div>
</footer>

<script src="/assets/js/site.js"></script>
</body>
</html>
'''


def carousel():
    slides = []
    for i, p in enumerate(PROJECTS[:9]):
        cap = ' — '.join(x for x in [p.get('short', p['title']), p.get('artist'), p.get('year')] if x)
        load = 'fetchpriority="high"' if i == 0 else 'loading="lazy"'
        slides.append(
            f'    <a class="slide{" on" if i == 0 else ""}" href="/work/{p["slug"]}/" data-cap="{E(cap)}" aria-label="{E(p["title"])} — view project"{"" if i == 0 else " tabindex=\"-1\""}>'
            f'<img src="/assets/img/{p["still"]}" alt="{E(p["alt"])}" {load} style="object-position:{p["pos"]}">{laurel_for(p)}{tag(p)}</a>')
    n = len(slides)
    first_cap = re.search(r'data-cap="([^"]*)"', slides[0]).group(1)
    return ('  <div class="reel carousel" aria-roledescription="carousel" aria-label="Selected projects">\n'
            + '\n'.join(slides) + '\n'
            '    <div class="scan"></div>\n'
            f'    <div class="cap mono"><span class="cap-t">{first_cap}</span>'
            f'<span class="cnav"><button class="cprev" type="button" aria-label="Previous project">←</button>'
            f'<span class="ccount">01 / {n:02d}</span>'
            f'<button class="cnext" type="button" aria-label="Next project">→</button></span></div>\n'
            '  </div>')



def features_page():
    feats = [p for p in PROJECTS if p['kind'] == 'Feature']
    order = ['golden', 'curse-of-aurore', 'izzy-lyon']
    feats.sort(key=lambda p: order.index(p['slug']) if p['slug'] in order else 99)
    rows = []
    for i, p in enumerate(feats):
        honors = ''.join(f'<li>{E(h)}</li>' for h in p['honors'])
        honors = f'<ul class="laurels mono">{honors}</ul>' if honors else ''
        cta = 'Watch the trailer' if p.get('video_label') == 'Official trailer' else 'Watch'
        wl = ' · '.join(n for n, *_ in p['watch'][:4])
        where = f'<p class="fwhere mono">Streaming on {E(wl)}</p>' if wl else (f'<p class="fwhere mono">{E(p["status"])}</p>' if p.get('status') else '')
        rows.append(f'''    <article class="feature-row reveal">
      <a class="fstill" href="/work/{p['slug']}/" aria-label="{E(p['title'])}"><img src="/assets/img/{p['still']}" alt="{E(p['alt'])}" loading="{'eager' if i == 0 else 'lazy'}" style="object-position:{p['pos']}">{laurel_for(p)}{tag(p)}</a>
      <div class="ftext">
        <span class="mono fnum">{i + 1:02d} — {E(p['year'])}</span>
        <h2 class="display"><a href="/work/{p['slug']}/">{E(p['title']).replace(': ', ':<br>')}</a></h2>
        <p class="logline">{E(p['logline'])}</p>
        <p class="credit mono">{E(p['credit'])}</p>
        {honors}
        {where}
        <a class="btn" href="/work/{p['slug']}/">{cta} <span class="arrow">→</span></a>
      </div>
    </article>''')
    body = '\n'.join(rows)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Feature Films — Mehran C. Torgoley</title>
<meta name="description" content="Feature films directed by Mehran C. Torgoley: Curse of Aurore, Izzy Lyon: The Unspun Truth and Golden.">
<link rel="canonical" href="https://mehrantorgoley.com/features/">
<meta property="og:title" content="Feature Films — Mehran C. Torgoley">
<meta property="og:image" content="https://mehrantorgoley.com/assets/img/golden-doorway-og.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0B0B0B">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/anton-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/site.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>

<header class="site-header">
  <a class="brand" href="/">MEHRAN C. TORGOLEY</a>
  <button class="menu-btn" aria-label="Menu" aria-expanded="false" aria-controls="nav"><span></span><span></span></button>
  <nav class="nav" id="nav">
    {nav(current='/features/')}
  </nav>
</header>

<main id="main">
  <section class="page-head">
    <h1 class="display"><span class="mask"><span>Feature <span class="outline">films</span></span></span></h1>
    <span class="mono">{len(feats):02d} features</span>
  </section>

  <section class="wrap features-list">
{body}
  </section>
</main>

<footer class="contact" id="contact">
  <a class="big display" href="/contact/" style="font-size:clamp(56px,6.6vw,96px)">Let’s make<br>something <span class="arrow">→</span></a>
  <div class="foot">
    <a class="mail" href="mailto:hello@mehrantorgoley.com">hello@mehrantorgoley.com</a>
    <span class="mono" data-clock>California</span>
    <span class="links"><a href="https://www.imdb.com/name/nm1977604/" rel="noopener">IMDb</a><a href="https://vimeo.com/numbir9" rel="noopener">Vimeo</a></span>
  </div>
</footer>

<script src="/assets/js/site.js"></script>
</body>
</html>
'''


def main():
    for i, p in enumerate(PROJECTS):
        d = os.path.join(ROOT, 'work', p['slug']); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w').write(page(p, PROJECTS[(i + 1) % len(PROJECTS)]))
    os.makedirs(os.path.join(ROOT, 'features'), exist_ok=True)
    open(os.path.join(ROOT, 'features', 'index.html'), 'w').write(features_page())
    idx = os.path.join(ROOT, 'index.html'); s = open(idx).read()
    s2 = re.sub(r'  <div class="reel[^"]*"[^>]*>.*?\n  </div>(?=\n)', lambda m: carousel(), s, count=1, flags=re.S)
    assert s2 != s or 'class="reel carousel"' in s, 'carousel anchor not found'
    open(idx, 'w').write(s2)
    print('built', len(PROJECTS), 'project pages + carousel')


if __name__ == '__main__':
    main()
