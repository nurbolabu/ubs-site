"""Team list with expandable quotes (About page), as on the original Tilda page.

Photos are optional: put a square photo (at least 240x240) into docs/assets/img/team/ and
write its file name into 'photo'. A person with a photo gets a round portrait next to the name
(80 px on computers, 72 on tablets, 56 on phones); people without a photo keep the plain layout.
The current photos of the first four people are placeholders (stock / home page images).
"""

TEAM = [
    {
        'id': 'safa-butrous', 'photo': 'safa-butrous.jpg',
        'name': {'en': 'Safa Butrous', 'ru': 'Сафа Бутрус', 'kk': 'Сафа Бутрус'},
        'role': {'en': 'Founder', 'ru': 'Основатель', 'kk': 'Негізін қалаушы'},
        'text': {
            'en': 'Safa Butrous founded UBS Establishment in 1996 with a clear vision and strong commitment to quality and trust. His leadership shaped the company into a leading name in Kazakhstan’s IT market. Today, UBS continues to follow his principles, focusing on innovation and sustainable growth.',
            'ru': 'Сафа Бутрус основал UBS Establishment в 1996 году, сделав ставку на качество и доверие. Под его руководством компания стала одним из ведущих имён на IT-рынке Казахстана. Сегодня UBS продолжает следовать его принципам, уделяя особое внимание инновациям и устойчивому развитию.',
            'kk': 'Сафа Бутрус UBS Establishment компаниясын 1996 жылы сапа мен сенімге басымдық бере отырып құрды. Оның басшылығымен компания Қазақстанның IT-нарығындағы жетекші есімдердің біріне айналды. Бүгінде UBS оның қағидаттарын ұстанып, инновация мен тұрақты дамуға ерекше назар аударады.',
        },
    },
    {
        'id': 'rula-haddad', 'photo': 'rula-haddad.jpg',
        'name': {'en': 'Rula Haddad', 'ru': 'Рула Хаддад', 'kk': 'Рула Хаддад'},
        'role': {'en': 'General Director', 'ru': 'Генеральный директор', 'kk': 'Бас директор'},
        'text': {
            'en': '“UBS Establishment is more than just a service and technology provider — we are a true partner who prioritizes the comfort and satisfaction of our clients. We are committed to delivering personalized solutions tailored to each client’s specific needs. By closely monitoring developments in the tech industry, we ensure timely access to cutting-edge solutions that empower our clients to grow in today’s highly competitive market. Our principle is simple: we work for our customers.”',
            'ru': '«UBS Establishment — это не просто поставщик услуг и технологий, а настоящий партнёр, для которого комфорт и удовлетворённость клиентов стоят на первом месте. Мы предлагаем индивидуальные решения с учётом задач каждого клиента. Внимательно следя за развитием технологической отрасли, мы своевременно даём доступ к передовым решениям, которые помогают нашим клиентам расти на высококонкурентном рынке. Наш принцип прост: мы работаем для наших клиентов».',
            'kk': '«UBS Establishment — жай ғана қызмет пен технология жеткізушісі емес, клиенттердің жайлылығы мен қанағаттануын бірінші орынға қоятын нағыз серіктес. Біз әр клиенттің міндеттерін ескеретін жеке шешімдер ұсынамыз. Технологиялық саланың дамуын мұқият қадағалай отырып, клиенттерімізге бәсекесі жоғары нарықта өсуге көмектесетін озық шешімдерге уақтылы қол жеткізуді қамтамасыз етеміз. Біздің қағидатымыз қарапайым: біз клиенттеріміз үшін жұмыс істейміз».',
        },
    },
    {
        'id': 'samer-abu-laban', 'photo': 'samer-abu-laban.jpg',
        'name': {'en': 'Samer Abu-Laban', 'ru': 'Самер Абу-Лабан', 'kk': 'Самер Абу-Лабан'},
        'role': {'en': 'Site Division Manager', 'ru': 'Менеджер по инженерной модернизации проектов', 'kk': 'Жобаларды инженерлік жаңғырту жөніндегі менеджер'},
        'text': {
            'en': '“At UBS, I found a supportive environment and real opportunities for professional growth, alongside a collaborative team and positive atmosphere.”',
            'ru': '«В UBS я нашёл поддерживающую среду и реальные возможности для профессионального роста, а также сплочённую команду и позитивную атмосферу».',
            'kk': '«UBS-те мен қолдау көрсететін ортаны және кәсіби өсудің нақты мүмкіндіктерін, сондай-ақ ауызбіршілігі мықты команда мен жағымды атмосфераны таптым».',
        },
    },
    {
        'id': 'yevgeniy-zaitsev', 'photo': 'yevgeniy-zaitsev.jpg',
        'name': {'en': 'Yevgeniy Zaitsev', 'ru': 'Евгений Зайцев', 'kk': 'Евгений Зайцев'},
        'role': {'en': 'Business Development Manager', 'ru': 'Менеджер по развитию бизнеса', 'kk': 'Бизнесті дамыту жөніндегі менеджер'},
        'text': {
            'en': '“Although we operate exclusively in Kazakhstan, UBS has built a strong reputation as a trusted supplier to major companies in the region.”',
            'ru': '«Хотя мы работаем только в Казахстане, UBS заслужила прочную репутацию надёжного поставщика для крупных компаний региона».',
            'kk': '«Біз тек Қазақстанда жұмыс істесек те, UBS аймақтағы ірі компаниялардың сенімді жеткізушісі ретінде берік бедел қалыптастырды».',
        },
    },
    {
        'id': 'olesya-neb', 'photo': None,
        'name': {'en': 'Olesya Neb', 'ru': 'Олеся Неб', 'kk': 'Олеся Неб'},
        'role': {'en': 'Sales Manager, 1st Category', 'ru': 'Менеджер по продажам 1-й категории', 'kk': '1-санатты сату менеджері'},
        'text': {
            'en': '“Customer satisfaction is our top priority. We provide flexible solutions, competitive pricing, and timely deliveries to maintain our edge.”',
            'ru': '«Удовлетворённость клиентов — наш главный приоритет. Гибкие решения, конкурентные цены и своевременные поставки помогают нам сохранять лидерство».',
            'kk': '«Клиенттердің қанағаттануы — біздің басты басымдығымыз. Икемді шешімдер, бәсекеге қабілетті бағалар және уақтылы жеткізу көшбасшылықты сақтауға көмектеседі».',
        },
    },
    {
        'id': 'nelya-saidova', 'photo': None,
        'name': {'en': 'Nelya Saidova', 'ru': 'Неля Саидова', 'kk': 'Неля Саидова'},
        'role': {'en': 'Sales Manager', 'ru': 'Менеджер по продажам', 'kk': 'Сату менеджері'},
        'text': {
            'en': '“To me, UBS means stability and confidence in the future. With our presence in key cities across Kazakhstan, we’re always close to our clients.”',
            'ru': '«Для меня UBS — это стабильность и уверенность в будущем. Благодаря присутствию в ключевых городах Казахстана мы всегда рядом с клиентами».',
            'kk': '«Мен үшін UBS — тұрақтылық пен болашаққа деген сенім. Қазақстанның негізгі қалаларында болуымыздың арқасында біз әрдайым клиенттерге жақынбыз».',
        },
    },
    {
        'id': 'anatoly-amurin', 'photo': None,
        'name': {'en': 'Anatoly Amurin', 'ru': 'Анатолий Амурин', 'kk': 'Анатолий Амурин'},
        'role': {'en': 'Sales Manager', 'ru': 'Менеджер по продажам', 'kk': 'Сату менеджері'},
        'text': {
            'en': '“I have been working at UBS Establishment since June 2026. I really like the friendly atmosphere that prevails in the team: all employees are ready to help and prompt in any work process. The Company values every request and every project of the Customer, regardless of its size.”',
            'ru': '«Я работаю в UBS Establishment с июня 2026 года. Мне очень нравится дружеская атмосфера в коллективе: все сотрудники готовы помочь и подсказать в любом рабочем вопросе. Компания ценит каждый запрос и каждый проект клиента, независимо от его масштаба».',
            'kk': '«Мен UBS Establishment-те 2026 жылдың маусымынан бері жұмыс істеймін. Ұжымдағы достық атмосфера маған қатты ұнайды: барлық қызметкерлер кез келген жұмыс мәселесінде көмектесуге және кеңес беруге дайын. Компания клиенттің әр сұранысы мен әр жобасын көлеміне қарамастан бағалайды».',
        },
    },
    {
        'id': 'irina-volgina', 'photo': None,
        'name': {'en': 'Irina Volgina', 'ru': 'Ирина Волгина', 'kk': 'Ирина Волгина'},
        'role': {'en': 'Service Manager', 'ru': 'Сервис-менеджер', 'kk': 'Сервис-менеджер'},
        'text': {
            'en': '“UBS represents a team of dedicated professionals who are constantly evolving. We are committed to solving complex problems and delivering successful projects.”',
            'ru': '«UBS — это команда преданных своему делу профессионалов, которые постоянно развиваются. Мы нацелены на решение сложных задач и успешную реализацию проектов».',
            'kk': '«UBS — өз ісіне берілген, үнемі дамып отыратын кәсіпқойлар командасы. Біз күрделі міндеттерді шешуге және жобаларды табысты іске асыруға ұмтыламыз».',
        },
    },
    {
        'id': 'andrey-ilchenko', 'photo': None,
        'name': {'en': 'Andrey Ilchenko', 'ru': 'Андрей Ильченко', 'kk': 'Андрей Ильченко'},
        'role': {'en': 'Director of the Technical Department', 'ru': 'Директор технического департамента', 'kk': 'Техникалық департамент директоры'},
        'text': {
            'en': '“I’m proud to work for a company with a long-standing history and strong market presence. Our corporate culture encourages teamwork, which is at the heart of our success.”',
            'ru': '«Я горжусь тем, что работаю в компании с многолетней историей и сильными позициями на рынке. Наша корпоративная культура поощряет командную работу — она лежит в основе нашего успеха».',
            'kk': '«Көпжылдық тарихы бар және нарықта берік орны бар компанияда жұмыс істейтініме мақтанамын. Біздің корпоративтік мәдениетіміз командалық жұмысты қолдайды — табысымыздың негізі осы».',
        },
    },
]

UI = {
    'en': {'label': '[ TEAM ]', 'title': 'Our team'},
    'ru': {'label': '[ КОМАНДА ]', 'title': 'Наша команда'},
    'kk': {'label': '[ КОМАНДА ]', 'title': 'Біздің команда'},
}

PLUS = ('<svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
        '<path d="M1 12h22M12 1v22" stroke="currentColor" stroke-width="2" stroke-linecap="square" fill="none"/></svg>')


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def item(p, lang, suffix=''):
    name, role, text = p['name'][lang], p['role'][lang], p['text'][lang]
    pid = 'team-' + p['id'] + suffix
    photo = '@/assets/img/team/' + p['photo'] if p['photo'] else None
    avatar = ('<img class="acc__avatar" src="%s" alt="%s" width="80" height="80" loading="lazy">'
              % (photo, esc(name))) if photo else ''
    return f'''<li class="acc__item{' has-photo' if photo else ''}">
<h3 class="acc__head"><button type="button" class="acc__btn" aria-expanded="false" aria-controls="{pid}">{avatar}<span class="acc__titles"><span class="acc__name">{esc(name)}</span><span class="acc__role">{esc(role)}</span></span><span class="acc__icon">{PLUS}</span></button></h3>
<div class="acc__panel" id="{pid}" role="region" hidden><div class="acc__body"><p class="acc__text">{esc(text)}</p></div></div>
</li>'''


def accordion(page):
    lang = page.lang
    ui = UI[lang]
    # two independent columns on wide screens (as the original), one list in order on narrow ones
    left = ''.join(item(p, lang) for i, p in enumerate(TEAM) if i % 2 == 0)
    right = ''.join(item(p, lang) for i, p in enumerate(TEAM) if i % 2 == 1)
    single = ''.join(item(p, lang, '-m') for p in TEAM)
    return f'''<section class="team-acc" id="team">
<span class="team-acc__rings" aria-hidden="true"></span>
<div class="container">
<p class="team-acc__label" data-anim="fadeinright" data-anim-duration="2" data-anim-distance="20" data-anim-mobile="y">{ui['label']}</p>
<h2 class="team-acc__title grad-title" data-anim="fadeinleft" data-anim-duration="2" data-anim-distance="20" data-anim-mobile="y">{esc(ui['title'])}</h2>
<div class="acc acc--wide">
<ul class="acc__col">{left}</ul>
<ul class="acc__col">{right}</ul>
</div>
<div class="acc acc--narrow">
<ul class="acc__col">{single}</ul>
</div>
</div>
</section>'''
