#!/usr/bin/env python3
"""Word-count checker for DOE ConnectWerx FY26 Fall pitch documents.

Enforces the pitch structure limits that are verifiable from public sources:
  - Narrative answers: N1 <= 100, N2 <= 200, N3 <= 200, N4 <= 200 words
    (MNSBIR summary of the FY26 Fall Pitch Development Guide, 2026-11-05),
    and a self-imposed project budget of <= 500 words across all four.
  - Short answer 1 (feasibility result) <= 25 words (Grant Engine, 2026-11-05).
Short answers 2-3 and the structured answers have caps that are only stated
in the Pitch Development Guide inside AMP; the script reports their counts
without failing them.

Both pitch heading styles are tracked: Topic 3 uses "### Narrative N" /
"### Short answer N" and Topic 22 uses "### A1."-"### A4." / "### B1."-
"### B3." with the word limits stated inline. Sections tracked but whose
stated cap differs from the public cap would be flagged here — Topic 22's
stated limits (A1 100, A2-A4 200, B1-B3 25) match the public mapping.
A changed count mapping belongs in this list and nowhere else.

Usage:
    python3 check_pitch_words.py [file.md ...]

With no arguments, checks every pitch-topic*.md next to this script.
Exits 1 if any enforced limit is exceeded.
"""

import re
import sys
from pathlib import Path

# (section-title regex, word cap, enforced). Two heading styles, one mapping:
# Topic 3 "Narrative N"/"Short answer N" and Topic 22 "A1."-"A4."/"B1."-"B3."
# both map to narrative 1-4, short answer 1-3.
SECTIONS = [
    (r"^###\s+Narrative 1\b|^###\s+A1\.", 100, True),
    (r"^###\s+Narrative 2\b|^###\s+A2\.", 200, True),
    (r"^###\s+Narrative 3\b|^###\s+A3\.", 200, True),
    (r"^###\s+Narrative 4\b|^###\s+A4\.", 200, True),
    (r"^###\s+Short answer 1\b|^###\s+B1\.", 25, True),
    (r"^###\s+Short answer 2\b|^###\s+B2\.", None, False),
    (r"^###\s+Short answer 3\b|^###\s+B3\.", None, False),
]

# Titles that count toward the across-all-four narrative budget.
NARRATIVE_TITLE = re.compile(r"^Narrative|^A\d\.")

NARRATIVE_TOTAL_CAP = 500
HEADING = re.compile(r"^(#{2,3})\s+(.*)$")


def count_words(text: str) -> int:
    return len(text.split())


def parse_sections(md: str) -> list[tuple[str, int]]:
    """Return (title, word_count) for each tracked section.

    Any heading (of any depth) closes the currently open section, so a
    tracked `###` section never swallows following `##` content.
    """
    lines = md.splitlines()
    found: list[tuple[str, int]] = []
    current_title: str | None = None
    current_lines: list[str] = []

    def close() -> None:
        nonlocal current_title, current_lines
        if current_title is not None:
            found.append((current_title, count_words("\n".join(current_lines))))
        current_title = None
        current_lines = []

    for line in lines:
        m = HEADING.match(line)
        if m:
            title = m.group(2).strip()
            tracked = any(re.match(p, f"### {title}") for p, _c, _e in SECTIONS)
            close()
            if tracked:
                current_title = title
                current_lines = []
        elif current_title is not None:
            current_lines.append(line)
    close()
    return found


def check_file(path: Path) -> bool:
    md = path.read_text(encoding="utf-8")
    sections = parse_sections(md)
    ok = True
    narrative_total = 0
    print(f"\n{path}:")
    for title, words in sections:
        enforced_cap: int | None = None
        for pattern, cap, enforced in SECTIONS:
            if re.match(pattern, f"### {title}"):
                enforced_cap = cap if enforced else None
                break
        if enforced_cap is not None:
            status = "PASS" if words <= enforced_cap else "FAIL"
            if words > enforced_cap:
                ok = False
            if NARRATIVE_TITLE.match(title):
                narrative_total += words
            print(f"  [{status}] {title}: {words} words (cap {enforced_cap})")
        else:
            print(f"  [info] {title}: {words} words (cap not public; verify in AMP)")
    print(f"  [info] Narrative total: {narrative_total} words "
          f"(project budget {NARRATIVE_TOTAL_CAP})")
    if narrative_total > NARRATIVE_TOTAL_CAP:
        print(f"  [FAIL] Narrative total {narrative_total} exceeds "
              f"{NARRATIVE_TOTAL_CAP}")
        ok = False
    return ok


def main() -> int:
    args = sys.argv[1:]
    if args:
        files = [Path(a) for a in args]
    else:
        files = sorted(Path(__file__).parent.glob("pitch-topic*.md"))
    if not files:
        print("No pitch files found. Pass .md files as arguments.")
        return 1
    all_ok = all(check_file(f) for f in files)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
