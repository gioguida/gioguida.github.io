# Portfolio content

This is a static site. Install the one build-time dependency with `python3 -m pip install -r requirements.txt`, then run `python3 scripts/build.py` to validate the content without overwriting existing files. Use `python3 scripts/build.py --force` when you intentionally want to regenerate the published HTML and CSS from the data/config sources.

- `CV_DATA.yaml` is the authoritative source for personal, education, experience, and project facts.
- `data/projects.json` contains website-specific project presentation, media, links, and ordering.
- `config/site.json` contains metadata, navigation, homepage copy, and social links.
- `config/theme.json` documents the design tokens used by `style.css`.

To add a project, add its website presentation to `data/projects.json`, ensure its factual record exists in `CV_DATA.yaml`, add any media under `media/projects/`, then run `python3 scripts/build.py --force`.

The bio page draws birth date, birth city, current location, education, and internship facts from `CV_DATA.yaml`. Its portrait, CV download path, and selected internship IDs are in `config/site.json` under `bio`. After changing those, run `python3 scripts/build.py --force --page bio.html` to update only the bio page.

Fonts and other visual settings live in `config/theme.json`. Change `typography.primaryFont` to a Google Fonts family name, then run `python3 scripts/build.py --styles` to update the font import and CSS without replacing the published HTML pages.

Use the fixed top-right theme switch to toggle the Solarized light and Solarized dark color schemes. The selected scheme is remembered in the browser.
