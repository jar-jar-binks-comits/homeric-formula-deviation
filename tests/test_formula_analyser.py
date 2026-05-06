"""
Tests for homeric_formula_analyser.py

Run with:  pytest tests/ -v
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from homeric_formula_analyser import (
    find_character_mentions,
    extract_context_window,
    find_epithets_in_context,
    analyze_text,
    KNOWN_EPITHETS,
)


class TestFindCharacterMentions:
    def test_detects_achilles(self):
        line = {"num": "1", "text": "a)xilleu/s poda/rkhs di=os"}
        assert any(m["character"] == "Achilles" for m in find_character_mentions(line))

    def test_detects_hector(self):
        line = {"num": "2", "text": "e(/ktwr koruqai/olos prose/fh"}
        assert any(m["character"] == "Hector" for m in find_character_mentions(line))

    def test_one_mention_per_character_per_line(self):
        # Two different Achilles forms on the same line — should only count once
        line = {"num": "3", "text": "*)axilleu/s a)xilh=os fight"}
        result = [m for m in find_character_mentions(line) if m["character"] == "Achilles"]
        assert len(result) == 1

    def test_empty_line_returns_empty(self):
        assert find_character_mentions({"num": "4", "text": ""}) == []

    def test_no_false_positives(self):
        line = {"num": "5", "text": "kai me e)/fh o( h(/rws"}
        assert find_character_mentions(line) == []

    def test_multiple_characters_same_line(self):
        line = {"num": "6", "text": "a)xilleu/s kai e(/ktwr ma/xontai"}
        chars = {m["character"] for m in find_character_mentions(line)}
        assert "Achilles" in chars
        assert "Hector" in chars

    def test_captures_line_num(self):
        line = {"num": "99", "text": "a)xilleu/s"}
        m = next(m for m in find_character_mentions(line) if m["character"] == "Achilles")
        assert m["line_num"] == "99"

    def test_captures_line_text(self):
        text = "a)xilleu/s poda/rkhs"
        line = {"num": "1", "text": text}
        m = next(m for m in find_character_mentions(line) if m["character"] == "Achilles")
        assert m["line"] == text


class TestExtractContextWindow:
    def test_window_around_match(self):
        line = "alpha beta a)xilleu/s delta epsilon zeta"
        ctx = extract_context_window(line, "a)xilleu/s", window=2)
        assert "beta" in ctx and "delta" in ctx

    def test_start_of_line_no_crash(self):
        line = "a)xilleu/s beta gamma delta"
        ctx = extract_context_window(line, "a)xilleu/s", window=3)
        assert "a)xilleu/s" in ctx

    def test_end_of_line_no_crash(self):
        line = "alpha beta gamma a)xilleu/s"
        ctx = extract_context_window(line, "a)xilleu/s", window=3)
        assert "a)xilleu/s" in ctx

    def test_no_match_returns_full_line(self):
        line = "alpha beta gamma"
        assert extract_context_window(line, "NOTFOUND", window=2) == line


class TestFindEpithetsInContext:
    def test_detects_swift_footed(self):
        found = find_epithets_in_context("a)xilleu/s poda/rkhs di=os", KNOWN_EPITHETS)
        assert "poda/rkhs" in found

    def test_detects_helmet_glancing(self):
        found = find_epithets_in_context("e(/ktwr koruqai/olos e)/fh", KNOWN_EPITHETS)
        assert "koruqai/olos" in found

    def test_empty_context_returns_empty(self):
        assert find_epithets_in_context("", KNOWN_EPITHETS) == []

    def test_no_false_positives(self):
        found = find_epithets_in_context("kai me e)/fh prosfw/nhs", KNOWN_EPITHETS)
        assert found == []

    def test_multiple_epithets_detected(self):
        found = find_epithets_in_context("poda/rkhs di=os kai diogenh/s", KNOWN_EPITHETS)
        assert len(found) >= 2


class TestAnalyzeText:
    LINES = [
        {"num": "1", "text": "a)xilleu/s poda/rkhs di=os prose/fh"},
        {"num": "2", "text": "e(/ktwr koruqai/olos a)mei/beto"},
        {"num": "3", "text": "a)xilleu/s e)/fh"},
        {"num": "4", "text": "kai me e)/fh"},    # no character
    ]

    def test_mention_count(self):
        mentions, *_ = analyze_text(self.LINES)
        assert len(mentions) == 3

    def test_epithet_tracked(self):
        _, epithet_freq, *_ = analyze_text(self.LINES)
        assert epithet_freq.get("poda/rkhs", 0) >= 1

    def test_line_numbers_tracked(self):
        _, _, _, char_lines = analyze_text(self.LINES)
        assert "1" in char_lines["Achilles"]

    def test_empty_corpus(self):
        mentions, *_ = analyze_text([])
        assert len(mentions) == 0