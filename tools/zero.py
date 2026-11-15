"""Convert a Tilda Zero Block (T396) record into clean HTML + CSS.

Positions and styles are taken from the CSS Tilda already computes for every
breakpoint; the markup is rebuilt with short, neutral class names and every
runtime dependency on Tilda is removed.
"""
import json
import re
from collections import OrderedDict

from cssparse import parse

BREAKS = {
    None: None,
    'screen and (max-width:1199px)': 'max-width:1199px',
    'screen and (max-width:959px)': 'max-width:959px',
    'screen and (max-width:639px)': 'max-width:639px',
    'screen and (max-width:479px)': 'max-width:479px',
    '(hover),(min-width:0\\0)': 'hover:hover',
    '(min-width:1200px)': 'min-width:1200px',
}
MEDIA_ORDER = [None, 'hover:hover', 'min-width:1200px', 'max-width:1199px',
               'max-width:959px', 'max-width:639px', 'max-width:479px']

SEL_MAP = [
    (r'\.t396_safari ', None),  # drop safari-only hacks
    (r'\.t396__artboard', ''),
    (r'\.t396__carrier', '.z__bg'),
    (r'\.t396__filter', '.z__filter'),
    (r'\.tn-elem\.t396__elem--anim-hidden', '.el'),
    (r'\.tn-atom__button-content', '.btn__c'),
    (r'\.tn-atom__button-text', '.btn__t'),
    (r'\.tn-atom__button-icon', '.btn__i'),
    (r'\.tn-atom__button-border', '.btn__b'),
    (r'\.tn-atom__img', '.a__img'),
    (r'\.tn-atom', '.a'),
]

DROP_PROPS = {'-moz-transform', '-ms-flex-pack', '-webkit-box-pack', 'will-change'}


class Ctx:
    """Shared conversion context (asset map, translator, link rewriter)."""

    def __init__(self, asset_url, text, link):
        self.asset_url = asset_url  # f(original_url) -> url relative to css dir
        self.text = text            # f(html) -> translated html
        self.link = link            # f(href) -> rewritten href


def clean_value(prop, val, ctx):
    val = val.replace('--t396-', '--z-')
    val = val.replace("var(--t-text-font,Arial)", "'Montserrat',Arial,sans-serif")
    val = val.replace("var(--t-headline-font,Arial)", "'Montserrat',Arial,sans-serif")

    def repl(m):
        return "url('%s')" % ctx.asset_url(m.group(2))
    val = re.sub(r"url\((['\"]?)(https://[^'\")]+)\1\)", repl, val)
    return val


def rewrite_selector(sel, rec_id, elem_cls, scope):
    out = []
    for one in sel.split(','):
        one = one.strip()
        if '.t396_safari' in one:
            continue
        one = one.replace('#rec%s' % rec_id, scope)
        one = re.sub(r'\.tn-elem\[data-elem-id="(\d+)"\]',
                     lambda m: '.' + elem_cls.get(m.group(1), 'missing'), one)
        one = re.sub(r'\.tn-elem(\.t396__elem--anim-hidden)?\[data-elem-id="(\d+)"\]',
                     lambda m: '.' + elem_cls.get(m.group(2), 'missing'), one)
        for pat, rep in SEL_MAP:
            if rep is None:
                continue
            one = re.sub(pat, rep, one)
        one = re.sub(r'\s+', ' ', one).strip()
        if one.endswith(scope + ' ') or one == scope:
            one = scope
        out.append(one)
    return ', '.join(out)


def convert_css(rec, rec_id, elem_cls, scope, ctx):
    """Return {media: OrderedDict(selector -> OrderedDict(prop -> value))}."""
    rules = {m: OrderedDict() for m in MEDIA_ORDER}
    for st in rec.find_all('style'):
        for media, sel, decls in parse(st.string or ''):
            if 'data-elem-id' not in sel and 't396__' not in sel:
                continue
            m = BREAKS.get(media, 'UNKNOWN:' + str(media))
            nsel = rewrite_selector(sel, rec_id, elem_cls, scope)
            if not nsel:
                continue
            bucket = rules.setdefault(m, OrderedDict()).setdefault(nsel, OrderedDict())
            for p, v in decls:
                if not p or p in DROP_PROPS:
                    continue
                if v in ('px', '') or v.endswith(':px'):
                    continue
                if p in ('width', 'height', 'left', 'top') and v == 'px':
                    continue
                p = p.replace('--t396-', '--z-')
                bucket[p] = clean_value(p, v, ctx)
    # carrier/filter only duplicate artboard height: fold into artboard
    # (background layers are always 100% of the section in base.css)
    for m, sels in rules.items():
        for s in list(sels):
            parts = [x.strip() for x in s.split(',')]
            if len(parts) > 1 and scope in parts and all(
                    x == scope or x.endswith('.z__filter') or x.endswith('.z__bg') for x in parts):
                merged = sels.setdefault(scope, OrderedDict())
                merged.update(sels.pop(s))
            elif s.endswith('.z__filter') or s.endswith('.z__bg'):
                sels[s].pop('height', None)
                if not sels[s]:
                    del sels[s]
    # remove declarations identical to the base rule (Tilda repeats boilerplate)
    # (compared with the value that is in effect at that size, i.e. after the larger breakpoints)
    eff = {sel: dict(d) for sel, d in rules[None].items()}
    for m in MEDIA_ORDER[3:]:
        for sel, decls in list(rules[m].items()):
            cur = eff.setdefault(sel, {})
            for p in list(decls):
                if cur.get(p) == decls[p] and p not in ('left', 'top', 'width', 'height', 'display'):
                    del decls[p]
                else:
                    cur[p] = decls[p]
            if not decls:
                del rules[m][sel]
    return rules


def css_text(rules):
    out = []
    for m in MEDIA_ORDER:
        sels = rules.get(m)
        if not sels:
            continue
        body = []
        for sel, decls in sels.items():
            if not decls:
                continue
            d = ';'.join('%s:%s' % (p, v) for p, v in decls.items())
            body.append('%s{%s}' % (sel, d))
        if not body:
            continue
        if m is None:
            out.extend(body)
        elif m == 'hover:hover':
            out.append('@media (hover:hover){%s}' % ''.join(body))
        else:
            out.append('@media (%s){%s}' % (m, ''.join(body)))
    return '\n'.join(out)


def sbs_json(raw):
    if not raw:
        return None
    try:
        return json.dumps(json.loads(raw.replace("'", '"')), separators=(',', ':'))
    except ValueError:
        return None


GRID = {None: 1200, 'max-width:1199px': 960, 'max-width:959px': 640,
        'max-width:639px': 480, 'max-width:479px': 320}
RES_OF = {None: None, 'max-width:1199px': '960', 'max-width:959px': '640',
          'max-width:639px': '480', 'max-width:479px': '320'}


def field(el, name, media):
    """Value of a Tilda field at a breakpoint, inheriting from larger screens."""
    order = [None, 'max-width:1199px', 'max-width:959px', 'max-width:639px', 'max-width:479px']
    val = el.get('data-field-%s-value' % name)
    for m in order[1:order.index(media) + 1] if media else []:
        v = el.get('data-field-%s-res-%s-value' % (name, RES_OF[m]))
        if v is not None:
            val = v
    return val


def grid_percent_widths(elems, elem_cls, rules, scope):
    """Tilda measures % widths of grid-bound elements against the grid, not the window."""
    for el in elems:
        cls = '%s .%s' % (scope, elem_cls[el['data-elem-id']])
        for media, grid in GRID.items():
            if field(el, 'container', media) != 'grid' or field(el, 'widthunits', media) != '%':
                continue
            decls = rules.get(media, {}).get(cls)
            pct = field(el, 'width', media)
            if not pct:
                continue
            px = '%gpx' % (grid * float(pct) / 100)
            if decls is not None and decls.get('width', '').endswith('%'):
                decls['width'] = px
            elif media is not None and (decls is None or 'width' not in decls):
                rules[media].setdefault(cls, OrderedDict())['width'] = px


def anim_attrs(el, elem_cls=None):
    a = el.attrs
    out = OrderedDict()
    if a.get('data-animate-sbs-trgels') and elem_cls:
        ids = a['data-animate-sbs-trgels'].split(',')
        out['data-sbs-hover-els'] = ' '.join(elem_cls[i] for i in ids if i in elem_cls)
    if a.get('data-animate-style'):
        out['data-anim'] = a['data-animate-style']
        for k in ('duration', 'delay', 'distance', 'scale'):
            if a.get('data-animate-' + k):
                out['data-anim-' + k] = a['data-animate-' + k]
    if a.get('data-animate-sbs-event'):
        out['data-sbs'] = a['data-animate-sbs-event']
        out['data-sbs-steps'] = sbs_json(a.get('data-animate-sbs-opts'))
        for bp in ('320', '480', '640', '960'):
            v = sbs_json(a.get('data-animate-sbs-opts-res-%s' % bp))
            if v:
                out['data-sbs-steps-%s' % bp] = v
        if a.get('data-animate-sbs-trg'):
            out['data-sbs-trg'] = a['data-animate-sbs-trg']
        if a.get('data-animate-sbs-trgofst') not in (None, '', '0'):
            out['data-sbs-offset'] = a['data-animate-sbs-trgofst']
    if a.get('data-animate-mobile') == 'y':
        out['data-anim-mobile'] = 'y'
    return {k: v for k, v in out.items() if v is not None}


def esc(v):
    return (v.replace('&', '&amp;').replace('"', '&quot;')
            .replace('<', '&lt;').replace('>', '&gt;'))


def attrs_html(d):
    return ''.join(' %s="%s"' % (k, esc(str(v))) for k, v in d.items())


def inner_html(tag):
    return ''.join(str(c) for c in tag.contents).strip()


def clean_rich(html):
    html = re.sub(r'\s*field=\'[^\']*\'', '', html)
    html = re.sub(r'\sdata-[a-z-]+="[^"]*"', '', html)
    html = html.replace('<br/>', '<br>').replace('<br />', '<br>')
    return html.strip()


def form_html(el, ctx, extra_cls):
    a = el.attrs
    g = lambda k, d='': a.get('data-field-%s-value' % k, d)
    data = el.select_one('.tn-atom__inputs-data')
    inputs = json.loads(data['data-value']) if data else []
    fields = []
    for f in inputs:
        t = {'nm': 'text', 'em': 'email', 'ph': 'tel'}.get(f.get('li_type'), 'text')
        req = ' required' if f.get('li_req') == 'y' or t in ('email',) or f.get('li_name') == 'name' else ''
        ph = ctx.text(f.get('li_ph', ''))
        fields.append('<input class="zf__input" type="%s" name="%s" placeholder="%s" aria-label="%s"%s>'
                      % (t, f.get('li_name', 'field'), esc(ph), esc(ph), req))
    btn = ctx.text(g('buttontitle', 'SUBMIT'))
    return ('<form class="a zf js-form" action="send.php" method="post" novalidate>%s'
            '<input type="text" name="website" class="zf__hp" tabindex="-1" autocomplete="off" aria-hidden="true">'
            '<button type="submit" class="zf__btn">%s</button>'
            '<p class="zf__msg" role="status" aria-live="polite"></p></form>') % (''.join(fields), btn)


def form_css(el, cls, scope):
    a = el.attrs
    g = lambda k, d='': a.get('data-field-%s-value' % k, d)
    s = '%s .%s' % (scope, cls)
    css = [
        '%s .zf__input{height:%spx;margin-bottom:%spx;border:%spx solid %s;border-radius:%spx;'
        'color:%s;font:%s %spx %s,Arial,sans-serif}' % (
            s, g('inputheight', '50'), g('inputmargbottom', '20'), g('inputbordersize', '1'),
            g('inputbordercolor', '#000'), g('inputradius', '0'), g('inputcolor', '#000'),
            g('inputfontweight', '400'), g('inputfontsize', '14'), g('inputfontfamily', 'Arial')),
        '%s .zf__input::placeholder{color:%s;opacity:.5}' % (s, g('inputcolor', '#000')),
        '%s .zf__btn{height:%spx;color:%s;background:%s;border-radius:%spx;'
        'font:%s %spx %s,Arial,sans-serif}' % (
            s, g('buttonheight', '50'), g('buttoncolor', '#fff'), g('buttonbgcolor', '#000'),
            g('buttonradius', '0'), g('buttonfontweight', '600'), g('buttonfontsize', '14'),
            g('buttonfontfamily', 'Arial')),
    ]
    return '\n'.join(css)


def vh_center(art, rules, scope):
    """Full-screen sections: keep the design vertically centred at every breakpoint.

    Tilda writes plain px tops for smaller screens and recentres them with JS; here the
    centring is expressed in CSS: top = 50vh - designHeight/2 + top.
    """
    if not art.get('data-artboard-height_vh') or art.get('data-artboard-valign') != 'center':
        return
    base = rules[None]
    bp_of = {'max-width:1199px': '960', 'max-width:959px': '640', 'max-width:639px': '480', 'max-width:479px': '320'}
    default_h = int(art.get('data-artboard-height', '550'))
    for media, bp in bp_of.items():
        h = int(art.get('data-artboard-height-res-%s' % bp, default_h))
        for sel, decls in rules.get(media, {}).items():
            top = decls.get('top', '')
            btop = base.get(sel, {}).get('top', '')
            if re.fullmatch(r'-?\d+(\.\d+)?px', top) and '50vh' in btop:
                decls['top'] = 'calc(50vh - %dpx + %s)' % (h // 2, top)
            elif top.startswith('calc(%dpx ' % h) and '100vh' in btop:
                decls['top'] = top.replace('calc(%dpx ' % h, 'calc(100vh ', 1)
            elif top.startswith('calc(%dpx ' % (h // 2)) and '50vh' in btop:
                decls['top'] = top.replace('calc(%dpx ' % (h // 2), 'calc(50vh ', 1)
        # elements that only inherit the desktop top must be recentred for this design height
        if h != default_h:
            for sel, decls in base.items():
                if '50vh' in decls.get('top', '') and 'top' not in rules[media].get(sel, {}):
                    m = re.search(r'calc\(50vh - (\d+)px \+ (-?\d+)px\)', decls['top'])
                    if m and int(m.group(1)) == default_h // 2:
                        rules[media].setdefault(sel, OrderedDict())['top'] = 'calc(50vh - %dpx + %spx)' % (h // 2, m.group(2))


def convert(rec, ctx, scope_id, overrides=None):
    """Return (html, css) for one T396 record."""
    overrides = overrides or {}
    rec_id = rec['id'][3:]
    art = rec.select_one('.t396__artboard')
    elems = rec.select('.t396__elem')
    elem_cls = OrderedDict()
    for i, el in enumerate(elems, 1):
        elem_cls[el['data-elem-id']] = 'e%d' % i
    scope = '#' + scope_id
    rules = convert_css(rec, rec_id, elem_cls, scope, ctx)
    vh_center(art, rules, scope)
    grid_percent_widths(elems, elem_cls, rules, scope)
    extra_css = []
    parts = []
    for el in elems:
        eid = el['data-elem-id']
        cls = elem_cls[eid]
        typ = el['data-elem-type']
        if eid in overrides.get('remove', ()):
            continue
        custom = [c for c in el.get('class', []) if c.startswith('st-')]
        attrs = OrderedDict()
        attrs['class'] = ' '.join(['el', 'el--' + typ, cls] + custom)
        if typ == 'image' and 'logo_ubs' in str(el):
            attrs['class'] += ' el--logo'
        if 't396__elem--anim-hidden' in el.get('class', []):
            attrs['class'] += ' is-anim-hidden'
        attrs.update(anim_attrs(el, elem_cls))
        atom = el.select_one('.tn-atom')
        href = atom.get('href') if atom is not None else None
        target = atom.get('target') if atom is not None else None
        tag = 'a' if href else 'div'
        link_attr = ''
        if href:
            link_attr = ' href="%s"' % esc(ctx.link(href))
            if target == '_blank':
                link_attr += ' target="_blank" rel="noopener"'
        if typ == 'text':
            body = ctx.text(clean_rich(inner_html(atom)), eid)
            plain = re.sub(r'<[^>]+>', ' ', body)
            if len(plain.strip()) >= 110 and not any(c.startswith('st-slide') for c in custom):
                attrs['class'] += ' el--para'
                if rules[None].get('%s .%s' % (scope, cls), {}).get('text-align') == 'center':
                    attrs['class'] += ' is-center'
            body = re.sub(r'href="([^"]*)"', lambda m: 'href="%s"' % esc(ctx.link(m.group(1))), body)
            body = body.replace(' style="color: inherit"', '')
            inner = '<%s class="a"%s>%s</%s>' % (tag, link_attr, body, tag)
        elif typ == 'image':
            img = el.select_one('img')
            src = img.get('data-original') or img.get('src')
            alt = img.get('alt', '')
            inner = '<%s class="a"%s><img class="a__img" src="%s" alt="%s" loading="lazy"></%s>' % (
                tag, link_attr, ctx.asset_url(src), esc(alt), tag)
        elif typ == 'shape':
            bg = atom.get('data-original')
            if bg:
                rules[None].setdefault('%s .%s .a' % (scope, cls), OrderedDict())[
                    'background-image'] = "url('%s')" % ctx.asset_url(bg)
            inner = '<%s class="a"%s></%s>' % (tag, link_attr, tag)
            if 'st-progress-container' in custom:
                inner = '<div class="a"></div>'
        elif typ == 'button':
            text_el = el.select_one('.tn-atom__button-text')
            text = ctx.text(clean_rich(inner_html(text_el)), eid) if text_el else ''
            icon = el.select_one('.tn-atom__button-icon')
            icon_html = '<span class="btn__i"></span>' if icon is not None else ''
            if icon is not None and 'tn-atom__button-icon-arrow-default' in icon.get('class', []):
                icon_html = '<span class="btn__i btn__i--mask"></span>'
            label = ''
            if not text:
                if 'st-btn-prev' in custom:
                    label = ' aria-label="Previous slide"'
                elif 'st-btn-next' in custom:
                    label = ' aria-label="Next slide"'
            btn_tag = tag if href else 'button'
            type_attr = ' type="button"' if btn_tag == 'button' else ''
            inner = ('<%s class="a"%s%s%s><span class="btn__c">%s<span class="btn__t">%s</span></span>'
                     '<span class="btn__b"></span></%s>') % (
                btn_tag, link_attr, type_attr, label, icon_html, text, btn_tag)
        elif typ == 'form':
            inner = form_html(el, ctx, cls)
            extra_css.append(form_css(el, cls, scope))
        else:
            inner = '<div class="a"></div>'
        parts.append('<div%s>%s</div>' % (attrs_html(attrs), inner))

    zattrs = OrderedDict()
    zattrs['id'] = scope_id
    zattrs['class'] = 'z'
    if art.get('data-artboard-pos') == 'fixed':
        zattrs['class'] += ' z--fixed'
    if art.get('data-artboard-ovrflw') == 'visible':
        zattrs['class'] += ' z--visible'
    html = '<section%s>\n<div class="z__bg"></div><div class="z__filter"></div>\n%s\n</section>' % (
        attrs_html(zattrs), '\n'.join(parts))
    # The 480 px layout of the original project was never finished (elements pile up even in
    # English); the phone layout the designer did make is used for every screen below 640 px.
    # (phones keep exactly their cascade: 480-layer values overridden by the 320-layer ones)
    merged = rules.get('max-width:639px', OrderedDict())
    for sel, decls in rules.pop('max-width:479px', OrderedDict()).items():
        merged.setdefault(sel, OrderedDict()).update(decls)
    rules['max-width:639px'] = merged
    rules['max-width:479px'] = OrderedDict()
    css = css_text(rules) + ('\n' + '\n'.join(extra_css) if extra_css else '')
    leftovers = set(re.findall(r'(t396[\w-]*|tn-[\w-]+)', css))
    if leftovers:
        print('  ! leftover tilda tokens in', scope_id, leftovers)
    return html, css
