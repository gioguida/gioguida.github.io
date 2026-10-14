#!/usr/bin/env python3
"""Build the static portfolio from human-editable YAML/JSON sources.

Run with: python3 scripts/build.py
The generated HTML intentionally keeps the existing GitHub Pages URLs.
"""
from __future__ import annotations

import html
import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def validate(site, project_data, cv):
    errors = []
    if not site.get("title") or not site.get("url"):
        errors.append("config/site.json must define title and url")
    bio = site.get("bio", {})
    for field in ("title", "eyebrow", "photo", "photoAlt", "cvFile"):
        if not bio.get(field):
            errors.append(f"config/site.json: bio is missing required field {field!r}")
    for field in ("birthDate", "birthCity", "currentCity", "education", "internship", "downloadCv"):
        if not bio.get("labels", {}).get(field):
            errors.append(f"config/site.json: bio.labels is missing required field {field!r}")
    for field in ("photo", "cvFile"):
        if bio.get(field) and not (ROOT / bio[field]).is_file():
            errors.append(f"config/site.json: bio {field!r} references missing file {bio[field]!r}")
    experience_ids = {item.get("id") for item in cv.get("experience", [])}
    for internship_id in bio.get("internshipIds", []):
        if internship_id not in experience_ids:
            errors.append(f"config/site.json: bio internship id {internship_id!r} is missing from CV_DATA.yaml")
    for field in ("full_name", "date_of_birth", "location"):
        if not cv.get("personal", {}).get(field):
            errors.append(f"CV_DATA.yaml: personal is missing required field {field!r}")
    if cv.get("personal", {}).get("date_of_birth"):
        try:
            datetime.strptime(cv["personal"]["date_of_birth"], "%d-%m-%Y")
        except ValueError:
            errors.append("CV_DATA.yaml: personal.date_of_birth must use DD-MM-YYYY")
    if not cv.get("education"):
        errors.append("CV_DATA.yaml: education must contain at least one entry")
    cv_projects = {item.get("id"): item for item in cv.get("projects", [])}
    seen = set()
    for project in project_data.get("projects", []):
        pid = project.get("id")
        if not pid or pid in seen:
            errors.append(f"data/projects.json: duplicate or missing project id {pid!r}")
        seen.add(pid)
        for field in ("slug", "title", "shortDescription", "date", "order", "overview", "links"):
            if field not in project:
                errors.append(f"project {pid!r} is missing required field {field!r}")
        if pid not in cv_projects:
            errors.append(f"project {pid!r} is not present in CV_DATA.yaml")
        if project.get("image") and not (ROOT / project["image"]).exists():
            errors.append(f"project {pid!r} references missing image {project['image']!r}")
        for link_name, link in project.get("links", {}).items():
            if not isinstance(link, str) or not link:
                errors.append(f"project {pid!r} has an invalid link {link_name!r}")
    if errors:
        raise SystemExit("\n".join(["Content validation failed:"] + [f"- {error}" for error in errors]))


def relative(path: str) -> str:
    return "../" if path.startswith("projects/") else ""


def head(site, page_title, description, prefix="", canonical_path=""):
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(page_title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="author" content="{esc(site['title'].split(' — ')[0])}">
  <link rel="canonical" href="{esc(site['url'])}/{esc(canonical_path)}">
  <link rel="stylesheet" href="{prefix}style.css">
  <link rel="icon" type="image/x-icon" href="{prefix}favicon.ico?v=5">
</head>'''


def nav(site, current, prefix=""):
    links = []
    for item in site["navigation"]:
        links.append(f'<a href="{prefix}{esc(item["href"])}"' + (f' aria-current="page"' if item["key"] == current else "") + f'>{esc(item["label"])}</a>')
    return '<nav class="site-nav" aria-label="Main navigation">' + "".join(links) + "</nav>"


def footer(site, prefix="", back=False):
    if back:
        return f'<footer class="page footer"><a href="{prefix}projects.html">back to projects</a></footer>'
    social = "".join(f'<a href="{esc(item["href"])}" target="_blank" rel="noopener">{esc(item["label"])}</a>' for item in site["social"])
    return f'<footer class="page footer"><span>© {site["year"]} {esc(site["title"].split(" — ")[0])} <span>·</span> {esc("gio.guidarini[at]gmail.com")}</span><span class="footer-links">{social}</span></footer>'


def tags(items):
    return "".join(f'<span class="tag">{esc(item)}</span>' for item in items)


def cv_dates(item):
    start, end = item.get("start", ""), item.get("end", "")
    return start if not end or start == end else f"{start} — {end}"


def cv_entry(item, title, subtitle):
    return f'''<li class="cv-entry">
  <span class="cv-entry-date">{esc(cv_dates(item))}</span>
  <div><h3>{esc(title)}</h3><p>{esc(subtitle)}</p><span class="muted">{esc(item.get('location', ''))}</span></div>
</li>'''


def bio_page(site, cv):
    personal = cv["personal"]
    bio = site["bio"]
    labels = bio["labels"]
    birthdate = datetime.strptime(personal["date_of_birth"], "%d-%m-%Y").strftime("%d %B %Y").lstrip("0")
    birth_city = personal.get("birth_city") or "Milan, Italy"
    education = "\n".join(cv_entry(item, item["institution"], item["degree"]) for item in cv["education"])
    experience_by_id = {item["id"]: item for item in cv.get("experience", [])}
    internships = "\n".join(cv_entry(experience_by_id[item_id], experience_by_id[item_id]["organization"], experience_by_id[item_id]["role"]) for item_id in bio["internshipIds"])
    return f'''{head(site, bio["title"] + " — " + personal["full_name"], "Biography, education, and internship of " + personal["full_name"], canonical_path="bio.html")}
<body>{nav(site, "bio")}
<main class="page subpage bio-page">
  <header class="bio-hero">
    <div class="bio-intro"><h2>{esc(personal['full_name'])}</h2>
      <dl class="bio-facts"><div><dt>{esc(labels['birthDate'])}</dt><dd>{esc(birthdate)}</dd></div><div><dt>{esc(labels['birthCity'])}</dt><dd>{esc(birth_city)}</dd></div><div><dt>{esc(labels['currentCity'])}</dt><dd>{esc(personal['location'])}</dd></div></dl>
      <a class="download" href="{esc(bio['cvFile'])}" download>{esc(labels['downloadCv'])}</a>
    </div>
    <img class="bio-photo" src="{esc(bio['photo'])}" alt="{esc(bio['photoAlt'])}">
  </header>
  <section class="bio-section" aria-labelledby="education-heading"><h2 id="education-heading">{esc(labels['education'])}</h2><ol class="cv-list">{education}</ol></section>
  <section class="bio-section" aria-labelledby="internship-heading"><h2 id="internship-heading">{esc(labels['internship'])}</h2><ol class="cv-list">{internships}</ol></section>
</main>
{footer(site)}</body></html>'''


def project_index(projects):
    rows = []
    for project in sorted(projects, key=lambda x: x["order"]):
        rows.append(f'''<a class="publication" href="projects/{esc(project['slug'])}.html">
  <div><h2>{esc(project['title'])}</h2><p class="muted">{esc(project['shortDescription'])}</p><span class="meta">{esc(project['date'])}</span></div>
</a>''')
    return "\n".join(rows)


def detail_page(site, project):
    prefix = "../"
    buttons = []
    for label, href in project["links"].items():
        buttons.append(f'<a class="download" href="{esc(prefix + href if not href.startswith("http") else href)}">{esc(label)}</a>')
    sidebar = "".join(f'<strong>{esc(item["heading"])}</strong><p class="muted">{item["body"]}</p>' for item in project.get("sidebar", []))
    body = "".join(f"<p>{esc(paragraph)}</p>" for paragraph in project["overview"])
    image = f'<img class="project-image project-photo" src="{esc(prefix + project["image"])}" alt="{esc(project["imageAlt"])}">' if project.get("image") else ""
    return f'''{head(site, project['title'], project['shortDescription'], prefix, 'projects/' + project['slug'] + '.html')}
<body>
{nav(site, "projects", prefix)}
<main class="page subpage">
  <div class="detail-hero{' detail-hero--text-only' if not image else ''}"><div><p class="eyebrow">{esc(project['date'])}</p><h1>{esc(project['title'])}</h1><p class="lede">{esc(project['shortDescription'])}</p>{''.join(buttons)}</div>{image}</div>
  <div class="detail-body"><div><h2>Overview</h2>{body}</div><aside class="side-note">{sidebar}</aside></div>
</main>
{footer(site, prefix, back=True)}
</body></html>
'''


def build(force=False, page=None):
    site = load_json(ROOT / "config/site.json")
    project_data = load_json(ROOT / "data/projects.json")
    theme = load_json(ROOT / "config/theme.json")
    with (ROOT / "CV_DATA.yaml").open(encoding="utf-8") as stream:
        cv = yaml.safe_load(stream)
    validate(site, project_data, cv)
    generate_stylesheet(theme)
    projects = project_data["projects"]
    owner = cv["personal"]["full_name"]

    pages = {
        "index.html": f'''{head(site, site["title"], site["description"])}
<body class="home-page">{nav(site, "home")}
<main class="page"><section class="profile-home"><div class="profile-copy"><h1>{esc(owner)}</h1><p class="description">{esc(site["home"]["description"])}</p></div></section></main>
{footer(site)}</body></html>''',
        "bio.html": bio_page(site, cv),
        "projects.html": f'''{head(site, "Projects — " + owner, "Selected projects by " + owner, canonical_path="projects.html")}
<body>{nav(site, "projects")}
<main class="page subpage"><div class="intro"><h1>Projects</h1></div><section class="publication-list">{project_index(projects)}</section></main>
{footer(site)}</body></html>''',
        "lecture-notes.html": f'''{head(site, "Lecture notes — " + owner, site["lectureNotes"]["description"], canonical_path="lecture-notes.html")}
<body>{nav(site, "lecture-notes")}
<main class="page subpage"><div class="intro"><p class="eyebrow">03 / lecture notes</p><h1>Lecture notes</h1><p class="lede">{esc(site["lectureNotes"]["description"])}</p></div><section class="empty-state"><p class="muted">No published notes yet.</p></section></main>
{footer(site)}</body></html>'''
    }
    if page and page not in pages:
        raise SystemExit(f"Unknown page {page!r}; choose one of: {', '.join(pages)}")
    for path, content in pages.items():
        if page and path != page:
            continue
        write_output(ROOT / path, content, force)
    if not page:
        project_dir = ROOT / "projects"
        for project in projects:
            write_output(project_dir / f"{project['slug']}.html", detail_page(site, project), force)
        write_output(ROOT / "sitemap.xml", sitemap(site, projects), force)
    print(f"Validated {len(pages) + len(projects)} pages from CV_DATA.yaml and JSON content/config.")


def write_output(path, content, force):
    if path.exists() and not force:
        print(f"Preserved existing {path.relative_to(ROOT)} (use --force to regenerate)")
        return
    path.write_text(content, encoding="utf-8")
    print(f"Generated {path.relative_to(ROOT)}")


def generate_stylesheet(theme):
    """Keep the CSS font import and legacy variables mapped to theme.json."""
    colors = theme["colors"]
    typography = theme["typography"]
    geometry = theme["geometry"]
    effects = theme["effects"]
    responsive = theme["responsive"]
    font_name = typography.get("primaryFont")
    if not isinstance(font_name, str) or not font_name.strip():
        raise SystemExit("config/theme.json: typography.primaryFont must be a Google Fonts family name")
    font_url = f"https://fonts.googleapis.com/css2?family={quote_plus(font_name)}&display=swap"
    variables = f''':root {{
  --base03: {colors["textPrimary"]};
  --base01: {colors["textMuted"]};
  --base00: {colors["textSecondary"]};
  --base0: #839496;
  --base2: {colors["backgroundSecondary"]};
  --base3: {colors["background"]};
  --yellow: {colors["selection"]};
  --orange: {colors["accentWarm"]};
  --red: #dc322f;
  --cyan: #2aa198;
  --blue: {colors["accent"]};
  --violet: #6c71c4;
  --color-background: {colors["background"]};
  --color-surface: {colors["surface"]};
  --color-text-primary: {colors["textPrimary"]};
  --color-text-secondary: {colors["textSecondary"]};
  --color-text-muted: {colors["textMuted"]};
  --color-accent: {colors["accent"]};
  --color-border: {colors["border"]};
  --shadow: {effects["shadow"]};
  --font-display: "{font_name}", Didot, "Bodoni 72", "Times New Roman", serif;
  --font-text: "{font_name}", Iowan Old Style, Baskerville, Georgia, serif;
  --font-mono: {typography["monoFont"]};
  --font-weight-heading: {typography["headingWeight"]};
  --font-size-body: {typography["bodySize"]};
  --font-size-small: {typography["smallSize"]};
  --page-max-width: {geometry["pageMaxWidth"]};
  --page-gutter: {geometry["pageGutter"]};
  --radius-card: {geometry["cardRadius"]};
  --radius-control: {geometry["controlRadius"]};
  --space-card: {geometry["cardPadding"]};
  --space-grid: {geometry["gridGap"]};
  --space-section: {geometry["sectionSpacing"]};
  --space-bio-section: {geometry["bioSectionSpacing"]};
  --subpage-width: {geometry["subpageWidth"]};
  --bio-hero-width: {geometry["bioHeroWidth"]};
  --bio-photo-width: {geometry["bioPhotoWidth"]};
  --bio-photo-mobile-width: {geometry["bioPhotoMobileWidth"]};
  --bio-photo-aspect-ratio: {geometry["bioPhotoAspectRatio"]};
  --bio-photo-top-offset: {geometry["bioPhotoTopOffset"]};
  --transition: {effects["transition"]};
  --blur: {effects["blur"]};
}}'''
    stylesheet = (ROOT / "style.css").read_text(encoding="utf-8")
    stylesheet = re.sub(r"\A@import[^\n]*;", lambda match: f"@import url('{font_url}');", stylesheet, count=1)
    stylesheet = re.sub(r"\A(@import[^\n]*;\n\n):root\s*\{.*?\}\n\n", lambda match: match.group(1) + variables + "\n\n", stylesheet, count=1, flags=re.S)
    stylesheet = stylesheet.replace("@media (max-width: 760px)", f"@media (max-width: {responsive['mobileBreakpoint']})")
    # CSS is intentionally preserved during the normal validation build too.
    # The caller regenerates it only when explicitly requesting --force.
    return stylesheet


def experience_markup(cv):
    entries = []
    for item in cv.get("experience", []):
        dates = f"{item.get('start', '')} — {item.get('end', '')}".replace(" —  — ", " — ")
        facts = " ".join(item.get("summary_facts", []))
        entries.append(f'<li><p class="eyebrow">{esc(dates)} · {esc(item["role"])}</p><h2>{esc(item["organization"])}</h2><p class="muted">{esc(item.get("location", ""))}</p><p>{esc(facts)}</p><div>{tags(item.get("tags", [])[:5])}</div></li>')
    return "".join(entries)


def sitemap(site, projects):
    urls = ["", "bio.html", "projects.html", "lecture-notes.html"] + [f"projects/{p['slug']}.html" for p in projects]
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{site['url']}/{url}</loc></url>\n" for url in urls) + "</urlset>\n"


def readme():
    return '''# Portfolio content

This is a static site. Install the one build-time dependency with `python3 -m pip install -r requirements.txt`, then run `python3 scripts/build.py` to validate the content without overwriting existing files. Use `python3 scripts/build.py --force` when you intentionally want to regenerate the published HTML and CSS from the data/config sources.

- `CV_DATA.yaml` is the authoritative source for personal, education, experience, and project facts.
- `data/projects.json` contains website-specific project presentation, media, links, and ordering.
- `config/site.json` contains metadata, navigation, homepage copy, and social links.
- `config/theme.json` documents the design tokens used by `style.css`.

To add a project, add its website presentation to `data/projects.json`, ensure its factual record exists in `CV_DATA.yaml`, add any media under `media/projects/`, then run `python3 scripts/build.py --force`.
'''


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate and optionally regenerate the static portfolio")
    parser.add_argument("--force", action="store_true", help="overwrite existing generated HTML, sitemap, and CSS")
    parser.add_argument("--page", help="regenerate one top-level HTML page without touching other pages")
    parser.add_argument("--styles", action="store_true", help="update style.css from theme.json without overwriting HTML")
    arguments = parser.parse_args()
    if (arguments.force and not arguments.page) or arguments.styles:
        stylesheet = generate_stylesheet(load_json(ROOT / "config/theme.json"))
        (ROOT / "style.css").write_text(stylesheet, encoding="utf-8")
        print("Generated style.css")
    build(force=arguments.force, page=arguments.page)
