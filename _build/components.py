"""Reusable HTML components.

Every function returns an HTML string and takes only the data it renders, so a
component can be read on its own and reused on any page. Nothing here reaches
for globals; page composition happens in `pages.py`.
"""
from urllib.parse import urlparse

from .content import (BASE_URL, CHAPTER_NAV, EMAIL, SECTION_NAV, SITE_NAME, SOCIALS)
from .icons import icon

FONTS = ("https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@900"
         "&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400;1,6..72,500"
         "&family=Hanken+Grotesk:wght@400;500;600&display=swap")

SITE_HOST = urlparse(BASE_URL).netloc


def is_external(href: str) -> bool:
    """True when the link leaves this site, so it should open in a new tab."""
    parsed = urlparse(href)
    return parsed.scheme in ("http", "https") and parsed.netloc != SITE_HOST


def link_attrs(href: str, rel: str = "") -> str:
    """Attributes for one anchor. Off-site links open in a new tab (noopener)."""
    rels = [r for r in rel.split() if r]
    attrs = [f'href="{href}"']
    if is_external(href):
        attrs.append('target="_blank"')
        rels += ["noopener", "noreferrer"]
    if rels:
        attrs.append(f'rel="{" ".join(dict.fromkeys(rels))}"')
    return " ".join(attrs)


def anchor(label: str, href: str, css_class: str = "", rel: str = "",
           icon_name: str = "", icon_after: bool = False) -> str:
    """One anchor. Arrow icons trail the label; brand marks lead it."""
    cls = f' class="{css_class}"' if css_class else ""
    glyph = icon(icon_name) if icon_name else ""
    inner = f"{label}{glyph}" if icon_after else f"{glyph}{label}"
    return f"<a{cls} {link_attrs(href, rel)}>{inner}</a>"


# --- document shell --------------------------------------------------------

def head(*, title: str, description: str, canonical: str, extra: str = "",
         noindex: bool = False, og_type: str = "website", og_image: str = "") -> str:
    """The <head> every page shares: one font request, one token sheet, one stylesheet."""
    tags = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        f"<title>{title}</title>",
        f'<meta name="description" content="{description}">',
        f'<link rel="canonical" href="{canonical}">',
        '<meta name="theme-color" content="#070A14">',
        '<link rel="icon" href="/favicon.svg" type="image/svg+xml">',
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:site_name" content="{SITE_NAME}">',
        f'<meta property="og:title" content="{title}">',
        f'<meta property="og:description" content="{description}">',
        f'<meta property="og:url" content="{canonical}">',
        '<meta name="twitter:creator" content="@Ashi608">',
    ]
    if og_image:
        tags += [f'<meta property="og:image" content="{og_image}">',
                 '<meta name="twitter:card" content="summary_large_image">']
    else:
        tags.append('<meta name="twitter:card" content="summary">')
    if noindex:
        tags.append('<meta name="robots" content="noindex">')
    tags += [
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        f'<link rel="stylesheet" href="{FONTS}">',
        '<link rel="stylesheet" href="/tokens.css">',
        '<link rel="stylesheet" href="/style.css">',
    ]
    if extra:
        tags.append(extra)
    return "\n".join(tags)


def document(*, head_html: str, body_html: str, lang: str = "en") -> str:
    """The page shell. The swarm canvas and its veil sit behind every page."""
    return f"""<!doctype html>
<html lang="{lang}">
<head>
{head_html}
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<canvas id="swarm" aria-hidden="true"></canvas>
<div class="veil" aria-hidden="true"></div>
<div class="grain" aria-hidden="true"></div>
<div class="page">
{body_html}
</div>
<script src="/swarm.js" defer></script>
<script src="/site.js" defer></script>
</body>
</html>
"""


# --- header ----------------------------------------------------------------

def _nav_group(links, *, css_class: str, active: str, prefix: str = "") -> str:
    items = []
    for nav in links:
        href = f"{prefix}{nav.href}" if nav.href.startswith("#") else nav.href
        is_active = nav.href.lstrip("#/").rstrip("/") == active
        current = ' aria-current="page"' if is_active and not nav.href.startswith("#") else ""
        state = " active" if is_active else ""
        items.append(f'<a class="{css_class}{state}" href="{href}"{current}>{nav.label}</a>')
    return "".join(items)


def header(*, active: str = "", on_home: bool = False) -> str:
    """Two nav groups, divided: the homepage chapters, then the site's own pages."""
    prefix = "" if on_home else "/"
    chapters = _nav_group(CHAPTER_NAV, css_class="jump", active=active, prefix=prefix)
    sections = _nav_group(SECTION_NAV, css_class="page-link", active=active)
    return f"""<header class="top">
  <a class="wordmark" href="/">{SITE_NAME}</a>
  <nav aria-label="Primary">
    <div class="nav-group chapters" aria-label="Sections of this profile">{chapters}</div>
    <span class="nav-divider" aria-hidden="true"></span>
    <div class="nav-group pages">{sections}</div>
  </nav>
</header>"""


# --- shared pieces ---------------------------------------------------------

def social_row(css_class: str = "linkrow") -> str:
    """Email plus the off-site profiles. Appears in the hero and the footer."""
    links = [anchor(label, href, rel="me", icon_name=name) for name, href, label in SOCIALS]
    return f'<div class="{css_class}">{"".join(links)}</div>'


def footer(*, updated: str, lead: str = "") -> str:
    big = f'<p class="big">{lead}</p>' if lead else ""
    return f"""<footer class="reveal">
  <div>
    {big}
    {social_row()}
  </div>
  <p class="meta">Ashish Jain · Staff engineer · Bengaluru · Updated {updated}</p>
</footer>"""


def def_list(rows, css_class: str) -> str:
    """A term/description table: problem-approach-result, a timeline, a project's facts."""
    body = "".join(f"<dt>{term}</dt><dd>{desc}</dd>" for term, desc in rows)
    return f'<dl class="{css_class}">{body}</dl>'


def tag(label: str) -> str:
    variant = "live" if label.lower() == "live" else "soon"
    return f'<span class="tag {variant}">{label}</span>'


def page_intro(*, label: str, heading: str, dek: str) -> str:
    return f"""<section class="doc">
  <p class="label">{label}</p>
  <h1>{heading}</h1>
  <p class="dek">{dek}</p>
</section>"""


# --- homepage pieces -------------------------------------------------------

def hero(*, eyebrow: str, headline: str, proof: str, portrait: dict, stats, masthead) -> str:
    tiles = "".join(
        f'<div class="tile"><b class="num">{value}</b><span>{caption}</span></div>'
        for value, caption in stats
    )
    first, second = masthead
    return f"""<section class="hero" aria-label="Introduction">
  <figure class="photo">
    <img src="{portrait['src']}" alt="{portrait['alt']}" width="800" height="800" fetchpriority="high">
  </figure>
  <div class="lines">
    <p class="eb">{eyebrow}</p>
    <h1>{headline}</h1>
    <p class="proof">{proof}</p>
    {social_row()}
  </div>
  <div class="board">{tiles}</div>
  <p class="masthead" aria-hidden="true">{first} <span>{second}</span></p>
</section>
<div class="hint" id="hint"><span class="bar"></span><span>Scroll</span></div>"""


def entry(item) -> str:
    """One piece of work, always open: no disclosure control, nothing hidden."""
    return f"""<article class="entry">
  <h3 class="t">{item.title}</h3>
  <p class="r">{item.result}</p>
  {def_list(item.detail, "par " + item.layout)}
</article>"""


def project_row(title: str, label: str, blurb: str, href: str) -> str:
    return (f'<a class="row" href="{href}"><span class="t">{title} {tag(label)}</span>'
            f'<span class="r">{blurb}</span></a>')


def chapter(item) -> str:
    """A chapter: the giant word sticks while its body scrolls past."""
    body = "".join(entry(e) for e in item.entries)
    body += "".join(project_row(*row) for row in item.rows)
    if item.more:
        label, href = item.more
        body += f'<a class="row more" href="{href}">{label} <span aria-hidden="true">→</span></a>'
    return f"""<section class="chapter reveal" id="{item.slug}">
  <div class="side">
    <h2 class="word"><small>{item.word} <b>· {item.meta}</b></small>{item.word}</h2>
    <p class="sum">{item.summary}</p>
  </div>
  <div class="body">{body}</div>
</section>"""


# --- list pages ------------------------------------------------------------

def project_card(project) -> str:
    thumb = ""
    if project.thumb:
        href, src, alt, w, h = project.thumb
        thumb = (f'<a class="thumb" {link_attrs(href)}><img src="{src}" alt="{alt}" '
                 f'loading="lazy" width="{w}" height="{h}"></a>')
    links = "".join(anchor(label, href, icon_name=name or "", icon_after=True)
                    for label, href, name in project.links)
    stamp = f'<span class="push num">{project.stamp}</span>' if project.stamp else ""
    return f"""<article class="proj reveal" id="{project.slug}">
  <div class="head"><h3>{project.name}</h3>{tag(project.tag)}</div>
  {def_list(project.rows, "par")}
  {thumb}
  <p class="foot">{links}{stamp}</p>
</article>"""


def post_card(post) -> str:
    return f"""<article class="post-card reveal">
  <p class="post-meta"><time class="num" datetime="{post.date}">{post.date}</time><span>{post.read_time}</span></p>
  <h3><a href="{post.href}">{post.title}</a></h3>
  <p class="dek">{post.dek}</p>
  {def_list(post.rows, "par")}
  <a class="arrow-link" href="{post.href}">Read the post{icon('arrow-right')}</a>
</article>"""


def in_progress(items, note: str) -> str:
    rows = "".join(f'<li><span class="tag soon">Writing</span><span>{i}</span></li>' for i in items)
    return f"""<section class="doc nextup-wrap">
  <div class="nextup reveal">
    <p class="label">In progress</p>
    <ul>{rows}</ul>
    <p class="mini">{note}</p>
  </div>
</section>"""
