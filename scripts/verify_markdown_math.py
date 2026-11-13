#!/usr/bin/env python3
"""Verify (and optionally fix) GitHub CommonMark + MathJax rules across Markdown files."""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
FILES = [
    "README.md",
    "THEORY.md",
    "AGENTS.md",
    "paper/nested-space-cosmology-2.md",
]


def _brace_inline_subscripts(text: str) -> str:
    """In inline $...$ spans with >=2 underscores, brace unbraced _token subscripts."""
    def repl_inline(match: re.Match[str]) -> str:
        inner = match.group(1)
        if inner.count("_") >= 2:
            inner = re.sub(r"_(\\[A-Za-z]+|[A-Za-z0-9])", r"_{\1}", inner)
        return f"${inner}$"

    # Protect $$ ... $$ display blocks first
    disp_blocks: list[str] = []

    def save_disp(m: re.Match[str]) -> str:
        disp_blocks.append(m.group(0))
        return f"@@DISP_BLOCK_{len(disp_blocks) - 1}@@"

    temp = re.sub(r"\$\$.*?\$\$", save_disp, text, flags=re.S)
    temp = re.sub(r"(?<!\$)\$(?!\$)([^\$\n]+?)\$(?!\$)", repl_inline, temp)
    for idx, blk in enumerate(disp_blocks):
        temp = temp.replace(f"@@DISP_BLOCK_{idx}@@", blk)
    return temp


def main() -> int:
    do_fix = "--fix" in sys.argv
    failed = False
    for rel in FILES:
        p = ROOT / rel
        text = p.read_text(encoding="utf-8")
        if do_fix and rel != "AGENTS.md":
            fixed = _brace_inline_subscripts(text)
            if fixed != text:
                p.write_text(fixed, encoding="utf-8", newline="\n")
                text = fixed
        disp_blocks = re.findall(r"\$\$(.*?)\$\$", text, flags=re.S)
        no_disp = re.sub(r"\$\$.*?\$\$", "", text, flags=re.S)
        inlines = re.findall(r"(?<!\$)\$(?!\$)([^\$\n]+?)\$(?!\$)", no_disp)
        all_math = inlines + disp_blocks
        stars = [m for m in all_math if "*" in m]
        percs = [m for m in all_math if "%" in m]
        thin = [m for m in all_math if r"\," in m]
        punct_u = [m for m in all_math if re.search(r"[\}\|\)\]\']_", m)]
        bad_u = [
            m
            for m in inlines
            if m.count("_") >= 2 and re.search(r"_[A-Za-z0-9\\]", m)
        ]
        disp_ops = re.findall(r"\\operatorname", text)
        link_math = re.findall(r"\[[^\]]*\$[^\]]*\]\([^\)]+\)", text)
        print(
            f"{rel}: inline={len(inlines)}, disp={len(disp_blocks)}, *={len(stars)}, "
            f"%={len(percs)}, thin={len(thin)}, punct_={len(punct_u)}, bad_={len(bad_u)}, "
            f"op={len(disp_ops)}, link_math={len(link_math)}"
        )
        if stars or percs or thin or punct_u or bad_u or disp_ops or link_math:
            failed = True
            for label, items in [
                ("stars", stars),
                ("percs", percs),
                ("thin", thin),
                ("punct_u", punct_u),
                ("bad_u", bad_u),
                ("disp_ops", disp_ops),
                ("link_math", link_math),
            ]:
                if items:
                    print(f"  {label}: {items}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
