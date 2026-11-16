"""Hand-written replacements for Tilda's standard blocks.

Every function returns clean HTML; styles live in docs/assets/css/site.css.
Texts go through page.t() so they are translated per language.
'@/' = site root, '@@/' = root of the current language (resolved in build.py).
"""
import re

PHONE = '+7 (727) 250 34 34'
PHONE_HREF = 'tel:+77272503434'
EMAIL = 'ubs@ubsystem.kz'
# WhatsApp stays on the mobile number: a landline has no WhatsApp
WHATSAPP = 'https://wa.me/77717999872'
LINKEDIN = 'https://kz.linkedin.com/company/universal-business-systems-establishment'
LOGO = '@/assets/img/37646362-3462Mask_group.png'

NAV = [
    ('about-ubs/', 'About us'),
    ('ubs-services/', 'Services'),
    ('our-partners/', 'Our partners'),
    ('our-clients/', 'Our clients'),
    ('contacts-ubs/', 'Contacts'),
]
LANG_LABEL = {'en': 'En', 'kk': 'Kaz', 'ru': 'Ru'}
LANG_NAME = {'en': 'English', 'kk': 'Қазақша', 'ru': 'Русский'}

ICON_WHATSAPP = ('M50 100C77.6142 100 100 77.6142 100 50C100 22.3858 77.6142 0 50 0C22.3858 0 0 22.3858 0 50C0 77.6142 22.3858 100 50 100ZM69.7626 28.9928C64.6172 23.841 57.7739 21.0027 50.4832 21C35.4616 21 23.2346 33.2252 23.2292 48.2522C23.2274 53.0557 24.4823 57.7446 26.8668 61.8769L23 76L37.4477 72.2105C41.4282 74.3822 45.9107 75.5262 50.4714 75.528H50.4823C65.5029 75.528 77.7299 63.301 77.7363 48.2749C77.7408 40.9915 74.9089 34.1446 69.7626 28.9928ZM62.9086 53.9588C62.2274 53.6178 58.8799 51.9708 58.2551 51.7435C57.6313 51.5161 57.1766 51.4024 56.7228 52.0845C56.269 52.7666 54.964 54.2998 54.5666 54.7545C54.1692 55.2092 53.7718 55.2656 53.0915 54.9246C52.9802 54.8688 52.8283 54.803 52.6409 54.7217C51.6819 54.3057 49.7905 53.4855 47.6151 51.5443C45.5907 49.7382 44.2239 47.5084 43.8265 46.8272C43.4291 46.1452 43.7837 45.7769 44.1248 45.4376C44.3292 45.2338 44.564 44.9478 44.7987 44.662C44.9157 44.5194 45.0328 44.3768 45.146 44.2445C45.4345 43.9075 45.56 43.6516 45.7302 43.3049C45.7607 43.2427 45.7926 43.1776 45.8272 43.1087C46.0545 42.654 45.9409 42.2565 45.7708 41.9155C45.6572 41.6877 45.0118 40.1167 44.4265 38.6923C44.1355 37.984 43.8594 37.3119 43.671 36.8592C43.1828 35.687 42.6883 35.69 42.2913 35.6924C42.2386 35.6928 42.1876 35.6931 42.1386 35.6906C41.7421 35.6706 41.2874 35.667 40.8336 35.667C40.3798 35.667 39.6423 35.837 39.0175 36.5191C38.9773 36.5631 38.9323 36.6111 38.8834 36.6633C38.1738 37.4209 36.634 39.0648 36.634 42.2002C36.634 45.544 39.062 48.7748 39.4124 49.2411L39.415 49.2444C39.4371 49.274 39.4767 49.3309 39.5333 49.4121C40.3462 50.5782 44.6615 56.7691 51.0481 59.5271C52.6732 60.2291 53.9409 60.6475 54.9303 60.9612C56.5618 61.4796 58.046 61.4068 59.22 61.2313C60.5286 61.0358 63.2487 59.5844 63.8161 57.9938C64.3836 56.4033 64.3836 55.0392 64.2136 54.7554C64.0764 54.5258 63.7545 54.3701 63.2776 54.1395C63.1633 54.0843 63.0401 54.0247 62.9086 53.9588Z')
ICON_EMAIL = ('M50 100C77.6142 100 100 77.6142 100 50C100 22.3858 77.6142 0 50 0C22.3858 0 0 22.3858 0 50C0 77.6142 22.3858 100 50 100ZM51.8276 49.2076L74.191 33.6901C73.4347 32.6649 72.2183 32 70.8466 32H29.1534C27.8336 32 26.6576 32.6156 25.8968 33.5752L47.5881 49.172C48.8512 50.0802 50.5494 50.0945 51.8276 49.2076ZM75 63.6709V37.6286L53.4668 52.57C51.1883 54.151 48.1611 54.1256 45.9095 52.5066L25 37.4719V63.6709C25 65.9648 26.8595 67.8243 29.1534 67.8243H70.8466C73.1405 67.8243 75 65.9648 75 63.6709Z')
ICON_LINKEDIN = ('M50 100c27.6142 0 50-22.3858 50-50S77.6142 0 50 0 0 22.3858 0 50s22.3858 50 50 50Zm23-31.0002V52.363c0-8.9114-4.7586-13.0586-11.1079-13.0586-5.1234 0-7.4123 2.8199-8.6942 4.7942v-4.1124h-9.6468c.1297 2.7235 0 29.0136 0 29.0136h9.6484v-16.203c0-.8675.0657-1.731.3203-2.3513.6981-1.7351 2.284-3.5286 4.9491-3.5286 3.4905 0 4.8859 2.6611 4.8859 6.5602v15.5227H73ZM53.1979 44.0986v.094h-.0632c.0069-.0111.0148-.0228.0229-.0346.0137-.0198.0281-.0401.0403-.0594ZM28 31.0123C28 28.1648 30.1583 26 33.4591 26c3.3016 0 5.3302 2.1648 5.3934 5.0123 0 2.7851-2.0918 5.0156-5.4567 5.0156h-.064c-3.2351 0-5.3318-2.2305-5.3318-5.0156Zm10.2177 37.9875h-9.6445V39.9862h9.6445v29.0136Z')


def social(size, color, cls='social'):
    def one(href, label, path):
        return ('<li><a href="%s" target="_blank" rel="noopener" aria-label="%s">'
                '<svg width="%d" height="%d" viewBox="0 0 100 100" aria-hidden="true">'
                '<path fill-rule="evenodd" clip-rule="evenodd" d="%s" fill="%s"/></svg></a></li>') % (
            href, label, size, size, path, color)
    return '<ul class="%s">%s%s%s</ul>' % (
        cls, one(WHATSAPP, 'WhatsApp', ICON_WHATSAPP), one('mailto:' + EMAIL, 'Email', ICON_EMAIL),
        one(LINKEDIN, 'LinkedIn', ICON_LINKEDIN))


def lang_links(page, cls):
    out = []
    for l in ('en', 'kk', 'ru'):
        cur = ' aria-current="true"' if l == page.lang else ''
        out.append('<li><a class="%s" href="%s" hreflang="%s" lang="%s"%s>%s'
                   '<span class="visually-hidden"> — %s</span></a></li>' % (
                       cls, page.lang_urls[l], l, l, cur, LANG_LABEL[l], LANG_NAME[l]))
    return ''.join(out)


def header_extras(html, page):
    """Language dropdown opened by the globe button in the header."""
    menu = ('<div id="lang-menu" class="lang-menu" hidden aria-label="%s">'
            '<ul class="lang-menu__list">%s</ul></div>') % (page.t('Language'), lang_links(page, 'lang-menu__link'))
    return html + '\n' + menu


def burger(page):
    items = ''.join('<li><a class="menu__link" href="@@/%s">%s</a></li>' % (href, page.t(label))
                    for href, label in [
                        ('about-ubs/', 'ABOUT US'), ('ubs-services/', 'OUR SERVICES'),
                        ('our-partners/', 'OUR PARTNERS'), ('our-clients/', 'OUR CLIENTS'),
                        ('contacts-ubs/', 'Contacts us')])
    return f'''<div id="site-menu" class="menu" hidden aria-label="{page.t('Menu')}" role="dialog" aria-modal="true">
<div class="menu__panel">
<button type="button" class="menu__close" aria-label="{page.t('Close menu')}"><span></span><span></span></button>
<nav class="menu__nav"><ul class="menu__list">{items}</ul></nav>
<div class="menu__bottom">
<p class="menu__descr">{page.t('Universal business systems establishment')}<br>ISO 9001-2009</p>
{social(32, '#00a0e3', 'social social--menu')}
<a class="menu__btn" href="#popup:myform" data-menu-close><span class="icon-arrow" aria-hidden="true"></span>{page.t('Consultation')}</a>
<ul class="menu__langs">{lang_links(page, 'menu__lang')}</ul>
</div>
</div>
</div>'''


def popup(page):
    fields = [('company', 'text', 'Company name', False, 'organization'),
              ('email', 'email', 'Email', True, 'email'),
              ('name', 'text', 'Name', True, 'name'),
              ('phone', 'tel', 'Phone', True, 'tel')]
    inputs = ''.join(
        '<label class="popup__field"><span class="visually-hidden">%s</span>'
        '<input class="zf__input popup__input" type="%s" name="%s" placeholder="%s" autocomplete="%s"%s></label>' % (
            page.t(ph), typ, name, page.t(ph), ac, ' required' if req else '')
        for name, typ, ph, req, ac in fields)
    return f'''<div id="popup-consultation" class="popup" hidden role="dialog" aria-modal="true" aria-labelledby="popup-title">
<button type="button" class="popup__close" data-popup-close aria-label="{page.t('Close')}"><svg width="23" height="23" viewBox="0 0 23 23" aria-hidden="true"><path d="M.9.9l21.2 21.2M22.1.9L.9 22.1" stroke="currentColor" stroke-width="2"/></svg></button>
<div class="popup__wrap">
<div class="popup__box">
<h2 class="popup__title" id="popup-title">{page.t('Request for a consultation')}</h2>
<p class="popup__descr">{page.t('Simply enter your contact details, and we will get in touch with you.')}</p>
<form class="zf js-form popup__form" action="send.php" method="post" novalidate>
<input type="hidden" name="form" value="popup">
{inputs}
<input type="text" name="website" class="zf__hp" tabindex="-1" autocomplete="off" aria-hidden="true">
<button type="submit" class="zf__btn popup__submit"><span class="icon-arrow" aria-hidden="true"></span>{page.t('Submit')}</button>
<p class="zf__msg popup__msg" role="status" aria-live="polite"></p>
</form>
</div>
</div>
</div>'''


# Logo ribbon: current portfolio from the "Our partners" page (Belkin removed at the client's request).
BRANDS = [
    ('HP', '@/assets/img/38666533-HP_logo_630x630.png'),
    ('Dell Technologies', '@/assets/img/33643131-dell.png'),
    ('Hewlett Packard Enterprise', '@/assets/img/37663935-Hewlett_Packard_Ente.png'),
    ('Lenovo', '@/assets/img/61383730-Lenovo_Global_Corpor.png'),
    ('Cisco', '@/assets/img/65663733-CSCO-187e9f61.png'),
    ('APC by Schneider Electric', '@/assets/img/31636132-LogoAPCsvg.png'),
    ('Microsoft', '@/assets/img/39353139-Microsoft_logo_2012s.png'),
    ('Hikvision', '@/assets/img/39353165-Hikvision-Logowine.png'),
    ('Poly', '@/assets/img/65666136-poly-logo-freelogove.png'),
    ('NetApp', '@/assets/img/35646662-NetApp_logo_2020svg.png'),
    ('Eaton', '@/assets/img/37323164-Eaton_Corporation_lo.png'),
    ('Aruba', '@/assets/img/32323335-Aruba_Networks_logos.png'),
    ('VMware', '@/assets/img/66316531-Vmwaresvg.png'),
    ('AutoCAD', '@/assets/img/37646438-AutoCad_logosvg.png'),
    ('Kaspersky', '@/assets/img/KASPERSKY'),
    ('ESET', '@/assets/img/31376532-ESET_logo.png'),
]


def brands(page):
    items = ''.join('<li class="brands__item"><img src="%s" alt="%s" loading="lazy"></li>' % (
        page.asset_by_name(src), name) for name, src in BRANDS)
    return f'''<section class="brands" aria-label="{page.t('Our partners')}">
<button type="button" class="brands__nav brands__prev" aria-label="{page.t('Previous')}"><svg width="7" height="13" viewBox="0 0 7 13" aria-hidden="true"><path d="M6 1L1 6.5 6 12" fill="none" stroke="currentColor" stroke-width="1.2"/></svg></button>
<div class="brands__viewport"><ul class="brands__track">{items}</ul></div>
<button type="button" class="brands__nav brands__next" aria-label="{page.t('Next')}"><svg width="7" height="13" viewBox="0 0 7 13" aria-hidden="true"><path d="M1 1l5 5.5L1 12" fill="none" stroke="currentColor" stroke-width="1.2"/></svg></button>
</section>'''


def footer(page):
    pages = ''.join('<li><a href="@@/%s">%s</a></li>' % (href, page.t(label)) for href, label in NAV)
    return f'''<footer class="footer">
<div class="container footer__grid">
<div class="footer__col footer__col--brand">
<a class="footer__logo" href="@@/"><img src="{LOGO}" alt="UBS — Universal Business Systems Establishment" width="200"></a>
{social(25, '#000000', 'social social--footer')}
</div>
<div class="footer__col">
<h2 class="footer__title">{page.t('CONTACTS')}</h2>
<ul class="footer__list">
<li><a href="{PHONE_HREF}">{PHONE}</a></li>
<li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
<li>{page.t('Almaty, 050000<br>86 Gogol St.<br>Office (800–806)')}</li>
</ul>
</div>
<div class="footer__col">
<h2 class="footer__title">{page.t('Working hours')}</h2>
<p class="footer__text">{page.t('Monday – Friday')}<br>{page.t('9:00 AM – 6:00 PM')}</p>
<p class="footer__text footer__text--gap">{page.t('Saturday – Sunday: Closed')}</p>
</div>
<nav class="footer__col footer__col--pages" aria-label="{page.t('PAGES')}">
<ul class="footer__list footer__list--pages">{pages}</ul>
</nav>
</div>
</footer>'''


def _txt(el):
    return re.sub(r'\s+', ' ', el.get_text(' ', strip=True)) if el else ''


def values(page, rec):
    cards = []
    for c in rec.select('.t491__col'):
        img = c.select_one('img')
        src = page.asset(img.get('data-original') or img.get('src'))
        cards.append('<li class="values__item"><h3 class="values__name"><img src="%s" alt="" width="30" height="30">%s</h3>'
                     '<p class="values__text">%s</p></li>' % (
                         src, page.t(_txt(c.select_one('.t-card__title'))), page.t(_txt(c.select_one('.t-card__descr')))))
    return f'''<section class="values">
<div class="container">
<h2 class="values__title grad-title">{page.t('Core value')}</h2>
<ul class="values__grid">{''.join(cards)}</ul>
</div>
</section>'''


def tiles(page, rec):
    cards = []
    for col in rec.select('.t-card__col'):
        bg = col.select_one('.t686__bg')
        a = col.select_one('.t-card__title a')
        href = page.ctx.link(a.get('href'))
        title = page.t(_txt(a))
        descr = page.t(_txt(col.select_one('.t-card__descr')))
        cards.append(f'''<li class="tiles__item">
<a class="tiles__card" href="{href}">
<span class="tiles__bg" style="background-image:url('{page.asset(bg['data-original'])}')"></span>
<span class="tiles__overlay"></span>
<span class="tiles__body"><span class="tiles__title">{title}</span><span class="tiles__descr">{descr}</span>
<span class="tiles__btn"><span class="icon-arrow" aria-hidden="true"></span>{page.t('Learn more')}</span></span>
</a>
</li>''')
    return '<section class="tiles"><ul class="container tiles__grid">%s</ul></section>' % ''.join(cards)


OFFICE = (43.258995, 76.936811)  # 86 Gogol St., Almaty (coordinates from the original Tilda map)


def contact_map(page, rec):
    """Ad-free OpenStreetMap (Leaflet, self-hosted) + links to 2GIS / Yandex for directions."""
    landline = '<a href="%s">%s</a><br>' % (LANDLINE[1], LANDLINE[0]) if LANDLINE else ''
    lat, lng = OFFICE
    gis = 'https://2gis.kz/almaty/geo/%s%%2C%s?m=%s%%2C%s%%2F17' % (lng, lat, lng, lat)
    yandex = 'https://yandex.kz/maps/?pt=%s,%s&z=17&l=map' % (lng, lat)
    return f'''<section class="contact">
<div class="contact__map" data-map data-lat="{lat}" data-lng="{lng}" data-popup="UBS · {page.t('Almaty, 050000, 86 Gogol St.,<br>Office (800–806)')}" role="region" aria-label="{page.t('UBS office on the map')}">
<div class="contact__routes"><a href="{gis}" target="_blank" rel="noopener">{page.t('Open in 2GIS')}</a><a href="{yandex}" target="_blank" rel="noopener">{page.t('Open in Yandex Maps')}</a></div>
</div>
<div class="contact__card">
<h1 class="contact__title grad-title">{page.t('Contact us')}</h1>
<p class="contact__text"><a href="{PHONE_HREF}">{PHONE}</a><br>{landline}<a href="mailto:{EMAIL}">{EMAIL}</a><br>{page.t('Almaty, 050000, 86 Gogol St.,<br>Office (800–806)')}</p>
{social(30, '#00a0e3', 'social social--contact')}
</div>
</section>'''


PARTNER_NAMES = {
    'HP_logo': 'HP', 'dell': 'Dell Technologies', 'Hewlett_Packard': 'Hewlett Packard Enterprise',
    'Lenovo': 'Lenovo', 'CSCO': 'Cisco', 'APC': 'APC by Schneider Electric', 'Microsoft': 'Microsoft',
    'Xerox': 'Xerox', 'Hikvision': 'Hikvision', 'poly': 'Poly', 'NetApp': 'NetApp', 'Eaton': 'Eaton',
    'Aruba': 'Aruba', 'Vmware': 'VMware', 'AutoCad': 'AutoCAD', 'aspersky': 'Kaspersky', 'ESET': 'ESET',
}


def partner_name(src):
    for k, v in PARTNER_NAMES.items():
        if k.lower() in src.lower():
            return v
    return ''


def partners(page, rec):
    items = []
    for it in rec.select('.t999__item'):
        src = page.asset(it.select_one('img').get('data-original'))
        descr = page.t(_txt(it.select_one('.t999__descr')))
        items.append('<li class="partners__item"><img src="%s" alt="%s" width="160" loading="lazy">'
                     '<p class="partners__descr">%s</p></li>' % (src, partner_name(src), descr))
    return '<section class="partners"><ul class="container partners__grid">%s</ul></section>' % ''.join(items)


def partner_logos(page, rec):
    items = []
    for img in rec.select('img'):
        src = page.asset(img.get('data-original') or img.get('src'))
        items.append('<li class="logos__item"><img src="%s" alt="%s" loading="lazy"></li>' % (src, partner_name(src)))
    return '<section class="logos"><ul class="container logos__grid">%s</ul></section>' % ''.join(items)


def clients(page, rec):
    cards = []
    for c in rec.select('.t959__card'):
        img = c.select_one('[data-original]')['data-original']
        title = page.t(_txt(c.select_one('.t-card__title')))
        cards.append(f'''<li class="clients__item"><div class="clients__card">
<span class="clients__img" style="background-image:url('{page.asset(img)}')"></span>
<span class="clients__overlay"></span>
<h3 class="clients__name">{title}</h3>
</div></li>''')
    title = page.t(_txt(rec.select_one('.t-section__title')))
    descr = page.t(_txt(rec.select_one('.t-section__descr')))
    return f'''<section class="clients">
<div class="container clients__head">
<h2 class="clients__title grad-title">{title}</h2>
<p class="clients__descr">{descr}</p>
</div>
<ul class="clients__grid">{''.join(cards)}</ul>
</section>'''


# CEO + sales department for the Contacts page (client request).
# Personal phones / e-mails were not supplied yet: fill them in here and rebuild.
LANDLINE = None  # e.g. ('+7 727 000 00 00', 'tel:+77270000000')
TEAM = [
    {'name': 'Rula Haddad', 'role': 'General Director', 'phone': None, 'email': None},
    {'name': 'Yevgeniy Zaitsev', 'role': 'Business Development Manager', 'phone': None, 'email': None},
    {'name': 'Olesya Neb', 'role': 'Sales Manager, 1st Category', 'phone': None, 'email': None},
    {'name': 'Nelya Saidova', 'role': 'Sales Manager', 'phone': None, 'email': None},
    {'name': 'Anatoly Amurin', 'role': 'Sales Manager', 'phone': None, 'email': None},
]


def team(page):
    cards = []
    for p in TEAM:
        lines = []
        if p['phone']:
            lines.append('<a href="tel:%s">%s</a>' % (re.sub(r'[^\d+]', '', p['phone']), p['phone']))
        if p['email']:
            lines.append('<a href="mailto:%s">%s</a>' % (p['email'], p['email']))
        contact = ('<p class="team__contacts">%s</p>' % '<br>'.join(lines)) if lines else (
            '<a class="team__btn" href="#popup:myform"><span class="icon-arrow" aria-hidden="true"></span>%s</a>'
            % page.t('Contact'))
        cards.append('<li class="team__item"><h3 class="team__name">%s</h3><p class="team__role">%s</p>%s</li>' % (
            page.t(p['name']), page.t(p['role']), contact))
    return f'''<section class="team">
<div class="container">
<p class="team__label">{page.t('[ TEAM ]')}</p>
<h2 class="team__title grad-title">{page.t('Management and sales department')}</h2>
<ul class="team__grid">{''.join(cards)}</ul>
</div>
</section>'''
