"""Client edits on top of the original design (from "Comments to the site.docx").

Summary (details in CHANGES.md):
  * Services: IT Consulting & Audit, Comprehensive IT Solutions and Certified Service Center
    are removed; the service line-up is now IT outsourcing & support, warranty service and
    post-warranty service & repair (texts supplied by the client, formatted as requested).
  * About: team list removed, founder photo added (placeholder until the photo arrives).
  * Contacts: CEO and sales department block, landline placeholder.
  * Partners: "Our Partners Include", HP / Lenovo statuses corrected, Xerox wording neutral.
  * Logo ribbon: Belkin removed, current partner portfolio shown.
  * Mentions of certified service / audit of telecom systems / "over 32 specialists" removed.
"""
import html as htmllib
import re

import components as C
import services as S

SHARED_ZERO = {'4711345103'}


def norm_text(s):
    s = htmllib.unescape(s).replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', s).strip()


# English text replacements applied before translation (key = normalised original text).
REPLACE = {
    # Home hero, slide 2: no consulting / certified service any more
    'Comprehensive IT consulting, maintenance, and certified technical support. We optimize your infrastructure to ensure seamless business continuity and maximum efficiency.':
        'IT outsourcing, technical support, warranty and post-warranty service of office equipment. We keep your infrastructure running so your business works without interruptions.',
    # Services page cards
    '<a href="/ubs-services" style="color: inherit">IT Consulting & Audit</a>':
        '<a href="/it-consulting-audit">IT Outsourcing & Support</a>',
    '<a href="/ubs-services" style="color: inherit">Full IT maintenance covering servers, network devices, computers, and telecommunication systems. We evaluate your infrastructure and recommend improvements to ensure maximum security and efficiency</a>':
        '<a href="/it-consulting-audit">Help desk user support, workstation maintenance and a dedicated IT specialist on your site. Your infrastructure stays under professional control</a>',
    'Comprehensive IT Solutions': 'Warranty Service',
    'We supply and install original hardware, build robust network systems, license software, and integrate customized IT solutions using trusted global brands.':
        'Warranty support for equipment: technical consultations, help with malfunctions and handling of warranty claims after purchase.',
    'Service Support': 'Post-Warranty Service',
    'Professional maintenance of printers, workstations, laptops, servers, and data storage systems':
        'Diagnostics, repair and preventive maintenance of office equipment to extend its service life',
    'We provide reliable after-sales and certified technical support backed by manufacturers to ensure your devices operate efficiently.':
        'We provide reliable after-sales support, warranty and post-warranty service to keep your equipment operating efficiently.',
    'We equip industrial corporations with reliable IT solutions, from workstations to telecommunication systems, backed by certified on-site service to minimize operational downtime.':
        'We equip industrial corporations with reliable IT solutions, from workstations to office equipment, backed by on-site service to minimize operational downtime.',
    # Information security page: no "32+" claim
    'Protecting your enterprise data is a top priority for our 32+ specialized professionals. Operating from Almaty, Astana, and Atyrau, our experts integrate robust security protocols into your systems, ensuring your business data remains secure, compliant, and continuously monitored against vulnerabilities.':
        'Protecting your enterprise data is a top priority for our specialists. Operating from Almaty, Astana, and Atyrau, our experts integrate robust security protocols into your systems, ensuring your business data remains secure, compliant, and continuously monitored against vulnerabilities.',
    # About: one long block split into paragraphs (client: "clear paragraphs")
    'Since its establishment in 1996, UBS Establishment has aimed to be more than just a technology supplier—it strives to be a strategic and reliable partner in the digital transformation journey of its clients. The company has grown steadily thanks to its commitment to quality and professionalism, along with strong partnerships with the world’s leading IT manufacturers. On this page, you’ll discover our company history, vision, values, and the dedicated teams behind our success—along with detailed information about our branches and long-standing experience serving key sectors across Kazakhstan.':
        'Since its establishment in 1996, UBS Establishment has aimed to be more than just a technology supplier—it strives to be a strategic and reliable partner in the digital transformation journey of its clients.<br><br>The company has grown steadily thanks to its commitment to quality and professionalism, along with strong partnerships with the world’s leading IT manufacturers.<br><br>On this page, you’ll discover our company history, vision, values, and the dedicated teams behind our success—along with detailed information about our branches and long-standing experience serving key sectors across Kazakhstan.',
    # Partners page
    'Our Certified Partners Include:': 'Our Partners Include:',
    'Official HP Amplify Member': 'HP Amplify Synergy Partner',
    'Authorized distributor of hardware and infrastructure solutions': 'Lenovo 360 Authorized Partner',
    'Certified distributor of printing and office solutions': 'Printing and office solutions',
    '<ul><li>Provide genuine, original products directly from the source</li><li>Offer certified technical support backed by manufacturers</li><li>Grant access to exclusive partner programs and promotions</li><li>Ensure continuous software licensing and updates</li><li>Deliver and implement solutions with high efficiency and reliability</li></ul>':
        '<ul><li>Provide genuine, original products directly from the source</li><li>Offer technical support backed by manufacturers</li><li>Grant access to exclusive partner programs and promotions</li><li>Ensure continuous software licensing and updates</li><li>Deliver and implement solutions with high efficiency and reliability</li></ul>',
}
_PARTNERS_INTRO = ('we have become an authorized distributor and trusted solutions provider',
                   'we have become an authorized partner and trusted solutions provider')


def replace_text(text):
    k = norm_text(text)
    if k in REPLACE:
        return REPLACE[k]
    if _PARTNERS_INTRO[0] in k:
        return k.replace(*_PARTNERS_INTRO).replace('backed by certified support', 'backed by manufacturer support')
    return text


EDITS = {
    # Founder section removed: Safa Butrous is the first person of the team list
    'about-ubs': {'skip': {'2626429403'}},
    # Certified Service Center card removed from the services page
    'ubs-services': {'skip': {'3350072703'}},
    # CEO + sales department after the contact card
    'contacts-ubs': {'after_block': {'554': C.team}},
}


def get(slug):
    return EDITS.get(slug, {})


# ---------------------------------------------------------------- helpers on generated CSS
def shift_block(css, scope, dy, grow=None):
    """Move every element of a positioned section down by dy px and grow its height."""
    grow = dy if grow is None else grow

    def fix_rule(m):
        sel, body = m.group(1), m.group(2)
        s = sel.strip()
        if re.fullmatch(r'%s \.e\d+' % re.escape(scope), s):
            body = re.sub(r'(?<![-\w])top:([^;}]+)', lambda t: 'top:calc(%s + %dpx)' % (t.group(1), dy), body)
        elif scope in [x.strip() for x in s.split(',')]:
            body = re.sub(r'(?<![-\w])height:(\d+)px', lambda h: 'height:%dpx' % (int(h.group(1)) + grow), body)
        return '%s{%s}' % (sel, body)
    out = []
    for chunk in re.split(r'(@media[^{]*\{)', css):
        out.append(chunk if chunk.startswith('@media') else re.sub(r'([^{}@]+)\{([^{}]*)\}', fix_rule, chunk))
    return ''.join(out)


def on_zero(page, n, rec, html, css):
    """Called for every positioned (non-header) section; n = its order on the page."""
    slug = page.slug
    scope = '#' + re.search(r'<section id="([^"]+)"', html).group(1)
    text = rec.get_text(' ')
    if slug == 'about-ubs' and 'Safa Butrous' in text:
        html, css = founder_photo(page, html, css, scope)
    if n == 0 and (slug in S.SERVICES or slug in ('delivery', 'information-security')):
        html, css = S.service_hero(page, html, css, scope)
    elif slug in S.SERVICES:
        if 'How We Work' in text:
            return S.service_detail(page, rec), ''
    return html, css


FOUNDER_PHOTO = '@/assets/img/founder.svg'  # replace with the real photo (e.g. founder.jpg)


def founder_photo(page, html, css, scope):
    css = shift_block(css, scope, 250)
    photo = ('<div class="el founder-photo" data-anim="fadein" data-anim-duration="2" data-anim-mobile="y">'
             '<img src="%s" alt="%s" width="200" height="200" loading="lazy"></div>') % (
        FOUNDER_PHOTO, page.t('Safa Butrous, founder of UBS Establishment'))
    html = html.replace('<div class="z__bg"></div><div class="z__filter"></div>',
                        '<div class="z__bg"></div><div class="z__filter"></div>\n' + photo, 1)
    html = html.replace(' z--visible', '', 1)
    css += '\n%s .founder-photo{top:30px;left:calc(50%% - 100px);width:200px;height:200px;z-index:4}' % scope
    css += ('\n%s .founder-photo img{display:block;width:200px;height:200px;border-radius:50%%;'
            'object-fit:cover;box-shadow:0 20px 50px rgba(0,119,255,.12)}') % scope
    return html, css


def _hero_fix(scope):
    # Tilda kept 1585/1405/1275 px tall placeholders on tablets: give the cover image a sane height
    out = []
    for mq, h in (('max-width:1199px', 480), ('min-width:640px) and (max-width:959px', 420)):
        out.append('@media (%s){%s{height:%dpx}%s .e1{top:0;height:%dpx}}' % (mq, scope, h, scope, h))
    return '\n'.join(out)


EXTRA_CSS = {
    'about-ubs': _hero_fix('#s415403'),
    'our-partners': _hero_fix('#s878003'),
    'our-clients': _hero_fix('#s071503'),
}


def extra_css(slug):
    return S.EXTRA_CSS.get(slug, '') + EXTRA_CSS.get(slug, '')


_HERO_SMALL = ('@media (max-width:959px){#s400963 .e10 .a,#s400963 .e13 .a,#s400963 .e14 .a{font-size:30px}}'
               '@media (max-width:639px){#s400963 .e10 .a,#s400963 .e13 .a,#s400963 .e14 .a{font-size:23px}}')
LANG_CSS = {
    # long single words in the home hero titles: smaller on phones
    'ru': _HERO_SMALL,
    'kk': _HERO_SMALL,
}


def _labels_above_titles():
    """Why-us circles: long RU/KK words reach the [01]..[04] marks; on screens below 1200 px
    the marks sit above their titles instead of beside them."""
    import os
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        'docs/assets/css/page-ubs-services.css')
    css = open(path, encoding='utf8').read()
    out = []
    for media, block in S._media_blocks(css):
        if not media:
            continue
        for title, label in (('e7', 'e9'), ('e10', 'e12'), ('e13', 'e15'), ('e16', 'e18')):
            m = re.search(r'#s072903 \.%s\{([^}]*)\}' % title, block)
            if not m:
                continue
            d = dict(re.findall(r'(?<![-\w])(top|left):([^;]+)', m.group(1)))
            if 'top' in d and 'left' in d:
                out.append('%s{#s072903 .%s{top:calc(%s - 24px);left:%s}}' % (media, label, d['top'], d['left']))
    return '\n'.join(out)


def lang_css(lang):
    return LANG_CSS.get(lang, '').replace('#s', 'html[lang="%s"] #s' % lang)


def all_lang_css():
    return _labels_above_titles()
