# Chris Phelan — Résumé and Writing

Personal résumé, portfolio, and writing site for Chris Phelan, published with GitHub Pages.

**Live site:** [cppdx.github.io/phelanc](https://cppdx.github.io/phelanc/)

## Local preview

The site is static and has no build step. From the repository root, run:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

## Content workflow

- Keep résumé details aligned with Chris's canonical LinkedIn résumé.
- Add writing as a standalone HTML page using `styles.css` and `article.css`.
- Add each published page to the homepage writing grid, `sitemap.xml`, and `feed.xml`.
- Use the responsive `headshot-320.webp` / `headshot-640.webp` sources and `headshot-640.jpg` fallback.
- Keep LinkedIn as the public contact method; do not publish a direct email address.

## Validation

Run the dependency-free site check before publishing:

```bash
python3 scripts/validate_site.py
```

GitHub Actions runs the same check for pull requests and changes to `main`. GitHub Pages deploys the default branch.
