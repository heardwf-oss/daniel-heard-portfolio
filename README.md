# Daniel Heard Engineering Project Portfolio

Static employer-facing portfolio site built for GitHub Pages.

## Current Source Set

This rebuild is based on the corrected file set only:

- Professional PDFs limited to the C8676 temporary-works files downloaded on `2026-04-18`
- `C9211` intentionally excluded after user clarification
- Additional professional documents extracted from:
  - `attachments.zip`
  - `attachments (1).zip`
  - `attachments (2).zip`
  - `attachments (3).zip`
- Additional academic files extracted from:
  - `attachments (4).zip`
  - `uniwork.zip`

The published files are the original supplied documents copied unchanged into the repository.

## What The Repository Contains

- Landing page: [`index.html`](./index.html)
- Full document library: [`documents.html`](./documents.html)
- One generated page per project in [`projects/`](./projects)
- Original source PDFs in [`pdfs/source/`](./pdfs/source)
- Non-PDF source files and original source bundles in [`files/source/`](./files/source)
- Thumbnails and preview images in [`images/`](./images)
- Structured metadata in [`data/projects.json`](./data/projects.json)
- QA and review notes in [`docs/`](./docs)
- Rebuild script in [`scripts/build_portfolio.py`](./scripts/build_portfolio.py)

## Local Preview

Run a local web server:

```powershell
cd C:\Users\heard\OneDrive\Documents\daniel-heard-engineering-portfolio
python -m http.server 8000
```

Then open [http://127.0.0.1:8000/index.html](http://127.0.0.1:8000/index.html).

## Viewer Behaviour

- Project pages use a single native browser PDF iframe instead of PDF.js canvas rendering.
- This is materially faster for the supplied files and keeps the browser's own PDF controls available.
- Every project page also includes prominent `Open PDF` buttons.
- Preview images can be clicked to open a full-screen overlay.

## GitHub Pages Deployment

This is a buildless static site.

1. Create a GitHub repository and copy this folder into it.
2. Push the repository to `main` or your preferred default branch.
3. In GitHub, open `Settings` -> `Pages`.
4. Set `Source` to `Deploy from a branch`.
5. Select the default branch and `/ (root)`.
6. Save.

No build step is required for hosting.

## Rebuilding

The build script expects the same source files to still exist in `Downloads`, plus the six supplied zip bundles.

```powershell
cd C:\Users\heard\OneDrive\Documents\daniel-heard-engineering-portfolio
C:\Users\heard\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\scripts\build_portfolio.py
```

The script will:

- clear and recreate the generated site outputs
- copy the original PDFs unchanged into `pdfs/source/`
- copy the spreadsheet and zip bundles into `files/source/`
- regenerate thumbnails and preview images
- rewrite `index.html`, `documents.html`, and all project pages
- update `data/projects.json`
- update the QA and review notes in `docs/`

## Updating The Portfolio

To add another project or file set:

1. Add the source file reference to `PROJECTS`, `LIBRARY_FILES`, or `ARCHIVES` in [`scripts/build_portfolio.py`](./scripts/build_portfolio.py).
2. For zipped files, use `archive_source(...)`.
3. Add the project metadata, tags, and preview page selections.
4. Re-run the build script.
5. Review the generated pages and the files in [`docs/`](./docs).

## File Structure

```text
/
|-- index.html
|-- documents.html
|-- README.md
|-- assets/
|   |-- css/
|   `-- js/
|-- data/
|   `-- projects.json
|-- docs/
|   |-- known-issues.md
|   |-- qa-report.md
|   |-- redaction-manifest.json
|   `-- redaction-review.md
|-- files/
|   `-- source/
|-- images/
|   |-- previews/
|   `-- thumbnails/
|-- pdfs/
|   `-- source/
|-- projects/
`-- scripts/
```

## Notes

- Original source files in `Downloads` and the supplied zip bundles were left untouched.
- No redaction is applied in this version because the user explicitly requested the original files unchanged.
- The document library includes the spreadsheet file and all six original zip bundles alongside the project PDFs.
