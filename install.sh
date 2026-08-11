#!/usr/bin/env bash
# Install the product-reel skill into Claude Code.
#
# Skills live in ~/.claude/skills/<name>/ and are picked up on the next start.
# This script copies the three files that make up the skill and then reports
# which prerequisites are missing, rather than failing silently at build time.

set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}/product-reel"

echo "installing product-reel -> $DEST"
mkdir -p "$DEST"

for f in SKILL.md build_reel.py config.example.json; do
  if [ ! -f "$SRC/$f" ]; then
    echo "  ERROR: $f missing from $SRC" >&2
    exit 1
  fi
  cp "$SRC/$f" "$DEST/$f"
  echo "  copied $f"
done

echo
echo "checking prerequisites"

miss=0

if command -v ffmpeg >/dev/null 2>&1; then
  have=0
  for filt in xfade zoompan overlay sidechaincompress; do
    if ffmpeg -hide_banner -filters 2>/dev/null | grep -qE "[A-Z.]+ +$filt +"; then
      have=$((have + 1))
    else
      echo "  MISSING ffmpeg filter: $filt"
      miss=1
    fi
  done
  [ "$have" -eq 4 ] && echo "  ok      ffmpeg with all 4 required filters"
else
  echo "  MISSING ffmpeg — see the README for a no-root static build"
  miss=1
fi

PY="${PYTHON:-python3}"
if command -v "$PY" >/dev/null 2>&1; then
  echo "  ok      $PY ($($PY -c 'import sys;print(".".join(map(str,sys.version_info[:3])))'))"
  "$PY" -c "import PIL" 2>/dev/null \
    && echo "  ok      Pillow" \
    || { echo "  MISSING Pillow    -> $PY -m pip install --user Pillow"; miss=1; }
  "$PY" -c "import google.genai" 2>/dev/null \
    && echo "  ok      google-genai (Gemini TTS)" \
    || echo "  note    google-genai not installed — fine if you use tts_provider: openai"
else
  echo "  MISSING python3"
  miss=1
fi

# A bold Latin font is the minimum for English subtitles.
if fc-list 2>/dev/null | grep -qi 'DejaVuSans-Bold'; then
  echo "  ok      DejaVuSans-Bold (Latin subtitles)"
else
  echo "  note    DejaVuSans-Bold not found — set your own bold font path in config languages{}"
fi

echo
if [ "$miss" -eq 0 ]; then
  echo "done. restart Claude Code, then ask it to make a product reel."
else
  echo "installed, but some prerequisites are missing (see above)."
fi
echo "standalone use:  $PY $DEST/build_reel.py your-config.json"
