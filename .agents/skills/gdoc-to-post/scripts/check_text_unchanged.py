#!/usr/bin/env python3
"""Verify that a converted post contains exactly the draft's words — no text was edited.

Usage:
    python check_text_unchanged.py DRAFT.docx POST.md

Compares words only, after removing everything the conversion legitimately adds or moves:
HTML tags and link URLs, Markdown markers, box brackets, footnote markers, the generated
Sections list, the title (moved to front matter) and the documented conversions
("Conclusion" -> "Key takeaways", "|||" -> "III"). Body text and references are compared in
order; footnote texts are compared as a set, because renumbering reorders them.

Exit code 0 = text unchanged, 1 = differences found (printed).
"""
import difflib
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def norm_words(s):
    s = s.replace('|||', 'III')
    s = re.sub(r'(?m)^\s*(?:[-•]|\d+\.)\s+', ' ', s)      # list markers (per line)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = re.sub(r'\(\s+', '(', s)
    s = re.sub(r'\[\^?f[a-z]*?note\s*\w+\]:?', ' ', s, flags=re.I)
    s = re.sub(r'\(Footnote \d+\s*\)', ' ', s)
    s = re.sub(r'[*\[\]#|_]', '', s)
    s = re.sub(r'\bConclusions?\b', 'Key takeaways', s)
    # Punctuation attached to a link anchor may end up after the closing tag: normalise spacing.
    s = re.sub(r'\s+([,.;:)])', r'\1', s)
    return s.split()


def docx_parts(path):
    d = ET.fromstring(zipfile.ZipFile(path).read('word/document.xml'))
    parts = {'body': [], 'references': [], 'footnotes': []}
    cur, title_seen = 'body', False
    for p in d.iter(W + 'p'):
        st = p.find(f'{W}pPr/{W}pStyle')
        style = (st.get(W + 'val') if st is not None else '').lower()
        text = ''.join(t.text or '' for t in p.iter(W + 't')).strip()
        if not text:
            continue
        if style.startswith('heading') or style == 'title':
            if not title_seen:
                title_seen = True          # title lives in the front matter
                continue
            key = re.sub(r'^[#\s]+', '', text).strip().lower()
            if key in ('references', 'footnotes'):
                cur = key
                continue
            cur = 'body'
        if cur == 'footnotes':
            m = re.match(r'^\[\^?f[a-z]*?note\s*\w+\]\s*:\s*(.*)$', text, re.I | re.S)
            if m:
                parts['footnotes'].append(m.group(1))
            elif parts['footnotes']:
                parts['footnotes'][-1] += ' ' + text
        else:
            parts[cur].append(text)
    return parts


def post_parts(path):
    s = open(path, encoding='utf-8').read()
    s = s.split('{% include toggle-details.html %}', 1)[-1]
    s = re.sub(r'<details closed>\s*<summary><u>Sections list</u></summary>.*?</details>', ' ', s, flags=re.S)
    s = re.sub(r'!\[[^\]]*\]\([^)]*\)\{:[^}]*\}', ' ', s)     # image lines (alt repeats caption)
    parts = {'body': [], 'references': [], 'footnotes': []}
    cur = 'body'
    for line in s.splitlines():
        h = re.match(r'^#{2,4}\s+(.*)$', line)
        if h and h.group(1).strip().lower() in ('references', 'footnotes'):
            cur = h.group(1).strip().lower()
            continue
        if h:
            cur = 'body'
        if cur == 'footnotes':
            m = re.match(r'^\[\^(?:footnote\d+|unreferenced_\w+)\]:\s*(.*)$', line)
            if m:
                parts['footnotes'].append(m.group(1))
        else:
            parts[cur].append(line)
    return parts


def diff(label, a, b):
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    out = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op != 'equal':
            out.append(f'  [{label}] {op}: "{" ".join(a[max(i1-5,0):i2+5])}"\n'
                       f'        -> "{" ".join(b[max(j1-5,0):j2+5])}"')
    return out


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    d, p = docx_parts(sys.argv[1]), post_parts(sys.argv[2])
    problems = []
    for part in ('body', 'references'):
        problems += diff(part, norm_words('\n'.join(d[part])), norm_words('\n'.join(p[part])))
    fd = sorted(' '.join(norm_words(x)) for x in d['footnotes'])
    fp = sorted(' '.join(norm_words(x)) for x in p['footnotes'])
    for x in fd:
        if x not in fp:
            problems.append(f'  [footnotes] draft footnote missing or changed in post: "{x[:120]}"')
    for x in fp:
        if x not in fd:
            problems.append(f'  [footnotes] post footnote not in draft: "{x[:120]}"')
    if problems:
        print('TEXT DIFFERS FROM THE DRAFT:')
        print('\n'.join(problems))
        print('\nEvery difference must be explained (e.g. a footnote dropped on the author\'s request);'
              ' otherwise restore the draft wording.')
        sys.exit(1)
    n = len(norm_words('\n'.join(d['body'])))
    print(f'OK: text unchanged ({n} body words, {len(d["references"])} references, '
          f'{len(d["footnotes"])} footnotes match the draft).')


if __name__ == '__main__':
    main()
