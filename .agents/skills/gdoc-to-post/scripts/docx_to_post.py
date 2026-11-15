#!/usr/bin/env python3
"""Convert a Google Docs .docx blog draft into a Jekyll (Chirpy) post for Hrovatin.github.io.

Usage:
    python docx_to_post.py DRAFT.docx --out OUT_DIR [--date YYYY-MM-DD] [--slug name]

Writes:
    OUT_DIR/_posts/<date|TODO_YYYY-MM-DD>-<slug>.md
    OUT_DIR/assets/img/<date|TODO_YYYY-MM-DD>-<slug>/<figure>.jpg
    OUT_DIR/conversion_report.md   (TODOs, ignored comments, warnings)

The conversion rules are documented in ../SKILL.md. The draft's literal Markdown markers
(**bold**, *italic*, [^footnoteN]) are the source of truth; Word run formatting is ignored.
Links come from comments whose first line is a URL, and from real hyperlinks.
"""
import argparse
import io
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
PR = '{http://schemas.openxmlformats.org/package/2006/relationships}'

# Private-use sentinels that survive text processing until final rendering.
L_OPEN, L_MID, L_CLOSE = '\ue000', '\ue001', '\ue002'      # L_OPEN url L_MID text L_CLOSE
F_OPEN, F_CLOSE = '\ue003', '\ue004'                       # in-text figure reference
FN_MD, FN_HTML, FN_END = '\ue005', '\ue006', '\ue007'      # footnote reference tokens

BOX_STYLE_INTRO = 'border:1px solid #535353;border-radius: 7px;padding: 10px;margin: 15px 0px 15px 0px;'
BOX_STYLE = 'border:1px solid #535353;border-radius: 7px;padding: 10px;margin: 5px;'
END_SECTIONS = {'key takeaways', 'references', 'footnotes'}

FN_REF_RE = re.compile(r'\[\^?f[a-z]*?note\s*(\w+)\]', re.I)
FN_DEF_RE = re.compile(r'^\[\^?f[a-z]*?note\s*(\w+)\]\s*:\s*(.*)$', re.I | re.S)
URL_RE = re.compile(r'^\s*(https?://\S+)')

warnings = []


def warn(msg):
    warnings.append(msg)


# --------------------------------------------------------------------------- parsing

def load_xml(z, name):
    try:
        return ET.fromstring(z.read(name))
    except KeyError:
        return None


def load_comments(z):
    root = load_xml(z, 'word/comments.xml')
    comments = {}
    if root is None:
        return comments
    for c in root.iter(W + 'comment'):
        paras = [''.join(t.text or '' for t in p.iter(W + 't')).strip() for p in c.iter(W + 'p')]
        paras = [p for p in paras if p]
        first = paras[0] if paras else ''
        m = URL_RE.match(first)
        comments[c.get(W + 'id')] = {
            'author': c.get(W + 'author', ''),
            'lines': paras,
            'url': m.group(1) if m else None,
            'anchor': [],
            'paras': set(),
        }
    return comments


def load_rels(z):
    root = load_xml(z, 'word/_rels/document.xml.rels')
    rels = {}
    if root is not None:
        for r in root.iter(PR + 'Relationship'):
            rels[r.get('Id')] = (r.get('Target'), r.get('TargetMode'))
    return rels


def load_numbering(z):
    """Map numId -> {ilvl: numFmt} so ordered and bullet lists can be told apart."""
    root = load_xml(z, 'word/numbering.xml')
    fmt = {}
    if root is None:
        return fmt
    abstract = {}
    for an in root.iter(W + 'abstractNum'):
        lv = {}
        for l in an.iter(W + 'lvl'):
            nf = l.find(W + 'numFmt')
            lv[l.get(W + 'ilvl')] = nf.get(W + 'val') if nf is not None else 'bullet'
        abstract[an.get(W + 'abstractNumId')] = lv
    for n in root.iter(W + 'num'):
        a = n.find(W + 'abstractNumId')
        if a is not None:
            fmt[n.get(W + 'numId')] = abstract.get(a.get(W + 'val'), {})
    return fmt


def load_style_lists(z):
    """Map paragraph style id -> (numId, ilvl) for list styles defined in styles.xml."""
    root = load_xml(z, 'word/styles.xml')
    out = {}
    if root is None:
        return out
    for st in root.iter(W + 'style'):
        npr = st.find(f'{W}pPr/{W}numPr')
        if npr is None:
            continue
        ni, il = npr.find(W + 'numId'), npr.find(W + 'ilvl')
        sid = st.get(W + 'styleId')
        lvl = int(il.get(W + 'val')) if il is not None else (int(sid[-1]) - 1 if sid[-1].isdigit() else 0)
        out[sid] = (ni.get(W + 'val') if ni is not None else None, lvl)
    return out


def parse_docx(path):
    z = zipfile.ZipFile(path)
    comments = load_comments(z)
    rels = load_rels(z)
    numbering = load_numbering(z)
    style_lists = load_style_lists(z)
    doc = load_xml(z, 'word/document.xml')
    body = doc.find(W + 'body')
    if body.find('.//' + W + 'tbl') is not None:
        warn('The draft contains a table. Tables are not converted; add them by hand (Markdown table or HTML).')

    open_links = set()      # URL comment ids whose range is open
    active = set()          # all comment ids whose range is open (for anchor-text capture)
    blocks = []

    for pi, p in enumerate(body.iter(W + 'p')):
        ppr = p.find(W + 'pPr')
        style = ''
        list_level, ordered = None, False
        if ppr is not None:
            st = ppr.find(W + 'pStyle')
            style = st.get(W + 'val') if st is not None else ''
            npr = ppr.find(W + 'numPr')
            if npr is None and style in style_lists:   # list defined by the paragraph style
                nid, list_level = style_lists[style]
                ordered = numbering.get(nid, {}).get(str(list_level), 'bullet') not in ('bullet', 'none')
            if npr is not None:
                il = npr.find(W + 'ilvl')
                ni = npr.find(W + 'numId')
                list_level = int(il.get(W + 'val')) if il is not None else 0
                nid = ni.get(W + 'val') if ni is not None else None
                if nid == '0':
                    list_level = None
                else:
                    ordered = numbering.get(nid, {}).get(str(list_level), 'bullet') not in ('bullet', 'none')
        out = []
        block = {'style': style, 'list_level': list_level, 'ordered': ordered,
                 'images': [], 'caption_anchor': None, 'index': pi}
        # Links that continue from the previous paragraph are reopened here.
        for cid in sorted(open_links):
            out.append(L_OPEN + comments[cid]['url'] + L_MID)

        def emit(text):
            out.append(text)
            for cid in active:
                comments[cid]['anchor'].append(text)
                comments[cid]['paras'].add(pi)

        def walk(el):
            for ch in el:
                tag = ch.tag
                if tag == W + 'pPr' or tag == W + 'del':
                    continue
                if tag == W + 'commentRangeStart':
                    cid = ch.get(W + 'id')
                    if cid in comments:
                        active.add(cid)
                        comments[cid]['paras'].add(pi)
                        if comments[cid]['url']:
                            open_links.add(cid)
                            out.append(L_OPEN + comments[cid]['url'] + L_MID)
                elif tag == W + 'commentRangeEnd':
                    cid = ch.get(W + 'id')
                    active.discard(cid)
                    if cid in open_links:
                        open_links.discard(cid)
                        out.append(L_CLOSE)
                elif tag == W + 'hyperlink':
                    anchor = ch.get(W + 'anchor')
                    rid = ch.get(R + 'id')
                    if rid and rid in rels and rels[rid][1] == 'External':
                        out.append(L_OPEN + rels[rid][0] + L_MID)
                        walk(ch)
                        out.append(L_CLOSE)
                    elif anchor and re.match(r'figur_', anchor, re.I):
                        block['caption_anchor'] = anchor
                        walk(ch)
                    elif anchor and re.match(r'fig_', anchor, re.I):
                        out.append(F_OPEN)
                        walk(ch)
                        out.append(F_CLOSE)
                    else:
                        walk(ch)
                elif tag == W + 'r':
                    for sub in ch:
                        if sub.tag == W + 't':
                            emit(sub.text or '')
                        elif sub.tag in (W + 'tab', W + 'br', W + 'cr'):
                            emit(' ')
                        elif sub.tag in (W + 'drawing', W + 'pict', W + 'object'):
                            for blip in sub.iter(A + 'blip'):
                                rid = blip.get(R + 'embed')
                                if rid in rels:
                                    block['images'].append(rels[rid][0])
                elif tag in (W + 'instrText', W + 'fldChar'):
                    continue
                else:
                    walk(ch)

        walk(p)
        for cid in sorted(open_links):   # close links spanning the paragraph break
            out.append(L_CLOSE)
            warn(f'Comment {cid} (link) spans several paragraphs; the link was split per paragraph. Check it.')
        text = ''.join(out)
        text = re.sub(r'[ \t]+$', '', text.replace('\u00a0', ' ').replace('\u200b', ''))
        block['text'] = text
        blocks.append(block)
    media = {name: z.read(name) for name in z.namelist() if name.startswith('word/media/')}
    return blocks, comments, media


# --------------------------------------------------------------------------- inline rendering

def plain(text):
    """Text with all sentinels and markup removed (for alt text, summaries, comparisons)."""
    text = re.sub(L_OPEN + r'[^' + L_MID + r']*' + L_MID, '', text)
    text = re.sub('[' + L_CLOSE + F_OPEN + F_CLOSE + ']', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    return re.sub(r'\*+', '', text).strip()


def bold_figure_refs(text, html):
    b0, b1 = ('<b>', '</b>') if html else ('**', '**')
    had_links = F_OPEN in text

    def rep(m):
        label = re.sub(r'\*', '', m.group(1)).strip()
        panels = re.sub(r'\*', '', m.group(2) or '')
        return b0 + label + panels + b1
    # Linked reference, optional literal ** around it, optional panel letters right after
    # ("Figure 3" + "a" -> "Figure 3a"; "Figure 2" + "b, c" -> "Figure 2b, c").
    text = re.sub(r'\*{0,2}' + F_OPEN + r'(.*?)' + F_CLOSE + r'\*{0,2}'
                  r'((?:\*\*)?[a-zA-Z](?:\*\*)?(?:\s*[,\-–]\s*(?:\*\*)?[a-zA-Z](?:\*\*)?)*(?![A-Za-z]))?',
                  rep, text)
    # Fallback for figure references that were typed without an internal link.
    if not had_links:
        text = re.sub(r'(?<![\w<>*])\**(Figure \d+)\**([a-z](?:,\s?[a-z])*)?(?![\w*])(?! of\b)',
                      lambda m: b0 + m.group(1) + (m.group(2) or '') + b1, text)
    return text


def md_to_html(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<i>\1</i>', text)
    text = re.sub(r'\[([^\]^][^\]]*)\]\((https?://[^)\s]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
    return text


def inline(text, html=False, caption=False):
    text = text.replace('|||', 'III')
    tok = FN_HTML if html else FN_MD
    text = FN_REF_RE.sub(lambda m: tok + m.group(1) + FN_END, text)
    if not caption:
        text = bold_figure_refs(text, html)
    else:
        text = re.sub('[' + F_OPEN + F_CLOSE + ']', '', text)
    if html:
        text = md_to_html(text)
    return text


def finalize_links(text):
    return re.sub(L_OPEN + r'([^' + L_MID + r']*)' + L_MID + r'(.*?)' + L_CLOSE,
                  r'<a href="\1" target="_blank">\2</a>', text, flags=re.S)


# --------------------------------------------------------------------------- structure

def heading_level(block, title_done):
    style = block['style'].lower().replace(' ', '')
    m = re.match(r'heading(\d)', style)
    if style == 'title':
        return 1
    if m:
        lvl = int(m.group(1))
        return 1 if not title_done and lvl == 1 else lvl + 1
    m = re.match(r'^(#{1,4}) ', plain(block['text']))   # literal Markdown heading typed as text
    if m and block['list_level'] is None:
        return len(m.group(1))
    return 0


def clean_heading(text):
    text = plain(text)
    text = re.sub(r'^[#\\\s]+', '', text).strip()
    if re.fullmatch(r'conclusions?', text, re.I):
        text = 'Key takeaways'
    return text


def caption_parts(text):
    """Split a caption into (number, title, rest) following the published caption style."""
    t = re.sub('[' + F_OPEN + F_CLOSE + ']', '', text).strip()
    m = re.match(r'^\**\s*Figure\s+(\d+)\s*[:.]?\s*\**\s*:?\s*', t)
    num = m.group(1)
    rest = t[m.end():]
    m2 = re.match(r'^\*\*(.+?)\*\*\s*(.*)$', rest, re.S)
    if m2:
        title, rest = m2.group(1).strip(), m2.group(2)
    else:
        # First sentence: ends at '.' followed by space + capital/'(' or end; skip e.g./i.e./vs.
        m3 = re.match(r'^(.*?(?<!\be\.g)(?<!\bi\.e)(?<!\bvs)\.)(\s+(?=[A-Z(])|\s*$)(.*)$', rest, re.S)
        if m3:
            title, rest = m3.group(1).strip(), m3.group(3)
        else:
            title, rest = rest.strip(), ''
    return num, title, rest.strip()


def render_caption(text):
    num, title, rest = caption_parts(text)
    title_h = inline(title, html=True, caption=True)
    rest_h = inline(rest, html=True, caption=True)
    rest_h = re.sub(r'\((?:<b>)?([a-z])(?:</b>)?\)', r'(<b>\1</b>)', rest_h)
    title_h = re.sub(r'\((?:<b>)?([a-z])(?:</b>)?\)', r'</b>(<b>\1</b>)<b>', title_h)
    cap = f'_<b>Figure {num}: {title_h}</b>' + (f' {rest_h}' if rest_h else '') + '_'
    alt = plain(finalize_links(title)).rstrip('.').replace('"', '&quot;')
    return num, cap, alt


def image_name(caption_block, num, used):
    name = None
    if caption_block and caption_block.get('caption_anchor'):
        name = re.sub(r'^figu?r?_', '', caption_block['caption_anchor'], flags=re.I)
        name = re.sub(r'\.(png|jpe?g|gif|svg|webp)$', '', name, flags=re.I)
    if not name:
        name = f'figure{num}' if num else f'figure{len(used) + 1}'
        warn(f'Figure {num or "?"} has no caption anchor (#figur_<name>); saved as "{name}.jpg". Rename if needed.')
    base, k = name, 2
    while name in used:
        name = f'{base}_{k}'
        k += 1
    used.add(name)
    return name


def save_image(data, path):
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(data))
        if im.mode in ('RGBA', 'LA', 'P'):
            im = im.convert('RGBA')
            bg = Image.new('RGB', im.size, (255, 255, 255))
            bg.paste(im, mask=im.split()[-1])
            im = bg
        else:
            im = im.convert('RGB')
        im.save(path, 'JPEG', quality=92)
    except Exception as e:  # keep the original bytes if conversion fails
        warn(f'Could not convert {os.path.basename(path)} to JPG ({e}); saved original bytes.')
        with open(path, 'wb') as f:
            f.write(data)


def is_box_open(b):
    return not b['images'] and plain(b['text']) in ('[', '|')


def is_box_close(b):
    return not b['images'] and plain(b['text']) == ']'


def is_caption(b):
    return bool(re.match(r'^\**\s*Figure\s+\d+\s*[:.]', plain(b['text'])))


def render_list(items, html):
    """items: list of (level, ordered, text). Markdown list or nested HTML list."""
    lines = []
    if not html:
        counters = {}
        for lvl, ordered, text in items:
            counters[lvl] = counters.get(lvl, 0) + 1
            for deeper in [k for k in counters if k > lvl]:
                del counters[deeper]
            marker = f'{counters[lvl]}.' if ordered else '-'
            lines.append('  ' * lvl + f'{marker} {text}')
        return lines
    stack = []
    for lvl, ordered, text in items:
        tag = 'ol' if ordered else 'ul'
        while len(stack) > lvl + 1:
            lines.append(f'</{stack.pop()}>')
        while len(stack) < lvl + 1:
            stack.append(tag)
            lines.append(f'<{tag}>')
        lines.append(f'<li>{text}</li>')
    while stack:
        lines.append(f'</{stack.pop()}>')
    return lines


def render_paragraphs(blocks, html, intro_box=False):
    """Render a run of non-heading blocks (paragraphs and lists) as Markdown or HTML lines."""
    out, i = [], 0
    while i < len(blocks):
        b = blocks[i]
        if b['list_level'] is not None:
            items = []
            while i < len(blocks) and blocks[i]['list_level'] is not None:
                items.append((blocks[i]['list_level'], blocks[i]['ordered'],
                              inline(re.sub(r'^\s*[-*•]\s+', '', blocks[i]['text']), html=html)))
                i += 1
            out += render_list(items, html) + ['']
            continue
        if b['images']:
            warn('An image sits inside a text box; images are not supported in boxes. It was skipped. Move it out of the box.')
            i += 1
            continue
        text = inline(b['text'], html=html)
        if html:
            out += (['<p>', text, '</p>', ''] if intro_box else [f'<p>{text}</p>', ''])
        else:
            out += [text, '']
        i += 1
    return out


def convert(path, date=None, slug=None):
    blocks, comments, media = parse_docx(path)
    blocks = [b for b in blocks if plain(b['text']) or b['images']]
    slug = slug or re.sub(r'[^a-z0-9_]+', '_', os.path.splitext(os.path.basename(path))[0].lower()).strip('_')
    prefix = date or 'TODO_YYYY-MM-DD'

    # Title and description.
    title_i = next((i for i, b in enumerate(blocks) if heading_level(b, False) == 1), None)
    if title_i is None:
        warn('No title heading found (first Heading 1). Title set to TODO_title.')
        title, title_block = 'TODO_title', None
    else:
        title_block = blocks.pop(title_i)
        title = clean_heading(title_block['text'])
    description = None
    ignored = []
    for cid, c in comments.items():
        anchor = ''.join(c['anchor']).strip()
        if c['url']:
            continue
        if title_block is not None and title_block['index'] in c['paras'] and c['lines']:
            description = c['lines'][0]
            continue
        ignored.append((cid, c['author'], anchor, ' / '.join(c['lines'])))

    # Section scan: split into body and end sections.
    sections = []           # (level, text, start_index)
    body_out = []
    end = {'references': [], 'footnotes': []}
    current_end = None
    seen_section = False
    first_box_done = False
    box_open = None
    used_names = set()
    images_out = []
    toc = []
    pending_title = None

    i = 0
    stream = []   # list of ('md', lines) chunks in order
    while i < len(blocks):
        b = blocks[i]
        lvl = 0 if b['list_level'] is not None else heading_level(b, True)
        if lvl >= 2:
            htext = clean_heading(b['text'])
            key = htext.lower()
            if key in ('references', 'footnotes'):
                current_end = key
                i += 1
                continue
            current_end = None
            seen_section = True
            stream.append(('heading', lvl, htext))
            if key not in END_SECTIONS:
                toc.append((lvl, htext))
            i += 1
            continue
        if current_end:
            end[current_end].append(b)
            i += 1
            continue
        if is_box_open(b):
            # Title is the preceding paragraph.
            title_b = None
            if stream and stream[-1][0] == 'para':
                title_b = stream.pop()[1]
            j = i + 1
            content = []
            while j < len(blocks) and not is_box_close(blocks[j]):
                content.append(blocks[j])
                j += 1
            if j >= len(blocks):
                warn(f'Text box starting near "{plain(title_b["text"])[:50] if title_b else "?"}" has no closing "]".')
            box_title = inline(title_b['text'], html=True) if title_b else 'TODO_box_title'
            intro = not seen_section and not first_box_done
            first_box_done = True
            stream.append(('box', intro, box_title, content))
            i = j + 1
            continue
        if is_box_close(b):
            warn('Found a closing "]" without an opening "[" — ignored.')
            i += 1
            continue
        if b['images']:
            cap_b = blocks[i + 1] if i + 1 < len(blocks) and is_caption(blocks[i + 1]) else None
            for k, img in enumerate(b['images']):
                if cap_b and k == 0:
                    num, cap, alt = render_caption(cap_b['text'])
                else:
                    num, cap, alt = None, '_<b>TODO_caption</b>_', 'TODO_alt'
                    warn('An image has no "Figure N: ..." caption directly below it.')
                name = image_name(cap_b if k == 0 else None, num, used_names)
                data = media.get('word/' + img) or media.get(img.lstrip('/'))
                images_out.append((name, data))
                stream.append(('figure', name, alt, cap))
            i += 2 if cap_b else 1
            continue
        if is_caption(b):
            warn(f'Caption "{plain(b["text"])[:40]}" has no image above it; rendered as a normal paragraph.')
        stream.append(('para', b))
        i += 1

    # ---------------- emit markdown
    lines = []
    first_heading_emitted = False
    para_run = []

    def flush():
        nonlocal para_run
        if para_run:
            run = render_paragraphs(para_run, html=False)
            if not first_heading_emitted:   # intro: put each linked name on its own line
                run = [re.sub(r' ?' + L_OPEN, ' \n' + L_OPEN, l) if l.count(L_OPEN) >= 2 else l
                       for l in run]
            lines.extend(run)
            para_run = []

    for item in stream:
        kind = item[0]
        if kind == 'para':
            para_run.append(item[1])
            continue
        flush()
        if kind == 'heading':
            if not first_heading_emitted and toc:   # every post gets a Sections list
                lines += sections_list_lines(toc)
            first_heading_emitted = True
            lines += ['#' * item[1] + ' ' + item[2], '']
        elif kind == 'box':
            _, intro, btitle, content = item
            if intro:
                lines += [f'<div style="{BOX_STYLE_INTRO}">', '<p>', f'<b>{btitle}</b>', '</p>', '']
                lines += render_paragraphs(content, html=True, intro_box=True)
                lines += ['</div>', '']
            else:
                lines += ['<details closed>', f'<summary><u>{btitle}</u></summary>',
                          f'<div style="{BOX_STYLE}">', '']
                lines += render_paragraphs(content, html=True)
                lines += ['</div>', '</details>', '<p></p>', '']
        elif kind == 'figure':
            _, name, alt, cap = item
            lines += [f'![Desktop View]({name}.jpg){{: width="TODO_700" alt="{alt}" .shadow style="border-radius: 7px;"}}',
                      cap, '']
    flush()
    if not toc:
        warn('No section headings found, so no Sections list was added. Every post should have one: check the heading styles.')

    # References
    if end['references']:
        lines += ['## References', '']
        for b in end['references']:
            lines.append('- ' + inline(re.sub(r'^\s*[-*•]\s+', '', b['text'])))
        lines.append('')
    else:
        warn('No "References" section found.')

    # Footnote definitions
    defs, order_defs, last = {}, [], None
    for b in end['footnotes']:
        m = FN_DEF_RE.match(b['text'].strip())
        if m:
            last = m.group(1)
            defs[last] = m.group(2).strip()
            order_defs.append(last)
        elif last:
            defs[last] += ' ' + b['text'].strip()
            warn(f'Footnote {last} spans several paragraphs; they were joined into one line.')
        else:
            warn(f'Text in Footnotes section is not a footnote definition: "{plain(b["text"])[:60]}"')

    body = '\n'.join(lines)
    # Number footnotes by first appearance anywhere in the body (boxes and captions included).
    order = []
    for m in re.finditer('[' + FN_MD + FN_HTML + r'](\w+)' + FN_END, body):
        if m.group(1) not in order:
            order.append(m.group(1))
    new = {old: str(k + 1) for k, old in enumerate(order)}
    md_refs = set(re.findall(FN_MD + r'(\w+)' + FN_END, body))
    for old in order:
        if old not in defs:
            warn(f'Footnote reference "{old}" has no definition in the Footnotes section.')
        if old not in md_refs:
            warn(f'Footnote {new[old]} (draft "{old}") is referenced only inside text boxes. Kramdown does not '
                 f'render footnotes referenced only from HTML, so its text will not appear. Add a reference '
                 f'in normal text, or move the footnote text into the box.')
    unreferenced = [old for old in order_defs if old not in new]
    for old in unreferenced:
        warn(f'Footnote definition "{old}" is never referenced in the text. Its text was kept '
             f'(as [^unreferenced_{old}] at the end of the Footnotes) but will not appear on the site. '
             f'Ask the author whether to add a reference or delete it.')
    body = re.sub(FN_MD + r'(\w+)' + FN_END, lambda m: f'[^footnote{new[m.group(1)]}]', body)
    body = re.sub(FN_HTML + r'(\w+)' + FN_END, lambda m: f' (<b>Footnote {new[m.group(1)]}</b>)', body)
    body = re.sub(r'\s+\(<b>Footnote', ' (<b>Footnote', body)

    fn_lines = []
    for old in order:
        if old in defs:
            fn_lines.append(f'[^footnote{new[old]}]: ' + inline(defs[old]))
    for old in unreferenced:
        fn_lines.append(f'[^unreferenced_{old}]: ' + inline(defs[old]))
    if fn_lines:
        body += '\n## Footnotes\n\n' + '\n'.join(fn_lines) + '\n'
        # footnote definitions may themselves contain links, figure refs handled by inline()
    body = finalize_links(body)
    body = re.sub('[' + F_OPEN + F_CLOSE + FN_MD + FN_HTML + FN_END + ']', '', body)
    body = re.sub(r'\n{3,}', '\n\n', body)

    math = bool(re.search(r'\$\$|(?<![\\$])\$[^\s$][^$\n]*?[^\s\\]\$', body))
    if math:
        warn('LaTeX detected, so "math: true" was added. Check that "$" signs are math and not currency.')

    fm = ['---',
          f'title: "{title}"',
          f'date: {prefix} 00:01:00',
          f'last_modified_at: {prefix} 00:01:00',
          'categories: [TODO_category]',
          'tags: [TODO_tag1, TODO_tag2, TODO_tag3]  # TAG names should always be lowercase',
          f'description: {description}' if description else 'description: TODO_description',
          f'media_subpath: /assets/img/{prefix}-{slug}/',
          'image:',
          '  path: TODO_cover.jpg',
          '  alt: "<b>TODO_cover_caption</b><br><i>This image is AI generated.</i>"']
    if math:
        fm.append('math: true')
    fm += ['---', '', '{% include toggle-details.html %}', '']
    post = '\n'.join(fm) + '\n' + body.strip() + '\n'
    if not description:
        warn('No comment on the title, so description is TODO_description.')
    elif re.search(r':\s|\s#', description) or re.match(r'''^[\[\]{}>|*&!%@`'"#,?-]''', description):
        warn('The description is unquoted (site convention) but contains characters that YAML may '
             'misread (": ", " #", or a leading special character). Rephrase it, or quote it '
             'in this one post.')
    return post, images_out, prefix, slug, ignored, comments


def sections_list_lines(toc):
    out = ['<details closed>', '<summary><u>Sections list</u></summary>',
           f'<div style="{BOX_STYLE}">', '<ul>', '']
    i = 0
    while i < len(toc):
        lvl, text = toc[i]
        if lvl == 2:
            out.append(f'<li>{text}</li>')
            subs = []
            j = i + 1
            while j < len(toc) and toc[j][0] > 2:
                if toc[j][0] == 3:
                    subs.append(f'<li>{toc[j][1]}</li>')
                j += 1
            if subs:
                out += ['<ul>'] + subs + ['</ul>']
            out.append('')
            i = j
        else:
            i += 1
    out += ['</ul>', '</div>', '</details>', '']
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('docx')
    ap.add_argument('--out', required=True)
    ap.add_argument('--date', help='Publication date YYYY-MM-DD (otherwise TODO_YYYY-MM-DD)')
    ap.add_argument('--slug', help='Post slug (default: docx file name)')
    args = ap.parse_args()
    if args.date and not re.fullmatch(r'\d{4}-\d{2}-\d{2}', args.date):
        sys.exit('--date must be YYYY-MM-DD')

    post, images, prefix, slug, ignored, comments = convert(
        args.docx, args.date, args.slug)
    post_dir = os.path.join(args.out, '_posts')
    img_dir = os.path.join(args.out, 'assets', 'img', f'{prefix}-{slug}')
    os.makedirs(post_dir, exist_ok=True)
    post_path = os.path.join(post_dir, f'{prefix}-{slug}.md')
    with open(post_path, 'w', encoding='utf-8') as f:
        f.write(post)
    if images:
        os.makedirs(img_dir, exist_ok=True)
        for name, data in images:
            if data is None:
                warn(f'Image data for "{name}" not found in the docx.')
                continue
            save_image(data, os.path.join(img_dir, name + '.jpg'))

    todos = [(n + 1, l.strip()) for n, l in enumerate(post.splitlines()) if 'TODO' in l]
    rep = ['# Conversion report', '', f'Post: `{post_path}`',
           f'Images ({len(images)}): `{img_dir}`' if images else 'Images: none', '',
           '## TODO placeholders', '']
    rep += [f'- line {n}: `{l[:140]}`' for n, l in todos] or ['- none']
    rep += ['', '## Link comments applied', '']
    links = [(cid, ''.join(c['anchor']).strip(), c['url']) for cid, c in comments.items() if c['url']]
    rep += [f'- "{a}" → {u}' for _, a, u in links] or ['- none']
    rep += ['', '## Comments ignored (not URLs, not on the title)', '']
    rep += [f'- [{cid}] {au} on "{an}": {tx}' for cid, au, an, tx in ignored] or ['- none']
    rep += ['', '## Warnings', '']
    rep += [f'- {w}' for w in dict.fromkeys(warnings)] or ['- none']
    rep_path = os.path.join(args.out, 'conversion_report.md')
    with open(rep_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(rep) + '\n')
    print(f'Wrote {post_path}')
    print(f'Wrote {rep_path} ({len(todos)} TODO lines, {len(dict.fromkeys(warnings))} warnings)')


if __name__ == '__main__':
    main()
