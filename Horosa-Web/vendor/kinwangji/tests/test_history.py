"""Tests for kinwangji.history – historical dynasty/ruler data."""

import pytest
from kinwangji.history import load_history, history_for_year


class TestLoadHistory:
    """Tests for load_history()."""

    def test_returns_list(self):
        records = load_history()
        assert isinstance(records, list)

    def test_non_empty(self):
        records = load_history()
        assert len(records) > 0

    def test_record_keys(self):
        records = load_history()
        expected_keys = {"start_year", "duration", "dynasty", "title", "name", "era"}
        for rec in records:
            assert set(rec.keys()) == expected_keys

    def test_start_year_is_int(self):
        records = load_history()
        for rec in records:
            assert isinstance(rec["start_year"], int)

    def test_first_record(self):
        """First record should be the Xia dynasty (夏)."""
        rec = load_history()[0]
        assert rec["dynasty"] == "夏"


class TestHistoryForYear:
    """Tests for history_for_year()."""

    def test_known_year_tang(self):
        """Year 750 falls within the Tang dynasty (唐)."""
        records = history_for_year(750)
        dynasties = [r["dynasty"] for r in records]
        assert "唐" in dynasties

    def test_known_year_modern(self):
        """Year 2000 falls within modern China (當代)."""
        records = history_for_year(2000)
        dynasties = [r["dynasty"] for r in records]
        assert "當代" in dynasties

    def test_returns_list(self):
        records = history_for_year(1900)
        assert isinstance(records, list)

    def test_very_old_year(self):
        """Year -3000 should have no matching records."""
        records = history_for_year(-3000)
        assert records == []
