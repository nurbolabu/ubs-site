"""Build the static UBS site (EN / RU / KK) into docs/.

    python3 tools/build.py

Source: the original Tilda pages saved in src/orig/. Zero Blocks are converted
by zero.py, the standard blocks are re-implemented in components.py, texts are
translated with src/i18n/<lang>.json, page-level edits live in edits.py.
"""
import html as htmllib
import json
import os
import re
import sys
from collections import OrderedDict, defaultdict

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import components as C  # noqa: E402
import edits  # noqa: E402
import services as S  # noqa: E402
import zero  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'docs')
ASSETS = json.load(open(os.path.join(ROOT, 'tools/assets.json')))
LANGS = ['en', 'ru', 'kk']

# output slug -> (source page, edits key)
PAGES = OrderedDict([
    ('index', 'ubsubs'),
    ('about-ubs', 'about-ubs'),
    ('ubs-services', 'ubs-services'),
    ('it-outsourcing', 'it-consulting-audit'),
    ('warranty-service', 'comprehensive-it-solutions'),
    ('service-support', 'service-support'),
    ('delivery', 'delivery'),
    ('information-security', 'information-security'),
    ('our-partners', 'our-partners'),
    ('our-clients', 'our-clients'),
    ('contacts-ubs', 'contacts-ubs'),
])

# old Tilda paths -> new slugs (links inside content)
LINKS = {
    'ubsubs': 'index', '': 'index', 'about-ubs': 'about-ubs', 'ubs-services': 'ubs-services',
    'it-consulting-audit': 'it-outsourcing', 'comprehensive-it-solutions': 'warranty-service',
    'service-support': 'service-support', 'certified-service-center': 'ubs-services',
    'delivery': 'delivery', 'information-security': 'information-security',
    'our-partners': 'our-partners', 'contacts-ubs': 'contacts-ubs', 'our-clients': 'our-clients',
}

MISSING = defaultdict(set)
_HP = os.path.join(ROOT, 'src/heights.json')
HEIGHTS = json.load(open(_HP)) if os.path.exists(_HP) else {}


def add_heights(html, slug, scope):
    """data-eh = English heights of an element at the 1200/960/640/480/320 grids."""
    def repl(m):
        h = HEIGHTS.get('%s %s %s' % (slug, scope, m.group(2)))
        return m.group(0) + (' data-eh="%s"' % ','.join(map(str, h)) if h else '')
    return re.sub(r'<div class="(el [^"]*?\b(e\d+)\b[^"]*)"', repl, html)


def norm_text(s):
    s = htmllib.unescape(s).replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', s).strip()


class I18n:
    def __init__(self):
        self.d = {}
        for lang in ('ru', 'kk'):
            p = os.path.join(ROOT, 'src/i18n/%s.json' % lang)
            self.d[lang] = json.load(open(p)) if os.path.exists(p) else {}
        self.seen = OrderedDict()

    def t(self, lang, text, key=None):
        text = edits.replace_text(text) if text else text
        if not text or not re.search(r'[A-Za-z]', re.sub(r'<[^>]+>', '', text)):
            return text
        k = norm_text(text)
        self.seen.setdefault(k, None)
        if lang == 'en':
            return text
        d = self.d[lang]
        if k in d and d[k]:
            return d[k]
        MISSING[lang].add(k)
        return text


I18N = I18n()


def asset_ref(url):
    """Map a Tilda CDN url to '@/assets/...' (resolved per output file later)."""
    if not url:
        return url
    u = re.sub(r'https://thb\.tildacdn\.pro/(tild[^/]+)/-/.*/([^/]+)$',
               r'https://static.tildacdn.pro/\1/\2', url)
    u = u.replace('tildacdn.com', 'tildacdn.pro')
    if u in ASSETS:
        return '@/' + ASSETS[u]
    if u.startswith('@/'):
        return u
    print('  ! unmapped asset', url)
    return url


def link_ref(href):
    if not href:
        return href
    if href.startswith(('http', 'mailto:', 'tel:', '#')):
        return href
    m = re.match(r'^/?([A-Za-z0-9_-]*)/?(#.*)?$', href)
    if not m:
        return href
    slug = LINKS.get(m.group(1).lower())
    if slug is None:
        print('  ! unknown link', href)
        return href
    return '@@/' + ('' if slug == 'index' else slug + '/') + (m.group(2) or '')


class Page:
    def __init__(self, slug, src, lang):
        self.slug, self.src, self.lang = slug, src, lang
        self.css = OrderedDict()   # block id -> css (page scoped)
        self.body = []
        self.after = []            # popups etc.

    def t(self, text, key=None):
        return I18N.t(self.lang, text, key)

    def asset(self, url):
        return asset_ref(url)

    def asset_by_name(self, ref):
        if ref.endswith('KASPERSKY'):
            for v in ASSETS.values():
                if 'aspersky' in v.lower():
                    return '@/' + v
        return ref


def build_page(slug, src, lang, shared_css):
    page = Page(slug, src, lang)
    page.lang_urls = {l: rel_prefix(slug, lang) + lang_root(l) + ('' if slug == 'index' else slug + '/')
                      for l in LANGS}
    soup = BeautifulSoup(open(os.path.join(ROOT, 'src/orig/%s.html' % src), encoding='utf8').read(), 'lxml')
    E = edits.get(slug)
    ctx = zero.Ctx(asset_ref, lambda h, k=None: page.t(h, k), link_ref)
    page.ctx = ctx
    recs = soup.select('#allrecords > div.t-rec, .t-records > div.t-rec')
    if not recs:
        recs = soup.select('div.t-rec')
    header_done = False
    zero_n = 0
    for rec in recs:
        rid = rec['id'][3:]
        typ = rec.get('data-alias-record-type') or rec.get('data-record-type')
        if rid in E.get('skip', ()):
            continue
        if typ == '396':
            art = rec.select_one('.t396__artboard')
            if art is None:
                continue
            scope = 's' + rid[-6:]
            rec_edit = E.get('zero', {}).get(rid, {})
            src_rec = rec
            if rec_edit.get('patch'):
                rec_edit['patch'](rec, page)
            html, css = zero.convert(src_rec, ctx, scope, rec_edit)
            is_header = art.get('data-artboard-pos') == 'fixed'
            if lang != 'en' and not is_header:
                html = add_heights(html, slug, scope)
            if not is_header:
                html, css = edits.on_zero(page, zero_n, rec, html, css)
                zero_n += 1
            if is_header:
                html = html.replace('<section', '<header', 1).replace('</section>', '</header>')
                # the frosted background bar of the header (used by the phone header behaviour)
                for cls in re.findall(r'#%s \.(e\d+)\{[^}]*backdrop-filter' % scope, css):
                    html = re.sub(r'class="el el--shape %s"' % cls, 'class="el el--shape %s hdr-bg"' % cls, html)
                html = C.header_extras(html, page)
                header_done = True
            key = rid
            if css:
                if rid in edits.SHARED_ZERO:
                    shared_css[key] = css
                else:
                    page.css[key] = css
            page.body.append(html)
        elif typ == '702':
            page.after.append(C.popup(page))
        elif typ == '3112':
            page.after.append(C.burger(page))
        elif typ == '794':
            pass  # language menu is rendered by the header itself
        elif typ == '738':
            if rec.get('data-screen-max'):
                continue  # one responsive slider replaces the desktop/mobile pair
            page.body.append(C.brands(page))
        elif typ == '420':
            page.body.append(C.footer(page))
        elif typ == '491':
            page.body.append(C.values(page, rec))
        elif typ == '686':
            page.body.append(C.tiles(page, rec))
        elif typ == '554':
            page.body.append(C.contact_map(page, rec))
        elif typ == '999':
            page.body.append(C.partners(page, rec))
        elif typ == '594':
            page.body.append(C.partner_logos(page, rec))
        elif typ == '959':
            page.body.append(C.clients(page, rec))
        elif typ in ('360', '131', '270', '585'):
            pass
        else:
            print('  ! unhandled block', typ, rid, 'on', src)
        if typ in E.get('after_block', {}):
            page.body.append(E['after_block'][typ](page))
    for extra in E.get('insert', []):
        pos, fn = extra
        page.body.insert(pos, fn(page))
    return page


def rel_prefix(slug, lang):
    depth = (0 if lang == 'en' else 1) + (0 if slug == 'index' else 1)
    return '../' * depth


def lang_root(lang):
    return '' if lang == 'en' else lang + '/'


def finalize(text, slug, lang):
    pre = rel_prefix(slug, lang)
    text = text.replace('@@/', pre + lang_root(lang))
    text = text.replace('@/', pre)
    # directory links: keep trailing slash, point to index.html for file:// friendliness
    return text


TITLES = {
    'index': 'UBS', 'about-ubs': 'About us UBS', 'ubs-services': 'UBS services',
    'it-outsourcing': 'IT Outsourcing & Technical Support', 'warranty-service': 'Warranty Service',
    'service-support': 'Post-Warranty Service & Repair', 'delivery': 'Delivery',
    'information-security': 'Information Security', 'our-partners': 'UBS partners',
    'our-clients': 'UBS clients', 'contacts-ubs': 'Contacts',
}
DESCR = 'UBS Establishment — IT hardware, software and service support for business in Kazakhstan since 1996.'


def write_page(page, css_files):
    lang, slug = page.lang, page.slug
    title = S.SERVICES[slug][lang]['title'] if slug in S.SERVICES else page.t(TITLES[slug])
    descr = page.t(DESCR)
    alt = ''.join('<link rel="alternate" hreflang="%s" href="%s%s%s">' % (
        l, rel_prefix(slug, lang), lang_root(l), '' if slug == 'index' else slug + '/') for l in LANGS)
    css_links = ''.join('<link rel="stylesheet" href="@/assets/css/%s">' % c for c in css_files)
    doc = f'''<!DOCTYPE html>
<html lang="{lang}" data-root="@/">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{descr}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{descr}">
<meta property="og:type" content="website">
<meta property="og:image" content="@/assets/img/37646362-3462Mask_group.png">
<meta name="format-detection" content="telephone=no">
{alt}
<link rel="icon" href="@/favicon.ico" type="image/x-icon">
<link rel="preload" href="@/assets/fonts/31623734-TRYGrtsk-MediumTera-.woff" as="font" type="font/woff" crossorigin>
{css_links}
</head>
<body class="page-{slug}">
<a class="skip-link" href="#main">{page.t('Skip to content')}</a>
'''
    body = '\n'.join(page.body)
    # first fixed header stays outside <main>
    m = re.search(r'<header.*?</header>', body, re.S)
    if m:
        doc += m.group(0) + '\n<main id="main">\n' + body[:m.start()] + body[m.end():]
    else:
        doc += '<main id="main">\n' + body
    doc = doc.replace('<footer', '</main>\n<footer', 1) if '<footer' in doc else doc + '\n</main>'
    doc += '\n' + '\n'.join(page.after)
    doc += '\n<script src="@/assets/js/site.js" defer></script>\n</body>\n</html>\n'
    out_dir = os.path.join(DOCS, lang_root(lang), '' if slug == 'index' else slug)
    os.makedirs(out_dir, exist_ok=True)
    doc = finalize(doc, slug, lang)
    with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf8') as f:
        f.write(doc)


SITE_URL = 'https://ubsystem.kz'  # production domain (used in sitemap.xml / robots.txt)


def write_extras():
    urls = []
    for lang in LANGS:
        for slug in PAGES:
            urls.append('%s/%s%s' % (SITE_URL, lang_root(lang), '' if slug == 'index' else slug + '/'))
    with open(os.path.join(DOCS, 'sitemap.xml'), 'w', encoding='utf8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        f.write(''.join('  <url><loc>%s</loc></url>\n' % u for u in urls))
        f.write('</urlset>\n')
    with open(os.path.join(DOCS, 'robots.txt'), 'w', encoding='utf8') as f:
        f.write('User-agent: *\nAllow: /\nDisallow: /send.php\n\nSitemap: %s/sitemap.xml\n' % SITE_URL)
    with open(os.path.join(DOCS, '404.html'), 'w', encoding='utf8') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>404 — UBS</title>
<meta name="robots" content="noindex">
<link rel="icon" href="/favicon.ico">
<link rel="stylesheet" href="/assets/css/base.css">
<link rel="stylesheet" href="/assets/css/site.css">
<style>.nf{min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:24px;padding:40px 20px;text-align:center;background:linear-gradient(.25turn,#fff,#ebf8fe)}
.nf__code{font:500 120px/1 TRYGrtsk,Arial,sans-serif}.nf p{font:300 16px/1.6 Montserrat,Arial,sans-serif;color:#26262b}
.nf a{display:inline-flex;align-items:center;height:50px;padding:0 30px;border-radius:30px;background:#00a0e3;color:#fff;font:600 14px Montserrat,Arial,sans-serif;text-decoration:none}</style>
</head>
<body>
<main class="nf">
<img src="/assets/img/37376665-logo_ubs_new-2.png" alt="UBS" width="220">
<div class="nf__code grad-title">404</div>
<p>Page not found · Страница не найдена · Бет табылмады</p>
<a href="/">UBS — Home</a>
</main>
</body>
</html>
''')


def css_finalize(css):
    return css.replace("url('@/assets/", "url('../")


def main():
    shared_css = OrderedDict()
    page_css = OrderedDict()
    built = []
    for lang in LANGS:
        for slug, src in PAGES.items():
            page = build_page(slug, src, lang, shared_css)
            built.append(page)
            if lang == 'en':
                page_css[slug] = page.css
    os.makedirs(os.path.join(DOCS, 'assets/css'), exist_ok=True)
    with open(os.path.join(DOCS, 'assets/css/blocks.css'), 'w', encoding='utf8') as f:
        f.write('/* Shared positioned sections (header, consultation form, …). Generated by tools/build.py */\n')
        f.write(css_finalize('\n'.join(shared_css.values())) + '\n')
    for slug, blocks in page_css.items():
        with open(os.path.join(DOCS, 'assets/css/page-%s.css' % slug), 'w', encoding='utf8') as f:
            f.write('/* %s — positioned sections. Generated by tools/build.py */\n' % slug)
            f.write(css_finalize('\n'.join(blocks.values())) + '\n')
            f.write(css_finalize(edits.extra_css(slug)) + '\n')
    lang_css = OrderedDict()
    for lang in ('ru', 'kk'):
        lang_css[lang] = edits.lang_css(lang)
    with open(os.path.join(DOCS, 'assets/css/i18n.css'), 'w', encoding='utf8') as f:
        f.write('/* Per-language size/position adjustments for longer RU/KK texts. */\n')
        f.write(css_finalize('\n'.join(lang_css.values())) + '\n')
        f.write('/* Why-us number marks above titles below 1200 px (every language) */\n')
        f.write(css_finalize(edits.all_lang_css()) + '\n')
    for page in built:
        write_page(page, ['base.css', 'site.css', 'blocks.css', 'page-%s.css' % page.slug, 'i18n.css'])
    write_extras()
    os.makedirs(os.path.join(ROOT, 'src/i18n'), exist_ok=True)
    json.dump(list(I18N.seen), open(os.path.join(ROOT, 'src/i18n/_strings.en.json'), 'w'),
              ensure_ascii=False, indent=1)
    for lang, miss in MISSING.items():
        json.dump(sorted(miss), open(os.path.join(ROOT, 'src/i18n/_missing.%s.json' % lang), 'w'),
                  ensure_ascii=False, indent=1)
        print('missing %s translations: %d' % (lang, len(miss)))
    print('built', len(built), 'pages')


if __name__ == '__main__':
    main()
