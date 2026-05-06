"""
Homeric Formula Deviation Detection Engine

Loads the formulae database and character mentions produced by Phase 1,
computes information-theoretic surprisal for every mention, and reports
the moments where Homer deviates most from expected formulaic patterns.

Usage:
    python deviation_detection_engine.py
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

HIGH_SURPRISAL_THRESHOLD: float = 3.0      # bits; P < 12.5 %
BARE_MENTION_DEVIATION_RATE: float = 0.30
RARE_FORMULA_THRESHOLD: float = 0.10
REPORT_TOP_N: int = 50

@dataclass
class FormulaPattern:
    pattern: str        # lower-cased for matching
    original: str
    formula_type: str
    position: str
    frequency: int
    semantic: str = ""


@dataclass
class MentionAnalysis:
    line_num: str
    character: str
    line: str
    mention_type: str           # "formulaic" | "bare_mention"
    probability: float
    surprisal: float            # bits; math.inf for P == 0
    is_deviation: bool
    detected_formulae: list[str] = field(default_factory=list)
    primary_formula: Optional[str] = None

# I/O

def _load_json(path: str | Path, label: str) -> Any:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Cannot find {label} at '{p}'.")
    try:
        with p.open(encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        raise ValueError(f"'{p}' is not valid JSON: {exc}") from exc


def load_formula_database(path: str | Path = "formulae_database.json") -> dict:
    return _load_json(path, "formulae database")


def load_mentions(path: str | Path = "homer_analysis.json") -> list[dict]:
    data = _load_json(path, "homer_analysis.json")
    mentions = data.get("all_mentions")
    if mentions is None:
        raise KeyError("Key 'all_mentions' missing. Re-run Phase 1.")
    return mentions

#core

def build_formula_patterns(database: dict) -> dict[str, list[FormulaPattern]]:
    patterns: dict[str, list[FormulaPattern]] = {}
    for character, data in database.items():
        char_patterns: list[FormulaPattern] = []
        for formula_type, formulae in data.get("formulae_by_type", {}).items():
            for formula in formulae:
                raw = formula.get("pattern", "")
                char_patterns.append(FormulaPattern(
                    pattern=raw.lower(),
                    original=raw,
                    formula_type=formula_type,
                    position=formula.get("position", ""),
                    frequency=formula.get("frequency", 0),
                    semantic=formula.get("semantic_category", ""),
                ))
        patterns[character] = char_patterns
    return patterns


def detect_formulae(
    mention: dict,
    formula_patterns: dict[str, list[FormulaPattern]],
) -> list[FormulaPattern]:
    line_lower = mention["line"].lower()
    return [
        fp for fp in formula_patterns.get(mention["character"], [])
        if fp.pattern in line_lower
    ]


def build_expectations(
    mentions: list[dict],
    formula_patterns: dict[str, list[FormulaPattern]],
) -> dict[str, dict]:
    """
    Estimate P(formula | character).

    Each formula is counted at most once per mention (set-based dedup),
    fixing the double-counting bug in the original version where a formula
    appearing twice on one line was counted twice.
    """
    by_character: dict[str, list[dict]] = defaultdict(list)
    for m in mentions:
        by_character[m["character"]].append(m)

    expectations: dict[str, dict] = {}
    for character, char_mentions in by_character.items():
        total = len(char_mentions)
        formula_counts: Counter[str] = Counter()

        for mention in char_mentions:
            seen: set[str] = set()
            for fp in detect_formulae(mention, formula_patterns):
                if fp.pattern not in seen:
                    formula_counts[fp.pattern] += 1
                    seen.add(fp.pattern)

        expectations[character] = {
            "total_mentions": total,
            "formula_counts": dict(formula_counts),
            "formula_probabilities": (
                {p: c / total for p, c in formula_counts.items()}
                if total > 0 else {}
            ),
        }
    return expectations


def surprisal(probability: float) -> float:
    """Information-theoretic surprisal: -log2(P). Returns inf for P <= 0."""
    if probability <= 0.0:
        return math.inf
    if probability >= 1.0:
        return 0.0
    return -math.log2(probability)


def score_mention(
    mention: dict,
    formula_patterns: dict[str, list[FormulaPattern]],
    expectations: dict[str, dict],
) -> Optional[MentionAnalysis]:
    character = mention["character"]
    exp = expectations.get(character)
    if exp is None:
        return None

    detected = detect_formulae(mention, formula_patterns)

    if not detected:
        total = exp["total_mentions"]
        bare_count = max(0, total - sum(exp["formula_counts"].values()))
        bare_prob = bare_count / total if total > 0 else 0.0
        return MentionAnalysis(
            line_num=mention["line_num"],
            character=character,
            line=mention["line"],
            mention_type="bare_mention",
            probability=bare_prob,
            surprisal=surprisal(bare_prob),
            is_deviation=bare_prob < BARE_MENTION_DEVIATION_RATE,
        )

    primary = max(detected, key=lambda fp: fp.frequency)
    prob = exp["formula_probabilities"].get(primary.pattern, 0.0)
    return MentionAnalysis(
        line_num=mention["line_num"],
        character=character,
        line=mention["line"],
        mention_type="formulaic",
        probability=prob,
        surprisal=surprisal(prob),
        is_deviation=prob < RARE_FORMULA_THRESHOLD,
        detected_formulae=[fp.original for fp in detected],
        primary_formula=primary.original,
    )


def score_all(
    mentions: list[dict],
    formula_patterns: dict[str, list[FormulaPattern]],
    expectations: dict[str, dict],
) -> list[MentionAnalysis]:
    return [
        a for m in mentions
        if (a := score_mention(m, formula_patterns, expectations)) is not None
    ]


def high_surprisal(
    analyses: list[MentionAnalysis],
    threshold: float = HIGH_SURPRISAL_THRESHOLD,
) -> list[MentionAnalysis]:
    flagged = [a for a in analyses if a.surprisal > threshold]
    flagged.sort(key=lambda a: a.surprisal, reverse=True)
    return flagged


# Output

def _fmt(s: float) -> str:
    return "inf" if math.isinf(s) else f"{s:.2f}"


def write_report(
    analyses: list[MentionAnalysis],
    flagged: list[MentionAnalysis],
    database: dict,
    path: str | Path = "deviation_report.txt",
) -> None:
    total = len(analyses)
    if total == 0:
        print("No analyses to report.", file=sys.stderr)
        return

    formulaic_n = sum(1 for a in analyses if a.mention_type == "formulaic")
    bare_n = total - formulaic_n
    deviation_n = sum(1 for a in analyses if a.is_deviation)
    sep = "=" * 80

    with Path(path).open("w", encoding="utf-8") as fh:
        fh.write(f"{sep}\nHOMERIC FORMULA DEVIATION ANALYSIS\n{sep}\n\n")
        fh.write(f"Total mentions   : {total}\n")
        fh.write(f"Formulaic        : {formulaic_n} ({formulaic_n/total*100:.1f}%)\n")
        fh.write(f"Bare             : {bare_n} ({bare_n/total*100:.1f}%)\n")
        fh.write(f"Flagged          : {deviation_n} ({deviation_n/total*100:.1f}%)\n\n")
        fh.write(f"{sep}\n")
        fh.write(f"HIGH-SURPRISAL MOMENTS (> {HIGH_SURPRISAL_THRESHOLD} bits, top {REPORT_TOP_N})\n")
        fh.write(f"{sep}\n\n")

        for i, a in enumerate(flagged[:REPORT_TOP_N], 1):
            fh.write(f"{i:>3}. Line {a.line_num}: {a.character}\n")
            fh.write(f"     Surprisal : {_fmt(a.surprisal)} bits\n")
            fh.write(f"     P(formula): {a.probability*100:.2f}%\n")
            if a.mention_type == "bare_mention":
                fh.write("     Type      : BARE MENTION\n")
            else:
                fh.write(f"     Formula   : {a.primary_formula}\n")
            fh.write(f"     Line      : {a.line}\n\n")

        fh.write(f"{sep}\nBY CHARACTER\n{sep}\n\n")
        for character in database:
            char = [a for a in analyses if a.character == character]
            if not char:
                continue
            devs = [a for a in char if a.is_deviation]
            top3 = sorted(char, key=lambda a: a.surprisal, reverse=True)[:3]
            fh.write(f"{character}:\n")
            fh.write(f"  Mentions   : {len(char)}\n")
            fh.write(f"  Deviations : {len(devs)} ({len(devs)/len(char)*100:.1f}%)\n")
            for a in top3:
                fh.write(f"    Line {a.line_num}: {_fmt(a.surprisal)} bits\n")
            fh.write("\n")

    print(f"Saved deviation_report.txt")


def write_json_export(
    analyses: list[MentionAnalysis],
    flagged: list[MentionAnalysis],
    path: str | Path = "deviation_analysis.json",
) -> None:
    def _s(v: float) -> Optional[float]:
        return None if math.isinf(v) else v   # null in JSON, not 999

    with Path(path).open("w", encoding="utf-8") as fh:
        json.dump({
            "all_analyses": [
                {
                    "line_num": a.line_num,
                    "character": a.character,
                    "line": a.line,
                    "type": a.mention_type,
                    "probability": a.probability,
                    "surprisal": _s(a.surprisal),
                    "is_deviation": a.is_deviation,
                    "detected_formulae": a.detected_formulae,
                    "primary_formula": a.primary_formula,
                }
                for a in analyses
            ],
            "high_surprisal_count": len(flagged),
            "high_surprisal_threshold_bits": HIGH_SURPRISAL_THRESHOLD,
        }, fh, ensure_ascii=False, indent=2)
    print(f"Saved deviation_analysis.json")


# Entry point

if __name__ == "__main__":
    print("Homeric Formula Deviation Engine\n" + "=" * 80)

    try:
        database = load_formula_database()
        mentions = load_mentions()
    except (FileNotFoundError, KeyError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(mentions)} mentions, {len(database)} characters")

    patterns = build_formula_patterns(database)
    expectations = build_expectations(mentions, patterns)
    analyses = score_all(mentions, patterns, expectations)
    flagged = high_surprisal(analyses)

    print(f"Found {len(flagged)} high-surprisal moments (> {HIGH_SURPRISAL_THRESHOLD} bits)\n")

    write_report(analyses, flagged, database)
    write_json_export(analyses, flagged)

    print("\n" + "=" * 80 + "\nDone.")