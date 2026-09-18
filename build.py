#!/usr/bin/env python3
"""Build qriousguy.com.

    python3 build.py

Reads facts.json (the dated, checkable facts) and _build/content.py (the copy),
renders every page from the components in _build/, and writes llms.txt and
resume.json from the same facts so a number is never stated in two places.

Generated files are committed, because GitHub Pages serves the repo as-is.
"""
import json
import pathlib

from _build import pages
from _build.content import POSTS

ROOT = pathlib.Path(__file__).parent
CONTENT = ROOT / "content"


def write(relative_path: str, text: str) -> None:
    target = ROOT / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
    print(f"  {relative_path}")


def render_llms_txt(facts: dict) -> str:
    lines = [f"# {facts['name']}, qriousguy.com",
             f"> {facts['positioning']} {facts['summary']}", "",
             f"Updated {facts['updated']}.", "", "## Facts (dated, public)"]
    for figure in facts["figures"]:
        lines.append(f"- {figure['value']} {figure['what']} "
                     f"(source: {figure['source']}; confirmed {figure['confirmed']})")
    lines += ["", "## Experience"]
    for job in facts["work"]:
        span = f"{job['startDate']} to {job.get('endDate', 'present')}"
        summary = f". {job['summary']}" if job.get("summary") else ""
        lines.append(f"- {job['position']}, {job['name']}, {span}{summary}")
        lines += [f"  - {h}" for h in job.get("highlights", [])]
    lines += [f"- {e['institution']}, {e['endDate']}" for e in facts["education"]]
    lines += ["", "## Recognition"] + [f"- {a}" for a in facts["awards"]]
    lines += ["", "## Projects"]
    for project in facts["projects"]:
        url = f", {project['url']}" if project.get("url") else ""
        lines.append(f"- {project['name']} ({project['status']}{url}): {project['description']}")
    lines += ["", "## Writing"] + [f"- {p['title']} ({p['date']}): {p['url']}" for p in facts["posts"]]
    lines += ["", "## Contact", f"- Email: {facts['email']}"]
    lines += [f"- {p['network']}: {p['url']}" for p in facts["profiles"]]
    lines += ["", "## Machine-readable",
              "- https://qriousguy.com/resume.json (JSON Resume schema)", ""]
    return "\n".join(lines)


def render_resume(facts: dict) -> str:
    resume = {
        "$schema": "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json",
        "basics": {"name": facts["name"], "label": f"{facts['title']}, applied AI",
                   "email": facts["email"], "url": facts["url"],
                   "summary": f"{facts['positioning']} {facts['summary']}",
                   "location": facts["location"], "profiles": facts["profiles"]},
        "work": facts["work"],
        "education": facts["education"],
        "awards": [{"title": a} for a in facts["awards"]],
        "projects": facts["projects"],
        "publications": [{"name": p["title"], "releaseDate": p["date"], "url": p["url"],
                          "summary": p["dek"]} for p in facts["posts"]],
        "skills": [{"name": k} for k in facts["knowsAbout"]],
        "meta": {"lastModified": facts["updated"], "canonical": facts["url"] + "/resume.json"},
    }
    return json.dumps(resume, indent=2, ensure_ascii=False) + "\n"


def main() -> None:
    facts = json.loads((ROOT / "facts.json").read_text())
    print("building qriousguy.com")

    write("index.html", pages.home(facts))
    write("projects/index.html", pages.projects(facts))
    write("posts/index.html", pages.writing(facts))
    write("404.html", pages.not_found(facts))
    write("apps/index.html", pages.redirect("/projects/", "Projects — Ashish Jain"))

    for post in POSTS:
        prose = (CONTENT / "posts" / post.source).read_text()
        meta = {"title": post.title, "date": post.date, "read_time": post.read_time,
                "description": post.description, "href": post.href}
        write(post.href.lstrip("/"), pages.post(facts, meta, prose))

    write("llms.txt", render_llms_txt(facts))
    write("resume.json", render_resume(facts))
    print("done")


if __name__ == "__main__":
    main()
