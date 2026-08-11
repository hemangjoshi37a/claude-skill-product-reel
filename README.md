# product-reel — a Claude Code skill

Turn a folder of product photos plus a spec sheet into a polished **9:16 Instagram Reel**
(1080×1920, ≤90 s) with brand logo, Ken-Burns motion, transitions, per-language subtitles,
a synced AI voiceover, a persistent contact footer, and a side-chain-ducked music bed.

Built for [Claude Code](https://claude.com/claude-code), but `build_reel.py` is a plain
config-driven Python script — you can run it standalone without Claude at all.

```
photos + spec list  ─►  scene script  ─►  TTS voiceover  ─►  ffmpeg assembly  ─►  reel-en.mp4
```

## What you get

- **1080×1920 H.264 + AAC MP4**, one per language — the format Instagram Reels and WhatsApp Status want
- **Ken-Burns motion** rendered on a supersampled stage, so the zoom never jitters
- **Per-language subtitles** burned in with the correct script font (Latin, Devanagari, …)
- **AI voiceover** timed per scene, with the scene stretched to fit its own line
- **Optional multi-audio MKV master** — one selectable audio track per language, for archive/YouTube
- **Auto-generated, copyright-free music bed** (or bring your own cleared track)

Captions are rendered with Pillow into transparent PNG overlays, **not** ffmpeg's `drawtext` —
so a static ffmpeg build without libfreetype works fine.

## Install

```bash
git clone https://github.com/USERNAME/claude-skill-product-reel.git
cd claude-skill-product-reel
./install.sh
```

`install.sh` copies the skill into `~/.claude/skills/product-reel/`. Restart Claude Code and
ask it to *"make a product reel for …"*, or invoke `/product-reel`.

Manual install is just a copy:

```bash
mkdir -p ~/.claude/skills/product-reel
cp SKILL.md build_reel.py config.example.json ~/.claude/skills/product-reel/
```

To use it **without** Claude Code, skip the install and run the builder directly:

```bash
python3 build_reel.py my-config.json
```

## Prerequisites

| Need | Why | Check |
|---|---|---|
| **ffmpeg** with `xfade`, `overlay`, `zoompan`, `sidechaincompress` | assembly | `ffmpeg -filters \| grep xfade` |
| **Python 3.10+** with `Pillow` | caption overlays | `python3 -c "import PIL"` |
| `google-genai` **or** an OpenAI key | TTS voiceover | `python3 -c "import google.genai"` |
| A **bold font per language** | subtitles | `fc-list :lang=hi` |

No system ffmpeg? A static build needs no root:

```bash
curl -sSL -o ff.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
mkdir -p ffx && tar -xJf ff.tar.xz -C ffx --strip-components=1
cp ffx/ffmpeg ffx/ffprobe ~/.local/bin/ && export PATH="$HOME/.local/bin:$PATH"
```

## Quick start

1. Put your product photos in a folder (`images/`).
2. Copy `config.example.json` and edit: `out_prefix`, `images_dir`, the `company` block,
   `languages`, and the `scenes` array.
3. Drop your API key in the file named by `gemini_key_file` (or `openai_key_file`).
4. Build:

```bash
python3 build_reel.py my-config.json
```

Output lands in `out_dir/<out_prefix>-<lang>.mp4`.

The build is **slow** (TTS + two renders per scene per language) and **resumable** — it reuses
existing `.wav` and clip files, so re-running only does the missing work.

## Choosing a TTS provider

**Gemini** (default) — set `gemini_key_file`. Voices: `Puck` (upbeat), `Charon` (informative),
`Kore` (firm), `Aoede`/`Zephyr` (bright), `Sulafat` (warm).

**OpenAI** — set `tts_provider: "openai"` and `openai_key_file`. Voices include `alloy`, `ash`,
`coral`, `onyx`, `nova`, `verse`. You can also steer the delivery:

```json
{
  "tts_provider": "openai",
  "openai_key_file": ".tmp/openai_key",
  "voice": "coral",
  "tts_instructions": "Energetic, upbeat, confident. Punchy and fast-paced. Emphasise key numbers."
}
```

`tts_instructions` is the difference between a flat read-aloud and something that sounds like it
wants your attention. Use it.

## Writing a script that holds attention

- **Hook in the first 2 seconds.** Lead with the problem or the surprising number, never the brand.
- **One idea per line.** Each line is a scene, a subtitle, and a voiceover segment.
- **Aim for 3–4 seconds per visual.** 6+ seconds per image reads as a slideshow and viewers leave.
  More scenes with shorter lines beats fewer scenes with long ones.
- **Spell numbers out** so TTS reads them properly: `"zero point zero one millimeter"`, not `0.01mm`.
- Use `sub` when the caption should differ from the spoken words — show `acme.io`, speak `acme dot i-o`.

## Config reference

| Key | Meaning |
|---|---|
| `out_prefix` | output filename stem |
| `images_dir` / `out_dir` / `tmp_dir` | **project-local** paths, resolved relative to the config file |
| `gemini_key_file` / `openai_key_file` | path to a file containing just the API key |
| `tts_provider` | `"gemini"` (default) or `"openai"` |
| `voice` / `tts_instructions` | voice name; instructions are OpenAI-only |
| `languages` | `{lang: /path/to/Bold.ttf}` — one bold font per script |
| `company` | `logo`, `contact_line`, `address` for the persistent footer |
| `music` | `null` to auto-generate an original bed, or a path to your own cleared track |
| `music_volume` | bed level before ducking (lower is safer — see gotchas) |
| `multi_audio` | also write a multi-audio MKV master |
| `scenes[]` | `image` + per-language `vo`, optional per-language `sub` |

## Gotchas worth knowing

**Keep `tmp_dir` and `out_dir` project-local — never `/tmp`.** `tmp_dir` holds hours of
quota-limited TTS and slow renders. `/tmp` is wiped on reboot, and losing it means paying the
whole TTS cost again. The builder warns loudly if either resolves under the system temp dir.

**Gemini TTS free tier is 100 requests/model/day.** A 429 with `per_day` in the message means you
are done until it resets. The builder is resumable precisely because of this — re-run after the
reset and it only generates what is missing.

**Check the delivery format before you post.** The builder can emit audio at rates social
platforms handle badly, and the raw mix is quieter than the ~−14 LUFS platforms normalise to:

```bash
ffmpeg -i out.mp4 -c:v copy -c:a aac -ar 48000 -ac 2 -b:a 192k \
       -af loudnorm=I=-14:TP=-1.5:LRA=11 -movflags +faststart final.mp4
```

**If music drowns the voice, the bed is too loud — not the duck too weak.** Measure both:
`ffmpeg -i out.mp4 -af volumedetect -f null -`. You want the music sitting well below the voice
during speech. Lower `music_volume` first.

**Reels max out at 90 s.** 60–75 s suits a spec-heavy product.

**There is no API that posts to Instagram for you** — publishing needs a Meta Business app and a
hosted video. Deliver the MP4 and upload it by hand; you can swap in trending audio in-app.

## Layout

```
1080 × 1920
├── logo             top, white, y≈48
├── product image    940 px wide, Ken-Burns, y≈190
├── subtitle pill    y≈1250, wrapped, per-language font
└── footer bar       y≈1772 — accent rule + contact line + address
```

Everything except the image and subtitle persists across the whole reel.

## Repository layout

```
SKILL.md              the skill definition Claude Code reads
build_reel.py         the config-driven builder (edit layout/transitions here)
config.example.json   a complete bilingual EN+HI example
install.sh            copies the skill into ~/.claude/skills/
examples/             additional configs
```

## License

MIT — see [LICENSE](LICENSE). The generated music is original and license-safe for paid ads.
Third-party "free" tracks usually require attribution and are **not** cleared for advertising.
