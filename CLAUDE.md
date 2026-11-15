# Luther Aloud site — operating notes for Claude

## Episode cover conversion (color-faithful)

When the user attaches an `episode cover.png` to flip a Coming Soon card to
Live, convert it through `scripts/convert-cover.py`:

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
any channel is more than one step off `#3E1014`. That is the oxblood used
by the site CSS, the pipeline's cover template, and the playlist covers I
generate from HTML; keeping every cover within one step of it is what
stops the roadmap grid from drifting between warmer and cooler reds.

Older `ffmpeg`-based conversions landed at `#3C0E11` — two steps darker
per channel. If a cover already in `assets/` samples outside tolerance,
regenerate it from the source PNG with this script rather than nudging
the on-site display.

## Where covers come from

- **Episode covers** (`cover-ban.jpg`, `cover-baptism.jpg`,
  `cover-blessed-sacrament.jpg`, `cover-brief-explanation.jpg`,
  `cover-confession.jpg`) — the user attaches each PNG; convert with the
  script above.
- **Playlist covers** (`cover-fourteen-of-consolation.jpg`,
  `cover-good-works.jpg`, `cover-new-testament.jpg`,
  `cover-papacy-at-rome.jpg`) — rendered from a shared HTML template via
  Playwright at 1920×1080 against `background: #3E1014`, then put through
  the same `scripts/convert-cover.py` so the oxblood check runs on them
  too.

## Pushing changes

The git remote is still `stood6363/luther-aloud-site`; GitHub redirects
pushes to the current `LutherAloud/luther-aloud-site`. Don't change the
remote in-session.
