---
name: gdoc-to-post
description: Convert a Google Docs blog draft (downloaded as .docx) into a publish-ready Jekyll/Chirpy post for the Hrovatin.github.io website — front matter with TODO placeholders, collapsible text boxes, figures with captions, links taken from Google Docs comments, renumbered footnotes, references, and extracted images. Use this skill whenever the user uploads a .docx blog draft, mentions converting a Google Doc / gdoc / draft into a blog post, asks to prepare a post for Hrovatin.github.io or its _posts folder, or wants the "website md" for an interview-style blog post — even if they don't say "convert".
---

# Google Docs draft → Hrovatin.github.io post

The website (Jekyll, Chirpy theme) keeps posts in `_posts/YYYY-MM-DD-<slug>.md` and their
images in `assets/img/YYYY-MM-DD-<slug>/`. Drafts are written in Google Docs using a few plain-text
conventions (described below) and exported as `.docx`. This skill turns that export into the
published format.

The `.docx` is the right input because it is the only export that keeps **comments**, and comments
are where the author puts link URLs and the post description. The Google Docs Markdown export drops
comments, so links would be lost. If the user only has a Google Docs link, the agent usually cannot
open it; ask them to use *File → Download → Microsoft Word (.docx)* and upload the file.

## Never edit the text

**The post must contain exactly the author's words.** Never reword, shorten, correct typos,
fix grammar, change spelling (British/American), reorder sentences or paragraphs, move text into
or out of boxes, merge or split paragraphs, or delete anything — not even an obvious typo or a
duplicated word, and not even when it would clearly improve the post. The author proofreads in
Google Docs; the conversion only changes *format*.

What the conversion may change is limited to what the rules below define: Markdown/HTML markup,
links from comments, heading levels, the title moving into the front matter, footnote numbers,
the order of the end sections (References before Footnotes), the generated Sections list, and
the TODO placeholders.

If you notice a typo or a possible improvement, **list it in your summary for the author** and
leave the text as it is. Change wording only when the user explicitly asks for that specific
change (e.g. "put the M. inside the link"), and change only what they asked for.

Step 3 of the workflow checks this mechanically; never skip it.

## Workflow

1. **Run the converter.**
   ```bash
   python <skill-dir>/scripts/docx_to_post.py DRAFT.docx --out OUT_DIR \
       [--date YYYY-MM-DD] [--slug name]
   ```
   - `--date`: only if the user gave a publication date. Without it, every date becomes
     `TODO_YYYY-MM-DD`, so one find-and-replace fills them all.
   - `--slug`: defaults to the docx file name (lowercased, non-alphanumerics → `_`). Ask or
     choose a short, lowercase, underscore-separated slug if the file name is generic
     (e.g. `Draft (3).docx`).

   It writes `_posts/<prefix>-<slug>.md`, `assets/img/<prefix>-<slug>/*.jpg` and
   `conversion_report.md` (TODO lines, applied links, ignored comments, warnings).

2. **Read `conversion_report.md` and the post**, then do the review pass below. The script is
   deterministic; the review pass is where judgment is needed.

3. **Verify the text is unchanged** — after the review pass and after any later fix to the post:
   ```bash
   python <skill-dir>/scripts/check_text_unchanged.py DRAFT.docx <post>.md
   ```
   It compares every word of the draft with the post, ignoring markup and the documented format
   changes. It must print `OK: text unchanged`. If it reports a difference you introduced,
   restore the draft wording. The only acceptable differences are ones the user explicitly asked
   for; mention those in the summary.

4. **Deliver**, then give the user a short summary: what was filled automatically, the
   remaining TODOs, and any warnings that need their decision. Don't paste the whole post into
   the chat.
   - **Inside the website repo** (a coding agent working in the repo; this skill lives in
     `<repo>/.agents/skills/gdoc-to-post/`, a dot-folder that Jekyll never builds): use `--out <repo root>` so the post lands in
     `_posts/` and the images in `assets/img/<prefix>-<slug>/`. Write `conversion_report.md`
     outside the repo (pass `--out` a temp dir and move the post/images in, or delete the report
     afterwards) so it isn't committed or built. Don't commit or push — the author reviews first.
   - **Elsewhere** (e.g. a chat interface without repo access): copy the post and image folder to the outputs directory,
     keeping the `_posts/` and `assets/img/...` structure so it can be dropped into the repo,
     and present the `.md` file.

If the script fails or the draft does something it doesn't handle, fall back to applying the
rules in "Conversion rules" by hand — they describe exactly what the script does.

## Review pass (after the script)

Work through these; fix what is unambiguous, and list everything else for the user.

- **Warnings in the report.** Each one names a concrete decision. The most important:
  - *Footnote referenced only inside text boxes.* Kramdown doesn't render footnotes whose only
    reference is inside raw HTML, so the footnote text silently disappears from the site. In past
    posts the author either dropped such footnotes or moved the text into the box. Ask; don't decide.
  - *Footnote definition never referenced* — its text is kept as `[^unreferenced_N]` at the end
    of the Footnotes (it won't render). Ask whether a reference is missing or it should go.
  - *Image without caption / caption without image / box without closing `]`* — fix the structure.
- **Unlinked people and tools.** Interviewee names in the intro are always linked on the site.
  If a name in the intro has no link (no URL comment), wrap it as
  `<a href="TODO_url" target="_blank">Name</a>` so it shows up in the TODO grep. Also mention
  tools/datasets/portals named in the text that look like they deserve a link (e.g. a benchmark
  portal or software package), but leave adding them to the user.
- **Partial link anchors.** A link covers exactly the commented text. If a comment covers only
  part of a name (e.g. "M. Frank Erasmus" with only "Frank Erasmus" commented), point it out.
- **Image file names** come from the caption anchor and can carry the author's typos
  (`#figur_mesh_pacing` → `mesh_pacing.jpg`). If a name looks misspelled, mention it — renaming
  must change both the file and the `![...](name.jpg)` line.
- **Ignored comments** are editor notes or replies (e.g. "works for me"). Skim them: if one is
  actually an instruction for the post ("move this into a box", "cut this paragraph"), tell the user.
- **Never edit the text** (see "Never edit the text" above). Some published posts contain
  copyedits, reordered sections or paragraphs moved into boxes — those were the author's own
  later edits, not part of the conversion. Typos you notice go into the summary, not the post.

## Draft conventions (what the author types in Google Docs)

These are the inputs the converter recognises. Share this table with the user if they ask how to
write a draft, or if the draft deviates from it.

| In the Google Doc | Becomes on the site |
|---|---|
| First **Heading 1** | `title:` in front matter (removed from the body) |
| Comment on the title (any word of it), not a URL | `description:` in front matter |
| Later **Heading 1** / **Heading 2** / **Heading 3** (optionally with literal `##`, `###` in the text) | `##` / `###` / `####` |
| Heading "Conclusion" | `## Key takeaways` |
| Comment whose first line is a URL, on some text | `<a href="URL" target="_blank">text</a>` |
| A real Word/Docs hyperlink | same `<a href=... target="_blank">` link |
| Title line, then a line `[`, content, a line `]` (opener may be typed `\|`) | text box (first one before any section = always-visible box; others = collapsible) |
| Image, then a caption paragraph `Figure N: Title. Rest…` whose "Figure N:" links to bookmark `#figur_<name>` | `<name>.jpg` + styled caption |
| "Figure N" linked to bookmark `#fig_<name>`, optional panel letter right after | **Figure Na** (bold) |
| `[^footnoteN]` in text; `[^footnoteN]: text` lines under heading "Footnotes" | renumbered Markdown footnotes |
| Paragraphs under heading "References" | `- ` reference list |
| `**bold**`, `*italic*` typed literally | kept as Markdown (converted to `<b>`/`<i>` inside boxes) |
| Docs bullet/numbered lists | `- ` / `1.` lists (`<ul>`/`<ol>` inside boxes) |

Word run formatting (bold/italic set with the toolbar) is **ignored**: the author types Markdown
markers literally, and the toolbar formatting is only a visual aid in the draft. Figure-reference
bolding and caption title bolding are applied by the rules below, not taken from run formatting.

## Conversion rules

These are the rules the script implements, in processing order. Use them to check output or to
convert by hand.

### 1. Front matter and placeholders

Everything the draft doesn't contain becomes a placeholder starting with `TODO`, so
`grep -n TODO <post>.md` lists all open items. The placeholders are plain words, so the YAML
always parses.

`description:` is never quoted, following the site's convention. If the description contains
characters YAML could misread (`: `, ` #`, or a leading `[`, `*`, `-`, quote, etc.), the script
warns; suggest rephrasing rather than adding quotes.

```yaml
---
title: "<first Heading 1>"
date: TODO_YYYY-MM-DD 00:01:00
last_modified_at: TODO_YYYY-MM-DD 00:01:00
categories: [TODO_category]
tags: [TODO_tag1, TODO_tag2, TODO_tag3]  # TAG names should always be lowercase
description: <title comment, else TODO_description>   # never quoted
media_subpath: /assets/img/TODO_YYYY-MM-DD-<slug>/
image:
  path: TODO_cover.jpg
  alt: "<b>TODO_cover_caption</b><br><i>This image is AI generated.</i>"
math: true            # only if LaTeX ($…$ / $$…$$) appears; otherwise omitted
---

{% include toggle-details.html %}
```

- With `--date`, the date fills `date`, `last_modified_at`, `media_subpath` and the file name.
- Without a date, the file is named `TODO_YYYY-MM-DD-<slug>.md`. Jekyll ignores files that don't
  start with a real date, so an unfinished post can't be published by accident.
- Existing categories on the site: `Machine learning`, `Data curation & analysis`, `Coding` (use these
  names if suggesting one). Tags are lowercase.
- Other placeholders in the body: `width="TODO_700"` on every figure (700 is the usual width;
  the author picks 200–850 per figure), `TODO_url`, `TODO_caption`, `TODO_alt`, `TODO_box_title`.

### 2. Headings

- First Heading 1 → title. Later Heading 1 → `##`, Heading 2 → `###`, Heading 3 → `####`.
- Strip literal `#` markers and trailing spaces from heading text (drafts sometimes type `##`).
- "Conclusion"/"Conclusions" → "Key takeaways".
- End order is fixed: `## Key takeaways` (wherever the draft has it), then `## References`,
  then `## Footnotes`, even if the draft has Footnotes before References.

### 3. Links

- Comment whose first line starts with `http` → wrap exactly the commented text in
  `<a href="URL" target="_blank">…</a>`. Only the first line is used: Google Docs appends
  reaction lines ("1 total reaction", "X reacted with 👍 …") to the comment text.
- If several comments cover the same text, the one with a URL wins; replies are ignored.
- Real hyperlinks in the document are converted the same way.
- In intro paragraphs (before the first section heading) that contain two or more links, each
  link starts on its own line, as in the published posts:
  ```
  These … were discussed with 
  <a href="…" target="_blank">Surag Nair</a>, 
  <a href="…" target="_blank">Malte Lücken</a>, and 
  <a href="…" target="_blank">Kieran Didi</a>.
  ```

### 4. Text boxes

A box is: a title paragraph, a paragraph containing only `[` (or `|`), content paragraphs, a
paragraph containing only `]`. The title paragraph is consumed by the box.

The **first box that appears before any section heading** (the paper/participant summary)
is always visible:

```html
<div style="border:1px solid #535353;border-radius: 7px;padding: 10px;margin: 15px 0px 15px 0px;">
<p>
<b>Box title</b>
</p>

<p>
Paragraph…
</p>

</div>
```

All other boxes are collapsible and followed by an empty `<p></p>`:

```html
<details closed>
<summary><u>Box title</u></summary>
<div style="border:1px solid #535353;border-radius: 7px;padding: 10px;margin: 5px;">

<p>Paragraph…</p>

<ul>
<li>List item…</li>
</ul>

</div>
</details>
<p></p>
```

Inside boxes Markdown is not parsed, so the content must be HTML: each paragraph in `<p>`,
lists as `<ul>/<ol><li>`, `**x**` → `<b>x</b>`, `*x*` → `<i>x</i>`, links as `<a>`, figure
references as `<b>Figure N</b>`, and footnote references as ` (<b>Footnote N</b>)` (see §6).
Images inside boxes aren't supported — move them out.

### 5. Figures

Draft pattern: an image paragraph, directly followed by the caption paragraph
`Figure N: Title sentence. Rest of caption…`, where "Figure N:" links to bookmark
`#figur_<name>`.

```
![Desktop View](<name>.jpg){: width="TODO_700" alt="<title without final period>" .shadow style="border-radius: 7px;"}
_<b>Figure N: Title sentence.</b> (<b>a</b>) Rest of caption…_
```

- **File name**: from the caption bookmark — strip `figur_`/`fig_` and any extension
  (`#figur_unbalanced_data.png` → `unbalanced_data.jpg`). Without a bookmark: `figureN.jpg`
  (warning). Images are converted to JPG (transparency flattened onto white) and saved in
  `assets/img/<prefix>-<slug>/`.
- **Caption title**: the `**bold**` part after "Figure N:" if present, otherwise the first
  sentence (not split at "e.g.", "i.e.", "vs."). The whole caption is italic (`_…_`); the
  label + title are `<b>`.
- **Panel labels** `(a)`, `(**a**)` → `(<b>a</b>)`.
- **In-text references**: "Figure N" linked to `#fig_<name>` → `**Figure N**` (`<b>` in boxes),
  absorbing literal `**` around it and a panel letter right after: "(Figure 3a)" →
  `(**Figure 3a**)`. If the draft has no figure links at all, plain "Figure N" mentions are
  bolded instead, except "Figure N of …" (a figure in another paper) and inside captions.

### 6. Footnotes

- Fix typos: `[^footonote5]`, `[footnote1]` (missing `^`) → proper references.
- **Renumber** sequentially by first appearance anywhere in the body, including boxes and
  captions. A footnote cited twice keeps its first number.
- Definitions go under `## Footnotes`, one per line, no blank lines between, in new number order:
  ```
  [^footnote1]: Text…
  [^footnote2]: Text…
  ```
- References inside boxes become ` (<b>Footnote N</b>)`. If a footnote is referenced *only*
  inside boxes, its definition can't render on the site — warn and let the author decide.
- Definitions that are never referenced are kept, labelled `[^unreferenced_N]`, after the
  numbered ones (warning). They don't render, but no draft text is lost.

### 7. References, lists, text cleanup

- Each paragraph under "References" → `- ` item, consecutive lines, original order.
- Docs lists → `- item` (`1.` for numbered), two-space indent per nesting level.
- `|||` → `III` (the draft's way of typing the Roman numeral, e.g. "phase III").
- Non-breaking and zero-width spaces are normalised; trailing spaces stripped.

### 8. Sections list

Every post gets a Sections list. A collapsible box is inserted right before the first section
heading (i.e. after the italic disclaimers), listing `##` sections with their `###` subsections
nested, excluding Key takeaways / References / Footnotes:

```html
<details closed>
<summary><u>Sections list</u></summary>
<div style="border:1px solid #535353;border-radius: 7px;padding: 10px;margin: 5px;">
<ul>

<li>Section</li>
<ul>
<li>Subsection</li>
</ul>

</ul>
</div>
</details>
```

## Known limitations

- **Tables** aren't converted (warning); write them by hand as Markdown or HTML.
- **Comments spanning paragraphs** produce one link per paragraph (warning).
- **Math detection** is heuristic (`$…$` / `$$…$$`); the report asks to confirm, since a
  draft with prices in dollars could trigger it.
- The scripts never reword text; everything editorial is left to the author.
