# Luther Aloud site — operating notes for Claude

## Making a cover for a new card

Every new single-episode card AND every new playlist card gets its cover
rendered here, from the shared HTML template. The user does not attach
cover PNGs any more.

The flow has two steps.

### 1. Render the PNG from the template

Start from `scripts/cover-template.html`. Substitute the two placeholders:

- `__TITLE__` — the work's English title, e.g. `A Treatise on Good Works`.
  Capitalised exactly as it appears on the roadmap card; the template
  handles the line break at 140px / `padding: 0 180px`.
- `__YEAR__` — the year on the byline, e.g. `1520` or `1517`. Single year
  only — the byline reads `Martin Luther · <year>`.

Render the substituted HTML at exactly `1920 × 1080` with Playwright (or
any headless Chromium) and save the screenshot as a PNG. The background
is `#3E1014`, the gold rule and wordmark are `#C9A227`, the title is
`#F4EBD8`, and the font is Cormorant Garamond — the template loads it from
Google Fonts, so wait for `document.fonts.ready` before the screenshot.

### 2. Convert and check

```
scripts/convert-cover.py SRC.png assets/cover-<slug>.jpg
```

The script writes a 1280×720 sRGB JPEG at quality 92 with 4:4:4 chroma
(no subsampling) and no embedded ICC profile. It uses Pillow when
importable and falls back to ImageMagick with the equivalent flags
(`-colorspace sRGB -sampling-factor 4:4:4 -quality 92 -strip`) when
Pillow cannot be loaded. Same color math either way.

After writing the JPEG the script samples four points inside the oxblood
field — (15,15), (640,80), (100,400), (1200,700) — and exits non-zero if
any channel is more than one step off `#3E1014`. That's the oxblood used
by the site CSS and the cover template; keeping every cover within one
step of it is what stops the roadmap grid from drifting between warmer
and cooler reds. Treat a non-zero exit as a blocker, not a warning — do
not commit the JPEG until the check is green.

An older `ffmpeg`-based conversion landed at `#3C0E11`, two steps darker.
If a cover currently in `assets/` samples outside tolerance, regenerate
it from the template with this flow rather than nudging the on-site
display. **Existing cards stay as they are** unless the user asks for a
specific one to be redone; policy changes do not trigger retroactive
regeneration.

## What kind of card uses what

- **Single-episode card** (one video, one card) → render one cover from
  the template with that episode's title and year.
- **Multi-part work** (serialised across a YouTube playlist) → one
  playlist card, one cover from the template with the work's title and
  the year of the first part. Do not render per-part covers for the site.
- **Coming Soon card** → no cover; those render as text-only tiles with
  the dimmer `.card-soon` styling in `css/style.css`.

## Pushing changes

The git remote is still `stood6363/luther-aloud-site`; GitHub redirects
pushes to the current `LutherAloud/luther-aloud-site`. Don't change the
remote in-session.
