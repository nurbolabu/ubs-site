"""Tiny CSS parser for the flat CSS Tilda emits (rules + one level of @media)."""
import re

def split_top(s, sep):
    out, depth, quote, cur = [], 0, None, []
    for ch in s:
        if quote:
            cur.append(ch)
            if ch == quote: quote = None
            continue
        if ch in '"\'': quote = ch
        elif ch == '(': depth += 1
        elif ch == ')': depth -= 1
        if ch == sep and depth == 0:
            out.append(''.join(cur)); cur = []
        else:
            cur.append(ch)
    out.append(''.join(cur))
    return out

def parse(css):
    """Return list of (media, selector, [(prop, value), ...])."""
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    rules, i, n = [], 0, len(css)
    def block(text, media):
        for m in re.finditer(r'([^{}]+)\{([^{}]*)\}', text):
            sel = m.group(1).strip()
            decls = []
            for d in split_top(m.group(2), ';'):
                if ':' in d:
                    p, v = d.split(':', 1)
                    decls.append((p.strip(), v.strip()))
            rules.append((media, sel, decls))
    while i < n:
        j = css.find('@media', i)
        if j < 0:
            block(css[i:], None); break
        block(css[i:j], None)
        k = css.find('{', j)
        media = css[j + 6:k].strip()
        depth, p = 1, k + 1
        while depth and p < n:
            if css[p] == '{': depth += 1
            elif css[p] == '}': depth -= 1
            p += 1
        block(css[k + 1:p - 1], media)
        i = p
    return rules
