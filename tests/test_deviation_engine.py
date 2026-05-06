"""
Tests for deviation_detection_engine.py

Run with:  pytest tests/ -v
"""

import math
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from deviation_detection_engine import (
    FormulaPattern,
    build_formula_patterns,
    detect_formulae,
    build_expectations,
    surprisal,
    score_mention,
    high_surprisal,
    HIGH_SURPRISAL_THRESHOLD,
    RARE_FORMULA_THRESHOLD,
    BARE_MENTION_DEVIATION_RATE,
    MentionAnalysis,
)

# Shared test data

MINIMAL_DB = {
    "Achilles": {
        "formulae_by_type": {
            "epithet": [
                {"pattern": "poda/rkhs", "position": "post",
                 "frequency": 28, "semantic_category": "speed"},
                {"pattern": "di=os", "position": "post",
                 "frequency": 5, "semantic_category": "divine"},
            ]
        }
    }
}


def _mention(line: str, character: str = "Achilles", line_num: str = "1") -> dict:
    return {"character": character, "line": line, "line_num": line_num}


@pytest.fixture
def patterns():
    return build_formula_patterns(MINIMAL_DB)


@pytest.fixture
def expectations(patterns):
    mentions = [
        _mention("a)xilleu/s poda/rkhs di=os", line_num="1"),
        _mention("a)xilleu/s poda/rkhs", line_num="2"),
        _mention("a)xilleu/s poda/rkhs", line_num="3"),
        _mention("a)xilleu/s e)/fh bare", line_num="4"),
    ]
    return build_expectations(mentions, patterns)


# surprisal

class TestSurprisal:
    def test_zero_prob_is_inf(self):
        assert math.isinf(surprisal(0.0))

    def test_prob_one_is_zero(self):
        assert surprisal(1.0) == 0.0

    def test_half_is_one_bit(self):
        assert surprisal(0.5) == pytest.approx(1.0)

    def test_quarter_is_two_bits(self):
        assert surprisal(0.25) == pytest.approx(2.0)

    def test_never_negative(self):
        for p in [0.1, 0.5, 0.9, 1.0]:
            assert surprisal(p) >= 0.0

    def test_negative_input_treated_as_zero(self):
        assert math.isinf(surprisal(-0.5))


# build_formula_patterns

class TestBuildFormulaPatterns:
    def test_character_present(self, patterns):
        assert "Achilles" in patterns

    def test_patterns_are_lowercase(self, patterns):
        for fp in patterns["Achilles"]:
            assert fp.pattern == fp.pattern.lower()

    def test_original_case_preserved(self, patterns):
        originals = {fp.original for fp in patterns["Achilles"]}
        assert "poda/rkhs" in originals

    def test_frequency_preserved(self, patterns):
        freq_map = {fp.original: fp.frequency for fp in patterns["Achilles"]}
        assert freq_map["poda/rkhs"] == 28

    def test_empty_db(self):
        assert build_formula_patterns({}) == {}


# ---------------------------------------------------------------------------
# detect_formulae
# ---------------------------------------------------------------------------

class TestDetectFormulae:
    def test_detects_known_formula(self, patterns):
        m = _mention("a)xilleu/s poda/rkhs di=os")
        detected = {fp.original for fp in detect_formulae(m, patterns)}
        assert "poda/rkhs" in detected

    def test_bare_mention_returns_empty(self, patterns):
        m = _mention("a)xilleu/s e)/fh")
        assert detect_formulae(m, patterns) == []

    def test_unknown_character_returns_empty(self, patterns):
        m = _mention("e(/ktwr prose/fh", character="Hector")
        assert detect_formulae(m, patterns) == []


# build_expectations — the double-counting fix

class TestBuildExpectations:
    def test_formula_counted_once_even_if_twice_on_line(self, patterns):
        """Core regression test for the double-counting bug."""
        mentions = [_mention("poda/rkhs kai poda/rkhs a)xilleu/s", line_num="1")]
        exp = build_expectations(mentions, patterns)
        assert exp["Achilles"]["formula_counts"]["poda/rkhs"] == 1

    def test_total_mentions_correct(self, expectations):
        assert expectations["Achilles"]["total_mentions"] == 4

    def test_probabilities_in_range(self, expectations):
        for p in expectations["Achilles"]["formula_probabilities"].values():
            assert 0.0 <= p <= 1.0

    def test_bare_mention_not_counted_as_formula(self, patterns):
        mentions = [_mention("a)xilleu/s e)/fh")]
        exp = build_expectations(mentions, patterns)
        assert sum(exp["Achilles"]["formula_counts"].values()) == 0


# score_mention

class TestScoreMention:
    def test_bare_mention_type(self, patterns, expectations):
        m = _mention("a)xilleu/s e)/fh bare", line_num="4")
        result = score_mention(m, patterns, expectations)
        assert result.mention_type == "bare_mention"

    def test_formulaic_mention_type(self, patterns, expectations):
        m = _mention("a)xilleu/s poda/rkhs prose/fh")
        result = score_mention(m, patterns, expectations)
        assert result.mention_type == "formulaic"

    def test_primary_is_highest_frequency(self, patterns, expectations):
        # poda/rkhs (freq=28) beats di=os (freq=5)
        m = _mention("a)xilleu/s poda/rkhs di=os")
        result = score_mention(m, patterns, expectations)
        assert result.primary_formula == "poda/rkhs"

    def test_unknown_character_returns_none(self, patterns, expectations):
        m = _mention("e(/ktwr prose/fh", character="Hector")
        assert score_mention(m, patterns, expectations) is None

    def test_surprisal_non_negative(self, patterns, expectations):
        m = _mention("a)xilleu/s poda/rkhs")
        result = score_mention(m, patterns, expectations)
        assert result.surprisal >= 0.0


# high_surprisal

class TestHighSurprisal:
    def _a(self, s: float) -> MentionAnalysis:
        return MentionAnalysis(
            line_num="1", character="Achilles", line="",
            mention_type="formulaic", probability=0.1,
            surprisal=s, is_deviation=s > HIGH_SURPRISAL_THRESHOLD,
        )

    def test_filters_below_threshold(self):
        analyses = [self._a(s) for s in [1.0, 2.0, 4.0, 5.0]]
        assert len(high_surprisal(analyses)) == 2

    def test_sorted_descending(self):
        analyses = [self._a(s) for s in [5.0, 3.5, 4.0, 8.0]]
        vals = [a.surprisal for a in high_surprisal(analyses)]
        assert vals == sorted(vals, reverse=True)

    def test_empty_input(self):
        assert high_surprisal([]) == []