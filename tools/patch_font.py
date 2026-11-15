"""Add the Kazakh letters missing from the TRYGrtsk heading font.

The font has Russian Cyrillic but lacks Ә Ғ Қ Ң Ө Ұ Ү Һ (and lowercase). They are built
from existing glyphs of the same font (Э, Г, К, Н, О, Y, h, v, е) plus bars/descenders
of the font's own stroke weight, so headings in Kazakh stay in one typeface.

    <venv>/bin/python tools/patch_font.py      (needs fonttools + brotli)

Reads src/fonts/*.woff (originals), writes docs/assets/fonts/*.woff.
"""
import glob
import os

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rect(pen, x0, y0, x1, y1):
    pen.moveTo((x0, y0))
    pen.lineTo((x0, y1))
    pen.lineTo((x1, y1))
    pen.lineTo((x1, y0))
    pen.closePath()


def patch(path_in, path_out):
    f = TTFont(path_in)
    cmap = f.getBestCmap()
    gs = f.getGlyphSet()
    glyf, hmtx = f['glyf'], f['hmtx']
    g = lambda ch: cmap[ord(ch)]

    def bounds(name):
        b = BoundsPen(gs)
        gs[name].draw(b)
        return b.bounds

    hy = bounds('hyphen')
    t = hy[3] - hy[1]            # horizontal stroke thickness
    tv = round(t * 1.12)         # vertical stroke thickness (stems are a bit heavier)

    def build(code, base, extra=None, transform=None, add_width=0):
        pen = TTGlyphPen(gs)
        src = TransformPen(pen, transform) if transform else pen
        gs[base].draw(src)
        if extra:
            extra(pen)
        name = 'uni%04X' % code
        glyf[name] = pen.glyph()
        hmtx[name] = (hmtx[base][0] + add_width, hmtx[base][1])
        if name not in f.getGlyphOrder():
            f.setGlyphOrder(f.getGlyphOrder() + [name])
        for table in f['cmap'].tables:
            if table.isUnicode():
                table.cmap[code] = name

    cap, xh = 700, f['OS/2'].sxHeight or 545

    # Ә ә
    build(0x04D8, g('Э'))
    e = bounds(g('е'))
    build(0x04D9, g('е'), transform=(-1, 0, 0, -1, e[0] + e[2], e[1] + e[3]))
    # Ғ ғ — Г with a crossbar
    G = bounds(g('Г'))
    build(0x0492, g('Г'), lambda p: rect(p, max(0, G[0] - 80), cap * .43, G[0] + tv + 260, cap * .43 + t))
    gl = bounds(g('г'))
    build(0x0493, g('г'), lambda p: rect(p, max(0, gl[0] - 70), xh * .42, gl[0] + tv + 210, xh * .42 + t))
    # Қ қ — К with a descender on the right leg
    K = bounds(g('К'))
    build(0x049A, g('К'), lambda p: rect(p, K[2] - tv, -165, K[2], 30))
    kl = bounds(g('к'))
    build(0x049B, g('к'), lambda p: rect(p, kl[2] - tv, -165, kl[2], 30))
    # Ң ң — Н with a descender on the right stem
    H = bounds(g('Н'))
    build(0x04A2, g('Н'), lambda p: rect(p, H[2] - tv, -165, H[2] + 45, t), add_width=45)
    hl = bounds(g('н'))
    build(0x04A3, g('н'), lambda p: rect(p, hl[2] - tv, -165, hl[2] + 40, t), add_width=40)
    # Ө ө — О with a horizontal bar
    O = bounds(g('О'))
    build(0x04E8, g('О'), lambda p: rect(p, O[0] + 20, (O[1] + O[3]) / 2 - t / 2, O[2] - 20, (O[1] + O[3]) / 2 + t / 2))
    ol = bounds(g('о'))
    build(0x04E9, g('о'), lambda p: rect(p, ol[0] + 15, (ol[1] + ol[3]) / 2 - t / 2, ol[2] - 15, (ol[1] + ol[3]) / 2 + t / 2))
    # Ү Ұ — Y, Y with a bar on the stem
    Y = bounds('Y')
    yc = (Y[0] + Y[2]) / 2
    build(0x04AE, 'Y')
    build(0x04B0, 'Y', lambda p: rect(p, yc - 170, cap * .26, yc + 170, cap * .26 + t))
    # ү ұ — v with a stem going down
    V = bounds('v')
    vc = (V[0] + V[2]) / 2
    build(0x04AF, 'v', lambda p: rect(p, vc - tv / 2, -200, vc + tv / 2, 70))
    build(0x04B1, 'v', lambda p: (rect(p, vc - tv / 2, -200, vc + tv / 2, 70),
                                  rect(p, vc - 150, -110, vc + 150, -110 + t)))
    # Һ һ — shaped like h
    build(0x04BA, 'h')
    build(0x04BB, 'h')
    f['maxp'].numGlyphs = len(f.getGlyphOrder())
    f.flavor = 'woff'
    f.save(path_out)


if __name__ == '__main__':
    for p in glob.glob(os.path.join(ROOT, 'src/fonts/*TRYGrtsk*.woff')):
        out = os.path.join(ROOT, 'docs/assets/fonts', os.path.basename(p))
        patch(p, out)
        print('patched', os.path.basename(p))
