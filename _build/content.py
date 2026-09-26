"""All site copy, as data.

Nothing here knows about HTML structure -- `components.py` owns that. Values may
contain inline markup (<b>, <i>, <a>) and are therefore trusted fragments, never
escaped. Facts that also feed llms.txt / resume.json live in facts.json instead,
so a number is never stated in two places.
"""
from dataclasses import dataclass, field

Html = str  # a trusted inline-markup fragment, not escaped on render

SITE_NAME = "qriousguy.com"
BASE_URL = "https://qriousguy.com"
EMAIL = "ashishjain608@gmail.com"

# --- navigation ------------------------------------------------------------
# Two groups, rendered with a divider between them. `anchor` links point at
# homepage sections and are prefixed with "/" on every page but the homepage.


@dataclass(frozen=True)
class NavLink:
    label: str
    href: str


CHAPTER_NAV = [NavLink("Now", "#now"), NavLink("Before", "#before"), NavLink("Next", "#next")]
SECTION_NAV = [NavLink("Projects", "/projects/"), NavLink("Writing", "/posts/")]

SOCIALS = [
    ("mail", f"mailto:{EMAIL}", EMAIL),
    ("github", "https://github.com/Ashishjain608", "GitHub"),
    ("linkedin", "https://www.linkedin.com/in/ashishjain608", "LinkedIn"),
    ("x", "https://x.com/Ashi608", "X"),
]

# --- homepage --------------------------------------------------------------

HERO = {
    "eyebrow": "Ashish Jain · Staff engineer · 10+ years",
    "headline": "I build AI systems that <i>survive</i> production.",
    "proof": (
        "Real-time vision at <b>2M+ security events a day</b>, across <b>5,000+ cameras</b> "
        "and <b>150+ customers</b>. Edge inference that cut CPU by ~60% and avoided ~$500K."
    ),
    "portrait": {"src": "/assets/ashish-800.webp", "alt": "Ashish Jain"},
    "masthead": ("Ashish", "Jain"),
}

STATS = [
    ("2M+", "security events a day"),
    ("5,000+", "cameras, real time"),
    ("150+", "customers served"),
    ("10+", "years in production"),
]


@dataclass(frozen=True)
class Entry:
    """One piece of work: a title, a one-line result, and the problem/approach/result.

    `layout` picks how the detail reads: "par" for labelled prose, "timeline"
    for dated rows, which need a wider, untracked term column.
    """
    title: str
    result: Html
    detail: list = field(default_factory=list)   # [(term, description)]
    layout: str = "par"


@dataclass(frozen=True)
class Chapter:
    slug: str
    word: str
    meta: str
    summary: Html
    entries: list = field(default_factory=list)
    rows: list = field(default_factory=list)     # [(title, tag, blurb, href)]
    more: tuple = ()                             # (label, href)


NO_RECEIPT = '<span class="rc none">no public receipt</span>'

CHAPTERS = [
    Chapter(
        slug="now",
        word="Now",
        meta="Hakimo.ai · Feb 2023 to present",
        summary=(
            "<b>Staff engineer at Hakimo.ai.</b> AI security: real-time vision across thousands "
            "of cameras, and the console operators watch it on."
        ),
        entries=[
            Entry(
                title="Vision pipeline, gateway and ingestion",
                result="<b>2M+ events a day</b> · CPU down ~60% · ~$500K avoided",
                detail=[
                    ("Problem", "Thousands of cameras produce far more than a cloud path can process at a sane cost."),
                    ("Approach", "Co-architected the gateway and ingestion layer. Moved detection to the edge on <b>YOLOv11 and RF-DETR</b>."),
                    ("Result", f"<b>2M+ events a day</b> across 5,000+ cameras and 150+ customers. CPU down ~60%. The in-house path avoided <b>~$500K</b>. {NO_RECEIPT}"),
                ],
            ),
            Entry(
                title="Operator console",
                result="<b>Hundreds of live streams</b> at sub-second latency",
                detail=[
                    ("Problem", "Operators need hundreds of camera streams at once, live, without lag."),
                    ("Approach", "A WebSocket monitoring console with an NVR-style grid."),
                    ("Result", f"Hundreds of parallel streams rendered at <b>sub-second latency</b>. {NO_RECEIPT}"),
                ],
            ),
        ],
    ),
    Chapter(
        slug="before",
        word="Before",
        meta="2015 to 2023",
        summary="<b>Ten years of production systems</b> before the AI ones. Compass, VMware, SAP Labs, Infosys.",
        entries=[
            Entry(
                title="Career, by month",
                result="Five companies · B.Tech 2015",
                layout="timeline",
                detail=[
                    ("Feb 2023 to present", "<b>Hakimo.ai</b>, Staff Engineer"),
                    ("Feb 2022 to Jan 2023", "<b>Compass</b>, Senior Software Engineer"),
                    ("May 2020 to Feb 2022", "<b>VMware</b>, Member of Technical Staff"),
                    ("Mar 2018 to Apr 2020", "<b>SAP Labs</b>, Software Developer"),
                    ("Aug 2015 to Mar 2018", "<b>Infosys</b>, Senior Systems Engineer"),
                    ("2015", "B.Tech, Electronics and Communication Engineering"),
                ],
            ),
            Entry(
                title="Recognition",
                result="Hackathon top-10 · seed-stage advisor",
                layout="timeline",
                detail=[
                    ("2025", "<b>Top-10 finalist</b>, Gen AI Exchange Hackathon"),
                    ("Advisory", "Advised <b>LawMatrix</b> (legal-tech) through its seed round"),
                ],
            ),
        ],
    ),
    Chapter(
        slug="next",
        word="Next",
        meta="built outside work, yours to run",
        summary='<b>Tools I ship in public.</b> Full write-ups on the <a class="rc" href="/projects/">projects page</a>.',
        rows=[
            ("Notes &amp; Goals", "Live", "A calm, local-first macOS app. Tasks, notes and goals as plain files.", "/projects/#notes-goals"),
            ("agent-experience", "Live", "Six practices that survived fact-checking, 16 claims that did not.", "/projects/#agent-experience"),
            ("Prentice", "Launching soon", "A workshop for the agents you train, running on your own Mac.", "/projects/#prentice"),
            ("ai-events-radar", "Live", "A field guide to Bengaluru's AI and agent events scene.", "/projects/#ai-events-radar"),
        ],
        more=("All projects", "/projects/"),
    ),
]

FOOTER_LINE = (
    "Always up for a conversation about vision pipelines, edge inference, "
    "or agents that do real work."
)

# --- /projects/ ------------------------------------------------------------


@dataclass(frozen=True)
class Project:
    slug: str
    name: str
    tag: str                                    # "Live" or "Launching soon"
    rows: list = field(default_factory=list)    # [(term, description)]
    links: list = field(default_factory=list)   # [(label, href, icon_name|None)]
    stamp: str = ""
    thumb: tuple = ()                           # (href, src, alt, width, height)


PROJECTS = [
    Project(
        slug="notes-goals", name="Notes &amp; Goals", tag="Live",
        rows=[
            ("What", "A calm, local-first macOS app that keeps tasks, notes and goals as plain files in a folder you choose."),
            ("Why", "Every tool in this category wants an account and a sync server. This one wants a folder."),
            ("How", "No cloud, no accounts. <b>Today</b> is a live query across all your tasks. A ⌘K palette finds a task, a goal, or a line inside a note."),
        ],
        thumb=("https://qriousguy.com/notes-goals-app/", "/assets/notes-goals-dark.webp", "Notes and Goals, Today view", 720, 470),
        links=[("Project page", "https://qriousguy.com/notes-goals-app/", "arrow-up-right"),
               ("GitHub", "https://github.com/Ashishjain608/notes-goals-app", None)],
        stamp="first commit 2026-06-07 · public 2026-09-14",
    ),
    Project(
        slug="agent-experience", name="agent-experience", tag="Live",
        rows=[
            ("Problem", 'Most advice on "agent-ready codebases" has never been tested against a real one.'),
            ("Approach", "Mined <b>380</b> of my own Claude Code sessions, about 1,600 messages, then put each popular claim through adversarial fact-checking."),
            ("Result", "A field guide: <b>six practices</b> that held up, <b>16</b> popular claims that did not, and a do-it-yourself checklist."),
        ],
        links=[("Read the field guide", "https://qriousguy.com/agent-experience/", "arrow-up-right"),
               ("GitHub", "https://github.com/Ashishjain608/agent-experience", None)],
        stamp="first commit 2026-07-07",
    ),
    Project(
        slug="prentice", name="Prentice", tag="Launching soon",
        rows=[
            ("What", "A workshop for the agents you train, running on your own Mac."),
            ("Idea", "An agent is a folder you own: a prompt, the direction you have folded in, and a manifest. Nothing hidden in someone else's account."),
            ("How", "Prentice schedules it, sandboxes it, records what each run did and what it cost, and gives you a <b>Desk</b> to judge its work. Six screens: Desk · Review · Agents · History · Spend · Policy."),
        ],
        stamp="first commit 2026-09-06 · open-sourcing next",
    ),
    Project(
        slug="ai-events-radar", name="ai-events-radar", tag="Live",
        rows=[("What", "A field guide to Bengaluru's AI and agent events scene — what is on, who runs it, and whether it is worth the evening.")],
        links=[("Open it", "https://qriousguy.com/ai-events-radar/", "arrow-up-right"),
               ("GitHub", "https://github.com/Ashishjain608/ai-events-radar", None)],
        stamp="first commit 2026-07-07",
    ),
]

PROJECTS_INTRO = (
    "Tools I build on my own time and ship in public. Live ones link to the real thing; "
    "the rest are being open-sourced next. Every claim here has a link behind it."
)

# --- /posts/ ---------------------------------------------------------------


@dataclass(frozen=True)
class Post:
    """One published post. `source` is its prose fragment under content/posts/."""
    title: str
    href: str
    date: str
    read_time: str
    dek: Html
    description: str                            # meta description for the post page
    source: str
    rows: list = field(default_factory=list)    # [(term, description)]


POSTS = [
    Post(
        title="Six free data sources, one LLM, and 3,872 AI companies",
        href="/posts/six-free-sources-one-llm.html",
        date="2026-07-11",
        read_time="9 min read",
        dek=("Zero paid APIs. The Wayback Machine, SEC Form D filings and four other public sources, "
             "reconciled into one dataset and classified by a single LLM pass."),
        description=("How six free public data sources and one LLM classification pass built a radar of 3,872 "
                     "recently funded AI companies: 551 with live AI roles, 362 with an Indian entity."),
        source="six-free-sources-one-llm.html",
        rows=[
            ("The catch", "Haiku failed the canary test on ambiguous company descriptions; Sonnet was the sweet spot on cost against accuracy."),
            ("Takeaway", 'Most "you need a paid data API" problems are really entity-resolution problems wearing a disguise.'),
        ],
    ),
]

POSTS_INTRO = "Long-form writing from real work: things built, broken and measured. Depth over hot takes."

IN_PROGRESS = [
    "Profiling edge inference: where the ~60% CPU went",
    "What 380 Claude Code sessions taught me about agent-readable codebases",
    "Prentice: a workshop for the agents you train",
]

IN_PROGRESS_NOTE = "Two posts a month is the target."
