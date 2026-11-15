"""Download every Tilda-hosted asset referenced by the original pages into docs/assets."""
import os, re, json, subprocess, concurrent.futures as cf
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
urls = [u.strip() for u in open(os.path.join(ROOT, 'tools/urls.txt')) if u.strip()]
def local_name(u):
    m = re.search(r'/tild([0-9a-f]{4})-([0-9a-f-]+)/([^/?#]+)$', u)
    name = m.group(3) if m else u.rsplit('/', 1)[-1]
    name = re.sub(r'[^A-Za-z0-9._-]', '_', name)
    ext = name.rsplit('.', 1)[-1].lower()
    sub = 'fonts' if ext in ('woff', 'woff2', 'ttf', 'otf') else 'icons' if '/lib/icons/' in u else 'img'
    if m: name = m.group(1) + m.group(2)[:4] + '-' + name
    return f'assets/{sub}/{name}'
mapping = {u: local_name(u) for u in urls}
def get(u):
    dst = os.path.join(ROOT, 'docs', mapping[u])
    if os.path.exists(dst) and os.path.getsize(dst) > 0: return
    subprocess.run(['curl', '-sfL', '-A', 'Mozilla/5.0', '-o', dst, u], check=True)
with cf.ThreadPoolExecutor(8) as ex:
    list(ex.map(get, urls))
json.dump(mapping, open(os.path.join(ROOT, 'tools/assets.json'), 'w'), indent=1)
print(len(mapping), 'assets')
