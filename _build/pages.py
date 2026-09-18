"""One function per page. Each composes components; none of them build markup by hand."""
import json

from . import components as c
from .content import (BASE_URL, CHAPTERS, EMAIL, FOOTER_LINE, HERO, IN_PROGRESS,
                      IN_PROGRESS_NOTE, POSTS, POSTS_INTRO, PROJECTS, PROJECTS_INTRO, STATS)

TAGLINE = "Ashish Jain — staff engineer, AI systems in production"
DESCRIPTION = ("Ashish Jain, staff engineer in Bengaluru. Builds AI systems that survive production: "
               "real-time vision at 2M+ security events a day, LLM pipelines, agentic tooling.")


def _json_ld(facts: dict) -> str:
    data = {
        "@context": "https://schema.org", "@type": "Person",
        "name": facts["name"], "jobTitle": facts["title"], "description": facts["summary"],
        "url": facts["url"] + "/", "email": "mailto:" + facts["email"],
        "worksFor": {"@type": "Organization", "name": "Hakimo.ai", "url": "https://hakimo.ai"},
        "address": {"@type": "PostalAddress", "addressLocality": facts["location"]["city"],
                    "addressCountry": facts["location"]["countryCode"]},
        "sameAs": [p["url"] for p in facts["profiles"]], "knowsAbout": facts["knowsAbout"],
    }
    return ('<script type="application/ld+json">\n'
            + json.dumps(data, indent=2, ensure_ascii=False) + "\n</script>")


def home(facts: dict) -> str:
    body = "\n".join([
        c.header(active="now", on_home=True),
        '<main id="main">',
        c.hero(eyebrow=HERO["eyebrow"], headline=HERO["headline"], proof=HERO["proof"],
               portrait=HERO["portrait"], stats=STATS, masthead=HERO["masthead"]),
        "\n".join(c.chapter(ch) for ch in CHAPTERS),
        "</main>",
        c.footer(updated=facts["updated"], lead=FOOTER_LINE),
    ])
    return c.document(head_html=c.head(
        title=TAGLINE, description=DESCRIPTION, canonical=BASE_URL + "/",
        og_type="profile", og_image=f"{BASE_URL}/assets/ashish-800.webp",
        extra=_json_ld(facts)), body_html=body)


def projects(facts: dict) -> str:
    cards = "\n".join(c.project_card(p) for p in PROJECTS)
    body = "\n".join([
        c.header(active="projects"),
        '<main id="main">',
        c.page_intro(label="Built outside work", heading="Projects", dek=PROJECTS_INTRO),
        f'<section class="projlist">{cards}</section>',
        "</main>",
        c.footer(updated=facts["updated"]),
    ])
    return c.document(head_html=c.head(
        title="Projects — Ashish Jain",
        description=("Tools Ashish Jain builds and ships in public: local-first macOS apps, agent tooling, "
                     "and field guides. What is live, and what is coming next."),
        canonical=BASE_URL + "/projects/"), body_html=body)


def writing(facts: dict) -> str:
    cards = "\n".join(c.post_card(p) for p in POSTS)
    body = "\n".join([
        c.header(active="posts"),
        '<main id="main">',
        c.page_intro(label="Writing", heading="Posts", dek=POSTS_INTRO),
        f'<section class="projlist">{cards}</section>',
        c.in_progress(IN_PROGRESS, IN_PROGRESS_NOTE),
        "</main>",
        c.footer(updated=facts["updated"]),
    ])
    return c.document(head_html=c.head(
        title="Writing — Ashish Jain",
        description=("Long-form writing from real work: things built, broken and measured. "
                     "Edge inference, LLM pipelines, and agent tooling."),
        canonical=BASE_URL + "/posts/"), body_html=body)


def post(facts: dict, meta: dict, article_html: str) -> str:
    """A published post: shared chrome, the prose comes from content/posts/."""
    body = "\n".join([
        c.header(active="posts"),
        '<main id="main">',
        '<article class="post">',
        f'<a class="back" href="/posts/">{c.icon("arrow-left")}All posts</a>',
        f'<h1>{meta["title"]}</h1>',
        f'<p class="post-meta"><time class="num" datetime="{meta["date"]}">{meta["date"]}</time>'
        f'<span>{meta["read_time"]}</span><span>Ashish Jain</span></p>',
        article_html.strip(),
        "</article>",
        "</main>",
        c.footer(updated=facts["updated"]),
    ])
    return c.document(head_html=c.head(
        title=f'{meta["title"]} — Ashish Jain', description=meta["description"],
        canonical=BASE_URL + meta["href"], og_type="article",
        extra=f'<meta property="article:published_time" content="{meta["date"]}">'), body_html=body)


def not_found(facts: dict) -> str:
    body = "\n".join([
        c.header(),
        '<main id="main">',
        '<section class="lost">',
        '<p class="label">404</p>',
        "<h1>Nothing here.</h1>",
        '<p class="dek">The page moved, or never existed. <a href="/">Back to the homepage</a>, '
        'or try <a href="/projects/">projects</a> and <a href="/posts/">writing</a>.</p>',
        "</section>",
        "</main>",
        c.footer(updated=facts["updated"]),
    ])
    return c.document(head_html=c.head(
        title="Page not found — Ashish Jain", description="Page not found.",
        canonical=BASE_URL + "/404.html", noindex=True), body_html=body)


def redirect(to: str, title: str) -> str:
    """A minimal moved-page stub. No chrome: nobody should see this for longer than a frame."""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<link rel="canonical" href="{BASE_URL}{to}">
<meta http-equiv="refresh" content="0; url={to}">
<meta name="robots" content="noindex">
</head>
<body>
<p>This page moved to <a href="{to}">{to}</a>.</p>
<script>location.replace('{to}');</script>
</body>
</html>
"""
