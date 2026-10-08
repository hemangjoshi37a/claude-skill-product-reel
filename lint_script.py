"""Check a reel config against the story rules BEFORE you spend a render on it.

Every rule here came out of measuring 33 shorts from a 931k-subscriber channel in
this exact niche (@newtechindia, 797 sentences). They are in SKILL.md as prose;
this is the same thing as an exit code, because a rule nobody can check is a rule
everybody forgets on the line they are actually writing.

    python3 lint_script.py promo/my-reel.json
    python3 lint_script.py promo/my-reel.json --lang hi

Nothing here is fatal — it prints findings and exits 1 if any are hard. A reel
that breaks a rule on purpose is fine; a reel that breaks one by accident is the
thing this catches.
"""

from __future__ import annotations

import json
import re
import statistics as st
import sys

#: Sentence-opening connectives. The measured corpus opens 19% of its sentences
#: with one of these — `लेकिन` (but) far ahead of the rest.
CONNECTIVES = {
    "en": {
        "but", "so", "because", "if", "although", "though", "even", "which",
        "and", "or", "then", "now", "once", "until", "unless", "otherwise",
        "still", "yet", "while", "since", "after", "before", "instead", "that",
    },
    "hi": {
        "लेकिन", "मगर", "तो", "क्योंकि", "इसलिए", "अगर", "यदि", "फिर", "अब",
        "हालांकि", "वरना", "बल्कि", "जबकि", "जब", "या", "और", "यानी", "जिससे",
        "ताकि", "बावजूद", "चाहे",
    },
}

#: A hook that is a complete, self-contained sentence hands the thumb a clean
#: exit at the first full stop. These are the openers that cannot finish on
#: their own — the main clause has not arrived yet.
UNFINISHED_OPENERS = {
    "en": ("if ", "when ", "whenever ", "the ", "every time", "most ", "a lot of",
           "everyone who", "anyone who", "you know that", "imagine", "ever "),
    "hi": ("अगर", "यदि", "जब", "जब भी", "जिन", "जो", "बहुत से", "बहुत सारे",
           "क्या आप", "कभी", "चाहे"),
}

SENT_SPLIT = re.compile(r"[।?!]|(?<=[a-z0-9\"'])\.(?:\s|$)")


def sentences(text: str):
    return [s.strip() for s in SENT_SPLIT.split(text or "") if s and s.strip()]


def check(cfg: dict, lang: str) -> list[tuple[str, str]]:
    """Return [(severity, message)]. severity is 'hard' or 'soft'."""
    out: list[tuple[str, str]] = []
    lines = [sc["vo"][lang] for sc in cfg["scenes"] if lang in sc.get("vo", {})]
    if not lines:
        return [("hard", f"no {lang} voiceover in this config")]

    conn = CONNECTIVES.get(lang, CONNECTIVES["en"])
    words = lambda s: re.findall(r"[^\s]+", s)

    # ---- 1. is it one story, or a list? --------------------------------------
    opens = 0
    for ln in lines[1:]:                     # the hook is exempt; it starts things
        first = (words(ln) or [""])[0].lower().strip(",.—-")
        if first in conn:
            opens += 1
    ratio = opens / max(1, len(lines) - 1)
    if ratio < 0.18:
        out.append(("hard", f"only {opens}/{len(lines)-1} lines ({ratio:.0%}) open with a "
                            f"connective — the corpus runs 19%. This will play as a list "
                            f"of true sentences rather than one story."))
    elif ratio > 0.55:
        # The overcorrection, and it is just as bad. The corpus opens 19% of its
        # sentences with a connective; the other 80% connect from INSIDE — a
        # mid-sentence "so", or a pronoun pointing at the line before. Start
        # every line with And/So/But and the device stops being invisible and
        # becomes a tic, which is its own kind of list.
        out.append(("hard", f"{opens}/{len(lines)-1} lines ({ratio:.0%}) open with a "
                            f"connective — the corpus runs 19%. Above about half it reads "
                            f"as a verbal tic; carry the rest from inside the sentence or "
                            f"with a pronoun pointing back."))
    else:
        out.append(("ok", f"{opens}/{len(lines)-1} lines ({ratio:.0%}) open with a connective"))

    anywhere = sum(1 for ln in lines if any(
        re.search(r"(^|\s)" + re.escape(c) + r"(\s|$)", ln, re.I) for c in conn))
    if anywhere / len(lines) < 0.35:
        out.append(("soft", f"only {anywhere}/{len(lines)} lines contain a connective "
                            f"anywhere — the corpus runs 43%."))

    # ---- 2. sentence length ---------------------------------------------------
    lens = [len(words(s)) for ln in lines for s in sentences(ln)] or [0]
    med = st.median(lens)
    if med > 16:
        out.append(("hard", f"median sentence is {med:.0f} words — the corpus runs 12. "
                            f"Long lines cannot build momentum."))
    elif med > 14:
        out.append(("soft", f"median sentence {med:.0f} words; aim for about 12."))
    elif med < 7:
        # The opposite failure, and it is easy to fall into after being told to
        # cut: a run of four-word fragments is staccato, not momentum. Nothing
        # can carry a clause from one line to the next if no line HAS a clause,
        # so the script reads as joined sentences however many connectives are
        # bolted on.
        out.append(("hard", f"median sentence is only {med:.0f} words — the corpus runs 12. "
                            f"Fragments this short cannot hold a connective, so the script "
                            f"reads as a list no matter what you put at the start of a line."))
    else:
        out.append(("ok", f"median sentence {med:.0f} words"))

    # ---- 3. the hook ----------------------------------------------------------
    hook = lines[0].strip()
    low = hook.lower()
    unfinished = any(low.startswith(o) for o in UNFINISHED_OPENERS.get(lang, ()))
    if not unfinished and len(sentences(hook)) >= 1 and len(words(hook)) < 14:
        out.append(("soft", f"hook is a finishable sentence: {hook!r}. The corpus opens on "
                            f"a clause that cannot stand alone (if… / whenever… / the people "
                            f"who… / most people think…), so there is nowhere to stop."))
    else:
        out.append(("ok", "hook does not offer a clean stopping point"))

    # ---- 4. orphan lines ------------------------------------------------------
    # A line that neither opens with a connective nor refers back with a pronoun
    # could be moved anywhere in the script and nobody would notice.
    BACKREF = {"en": ("it", "that", "this", "they", "them", "yours", "there", "those"),
               "hi": ("वो", "ये", "उस", "इस", "वही", "यही", "उन", "इन", "आपका", "आपकी")}
    refs = BACKREF.get(lang, BACKREF["en"])
    orphans = []
    for i, ln in enumerate(lines[1:], 1):
        w = [x.lower().strip(",.—-") for x in words(ln)]
        if not w:
            continue
        if w[0] in conn or any(r in w[:4] for r in refs):
            continue
        orphans.append((i, ln))
    if len(orphans) > len(lines) * 0.55:
        out.append(("soft", f"{len(orphans)}/{len(lines)-1} lines attach to nothing before "
                            f"them. First: [{orphans[0][0]}] {orphans[0][1]!r}"))

    # ---- 5. the close ---------------------------------------------------------
    close = lines[-1]
    if len(sentences(close)) > 2:
        out.append(("soft", "the close is more than two sentences — the corpus closes on a "
                            "single instruction."))
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    cfg = json.load(open(sys.argv[1], encoding="utf-8"))
    langs = ([sys.argv[sys.argv.index("--lang") + 1]] if "--lang" in sys.argv
             else list(cfg.get("languages", {}) or {"en": None}))

    hard = 0
    for lang in langs:
        print(f"\n=== {lang} ===")
        for sev, msg in check(cfg, lang):
            mark = {"ok": "  ok ", "soft": "  ~~ ", "hard": "  !! "}[sev]
            print(mark + msg)
            hard += sev == "hard"
    print()
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
