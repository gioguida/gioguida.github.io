# Portfolio content

This is a static site. Install the one build-time dependency with `python3 -m pip install -r requirements.txt`, then run `python3 scripts/build.py` to validate content and synchronize the generated CSS from the data/config sources. Use `python3 scripts/build.py --force` when you intentionally want to regenerate the published HTML from those sources.

- `CV_DATA.yaml` is the authoritative source for personal, education, experience, and project facts.
- `data/projects.json` contains website-specific project presentation, media, links, and ordering.
- `config/site.json` contains metadata, navigation, homepage copy, and social links.
- `config/theme.json` documents the design tokens used by `style.css`.

To add a project, add its website presentation to `data/projects.json`, ensure its factual record exists in `CV_DATA.yaml`, add any media under `media/projects/`, then run `python3 scripts/build.py --force`.

The bio page draws birth date, birth city, current location, education, and internship facts from `CV_DATA.yaml`. Its portrait, CV download path, and selected internship IDs are in `config/site.json` under `bio`. After changing those, run `python3 scripts/build.py --force --page bio.html` to update only the bio page.

Fonts and other visual settings live in `config/theme.json`. Change a theme value, then run `python3 scripts/build.py` to update the generated CSS without replacing the published HTML pages. The legacy `--styles` option remains accepted for compatibility.

Use the fixed top-right theme switch to toggle the Solarized light and Solarized dark color schemes. The selected scheme is remembered in the browser.

Floating-menu navigation uses a staged page transition: a visible footer exits, the pages slide in menu order, and a visible destination footer enters. Tune `effects.pageSlideDuration`, `effects.pageSlideEasing`, `effects.footerSlideDuration`, and `effects.footerSlideEasing` in `config/theme.json`, then run `python3 scripts/build.py` to update the CSS variables. Reduced-motion preferences skip the animation. Ordinary links and failed page loads use normal navigation.

Menu destinations are fetched after the initial page loads and again on menu hover or keyboard focus. The bio portrait is served as an optimized WebP asset; its original PNG is retained as the editable source.

To preview page transitions locally, run `python3 -m http.server 8000` from the repository root and open `http://localhost:8000/`. Opening an HTML file directly with a `file://` URL prevents browsers from loading the next page for the transition.
