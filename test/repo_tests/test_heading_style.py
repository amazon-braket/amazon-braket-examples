"""Enforce sentence-case notebook headings (see PR #901).

Heading conventions:
  * Sentence case: only the first word of the heading is capitalized.
  * The first word after a colon separator is capitalized.
  * Proper nouns, acronyms, and code identifiers are preserved.
  * No trailing colon.

Reliability strategy
--------------------
Rather than trying to enumerate every proper noun, a word is only flagged
when it is plain "Titlecase" (leading capital, lowercase remainder) *and* is
not one of the following, which are detected automatically or via a small
allowlist:
  * the first content word of the heading or of a colon-separated segment,
  * an all-caps acronym (``QAOA``, ``VQE``, ``SV1``, ...),
  * an identifier with an internal capital (``PennyLane``, ``IonQ``,
    ``OpenQASM``, ``GPi2``, ``MinimumEigenOptimizer``),
  * a known proper noun from :data:`PROPER_NOUNS` /
    :data:`PROPER_PHRASES`.

Because acronyms and CamelCase identifiers are auto-detected, only ordinary
Titlecase words get flagged, which keeps false positives low.

Run as a script to list violations::

    python test/repo_tests/test_heading_style.py [examples_dir]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Titlecase proper nouns that must stay capitalized mid-heading.
PROPER_NOUNS = {
    # Brands / products / tools
    "Amazon",
    "Braket",
    "AWS",
    "Qiskit",
    "Mitiq",
    "Docker",
    "Python",
    "Jupyter",
    "Aquila",
    "Rigetti",
    "Cepheus",
    "Garnet",
    "Forte",
    "Enterprise",
    "QuEra",
    "NVIDIA",
    # Product feature name (PR #901 decision): "Hybrid Job(s)"
    "Hybrid",
    "Job",
    "Jobs",
    # Physics / math eponyms (people)
    "Hamiltonian",
    "Rydberg",
    "Ising",
    "Pauli",
    "Bell",
    "Rabi",
    "Richardson",
    "Grover",
    "Simon",
    "Hartree",
    "Fock",
    "Jordan",
    "Wigner",
    "Hayden",
    "Preskill",
    "Hadamard",
    "Alice",
    "Bob",
    "Rz",
    "Trotter",
    "Heisenberg",
    "Fourier",
    "Kraus",
    "Born",
    "Schroedinger",
    "Schrodinger",
    "Lindblad",
    "Bloch",
    "Toffoli",
    "Clifford",
    "Majorana",
    "Coulomb",
    "Hilbert",
    # Misc
    "GPi",  # gate name that is otherwise Titlecase-looking
}

# Multi-word proper-noun phrases (e.g. NVIDIA product names, PR #901 commit
# 4508d06). Removed from the heading before word-level analysis.
PROPER_PHRASES = [
    "CUDA-Q Applications Hub",
    "CUDA-Q Academic",
]

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
# Spans removed before word analysis (content preserved elsewhere).
LATEX_RE = re.compile(r"\$[^$]*\$")
CODE_RE = re.compile(r"`[^`]*`")
HTML_RE = re.compile(r"<[^>]+>")
MDLINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")  # keep link text, drop target
NONASCII_RE = re.compile(r"[^\x00-\x7F]+")  # e.g. warning emoji
_STRIP = "(),.;:!?\"'&/[]{}"


def _clean(text: str) -> str:
    """Remove non-prose spans so only natural-language words remain."""
    for phrase in PROPER_PHRASES:
        text = text.replace(phrase, " ")
    text = MDLINK_RE.sub(r"\1", text)
    text = LATEX_RE.sub(" ", text)
    text = CODE_RE.sub(" ", text)
    text = HTML_RE.sub(" ", text)
    text = NONASCII_RE.sub(" ", text)
    return text


def _word_is_ok(word: str) -> bool:
    """Return True if a non-initial heading word is acceptable as-is."""
    core = word.strip(_STRIP)
    core = re.sub(r"['\u2019]s$", "", core)  # drop possessive: Grover's -> Grover
    if not core:
        return True
    if not core[0].isupper():
        return True  # lowercase word -> fine in sentence case
    if core in PROPER_NOUNS:
        return True
    if core.upper() == core:
        return True  # all-caps acronym (QAOA, VQE, SV1, H2)
    if any(c.isupper() for c in core[1:]):
        return True  # internal capital -> identifier/brand (PennyLane, IonQ)
    return any(c.isdigit() for c in core)  # allow tokens with a digit (e.g. 3D)


def _is_bracket_tag(token: str) -> bool:
    """True for parenthetical/bracketed asides like '[optional]' or '(VQE)'."""
    return bool(re.fullmatch(r"[\[(].*[\])]", token))


def check_heading(text: str) -> list[str]:
    """Return a list of style-violation messages for a single heading."""
    problems = []
    if text.strip().endswith(":"):
        problems.append("trailing colon")

    offending: list[str] = []
    for segment in _clean(text).split(":"):
        seen_content = False
        for token in segment.split():
            is_tag = _is_bracket_tag(token)
            segment_start = not seen_content
            for part in re.split(r"[-/]", token):
                if not any(ch.isalpha() for ch in part):
                    continue
                # The first content word of a segment may be capitalized;
                # bracketed asides do not consume that slot.
                if not segment_start and not _word_is_ok(part):
                    offending.append(part.strip(_STRIP))
            if any(ch.isalpha() for ch in token) and not is_tag:
                seen_content = True

    if offending:
        problems.append("non-sentence-case word(s): " + ", ".join(dict.fromkeys(offending)))
    return problems


def iter_headings(nb_path: Path):
    """Yield each markdown heading string in a notebook (skips code fences)."""
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        src = cell.get("source", [])
        text = "".join(src) if isinstance(src, list) else src
        in_fence = False
        for line in text.splitlines():
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if not in_fence and (m := HEADING_RE.match(line)):
                yield m.group(2)


def find_violations(examples_dir: Path) -> list[tuple[Path, str, list[str]]]:
    """Return (notebook, heading, problems) for every non-conforming heading."""
    violations = []
    for nb in sorted(examples_dir.rglob("*.ipynb")):
        if ".ipynb_checkpoints" in str(nb):
            continue
        violations.extend(
            (nb, heading, problems)
            for heading in iter_headings(nb)
            if (problems := check_heading(heading))
        )
    return violations


def test_heading_style():
    """All notebook headings should follow the sentence-case convention."""
    examples_dir = Path(__file__).parent.parent.parent.resolve() / "examples"
    violations = find_violations(examples_dir)
    report = "\n".join(
        f"  {nb.relative_to(examples_dir.parent)}: {heading!r} -> {'; '.join(p)}"
        for nb, heading, p in violations
    )
    assert not violations, (
        f"{len(violations)} notebook heading(s) are not in sentence case "
        f"(see PR #901 conventions):\n{report}"
    )


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples")
    found = find_violations(root)
    for nb, heading, problems in found:
        print(f"{nb}\n    {heading!r}\n    -> {'; '.join(problems)}")
    print(f"\n{len(found)} heading(s) flagged")
    sys.exit(1 if found else 0)
