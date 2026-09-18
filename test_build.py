#!/usr/bin/env python3
"""Checks for the generated site.

    python3 test_build.py

Run it after `python3 build.py`. It fails loudly on the things that are easy to
break by hand and expensive to notice later: a dead internal link, an off-site
link that steals the tab, a colour hard-coded outside tokens.css, or the review
scaffolding creeping back in.
"""
import pathlib
import re
import sys
import xml.etree.ElementTree as ElementTree

ROOT = pathlib.Path(__file__).parent
PAGES = ["index.html", "projects/index.html", "posts/index.html", "404.html",
         "posts/six-free-sources-one-llm.html"]

failures = []


def check(condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def resolves(href: str) -> bool:
    """True if an internal href points at a file this site actually ships."""
    path = href.split("#")[0].split("?")[0]
    if not path or path == "/":
        return (ROOT / "index.html").exists()
    target = ROOT / path.lstrip("/")
    return target.exists() or (target / "index.html").exists()


def main() -> int:
    tokens = (ROOT / "tokens.css").read_text()
    styles = (ROOT / "style.css").read_text()

    # --- the design system stays centralised --------------------------------
    stripped = re.sub(r"/\*.*?\*/", "", styles, flags=re.S)
    # mask-image and SVG filter ids carry colours that are shapes, not palette values
    palette_lines = [ln for ln in stripped.splitlines()
                     if "mask-image" not in ln and "data:image/svg" not in ln]
    stray = re.findall(r"#[0-9a-fA-F]{3,8}\b", "\n".join(palette_lines))
    check(not stray, f"style.css hard-codes colours, move them to tokens.css: {stray}")

    used = set(re.findall(r"var\((--[a-z0-9-]+)", stripped))
    defined = set(re.findall(r"(--[a-z0-9-]+)\s*:", tokens + styles))
    check(used <= defined, f"style.css uses undefined tokens: {sorted(used - defined)}")

    check("--swarm-veil" in tokens, "tokens.css must expose the swarm veil knob")

    # --- the favicon is valid, and drawn from the palette -------------------
    favicon = ROOT / "favicon.svg"
    try:
        ElementTree.parse(favicon)          # XML comments cannot contain "--"
    except ElementTree.ParseError as error:
        check(False, f"favicon.svg is not well-formed: {error}")
    palette = {h.lower() for h in re.findall(r"#[0-9a-fA-F]{6}", tokens)}
    used_in_icon = {h.lower() for h in re.findall(r"#[0-9a-fA-F]{6}", favicon.read_text())}
    check(used_in_icon <= palette,
          f"favicon.svg uses colours outside the palette: {sorted(used_in_icon - palette)}")

    # --- the review-only scaffolding is gone --------------------------------
    for page in PAGES:
        html = (ROOT / page).read_text()
        for banned, why in [("<details", "disclosure widgets were removed"),
                            ('class="seg"', "the Essentials/Everything toggle was removed"),
                            ('class="picker"', "the palette picker was review-only"),
                            ("vswitch", "the variant switcher was review-only"),
                            ("data-v=", "the light variant was removed"),
                            ("feed.xml", "RSS is not surfaced in the UI"),
                            (">RSS<", "RSS is not surfaced in the UI")]:
            check(banned not in html, f"{page}: {banned} still present ({why})")

        # --- both nav groups on every page ----------------------------------
        check('class="nav-group chapters"' in html, f"{page}: missing the chapter nav group")
        check('class="nav-group pages"' in html, f"{page}: missing the page nav group")
        check('class="nav-divider"' in html, f"{page}: nav groups are not separated")
        for label in ("Now", "Before", "Next", "Projects", "Writing"):
            check(f">{label}</a>" in html, f"{page}: nav is missing {label}")

        # --- links ----------------------------------------------------------
        for match in re.finditer(r"<a\b([^>]*)>", html):
            attrs = match.group(1)
            href = re.search(r'href="([^"]+)"', attrs)
            if not href:
                continue
            href = href.group(1)
            if href.startswith(("http://", "https://")) and "qriousguy.com" not in href:
                check('target="_blank"' in attrs, f"{page}: {href} does not open in a new tab")
                check("noopener" in attrs, f"{page}: {href} opens a new tab without noopener")
            elif href.startswith("/"):
                check(resolves(href), f"{page}: dead internal link {href}")

    if failures:
        print(f"FAILED ({len(failures)})")
        for failure in failures:
            print("  -", failure)
        return 1
    print(f"ok — {len(PAGES)} pages: nav groups, links, and centralised colour all check out")
    return 0


if __name__ == "__main__":
    sys.exit(main())
