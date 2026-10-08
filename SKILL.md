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

> **Order matters: SCRIPT FIRST, VISUALS SECOND.** Do not start from the folder of
> screenshots/photos and narrate whatever happens to be in it — that reliably produces
> a feature list ("here is X, here is Y, here is Z") with no reason to keep watching.
> Write the story, decide what each beat must SHOW, and only then capture or generate
> the visual that serves it. If a beat has no visual, capture one. If a visual serves
> no beat, cut it.

### 0. Write the story FIRST — before you look at a single image

A reel is not a spec sheet read aloud. It is a **60-75 second story with four movements**.
Draft it as prose in the user's language of record, get it right, and only then map visuals.

**HOOK (0-3 s, 1-2 lines).** One provocation that makes scrolling feel like a loss.
State a *tension the viewer already feels*, not a product fact. Never open with the
product name — nobody is looking for it yet.
- Weak: "Meet the hjLabs AI Playground." (a fact, no tension)
- Strong: "Every AI app you use sends your work to someone else's computer."

**INTRO (3-12 s, 2-3 lines).** Sharpen the tension, then turn. Name the cost the viewer
is paying today (money, privacy, setup, waiting), then pivot on a single word — *but*,
*meanwhile*, *except* — to the thing they already own that makes it unnecessary. The
product is REVEALED here as the answer, not announced at the top.

**MAIN (12-55 s, 8-12 lines).** The substance, ordered as a **journey, not a catalogue**.
Follow one throughline the viewer can ride: first-use → the payoff moment → the breadth
→ the proof. Every claim must be visible in its own frame (see "Narration must match the
frame"). Put the single most striking visual at roughly the 60% mark, not at the end —
that is where retention decides.

**OUTRO + CTA (55-75 s, 2-3 lines).** Resolve the tension you opened with, in a sentence
that only makes sense *because* of everything shown. Then one unambiguous action and the
URL. Never introduce a new feature in the outro.

Checks before you write a line of config:
- Read the script aloud with no images. Does it still hold together as an argument? If it
  only makes sense as captions for pictures, it is not a script yet.
- Does line 1 work with the sound off, as a caption alone?
- Could any two MAIN lines swap without anyone noticing? If yes, there is no throughline
  — reorder until there is.
- Does the outro pay off the hook? If the hook is about privacy, the outro must land on
  privacy.

### It must be ONE STORY, not a list of true sentences

This is the failure that survives every other fix. You can have a good hook, real
frames, tight pacing and a beat, and the thing still plays as a slideshow with a
narrator — because each line *starts over*. The lines are all true, all about the
same product, and connected by nothing.

Reverse-engineered from 33 shorts on a 931k-subscriber Indian machines channel
(`@newtechindia`, 797 sentences of transcript). Measured, not guessed:

| | measured |
|---|---|
| median sentence | **12 words** (mean 15) |
| sentences **opening** with a connective | **19%** — `लेकिन` (but) is #1, then `तो` (so), `अब` (now), `फिर` (then), `यदि` (if) |
| sentences **containing** a connective | **43%** |
| delivery | **≈223 wpm** |

So the rule, and it is checkable:

- **About one line in five OPENS with a connective — and not many more than
  that.** Two in five should CONTAIN one. Both bounds matter: under the floor it
  reads as a list, and over about half it reads as a tic, because every line
  starting with And/So/But is just as mechanical as none of them doing it. The
  other eighty per cent connect from INSIDE the sentence, or with a pronoun
  pointing at the line before. *but · so · because · if · which is why · even though ·
  although · and that is before · until · once · now · then · otherwise.*
  In Hindi: *लेकिन · तो · क्योंकि · इसलिए · अगर/यदि · फिर · अब · हालांकि · वरना ·
  बल्कि · जबकि.*
- **Every line after the first must attach backwards** — by a connective, or by a
  pronoun that refers to the previous line ("that", "it", "yours"). If a line
  could be moved anywhere in the script without anyone noticing, it is a bullet
  point, not a sentence in a story.
- **Test it by deletion.** Remove any middle line. If the two either side still
  join up perfectly, the line was doing nothing and the script is a list.

Before and after, same facts:

    ✗  Your coiler, per minute. Your wire, per kilo.
       Your oven, per load.
       Set them once.
       Now every spring carries your price.

    ✓  So don't — publish your rates instead.
       Your coiler per minute, your wire per kilo, your oven per load.
       Set them once, and you never price a spring again,
       because every spring anyone designs now comes out at YOUR number.

### The hook must not be a finishable sentence

The single most transferable trick in that corpus. Almost every top-performing
short opens on a **subordinate clause** — the main clause has not arrived yet, so
there is no grammatical place to stop:

- *"If you're STILL topping water into that old tubular battery…"* (if)
- *"Whenever we press a shirt with a normal steam iron, then…"* (whenever…then)
- *"The parents who taught us to climb stairs holding their fingers…"* (who)
- *"A lot of people think a roti machine has to be huge —"* (a belief, about to be contradicted)
- *"Your long-standing complaint was that roti machines are too big. Just look at this one."* (their complaint, named, then answered)

None of them opens with the product. Every one opens with **the viewer's own
situation, a named character, or a belief to break**. A hook that is a complete
sentence about a product gives the thumb a clean exit on the first full stop.

### Close on ONE imperative

Every close in the corpus is a single instruction — "click below", "see the full
demo". Not a summary, not three benefits, not a new feature. One thing to do.

Craft rules: one idea per line; median twelve words; spell numbers and units out
for TTS ("ten point seven megabytes a second", "नब्बे से चार सौ अस्सी डिग्री");
write each language natively rather than translating literally. Around 16-18
short lines ≈ 50-60 s at reel pace.

**Lint before you render.** `python3 lint_script.py <config.json>` checks the
connective ratio, the median line length, whether the hook is a finishable
sentence and whether any line is orphaned. It is cheap; a render is not.

### 1. Map each beat to the visual it needs — then capture/generate exactly those

Write the beat list first, then go and get the frames. For each line, name the ONE thing
the frame must prove. Only now open the camera, the browser, or the image generator.

**The frame PROVES; the voice MEANS. Never read the screen aloud.**

This is the rule that separates a reel somebody watches from a reel somebody
scrolls, and it has two halves that are easy to confuse.

*Half one — the voice may not contradict the frame.* The viewer is reading the
screen while listening. If the voice says "twenty-one tasks" while the frame
shows a chat window, the mismatch is felt as sloppiness even when it is not
consciously noticed. So a figure you speak must be a figure that is **true of
that frame** — not one from a spec sheet, and not one from a different screen.

*Half two, and the one everybody gets wrong — a number that is ON the frame must
not be RECITED from it.* The screen already said it. Saying it again is the
narrator reading the viewer their own screen, which is the single most boring
thing a voiceover can do, and it is what turns a reel into a specification read
aloud. The number is the evidence; the voice's job is the **consequence**.

    frame: "1.40 N/mm   spring rate"
    ✗  "One point four newtons per millimetre. Safe to twenty nine point nine."
    ✓  "Push it a millimetre, it pushes back — and it tells you where it gives up."

    frame: "39%  ·  34 of 88 MB"
    ✗  "Thirty nine percent. Thirty four of eighty eight megabytes."
    ✓  "That is the whole model coming down — on your line, not a datacentre's."

    frame: the shop comparison table
    ✗  "Each shop's own rate, its own queue, its own dispatch date."
    ✓  "The cheapest one is three days out. That trade-off is the whole point."

Rules that follow, and they are testable:
- **Read the script with the pictures covered.** If a line only makes sense as a
  caption for something, it is a caption, not narration. Cut it or rewrite it.
- **At most two spoken figures in the whole reel**, and each must be doing work a
  sentence could not do without it. Everything else stays on screen where it
  belongs.
- **No line may be a list of nouns.** "Wire, bore, coils, pitch" is a form, read
  out. "Four numbers and it is a part" is a sentence.
- **Say the thing the viewer would say.** Write the line you would say to a
  friend who asked what this does. Then delete the first half of it.
- If a frame cannot carry the claim, either change the claim or get a better frame.
- Reject any frame that shows an error, a warning banner, an empty state or a placeholder
  the narration does not acknowledge. Keep the rejects in a `_rejected/` folder with a
  one-line reason each, so a later pass does not silently reintroduce them.

**Framing for 1080x1920.** The image band is ~940 px wide and ~1060 px tall, so aim for a
source aspect near **0.89**. Full-page screenshots (~0.56) and desktop grabs (~1.60) both
shrink to illegibility; crop tall shots to the region that carries the message and
letterbox wide ones onto the brand ground instead of cropping the content out.

### 2. (Optional) Generate spec-rich images from the REAL product photos
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

### Pacing: the reel defaults, and why they are what they are

`"pace"` is `"reel"` by default. The old numbers are still there as
`"pace": "calm"` for a product film, but do not reach for them on anything going
into a feed. What changed, and the measurement that forced it:

A 13-scene cut built on the old defaults was **12% silence**, arriving as a
~0.7 s hole between every single line (0.32 s `vo_pad` + a 0.5 s dissolve, paid
on every cut). A viewer reads a hole like that as the video buffering, and
buffering is a scroll. `"reel"` sets `vo_pad` 0.10, `vo_min_gap` 0.06 and a
0.12 s dissolve — which lands as a cut, because a cut says "and another thing"
where a dissolve says "time passed", and between two lines of one argument the
first is the right sentence.

Three more things the builder now does for you, so the config does not have to:

- **No still holds longer than `max_hold` (2.6 s).** A scene is as long as its
  line takes to say, often six or eight seconds, and parking one frame there
  means the viewer finished looking after two and spent the rest waiting. Where
  a scene has one image the builder re-stages that same image as two to four
  shots with different moves. You still get a better reel by giving it real
  variety — see below — but it can no longer produce a slideshow.
- **Every shot drifts.** A centred zoom is what people mean by "it looks like a
  slideshow": nothing moves relative to anything else, so the eye reads a still
  that is slowly growing. Shots now pan as well as zoom, and the direction walks
  round the compass so six moves in a row do not feel like one.
- **Zoom head-room is 1.16**, up from 1.06. At six percent the move was below
  the threshold of noticing, which is the worst place to be: it costs the render
  and buys nothing.

What is still yours to get right: a scene's `"image"` takes a **list** as well as
a single filename, and two genuinely different frames always beat one frame
shown twice. Vary the subject across scenes — product, close-up crop, UI page,
in-action shot — so consecutive scenes never show near-identical pictures. A
deliberate long hold is fine ONLY for the final CTA card.

### 3. Turn the script into scenes
One script line = one scene = one subtitle + one voiceover segment. By now the story is
already written (step 0) and the visuals already chosen (step 1); this step is only
transcription into the `scenes` array. If you find yourself *writing* copy here, go back
to step 0 — narration invented next to a config field is how feature lists happen.

### 4. Fill the config
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

### 5. Build
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

### 6. Review + iterate
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
Logo (top, white, ~y48) · **product image 1080x1216 at y172** with Ken-Burns ·
subtitle pill (wrapped, language font, anchored just above the footer) · footer
bar (y1772): cyan rule + contact line + grey address. All persistent except the
image + subtitle.

The band used to be 1080x1000 at y200, which left a ~450 px slab of empty ground
between the picture and the subtitle — a third of the frame doing nothing, in
the format where screen area is scarcest. 1216 tall is also **0.888**, the source
aspect this skill asks you to shoot, so a correctly-framed capture now FILLS the
band instead of letterboxing inside it. `stage_w/h/x/y` override it.

Two things not to break:
- The Ken-Burns stage is rendered at `zoom_ss`× resolution (supersampled) so
  `zoompan` never shows jitter/shake. Keep the supersample.
- **`zoom_headroom` is not `maxzoom`.** The stage is built with a little slack
  (1.06) so a move does not instantly overscan; `maxzoom` (1.16) is then free to
  be lively. They were one number, and that had a nasty property — turning the
  zoom up to make the reel feel alive SHRANK the picture, because the image was
  pre-scaled by 1/maxzoom to guarantee no crop ever. Fourteen percent off every
  frame, permanently, to avoid a crop that happens only at the extreme of a move
  and that nobody has ever noticed.

## Gotchas learned
- **Silence is trimmed wherever a clip comes from.** The Gemini path always
  trimmed inline; nothing else did, so a clip from the OpenAI provider or one
  dropped in pre-rendered under the legacy name kept whatever head and tail its
  synthesiser added — and that silence is paid TWICE, once as the hole you hear
  and again as scene length, because every scene is timed to its own voiceover.
  `_adopt_legacy()` now trims on the way in.
- **`company.logo` resolves against the SHELL CWD**, not the config file's
  directory the way `images_dir`/`out_dir`/`tmp_dir` do — and a logo that does
  not resolve is skipped **silently**, so the reel just quietly has no brand on
  it. Either give it an absolute path or run the builder from the directory the
  path is relative to.
- **A logo asset with a filled plate comes out as a white blob.** `white_logo()`
  fills whatever alpha it finds with solid white, so a mark on a coloured
  rounded rectangle — exactly right on a PDF or a share card — loses its inner
  detail entirely. The reel wants the mark as STROKES on transparency.
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
