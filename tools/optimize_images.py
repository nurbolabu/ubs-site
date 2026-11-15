"""Recompress heavy photos in docs/assets/img (needs Pillow).

Large opaque PNG photos become JPEG (assets.json is updated so the build links the new
file); JPEGs wider than 2400 px are downscaled. Logos / transparent images are untouched.
"""
import json
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, 'docs/assets/img')
MAP = os.path.join(ROOT, 'tools/assets.json')
assets = json.load(open(MAP))
renamed = {}
for name in sorted(os.listdir(IMG)):
    path = os.path.join(IMG, name)
    ext = name.rsplit('.', 1)[-1].lower()
    size = os.path.getsize(path)
    if ext not in ('png', 'jpg', 'jpeg') or size < 250_000:
        continue
    im = Image.open(path)
    has_alpha = im.mode in ('RGBA', 'LA', 'P') and (
        im.mode != 'P' or 'transparency' in im.info)
    if has_alpha and im.mode != 'P':
        alpha = im.getchannel('A')
        has_alpha = alpha.getextrema()[0] < 250
    if ext == 'png' and has_alpha:
        continue
    im = im.convert('RGB')
    if im.width > 2400:
        im = im.resize((2400, round(im.height * 2400 / im.width)), Image.LANCZOS)
    new_name = name.rsplit('.', 1)[0] + '.jpg'
    out = os.path.join(IMG, new_name)
    im.save(out, 'JPEG', quality=82, optimize=True, progressive=True)
    if new_name != name:
        os.remove(path)
        renamed['assets/img/' + name] = 'assets/img/' + new_name
    print('%-45s %5d KB -> %5d KB' % (name, size // 1024, os.path.getsize(out) // 1024))
for k, v in assets.items():
    if v in renamed:
        assets[k] = renamed[v]
json.dump(assets, open(MAP, 'w'), indent=1)
