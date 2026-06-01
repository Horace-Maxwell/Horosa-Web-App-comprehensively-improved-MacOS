# -*- coding: utf-8 -*-
"""Tests for the kinwangji.classics module."""

import pytest

from kinwangji.classics import list_classics, load_classic, get_sections, CLASSICS


class TestListClassics:
    def test_returns_three_entries(self):
        result = list_classics()
        assert len(result) == 3

    def test_each_entry_has_required_keys(self):
        for item in list_classics():
            assert "key" in item
            assert "title" in item
            assert "author" in item
            assert "description" in item


class TestLoadClassic:
    @pytest.mark.parametrize("key", list(CLASSICS.keys()))
    def test_load_returns_nonempty_string(self, key):
        text = load_classic(key)
        assert isinstance(text, str)
        assert len(text) > 100

    @pytest.mark.parametrize("key", list(CLASSICS.keys()))
    def test_load_starts_with_markdown_heading(self, key):
        text = load_classic(key)
        assert text.startswith("# ")

    def test_unknown_key_raises(self):
        with pytest.raises(KeyError):
            load_classic("nonexistent")


class TestGetSections:
    @pytest.mark.parametrize("key", list(CLASSICS.keys()))
    def test_returns_nonempty_list(self, key):
        sections = get_sections(key)
        assert isinstance(sections, list)
        assert len(sections) > 0

    @pytest.mark.parametrize("key", list(CLASSICS.keys()))
    def test_section_has_required_fields(self, key):
        sections = get_sections(key)
        for sec in sections:
            assert "level" in sec
            assert "title" in sec
            assert "content" in sec
            assert sec["level"] in (2, 3)

    def test_huangji_has_volumes(self):
        sections = get_sections("huangji_jingshi_shu")
        titles = [s["title"] for s in sections]
        assert any("皇极经世书卷" in t for t in titles)

    def test_xinyi_has_volumes(self):
        sections = get_sections("xinyi_fawei")
        titles = [s["title"] for s in sections]
        assert any("卷之" in t for t in titles)

    def test_guanwu_has_volumes(self):
        sections = get_sections("guanwu_yanyi")
        titles = [s["title"] for s in sections]
        assert any("卷" in t for t in titles)
