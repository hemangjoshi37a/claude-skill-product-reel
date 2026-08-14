---
name: product-reel
description: >
  Create premium, multi-language Instagram Reels (and matching 1:1 promo images)
  for a physical product from its photos + a spec sheet. Use when the user asks to
  make a reel / short video ad / promo carousel for a product, or to localize an ad
  into another language (e.g. English + Hindi). Handles reference-faithful image
  generation, scene scripting, Gemini TTS voiceover, and ffmpeg assembly with music,
  transitions, subtitles, logo and contact footer. Reuse it for a NEW product by
  swapping the product images, the voiceover scenes, and the company block.
---

# Product Reel

Turn a folder of product photos + a spec/feature list into a polished 9:16 Reel
(1080x1920, <=90 s) with brand logo, Ken-Burns motion, transitions, per-language
subtitles, a synced voiceover, a persistent contact footer, and a ducked music bed.
Optionally also produce spec-rich 1:1 promo images and application shots.

**Works in ANY project.** This skill is fully self-contained and project-agnostic:
drop your product images in a folder, write one JSON config, and run the builder.
Nothing here is tied to a specific repo — all paths come from the config you write.

## Inputs to collect from the user
- **Product photos** (real): the machine/product from a few angles, plus any UI /
  detail shots. A close-up crop of the "business end" helps a lot (see image tips).
- **Spec / feature list**: the selling points and exact numbers (dimensions, speed,
  accuracy, temps, connectivity, price/contact...).
- **Company block**: logo file, one contact line (site + phone), address line, and
  any web-app URL. Ask if missing — never invent contact details.
- **Languages**: e.g. `en`, `hi`. Each needs a font that covers its script
  (DejaVuSans-Bold for Latin/English, NotoSansDevanagari-Bold for Hindi in the
  example; other languages need an appropriate bold-font path for their script).
- **Gemini API key**: needed for image gen + TTS. Put it in the project's gitignored
  `.tmp/gkey` and reference it via `gemini_key_file`, or set `gemini_key` directly.

## Prerequisites (verify first)
- **ffmpeg** with the `xfade`, `overlay`, `zoompan`, and `sidechaincompress` filters
  (all standard in a normal build). `drawtext` is **NOT** required — every caption is
  rendered with **Pillow** into transparent PNG overlays, so a static ffmpeg without
  libfreetype is fine. Check with `ffmpeg -version` / `ffmpeg -filters`.
- **A Python with `google-genai` and `Pillow` installed.** You already have a
  ready-to-use interpreter at `~/.claude/image-gen-mcp/.venv/bin/python` — use it as-is.
- **A Gemini API key.** Store it in the project's gitignored `.tmp/gkey` and point
  `gemini_key_file` at it, or set `gemini_key` in the config directly.
- **Fonts** covering each target language. The example references
  `DejaVuSans-Bold` (Latin/English) and `NotoSansDevanagari-Bold` (Hindi); any other
  language needs the absolute path to an appropriate **bold** font for its script.
  Confirm a script is covered with e.g. `fc-list :lang=hi`.

## Workflow

### 1. (Optional) Generate spec-rich images from the REAL product photos
Use **Gemini "Nano Banana Pro"** (`gemini-3-pro-image`) via `edit_image` with the
real photo as reference — it keeps the exact product while restyling the scene. Two
ways to call it:
- MCP tool `image-gen-mcp/edit_image` with `image_data` = a **file path** (the
  image-gen server accepts paths and uses Gemini for editing), or
- directly: `client.models.generate_content(model="gemini-3-pro-image",
  contents=[prompt, PIL.Image], config=GenerateContentConfig(response_modalities=["Image"],
  image_config=ImageConfig(aspect_ratio="1:1")))`.

Image prompt rules that worked well:
- "KEEP THE EXACT SAME <product> unchanged and recognizable: <describe it>. Do NOT
  redesign it." Then relight onto a deep charcoal (#0d1117) + blue-grid background,
  cyan/amber accents, bold white headline, small brand wordmark. "NO festival / flags
  / religious imagery, no people."
- For **in-action** shots (product doing its job): feed a **tight crop of the working
  head/tool** as the reference and add a strict single-tool constraint — e.g. "there
  is EXACTLY ONE <tool>, the machine's own; do NOT bend/duplicate/re-angle it; its tip
  touches the work". This fixes the common "second floating tool / bent tool" artifact.
- Text renders reliably; keep numbers/URLs/phones spelled exactly in the prompt.

### 2. Write the reel scene script
Aim for a scroll-stopping **hook** first, then reveal → specs → applications → CTA.
Keep each line short (one idea). Write it in every target language (natural, not
literal; spell out numbers/units so TTS reads them well — "zero point zero one
millimeter", "नब्बे से चार सौ अस्सी डिग्री"). One scene per line; each line becomes a
subtitle and a voiceover segment. ~16-18 lines ≈ 60-75 s.

### 3. Fill the config
Copy `config.example.json`, then change only: `out_prefix`, `images_dir`, the
`company` block, `languages` (+ fonts), and the `scenes` array (image + per-language
`vo`). Leave `music: null` to auto-generate a copyright-free ambient bed, or set a
path to your own cleared track. `voice` picks a Gemini voice (Puck=upbeat,
Charon=informative, Kore=firm, Aoede/Zephyr=bright, Sulafat=warm).

**Where files go (IMPORTANT — never `/tmp`).** `images_dir`, `out_dir`, `tmp_dir`
and `gemini_key_file` are resolved **relative to the config file's own directory**
(not the shell CWD), so you can run the builder from anywhere and it still writes
next to the project; absolute paths are used as-is. **ALL** working files — TTS
`.wav` clips, per-scene `.mp4` clips, Ken-Burns stage PNGs, overlay PNGs, the
generated music bed, the stitched video — land in `tmp_dir`, and the final
MP4/MKV in `out_dir`. Both **must be project-local** (e.g. `".reel_build"` and
`"promo"`). Do **not** put them under `/tmp` or `/var/tmp`: those are wiped on
reboot/power loss, which throws away the resumable progress and forces a full
re-run against the 100-requests/day Gemini TTS cap. The builder prints a loud
stderr warning if either resolves into the system temp dir (it will not silently
override an explicit absolute path you chose).

### 4. Build
```
~/.claude/image-gen-mcp/.venv/bin/python ~/.claude/skills/product-reel/build_reel.py <your-config.json>
```
It generates TTS per scene (retried), times each scene to its longest-language
voiceover, renders per-scene clips (image + Ken-Burns on a branded canvas + logo +
subtitle + footer overlay), stitches them with crossfade/slide transitions, and muxes
voiceover + side-chain-ducked music. Output: `out_dir/<out_prefix>-<lang>.mp4`.
**This is slow on the first run** (TTS + ~2 clip renders per scene per language) —
run it in the background if it risks the tool timeout. Every artifact is cached in
`tmp_dir` under a **content-hash filename** (voice+text for audio, image-bytes+
caption+duration+branding for clips, duration for music), so re-runs are
**surgically incremental**: edit one scene's text and ONLY that scene's audio is
regenerated; swap one image and ONLY that scene's clips re-encode; everything
untouched is reused as-is. A no-change re-run only re-stitches and re-muxes
(seconds, no API calls). Never delete `tmp_dir` between iterations.

### 5. Review + iterate
Extract frames to check layout/sync:
`ffmpeg -ss <t> -i out.mp4 -frames:v 1 frame.png`. Common tweaks: voice, `music_volume`,
`min_scene`, transitions in `transition()`, subtitle font size, logo size.

## Outputs
- **Per-language single-track MP4s** — `out_dir/<out_prefix>-<lang>.mp4`. This is the
  correct format for **Instagram Reels / WhatsApp status**: a single H.264+AAC MP4,
  ≤90 s. Deliver these for social posting.
- **Optional multi-audio MKV master** — set `"multi_audio": true` and the builder also
  writes `out_dir/<out_prefix>-multiaudio.mkv`: one selectable **audio track per
  language** plus **soft subtitle tracks**, in a single file. Great for archive /
  YouTube / VLC. **NOTE:** Instagram and WhatsApp do **NOT** support multi-audio or
  MKV — use the per-language MP4s for those; the MKV is only a master/archive copy.

## Layout (1080x1920)
Logo (top, white, ~y48) · product image 940px with Ken-Burns (y190) · subtitle pill
(y1250, wrapped, language font) · footer bar (y1772): cyan rule + contact line + grey
address. All persistent except the image + subtitle. The Ken-Burns stage is rendered
at `zoom_ss`× resolution (supersampled) so `zoompan` never shows jitter/shake — keep
that; don't drop the supersample.

## Gotchas learned
- **Gemini TTS daily quota.** `gemini-2.5-flash-preview-tts` free tier = **100
  requests / model / DAY** (a 429 `RESOURCE_EXHAUSTED` with `per_day` in the message;
  resets ~24 h later). The builder caches each voiceover at
  `<tmp_dir>/{lang}{i}_<hash>.wav` where the hash covers provider+model+voice+text —
  a cached clip is NEVER regenerated unless its text or voice changes, and a legacy
  index-named `{lang}{i}.wav` is adopted automatically on first run. Re-running
  after a quota reset generates only what is genuinely missing.
- **Durability: keep `tmp_dir` and `out_dir` PROJECT-LOCAL — never `/tmp`.** That
  resumability is only worth something if the files survive. `tmp_dir` holds hours of
  quota-limited TTS and slow renders; `/tmp` and `/var/tmp` are erased on reboot or
  power loss, so a crash there means paying the whole TTS/render cost again. All
  config paths resolve relative to the **config file's directory**, so a plain
  `".reel_build"` already lands inside the project — keep it that way. The builder
  warns loudly on stderr if either directory resolves under the system temp dir.
- ffmpeg captions use **Pillow overlays**, not `drawtext` (no libfreetype needed);
  `vibrato`/`tremolo` min freq = 0.1 Hz.
- Gemini TTS occasionally returns an empty response — always retry (6x) and sanitize
  odd punctuation (em-dash) that can trip it.
- Reels max 90 s; 60-75 s suits a spec-heavy product. Keep the hook in the first ~2 s.
- There is no MCP that posts to Instagram (the API needs a Meta Business app + hosted
  video) — deliver the `.mp4` for the user to upload; they can add trending audio
  in-app if they prefer over the baked bed.
- Music is auto-generated and original (license-safe for paid ads). Third-party "free"
  tracks (NCS etc.) usually require attribution and are not cleared for ads — avoid.

## Make a reel for a NEW product
Copy `config.example.json`, then change:
- `images_dir` — the folder holding this product's photos (and the `image` filenames
  in each scene point into it),
- the `company` block — `logo`, `contact_line`, `address`,
- `languages` — the language→bold-font-path map for your target languages,
- `voice` — the Gemini voice,
- the `scenes` array — one entry per scene: `image` plus a per-language `vo` (the
  spoken line); add an optional per-language `sub` when the on-screen caption should
  differ from the spoken words (e.g. show "hjLabs.in" but speak "hjLabs dot in").

Everything else (scene timing, transitions, ducked music, subtitle/footer layout,
optional MKV master) is automatic.

## Files in this skill
- `build_reel.py` — the config-driven builder (edit the layout/transitions here).
- `config.example.json` — a complete, runnable example (a bilingual EN+HI product reel).
