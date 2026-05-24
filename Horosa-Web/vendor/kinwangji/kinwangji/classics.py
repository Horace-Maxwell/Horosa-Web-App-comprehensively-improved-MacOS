# -*- coding: utf-8 -*-
"""
Utility for loading and browsing the three classical texts bundled with
the **kinwangji** package.

The Markdown files live under ``kinwangji/data/classics/`` and are produced
from the original TXT sources in ``examples/``.

Texts included
--------------
* **皇極經世書** — Shao Yong (宋), the core classic.
* **皇極經世心易發微** — Yang Tiren (明), practical divination methods.
* **皇極經世觀物外篇衍義** — Zhang Xingcheng (宋), commentary on 觀物外篇.
"""

from __future__ import annotations

import os
import re
from typing import Dict, List

_BASE: str = os.path.abspath(os.path.dirname(__file__))
_CLASSICS_DIR: str = os.path.join(_BASE, "data", "classics")

# Mapping of short keys to file names
CLASSICS: Dict[str, Dict[str, str]] = {
    "huangji_jingshi_shu": {
        "file": "huangji_jingshi_shu.md",
        "title": "皇極經世書",
        "author": "（宋）邵雍",
        "description": "邵雍原著，包含觀物篇、元會運世等內容。",
    },
    "xinyi_fawei": {
        "file": "xinyi_fawei.md",
        "title": "皇極經世心易發微",
        "author": "（明）楊體仁（野厓）",
        "description": "實用發揮，著重起卦法、體用、占例、聲音說、納甲、卜筮等應用。",
    },
    "guanwu_yanyi": {
        "file": "guanwu_yanyi.md",
        "title": "皇極經世觀物外篇衍義",
        "author": "（宋）張行成",
        "description": "對《皇極經世》觀物外篇的衍義與註解。",
    },
}


def list_classics() -> List[Dict[str, str]]:
    """Return metadata for every bundled classic text.

    Each dict contains ``key``, ``title``, ``author``, and ``description``.
    """
    return [
        {"key": k, **{f: v[f] for f in ("title", "author", "description")}}
        for k, v in CLASSICS.items()
    ]


def load_classic(key: str) -> str:
    """Return the full Markdown content for the classic identified by *key*.

    Parameters
    ----------
    key : str
        One of ``"huangji_jingshi_shu"``, ``"xinyi_fawei"``,
        ``"guanwu_yanyi"``.

    Raises
    ------
    KeyError
        If *key* is not recognised.
    FileNotFoundError
        If the underlying Markdown file is missing.
    """
    if key not in CLASSICS:
        raise KeyError(
            f"Unknown classic key {key!r}. "
            f"Choose from: {', '.join(CLASSICS)}"
        )
    path = os.path.join(_CLASSICS_DIR, CLASSICS[key]["file"])
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def get_sections(key: str) -> List[Dict[str, str]]:
    """Parse the Markdown for *key* and return a list of section dicts.

    Each dict has:
    * ``level`` (int) — heading level (2 for ``##``, 3 for ``###``).
    * ``title`` (str) — heading text.
    * ``content`` (str) — body text under that heading (may be empty).
    """
    text = load_classic(key)
    sections: List[Dict[str, str]] = []
    current_title = ""
    current_level = 0
    buf: List[str] = []

    for line in text.split("\n"):
        m = re.match(r"^(#{2,3})\s+(.*)", line)
        if m:
            # Flush previous section
            if current_title:
                sections.append(
                    {
                        "level": current_level,
                        "title": current_title,
                        "content": "\n".join(buf).strip(),
                    }
                )
            current_level = len(m.group(1))
            current_title = m.group(2).strip()
            buf = []
        else:
            buf.append(line)

    # Flush last section
    if current_title:
        sections.append(
            {
                "level": current_level,
                "title": current_title,
                "content": "\n".join(buf).strip(),
            }
        )

    return sections
