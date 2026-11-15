"""The three service pages requested by the client.

Texts come from the client's brief (Russian original), formatted as requested:
bold heading + bold subtitle, intro, bulleted list, bold "Result".
"""
import re

from bs4 import BeautifulSoup

ADVANTAGES = {
    'en': ('Our advantages', ['Comprehensive approach', 'Focus on results', 'Individual solutions', 'Long-term cooperation']),
    'ru': ('Наши преимущества', ['Комплексный подход', 'Ориентация на результат', 'Индивидуальные решения', 'Долгосрочное сотрудничество']),
    'kk': ('Біздің артықшылықтарымыз', ['Кешенді тәсіл', 'Нәтижеге бағдарлану', 'Жеке шешімдер', 'Ұзақ мерзімді ынтымақтастық']),
}
UI = {
    'en': {'label': '[ SERVICE ]', 'how': 'How We Work', 'result': 'Result:', 'btn': "LET'S GO!"},
    'ru': {'label': '[ УСЛУГА ]', 'how': 'Как мы работаем', 'result': 'Результат:', 'btn': 'ОСТАВИТЬ ЗАЯВКУ'},
    'kk': {'label': '[ ҚЫЗМЕТ ]', 'how': 'Біз қалай жұмыс істейміз', 'result': 'Нәтиже:', 'btn': 'ӨТІНІМ ҚАЛДЫРУ'},
}

SERVICES = {
    'it-outsourcing': {
        'en': {
            'title': 'IT Outsourcing & Technical Support',
            'subtitle': 'IT infrastructure under professional control.',
            'intro': 'We provide comprehensive IT support for companies, helping keep equipment running smoothly and work processes uninterrupted.',
            'text': 'We take care of your employees’ technical issues, maintain workstations and organise IT support that takes the specifics of your business into account.',
            'list_title': 'Our capabilities:',
            'list': ['Technical support for users.', 'Maintenance and configuration of workstations.',
                     'Diagnostics and troubleshooting of technical faults.',
                     'A dedicated IT specialist on the client’s premises.', 'Comprehensive IT outsourcing.'],
            'result': 'your team keeps working, while technical issues stay under the control of specialists.',
        },
        'ru': {
            'title': 'IT-аутсорсинг и техническая поддержка',
            'subtitle': 'IT-инфраструктура под профессиональным контролем.',
            'intro': 'Обеспечиваем комплексное IT-сопровождение компаний, помогая поддерживать стабильную работу оборудования и бесперебойность рабочих процессов.',
            'text': 'Мы берём на себя решение технических вопросов сотрудников, обслуживание рабочих станций и организацию IT-поддержки с учётом особенностей вашего бизнеса.',
            'list_title': 'Наши возможности:',
            'list': ['Техническая поддержка пользователей.', 'Обслуживание и настройка рабочих станций.',
                     'Диагностика и устранение технических неисправностей.',
                     'Предоставление выделенного IT-специалиста на территории заказчика.', 'Комплексный IT-аутсорсинг.'],
            'result': 'ваша команда работает, а технические вопросы находятся под контролем специалистов.',
        },
        'kk': {
            'title': 'IT-аутсорсинг және техникалық қолдау',
            'subtitle': 'IT-инфрақұрылым кәсіби бақылауда.',
            'intro': 'Компанияларға кешенді IT-сүйемелдеу көрсетеміз: жабдықтың тұрақты жұмысын және жұмыс процестерінің үздіксіздігін қамтамасыз етуге көмектесеміз.',
            'text': 'Қызметкерлеріңіздің техникалық мәселелерін шешуді, жұмыс станцияларына қызмет көрсетуді және бизнесіңіздің ерекшеліктерін ескере отырып IT-қолдауды ұйымдастыруды өз мойнымызға аламыз.',
            'list_title': 'Біздің мүмкіндіктеріміз:',
            'list': ['Пайдаланушыларды техникалық қолдау.', 'Жұмыс станцияларына қызмет көрсету және баптау.',
                     'Техникалық ақауларды диагностикалау және жою.',
                     'Тапсырыс берушінің аумағында арнайы IT-маман ұсыну.', 'Кешенді IT-аутсорсинг.'],
            'result': 'командаңыз жұмыс істей береді, ал техникалық мәселелер мамандардың бақылауында болады.',
        },
    },
    'warranty-service': {
        'en': {
            'title': 'Warranty Service',
            'subtitle': 'Reliable support after purchase.',
            'intro': 'We provide warranty support for equipment, helping clients keep it in working order and receive the technical assistance they need after purchase.',
            'text': '',
            'list_title': 'Our services:',
            'list': ['Technical consultations.', 'Assistance when malfunctions occur.',
                     'Handling of warranty claims.', 'Support on equipment operation.'],
            'result': 'you get not just equipment, but technical support and assistance after purchase.',
        },
        'ru': {
            'title': 'Гарантийное обслуживание оборудования',
            'subtitle': 'Надёжная поддержка после покупки.',
            'intro': 'Мы обеспечиваем гарантийное сопровождение оборудования, помогая клиентам сохранять его работоспособность и получать необходимую техническую поддержку после приобретения.',
            'text': '',
            'list_title': 'Наши услуги:',
            'list': ['Технические консультации.', 'Помощь при возникновении неисправностей.',
                     'Сопровождение гарантийных обращений.', 'Поддержка по вопросам эксплуатации оборудования.'],
            'result': 'вы получаете не просто оборудование, а техническую поддержку и сопровождение после покупки.',
        },
        'kk': {
            'title': 'Жабдыққа кепілдік қызмет көрсету',
            'subtitle': 'Сатып алғаннан кейінгі сенімді қолдау.',
            'intro': 'Жабдықты кепілдік бойынша сүйемелдейміз: клиенттерге оның жұмысқа қабілеттілігін сақтауға және сатып алғаннан кейін қажетті техникалық қолдау алуға көмектесеміз.',
            'text': '',
            'list_title': 'Біздің қызметтеріміз:',
            'list': ['Техникалық кеңес беру.', 'Ақаулар туындаған кезде көмек көрсету.',
                     'Кепілдік өтініштерін сүйемелдеу.', 'Жабдықты пайдалану мәселелері бойынша қолдау.'],
            'result': 'сіз жай ғана жабдық емес, сатып алғаннан кейінгі техникалық қолдау мен сүйемелдеуді аласыз.',
        },
    },
    'service-support': {
        'en': {
            'title': 'Post-Warranty Service & Repair of Office Equipment',
            'subtitle': 'We extend the service life of equipment and restore its performance.',
            'intro': 'We provide professional diagnostics, repair and preventive maintenance of office equipment.',
            'text': 'We help detect faults in time, prevent serious breakdowns and keep equipment in working order.',
            'list_title': 'Our services:',
            'list': ['Diagnostics of office equipment.', 'Equipment repair.', 'Preventive maintenance.',
                     'Detection and elimination of faults.', 'Technical recommendations on operation.'],
            'result': 'working equipment, fewer unplanned downtimes and rational use of company resources.',
        },
        'ru': {
            'title': 'Послегарантийное обслуживание и ремонт офисной техники',
            'subtitle': 'Продлеваем срок службы оборудования и восстанавливаем его работоспособность.',
            'intro': 'Обеспечиваем профессиональную диагностику, ремонт и профилактическое обслуживание офисной техники.',
            'text': 'Помогаем своевременно выявлять неисправности, предотвращать серьёзные поломки и поддерживать оборудование в рабочем состоянии.',
            'list_title': 'Наши услуги:',
            'list': ['Диагностика офисной техники.', 'Ремонт оборудования.', 'Профилактическое обслуживание.',
                     'Выявление и устранение неисправностей.', 'Технические рекомендации по эксплуатации.'],
            'result': 'исправная техника, меньше незапланированных простоев и рациональное использование ресурсов компании.',
        },
        'kk': {
            'title': 'Кеңсе техникасына кепілдіктен кейінгі қызмет көрсету және жөндеу',
            'subtitle': 'Жабдықтың қызмет ету мерзімін ұзартып, жұмысқа қабілеттілігін қалпына келтіреміз.',
            'intro': 'Кеңсе техникасын кәсіби диагностикалауды, жөндеуді және профилактикалық қызмет көрсетуді қамтамасыз етеміз.',
            'text': 'Ақауларды уақтылы анықтауға, елеулі бұзылулардың алдын алуға және жабдықты жұмыс күйінде ұстауға көмектесеміз.',
            'list_title': 'Біздің қызметтеріміз:',
            'list': ['Кеңсе техникасын диагностикалау.', 'Жабдықты жөндеу.', 'Профилактикалық қызмет көрсету.',
                     'Ақауларды анықтау және жою.', 'Пайдалану бойынша техникалық ұсынымдар.'],
            'result': 'жарамды техника, жоспардан тыс тоқтап қалулардың азаюы және компания ресурстарын тиімді пайдалану.',
        },
    },
}
# Short names used in menus / cards (EN keys are translated through the i18n files)
TITLES = {slug: {l: d[l]['title'] for l in d} for slug, d in SERVICES.items()}


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def _media_blocks(css):
    """Yield (media_prefix, body) pairs: ('', base rules) and ('@media (...)', rules)."""
    pos = 0
    for m in re.finditer(r'@media([^{]*)\{((?:[^{}]*\{[^}]*\})*)\}', css):
        yield '', css[pos:m.start()]
        yield '@media' + m.group(1), m.group(2)
        pos = m.end()
    yield '', css[pos:]


def service_hero(page, html, css, scope):
    """Replace the fixed-size glass card of a service hero with a flowing one (fits any language)."""
    ui = UI[page.lang]
    soup = BeautifulSoup(html, 'html.parser')
    sec = soup.find('section')
    texts = [e for e in sec.select('.el--text')]
    btn = sec.select_one('.el--button')
    panel = None
    for e in sec.select('.el--shape'):
        cls = [c for c in e['class'] if re.fullmatch(r'e\d+', c)][0]
        if re.search(r'%s \.%s\{[^}]*backdrop-filter' % (re.escape(scope), cls), css):
            panel = e
            break
    pcls = [c for c in panel['class'] if re.fullmatch(r'e\d+', c)][0]
    if page.slug in SERVICES:
        d = SERVICES[page.slug][page.lang]
        title = esc(d['title'])
        body = ('<p class="svc-card__lead"><strong>%s</strong></p><p class="svc-card__text">%s</p>' % (
            esc(d['subtitle']), esc(d['intro'])))
        label = esc(ui['btn'])
    else:  # Delivery / Information security keep their own (translated) texts
        title = ''.join(str(c) for c in texts[0].select_one('.a').contents).strip()
        body = '<p class="svc-card__text">%s</p>' % ''.join(str(c) for c in texts[1].select_one('.a').contents).strip()
        t = btn.select_one('.btn__t')
        label = t.get_text() if t else esc(ui['btn'])
    # panel geometry for every breakpoint
    geo = []
    for media, block in _media_blocks(css):
        for m in re.finditer(r'%s \.%s\{([^}]*)\}' % (re.escape(scope), pcls), block):
            decl = dict(re.findall(r'(?<![-\w])(top|left|width|height):([^;]+)', m.group(1)))
            if decl:
                geo.append((media, decl))
    for e in texts + [btn, panel]:
        e.decompose()
    card = BeautifulSoup(
        '<div class="el svc-card" data-anim="fadeinleft" data-anim-duration="2" data-anim-distance="20" data-anim-mobile="y">'
        '<div class="svc-card__in"><h1 class="svc-card__title">%s</h1>%s'
        '<a class="svc-card__btn" href="#popup:myform">%s</a></div></div>' % (title, body, label),
        'html.parser')
    sec.append(card)
    rules = []
    for media, decl in geo:
        if media and ('959' in media or '639' in media):
            continue  # tablets get their own layout below (the original had none)
        b = ';'.join('%s:%s' % (k, 'auto' if k == 'height' else v) for k, v in decl.items())
        if 'height' in decl:
            b += ';min-height:%s' % decl['height']
        r = '%s .svc-card{%s}' % (scope, b)
        rules.append('%s{%s}' % (media, r) if media else r)
    img = [c for c in sec.select_one('.el')['class'] if re.fullmatch(r'e\d+', c)][0]
    for mq, h, top, w in (('max-width:959px', 620, 160, 600), ('max-width:639px', 640, 140, 460)):
        rules.append('@media (%s){%s{height:%dpx}%s .%s{top:0;height:%dpx}'
                     '%s .svc-card{top:%dpx;left:calc(50%% - %dpx);width:%dpx;min-height:0}}' % (
                         mq, scope, h, scope, img, h, scope, top, w // 2, w))
    css += '\n' + '\n'.join(rules)
    return str(soup), css


def service_detail(page, rec):
    d = SERVICES[page.slug][page.lang]
    ui = UI[page.lang]
    adv_title, adv = ADVANTAGES[page.lang]
    img = None
    for el in rec.select('[data-original]'):
        img = el['data-original']
        break
    items = ''.join('<li>%s</li>' % esc(x) for x in d['list'])
    advs = ''.join('<li class="svc__adv-item"><span class="svc__plus" aria-hidden="true">+</span>%s</li>' % esc(a) for a in adv)
    text = '<p class="svc__p">%s</p>' % esc(d['text']) if d['text'] else ''
    return f'''<section class="svc">
<span class="svc__circle" aria-hidden="true"></span>
<div class="svc__grid">
<div class="svc__head">
<p class="svc__label" data-anim="fadeinright" data-anim-duration="2" data-anim-distance="20" data-anim-mobile="y">{ui['label']}</p>
<h2 class="svc__title grad-title" data-anim="fadeinright" data-anim-duration="2" data-anim-distance="20" data-anim-mobile="y">{esc(ui['how'])}</h2>
</div>
<div class="svc__img" style="background-image:url('{page.asset(img)}')" role="img" aria-label="{esc(d['title'])}"></div>
<div class="svc__body">
<h3 class="svc__h" data-anim="fadeinleft" data-anim-duration="2" data-anim-distance="20" data-anim-mobile="y">{esc(d['subtitle'])}</h3>
<div data-anim="fadeinright" data-anim-duration="2" data-anim-delay="0.1" data-anim-distance="20" data-anim-mobile="y">
{text}
<p class="svc__list-title"><strong>{esc(d['list_title'])}</strong></p>
<ul class="svc__list">{items}</ul>
<p class="svc__result"><strong>{esc(ui['result'])}</strong> {esc(d['result'])}</p>
</div>
<div class="svc__adv" data-anim="fadein" data-anim-duration="3" data-anim-delay="0.1" data-anim-mobile="y">
<p class="svc__adv-title">{esc(adv_title)}</p>
<ul class="svc__adv-list">{advs}</ul>
</div>
</div>
</div>
</section>'''


EXTRA_CSS = {}
