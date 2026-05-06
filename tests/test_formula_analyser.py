"""
Tests for homeric_formula_analyser.py

Run with:  pytest tests/ -v
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from homeric_formula_analyser import (
    find_mentions,
    extract_context,
    find_epithets,
    analyse,
)


class TestFindMentions:
    def test_detects_achilles(self):
        line = {"num": "1", "text": "a)xilleu/s poda/rkhs di=os"}
        assert any(m.character == "Achilles" for m in find_mentions(line))

    def test_detects_hector(self):
        line = {"num": "2", "text": "e(/ktwr koruqai/olos prose/fh"}
        assert any(m.character == "Hector" for m in find_mentions(line))

    def test_one_mention_per_character_per_line(self):
        # Two different Achilles forms on same line
        line = {"num": "3", "text": "*)axilleu/s a)xilh=os fight"}
        result = [m for m in find_mentions(line) if m.character == "Achilles"]
        assert len(result) == 1

    def test_empty_line(self):
        assert find_mentions({"num": "4", "text": ""}) == []

    def test_no_false_positives(self):
        line = {"num": "5", "text": "kai me e)/fh o( h(/rws"}
        assert find_mentions(line) == []

    def test_multiple_characters_same_line(self):
        line = {"num": "6", "text": "a)xilleu/s kai e(/ktwr ma/xontai"}
        chars = {m.character for m in find_mentions(line)}
        assert "Achilles" in chars
        assert "Hector" in chars

    def test_captures_line_num(self):
        line = {"num": "99", "text": "a)xilleu/s"}
        m = next(m for m in find_mentions(line) if m.character == "Achilles")
        assert m.line_num == "99"


class TestExtractContext:
    def test_window_around_match(self):
        line = "alpha beta a)xilleu/s delta epsilon zeta"
        ctx = extract_context(line, "a)xilleu/s", window=2)
        assert "beta" in ctx and "delta" in ctx

    def test_start_of_line_no_crash(self):
        line = "a)xilleu/s beta gamma delta"
        ctx = extract_context(line, "a)xilleu/s", window=3)
        assert "a)xilleu/s" in ctx

    def test_end_of_line_no_crash(self):
        line = "alpha beta gamma a)xilleu/s"
        ctx = extract_context(line, "a)xilleu/s", window=3)
        assert "a)xilleu/s" in ctx

    def test_no_match_returns_full_line(self):
        line = "alpha beta gamma"
        assert extract_context(line, "NOTFOUND", window=2) == line


class TestFindEpithets:
    def test_detects_swift_footed(self):
        assert "poda/rkhs" in find_epithets("a)xilleu/s poda/rkhs di=os")

    def test_detects_helmet_glancing(self):
        assert "koruqai/olos" in find_epithets("e(/ktwr koruqai/olos e)/fh")

    def test_empty_returns_empty(self):
        assert find_epithets("") == []

    def test_multiple_epithets(self):
        found = find_epithets("poda/rkhs di=os kai diogenh/s")
        assert len(found) >= 2


class TestAnalyse:
    LINES = [
        {"num": "1", "text": "a)xilleu/s poda/rkhs di=os prose/fh"},
        {"num": "2", "text": "e(/ktwr koruqai/olos a)mei/beto"},
        {"num": "3", "text": "a)xilleu/s e)/fh"},
        {"num": "4", "text": "kai me e)/fh"},   # no character
    ]

    def test_mention_count(self):
        assert analyse(self.LINES)["total_mentions"] == 3

    def test_epithet_tracked(self):
        assert analyse(self.LINES)["epithet_frequency"].get("poda/rkhs", 0) >= 1

    def test_line_numbers_tracked(self):
        result = analyse(self.LINES)
        assert "1" in result["character_line_numbers"]["Achilles"]

    def test_empty_corpus(self):
        assert analyse([])["total_mentions"] == 0