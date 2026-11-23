#!/usr/bin/env python3
"""SEO pass over every page. Run after build_projects.py (it calls this automatically).

- Fills in Open Graph / Twitter tags from each page's <title>, description, canonical and og:image.
- Adds schema.org JSON-LD: Person + WebSite on the homepage, Movie / MusicVideo on project pages.
- Writes sitemap.xml and robots.txt; marks 404 as noindex.
Idempotent: everything it adds is wrapped in <!-- seo --> ... <!-- /seo --> and replaced on each run.
"""
import os, re, json, glob, html, datetime, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://mehrantorgoley.com'
NAME = 'Mehran C. Torgoley'
sys.path.insert(0, os.path.join(ROOT, 'tools'))

PERSON = {
    '@type': 'Person', '@id': SITE + '/#person', 'name': NAME,
    'alternateName': ['Mehran Torgoley'],
    'jobTitle': 'Film director, screenwriter and editor',
    'description': 'Director and writer of feature films, short films, music videos and commercials, based in Southern California.',
    'url': SITE + '/', 'image': SITE + '/assets/img/mehran-torgoley-headshot.jpg',
    'homeLocation': {'@type': 'Place', 'name': 'Southern California'},
    'email': 'mailto:hello@mehrantorgoley.com',
    'knowsAbout': ['Film directing', 'Screenwriting', 'Film editing', 'Music video direction', 'Commercial production', 'Motion graphics'],
    'sameAs': ['https://www.imdb.com/name/nm1977604/', 'https://vimeo.com/numbir9'],
}
DIRECTOR = {'@type': 'Person', '@id': SITE + '/#person', 'name': NAME, 'url': SITE + '/'}


def meta(s, prop=None, name=None):
    pat = (r'<meta property="%s" content="([^"]*)"' % prop) if prop else (r'<meta name="%s" content="([^"]*)"' % name)
    m = re.search(pat, s)
    return html.unescape(m.group(1)) if m else None


def tag(k, v, prop=True):
    return f'<meta {"property" if prop else "name"}="{k}" content="{html.escape(v, quote=True)}">'


def ld(obj):
    obj = dict({'@context': 'https://schema.org'}, **obj)
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace('</', '<\\/') + '</script>'


def project_ld(p, url):
    from build_projects import TAGS  # noqa
    img = SITE + '/assets/img/' + p['still']
    if p['kind'] == 'Music video':
        o = {'@type': 'MusicVideoObject', 'name': f"{p['title']} — {p.get('artist', '')}".strip(' —'),
             'url': url, 'thumbnailUrl': img, 'description': f"Music video for {p.get('artist')}, directed by {NAME}.",
             'creator': DIRECTOR}
        if p.get('artist'):
            o['byArtist'] = {'@type': 'MusicGroup', 'name': p['artist']}
    else:
        o = {'@type': 'Movie', 'name': p['title'], 'url': url, 'image': img,
             'description': p.get('logline') or '', 'genre': 'Short film' if p['kind'] == 'Short film' else None,
             'director': [DIRECTOR] + ([{'@type': 'Person', 'name': 'Dan Lanigan'}] if 'Dan Lanigan' in p.get('credit', '') else []),
             'dateCreated': p.get('year') or None}
        aw = [re.sub(r'<[^>]+>', '', h) for h in p.get('honors', [])]
        if aw:
            o['award'] = aw
        if p.get('video') and p['video'][0] == 'yt':
            vid = p['video'][1]
            o['trailer' if p.get('video_label') == 'Official trailer' else 'video'] = {
                '@type': 'VideoObject', 'name': f"{p['title']} — {p.get('video_label')}",
                'embedUrl': f'https://www.youtube.com/embed/{vid}',
                'thumbnailUrl': f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg',
                'description': p.get('logline') or p['title']}
        o = {k: v for k, v in o.items() if v not in (None, '', [])}
    return o


def process(path, projects_by_url):
    s = open(path, encoding='utf-8').read()
    s = re.sub(r'\n?<!-- seo -->.*?<!-- /seo -->', '', s, flags=re.S)
    title = html.unescape(re.search(r'<title>(.*?)</title>', s, re.S).group(1)).strip()
    desc = meta(s, name='description') or ''
    canon = re.search(r'<link rel="canonical" href="([^"]+)"', s)
    url = canon.group(1) if canon else SITE + '/'
    img = meta(s, prop='og:image') or SITE + '/assets/img/golden-doorway-og.jpg'
    add = []
    if not meta(s, prop='og:site_name'): add.append(tag('og:site_name', NAME))
    if not meta(s, prop='og:url'): add.append(tag('og:url', url))
    if not meta(s, prop='og:description'): add.append(tag('og:description', desc))
    if not meta(s, prop='og:type'):
        p = projects_by_url.get(url)
        add.append(tag('og:type', 'video.movie' if p and p['kind'] != 'Music video' else ('video.other' if p else 'website')))
    if not meta(s, name='twitter:title'): add.append(tag('twitter:title', title, prop=False))
    if not meta(s, name='twitter:description'): add.append(tag('twitter:description', desc, prop=False))
    if not meta(s, name='twitter:image'): add.append(tag('twitter:image', img, prop=False))
    if os.path.basename(path) == '404.html' and 'noindex' not in s:
        add.append('<meta name="robots" content="noindex">')
    # structured data
    if url == SITE + '/':
        s = re.sub(r'<script type="application/ld\+json">\{"@context":"https://schema.org","@type":"Person".*?</script>\n?', '', s, flags=re.S)
        add.append(ld({'@graph': [PERSON, {'@type': 'WebSite', '@id': SITE + '/#website', 'url': SITE + '/', 'name': NAME, 'publisher': {'@id': SITE + '/#person'}}]}))
    elif url in projects_by_url:
        add.append(ld(dict(project_ld(projects_by_url[url], url), **{})))
    elif url.endswith('/features/') or url.endswith('/shorts/') or url.endswith('/music-videos/'):
        items = [p for p in projects_by_url.values() if
                 (url.endswith('/features/') and p['kind'] == 'Feature') or (url.endswith('/shorts/') and p['kind'] == 'Short film') or (url.endswith('/music-videos/') and p['kind'] == 'Music video')]
        add.append(ld({'@type': 'CollectionPage', 'name': title, 'url': url, 'about': {'@id': SITE + '/#person'},
                       'hasPart': [{'@type': 'CreativeWork', 'name': p['title'], 'url': f"{SITE}/work/{p['slug']}/"} for p in items]}))
    block = '<!-- seo -->\n' + '\n'.join(add) + '\n<!-- /seo -->'
    s = s.replace('</head>', block + '\n</head>', 1)
    open(path, 'w', encoding='utf-8').write(s)
    return url


def main():
    from build_projects import PROJECTS
    by_url = {f"{SITE}/work/{p['slug']}/": p for p in PROJECTS}
    urls = []
    for path in sorted(glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True)):
        if '/.git/' in path or os.path.basename(path).startswith('_'):
            continue
        u = process(path, by_url)
        if not path.endswith('404.html'):
            urls.append(u)
    today = datetime.date.today().isoformat()
    pri = lambda u: '1.0' if u == SITE + '/' else ('0.8' if u.count('/') <= 4 else '0.6')
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in sorted(set(urls), key=lambda u: (u != SITE + '/', u)):
        xml.append(f'  <url><loc>{u}</loc><lastmod>{today}</lastmod><priority>{pri(u)}</priority></url>')
    xml.append('</urlset>')
    open(os.path.join(ROOT, 'sitemap.xml'), 'w').write('\n'.join(xml) + '\n')
    open(os.path.join(ROOT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nDisallow: /tools/\n\nSitemap: {SITE}/sitemap.xml\n')
    print('seo: processed', len(urls) + 1, 'pages; sitemap', len(set(urls)), 'urls')


if __name__ == '__main__':
    main()
