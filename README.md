# Tigre Dictionaries — multilingual static site

Searchable, crawlable dictionaries built from the open
[BeitTigreAI/tigre-data-parallel-multilingual](https://huggingface.co/datasets/BeitTigreAI/tigre-data-parallel-multilingual)
corpus. One self-contained dictionary per target language, plus a landing hub. Everything in one repo.

## Contents

| Path | Dictionary | Entries | Pages |
|------|------------|--------:|------:|
| `index.html` | Landing hub | — | — |
| `english/` | Tigre → English | 58,298 | 117 |
| `arabic/` | Tigre → Arabic (right-to-left) | 31,311 | 63 |
| `german/` | Tigre → German | 26,932 | 54 |
| `swedish/` | Tigre → Swedish | 14,670 | 30 |
| `style.css`, `favicon.*`, `apple-touch-icon.png` | Shared assets | | |
| `sitemap.xml`, `robots.txt` | For search engines | | |

Each language folder has its own `index.html` (search box), numbered `page-XXXX.html`
(plain crawlable tables), and `dict.json` (the search index).

## Deploy (GitHub Pages)

1. Put everything in one repo (root), e.g. `tigre-dictionaries`.
2. Settings → Pages → Deploy from a branch → `main` / root.
3. Live at `https://<owner>.github.io/<repo>/`; dictionaries at `.../english/`, `.../arabic/`, `.../german/`, `.../swedish/`.

**Before deploying,** replace the placeholder `https://USERNAME.github.io/REPO/` in
`sitemap.xml` and `robots.txt` with your real URL, then submit the sitemap in Google Search Console
(verify this site as its own property — a different URL needs its own verification file).

## Notes

- **Search needs a web server** (it loads each `dict.json`); the numbered pages work anywhere.
- **Arabic** renders right-to-left with the Noto Naskh Arabic web font; the Tigre column stays left-to-right Ge'ez.
- **Gloss order** shows the clearest translation first; many Tigre entries have several target translations.
- **License & credit:** data belongs to BeitTigreAI — keep the attribution in the footers.

Regenerate with `gen_multi.py` (point `PARQUET` at the dataset file; edit `LANGS` to add/remove languages).
