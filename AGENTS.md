# AGENTS.md

## Purpose

This repository contains my personal portfolio website.

The website is maintained partly by coding agents. The primary goal of this file is to ensure that every change preserves a coherent visual system, keeps the repository human-editable, and improves rather than degrades the underlying architecture.

The website must NOT evolve into a collection of independently styled pages or hard-coded components.

The governing principle is:

> **One visual system, one content system, reusable components, human-editable configuration.**

Any implementation that works visually but violates this architecture is incomplete.

---

# 1. Before Making Any Change

Before editing the repository:

1. Inspect the repository structure.
2. Identify:
   - framework/build system;
   - page structure;
   - shared layouts;
   - shared components;
   - global CSS/theme files;
   - content/data files;
   - CV YAML source;
   - project data;
   - favicon/site metadata;
   - deployment/build configuration.
3. Determine whether the requested functionality already has an abstraction that should be extended.
4. Reuse existing abstractions where sensible.
5. Do not create a parallel implementation of an existing system.

Before implementing a feature, explicitly reason about:

- where its content belongs;
- where its visual configuration belongs;
- which reusable component renders it;
- whether it affects multiple pages;
- whether it introduces a new design token;
- how I can edit it manually afterward without touching component code.

Do not begin by directly modifying a page unless the change is genuinely page-specific.

---

# 2. Core Architectural Rule

There must be a strict separation between:

1. **content**
2. **design configuration**
3. **rendering logic**

In general:

```text
human-editable data/config
        ↓
shared rendering components
        ↓
pages
```

Pages should primarily compose reusable components and consume structured data.

They should NOT contain large amounts of:

- hard-coded text;
- hard-coded project entries;
- hard-coded colors;
- hard-coded typography;
- duplicated markup;
- duplicated style rules.

---

# 3. Human-Editable Content

## 3.1 Content must live outside components

Whenever reasonable, textual/content data must live in structured, human-readable files rather than inside JSX/TSX/HTML/components.

Prefer simple JSON for website-specific content.

Examples include:

```text
data/
  projects.json
  publications.json
  links.json
  homepage.json
  experience.json
  education.json
  skills.json
  navigation.json
```

The exact structure may be adapted to the existing repository, but the principle is mandatory.

I must be able to change wording, add an entry, remove an entry, or reorder entries without editing rendering code.

---

## 3.2 Existing CV YAML

The repository contains the same CV-data YAML used for my curricula.

Treat that file as an authoritative structured source wherever its information overlaps with the website.

DO NOT duplicate CV information into independent JSON files unless there is a strong architectural reason.

Instead:

- parse the YAML;
- transform it through a small adapter if necessary;
- render website components from it.

Website-specific information that does not belong in the CV may live in separate JSON files.

Avoid multiple competing sources of truth.

---

# 4. Projects Must Be Manually Addable

Projects are a particularly important example of the content architecture.

I must be able to add a project by editing a human-readable data file without touching application code.

A project representation should resemble something conceptually like:

```json
{
  "id": "example-project",
  "title": "Example Project",
  "shortDescription": "Short summary.",
  "description": "Longer description.",
  "date": "2026",
  "tags": ["FPGA", "SystemVerilog"],
  "image": "/assets/projects/example.png",
  "links": {
    "github": "https://github.com/...",
    "demo": null,
    "paper": null
  },
  "featured": true,
  "order": 10
}
```

This is illustrative, not a mandatory exact schema.

The actual schema should:

- be simple;
- be stable;
- be documented;
- use sensible optional fields;
- avoid requiring meaningless placeholders;
- support ordering;
- support featured/unfeatured projects;
- support links and media cleanly.

Adding a normal project must not require adding a new component.

If project cards and project detail pages exist, both should consume the same project data.

---

# 5. Central Design Control System

The entire visual identity of the website must be controlled centrally.

There should be one clearly identifiable human-editable configuration layer for the design system.

For example:

```text
config/
  theme.json
  site.json
```

or an equivalent structure appropriate to the framework.

The design configuration should expose, where applicable:

### Colors

- page background;
- secondary background;
- surface/card background;
- primary text;
- secondary/muted text;
- accent colors;
- borders;
- interactive states;
- selection colors;
- code colors if applicable.

### Typography

- primary font;
- secondary/display font if used;
- monospace font;
- base font size;
- small text size;
- navigation size;
- heading scale;
- line heights;
- font weights;
- letter spacing where appropriate.

### Geometry

- page maximum width;
- content width;
- spacing scale;
- section spacing;
- border radii;
- border widths;
- card padding;
- grid gaps.

### Effects

- shadows;
- opacity levels;
- hover transitions;
- animation timing;
- blur values if used.

### Responsive behaviour

Important breakpoints and responsive sizing rules should also be centralized when practical.

---

# 6. Design Tokens

Raw visual values should not be scattered throughout the codebase.

Avoid repeated values such as:

```css
color: #d3ff00;
font-size: 17px;
border-radius: 11px;
```

inside unrelated components.

Instead, visual values should come from semantic design tokens, for example:

```css
var(--color-background)
var(--color-text-primary)
var(--color-accent)
var(--font-size-body)
var(--font-size-heading-2)
var(--radius-card)
var(--space-section)
```

The exact implementation may use:

- CSS custom properties;
- generated CSS variables;
- framework theme configuration;
- TypeScript theme objects;

depending on the existing stack.

The important requirement is that there is ONE source of truth.

---

# 7. Global Visual Consistency

The portfolio must look like one coherent website.

A visual change made to the global identity must propagate everywhere.

This includes:

- homepage;
- project pages;
- CV/resume pages;
- about pages;
- contact pages;
- error pages;
- navigation;
- footer;
- cards;
- buttons;
- links;
- modal/dialog elements;
- mobile layouts;
- metadata visuals where applicable;
- favicon.

For example, if the website's background changes from dark blue to black, individual subpages must not retain the old dark blue because they contain local hard-coded styles.

A page may differ visually only when that difference is intentional and semantically justified.

---

# 8. Favicon Is Part of the Design System

The favicon is part of the visual identity, not an unrelated asset.

If a global branding change affects colors or other relevant graphical characteristics, inspect the favicon and update it where necessary.

Whenever practical:

- maintain a simple canonical favicon source, preferably SVG;
- derive variants from that source;
- use the site's design palette;
- avoid manually maintaining unrelated favicon versions.

If automated generation is appropriate for the existing stack, use it.

A theme/branding update is incomplete if the favicon visibly belongs to the previous design.

---

# 9. Shared Components

Repeated visual structures must become reusable components.

Examples:

- navigation;
- footer;
- page container;
- section heading;
- project card;
- tag/chip;
- external link;
- buttons;
- timeline entries;
- publication entries;
- social links;
- image wrappers.

Do not copy and paste markup between pages when the same semantic object exists more than once.

Prefer:

```text
data → reusable component → multiple pages
```

over:

```text
page A implementation
page B copied implementation
page C slightly different copied implementation
```

---

# 10. Every New Feature Must Join the System

This rule is mandatory.

Whenever adding a new feature, ask:

1. Does it contain user-editable content?
   - Put that content in the structured content layer.

2. Does it introduce a configurable visual property?
   - Add an appropriate design token/configuration option.

3. Does it introduce a reusable UI pattern?
   - Create or extend a shared component.

4. Does it introduce site-wide behaviour?
   - Implement it centrally rather than page-by-page.

5. Does it introduce new metadata/assets?
   - Place them in the established data/asset system.

Do NOT implement a feature as a one-off and promise to integrate it later.

Integration into the architecture is part of implementing the feature.

---

# 11. No Hidden Configuration

Do not hide important website choices inside implementation code.

Bad:

```tsx
<h2 style={{ fontSize: "37px", color: "#e3ff52" }}>
```

Better:

```tsx
<h2 className="section-title">
```

with the appearance controlled by the shared design system.

Similarly, avoid hiding:

- section order;
- project order;
- featured items;
- labels;
- social links;
- contact information;
- navigation entries;

inside components if they are naturally content/configuration.

---

# 12. Configuration Must Remain Understandable

Do not solve configurability by creating an enormous opaque configuration schema.

Human editability is a first-class requirement.

Configuration files should:

- use descriptive names;
- have shallow structures where reasonable;
- avoid unnecessary indirection;
- avoid implementation-specific jargon;
- contain examples when useful;
- use clear boolean/options fields;
- remain practical to edit manually.

Prefer:

```json
{
  "typography": {
    "bodySize": "1rem",
    "headingScale": 1.25
  }
}
```

over a highly abstract token graph that requires understanding the rendering implementation.

---

# 13. Schema Validation

Structured data should fail clearly when malformed.

Where appropriate, introduce lightweight schema validation for:

- project entries;
- site configuration;
- theme configuration;
- other important structured content.

Validation should produce useful errors such as:

```text
projects.json:
project "fpga-accelerator" is missing required field "title"
```

rather than failing later during rendering.

Do not make the validation system unnecessarily complicated.

---

# 14. Preserve Existing Appearance by Default

When implementing functionality, do NOT opportunistically redesign unrelated parts of the website.

Unless the task explicitly requests a redesign:

- preserve current visual identity;
- preserve layout hierarchy;
- preserve typography;
- preserve spacing;
- preserve animations;
- preserve responsive behaviour.

Architectural cleanup should reproduce the current appearance before changing it.

Refactoring and redesigning are separate tasks.

---

# 15. No Local Styling Exceptions Without Reason

Avoid page-specific style overrides.

Before introducing a local visual constant, determine whether it belongs in:

1. an existing global token;
2. a new semantic token;
3. a shared component variant.

Only use a local style when the value is genuinely unique to that element.

Do not use local overrides as the fastest way to make something "look right."

---

# 16. Responsive Design Is Mandatory

Every feature must be checked on:

- desktop;
- intermediate/tablet widths;
- mobile.

Do not consider a task complete because the desktop view works.

Watch specifically for:

- overflowing text;
- navigation collisions;
- clipped images;
- unreadable typography;
- excessive margins;
- broken project grids;
- horizontal scrolling;
- buttons/links with inadequate tap targets.

Responsive behaviour should remain visually consistent with the rest of the site.

---

# 17. Accessibility and Semantic HTML

Preserve basic accessibility.

Use:

- semantic HTML;
- proper heading hierarchy;
- descriptive link text;
- alt text where appropriate;
- keyboard-accessible interactions;
- visible focus states;
- sufficient contrast.

Do not sacrifice usability for visual effects.

---

# 18. Content Integrity

Do not invent biographical, academic, professional, or project information.

When information comes from the CV YAML, preserve its meaning.

Do not:

- embellish achievements;
- change dates;
- invent technologies;
- fabricate descriptions;
- silently rewrite facts.

If a requested website feature requires information that does not exist in the repository, use an explicit placeholder or ask for the missing information rather than inventing it.

---

# 19. Assets

Keep assets organized.

Prefer a predictable structure such as:

```text
public/
  images/
    projects/
    profile/
    branding/
  icons/
```

or the repository's existing equivalent.

Do not scatter new assets arbitrarily across the repository.

When replacing an asset, remove obsolete copies if they are no longer used.

Do not commit generated duplicate assets unless required by the deployment system.

---

# 20. Repository Modularity

The architecture should make common changes local and predictable.

Examples:

### Changing the accent color

Should require changing one design configuration value, not searching the repository for hex codes.

### Changing the body font

Should require changing one typography setting.

### Adding a project

Should require editing project data and adding its assets, not writing JSX.

### Changing social links

Should require editing a data/configuration file.

### Reordering homepage sections

Should preferably be controlled declaratively where doing so remains simple.

### Updating CV information

Should propagate from the authoritative CV data where the website derives that information from it.

---

# 21. Avoid Premature Abstraction

Modularity does not mean abstraction for its own sake.

Do not introduce:

- CMS infrastructure;
- databases;
- backend services;
- elaborate plugin architectures;
- unnecessary dependency injection;
- complex state management;

for a static personal portfolio unless explicitly requested.

The desired system is:

> simple, declarative, modular, and directly editable.

Not enterprise software.

---

# 22. Dependency Discipline

Do not add a dependency when the feature is trivial to implement with the existing stack.

Before adding a dependency:

1. check whether the repository already provides the functionality;
2. determine whether the dependency materially simplifies the implementation;
3. avoid large libraries for tiny UI effects.

Remove dependencies that become unused after a refactor.

---

# 23. Design-System Refactoring

If the current repository violates these rules, gradually migrate it toward this architecture.

When touching an area that contains duplicated/hard-coded design values:

- consolidate them when it is safe;
- avoid expanding the duplication;
- preserve visual behaviour;
- prefer incremental refactoring over a complete rewrite.

Do not rewrite the entire site solely because the current structure is imperfect unless explicitly asked.

---

# 24. Preferred Conceptual Repository Structure

Do not blindly impose this tree if the framework has a better native organization, but aim for equivalent separation:

```text
/
├── AGENTS.md
├── data/
│   ├── cv.yaml
│   ├── projects.json
│   ├── homepage.json
│   ├── links.json
│   └── ...
│
├── config/
│   ├── site.json
│   └── theme.json
│
├── src/
│   ├── components/
│   ├── layouts/
│   ├── pages/
│   ├── lib/
│   │   ├── content/
│   │   └── config/
│   └── styles/
│
└── public/
    ├── images/
    ├── icons/
    └── favicon...
```

The important property is not the exact directory names.

The important property is clear ownership:

```text
data       = what the site says
config     = how the site is configured
components = how reusable things are rendered
pages      = how those things are composed
styles     = global visual implementation
assets     = media
```

---

# 25. Central Theme Contract

The theme/configuration layer should ultimately be capable of controlling the site's major visual characteristics without modifying components.

At minimum, try to converge toward centralized control of:

```text
colors
fonts
font sizes
heading scale
line heights
content width
spacing
border radii
borders
shadows
transition timing
```

When a future task introduces another global visual parameter, extend this contract instead of hard-coding it.

---

# 26. New Feature Contract

Any substantial new feature should satisfy all applicable items below before it is considered complete:

- [ ] Content is externally editable where appropriate.
- [ ] No unnecessary hard-coded text exists in rendering code.
- [ ] Colors use shared tokens.
- [ ] Typography uses shared tokens.
- [ ] Spacing follows the shared system.
- [ ] Reusable UI has been componentized.
- [ ] Desktop layout works.
- [ ] Mobile layout works.
- [ ] Existing pages remain visually consistent.
- [ ] Favicon/branding has been considered if the visual identity changed.
- [ ] Existing structured data is reused instead of duplicated.
- [ ] Build passes.
- [ ] Existing tests pass.
- [ ] No unused code/assets/dependencies were introduced.

---

# 27. Visual Changes Require Site-Wide Audit

When making any global visual change, inspect all major routes.

Examples include changes to:

- background;
- foreground/text color;
- accent color;
- fonts;
- font scale;
- border style;
- card style;
- global spacing;
- navigation appearance;
- link appearance;
- general graphical language.

After such a change, verify that every page still looks like part of the same site.

Do not update only the route shown in the task description.

---

# 28. Implementation Strategy

For non-trivial tasks:

1. inspect;
2. identify the existing system;
3. determine the smallest coherent architectural change;
4. implement shared infrastructure first;
5. wire the feature into it;
6. remove obsolete/duplicated implementation;
7. validate;
8. inspect affected pages.

Do not repeatedly patch symptoms.

If three elements need the same fix, look for the common abstraction.

---

# 29. Scope Discipline

Do not make unrelated changes.

Do not:

- rewrite copy that was not part of the task;
- rename sections unnecessarily;
- redesign unrelated components;
- reformat the whole repository without reason;
- change URLs/routes casually;
- change external links;
- modify CV data unless requested.

A good patch should be easy to explain in terms of the requested feature and the architectural rules in this document.

---

# 30. When Requirements Are Ambiguous

Prefer existing website conventions over inventing a new visual language.

If the requested result can be implemented consistently using patterns already present in the site, do so.

Ask for clarification only when the ambiguity affects something substantial such as:

- factual public content;
- information architecture;
- destructive removal;
- branding direction;
- meaningfully different UX choices.

Do not ask about trivial implementation details that can be inferred from the repository.

---

# 31. Definition of Done

A feature is not complete merely because it appears on screen.

It is complete when:

1. it works;
2. it matches the existing visual language;
3. it is responsive;
4. its content is human-editable where appropriate;
5. its design parameters participate in the shared control system;
6. reusable pieces are reusable;
7. it has not created a second source of truth;
8. it has not introduced one-off styling that will make future changes difficult;
9. the repository is simpler or at least no harder to maintain than before.

The long-term objective is that I can make most routine portfolio updates myself by editing simple YAML/JSON configuration files while coding agents are needed only for genuinely new behaviour or new visual components.