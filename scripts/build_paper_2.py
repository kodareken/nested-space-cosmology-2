#!/usr/bin/env python3
"""Render the canonical Paper II Markdown manuscript as a publication-form PDF."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from functools import lru_cache
import hashlib
import html
from io import BytesIO
import json
import os
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import unquote, urlsplit

REPOSITORY = Path(__file__).resolve().parents[1]
SOURCE = REPOSITORY / "paper" / "nested-space-cosmology-2.md"
OUTPUT = REPOSITORY / "paper" / "nested-space-cosmology-2.pdf"
METADATA = REPOSITORY / "paper" / "metadata.json"
BUILD_MANIFEST = REPOSITORY / "paper" / "build-manifest.json"
BUILD_DIRECTORY = REPOSITORY / "paper" / ".build"

IMAGE_LINK = re.compile(r"!\[([^\]]*)\]\((<[^>]+>|[^)]+)\)")

PDF_COMPRESSION_OPTIONS = {
    "numiterations": 1,
    "blocksplitting": True,
    "blocksplittinglast": False,
    "blocksplittingmax": 15,
}


@contextmanager
def deterministic_pdf_compression():
    """Scope a fixed compressor to ReportLab's page, font and image streams."""
    from reportlab.pdfbase import pdfdoc
    from zopfli.zlib import compress

    original = pdfdoc.zlib

    @lru_cache(maxsize=None)
    def encode(data: bytes) -> bytes:
        return compress(data, **PDF_COMPRESSION_OPTIONS)

    pdfdoc.zlib = SimpleNamespace(compress=encode, decompress=original.decompress)
    try:
        yield
    finally:
        pdfdoc.zlib = original
        encode.cache_clear()


def local_image_path(source: Path, target: str) -> Path:
    """Resolve manuscript assets locally; never fetch a figure during a build."""
    target = target.strip()
    if target.startswith("<"):
        target = target[1 : target.index(">")]
    else:
        target = re.sub(r'\s+[\"\'][^\"\']*[\"\']$', "", target)
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError("paper images must name a local repository file: " + target)
    path = (source.parent / unquote(target)).resolve()
    if not path.is_relative_to(REPOSITORY.resolve()) or not path.is_file():
        raise ValueError("missing or escaping paper image: " + target)
    return path


def scientific_build_inputs(source: Path) -> list[dict[str, str]]:
    """Authenticate the renderer and every dataset used by a manuscript figure."""
    paths = ["scripts/build_paper_2.py"]
    text = source.read_text(encoding="utf-8")
    for match in IMAGE_LINK.finditer(text):
        path = local_image_path(source, match.group(2))
        paths.append(path.relative_to(REPOSITORY).as_posix())
    for target in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", text):
        target = target.strip().strip("<>").split("#", 1)[0]
        if urlsplit(target).scheme or not target.endswith((".json", ".npz")):
            continue
        path = (source.parent / unquote(target)).resolve()
        if not path.is_relative_to(REPOSITORY.resolve()) or not path.is_file():
            raise ValueError("missing or escaping manuscript evidence: " + target)
        paths.append(path.relative_to(REPOSITORY).as_posix())
    return [
        {
            "path": path,
            "sha256": hashlib.sha256((REPOSITORY / path).read_bytes()).hexdigest(),
        }
        for path in sorted(set(paths))
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument(
        "--clean",
        action="store_true",
        help="move the generated PDF to a recoverable local build archive",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="build twice without touching tracked files and require identical bytes",
    )
    return parser.parse_args()


def clean_output(path: Path) -> int:
    if not path.exists():
        print(f"nothing to clean: {path}")
        return 0
    trashit = shutil.which("trashit")
    if trashit:
        import subprocess

        subprocess.run([trashit, str(path)], check=True)
        print(f"moved generated PDF to the system Trash: {path}")
        return 0
    recovery = BUILD_DIRECTORY / "removed"
    recovery.mkdir(parents=True, exist_ok=True)
    destination = recovery / f"{path.name}.{time.time_ns()}"
    path.replace(destination)
    print(f"moved generated PDF to recoverable build storage: {destination}")
    return 0


def load_metadata() -> dict[str, object]:
    value = json.loads(METADATA.read_text(encoding="utf-8"))
    required = {
        "author",
        "date",
        "date_iso",
        "project",
        "source_date_epoch",
        "status",
        "subtitle",
        "title",
        "version",
    }
    missing = sorted(required - set(value))
    if missing:
        raise RuntimeError(f"paper metadata is missing: {', '.join(missing)}")
    return value


def build_pdf(
    source: Path, output: Path, metadata: dict[str, object]
) -> tuple[int, int, str]:
    try:
        import matplotlib
        import reportlab
        import zopfli
        from matplotlib.font_manager import FontProperties
        from matplotlib.mathtext import math_to_image
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import (
            BaseDocTemplate,
            Frame,
            Image,
            KeepTogether,
            ListFlowable,
            ListItem,
            NextPageTemplate,
            PageBreak,
            PageTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
            XPreformatted,
        )
        from reportlab.platypus.tableofcontents import TableOfContents
    except ImportError as exc:
        raise SystemExit(
            "Pinned paper dependencies are required. Use python scripts/run_python.py"
        ) from exc

    for name, required, observed in (
        ("Matplotlib", "3.11.2", getattr(matplotlib, "__version__", "unknown")),
        ("ReportLab", "4.4.9", getattr(reportlab, "Version", "unknown")),
        ("Zopfli", "0.4.3", getattr(zopfli, "__version__", "unknown")),
    ):
        if observed != required:
            raise SystemExit(
                f"{name} {required} is required for the canonical PDF; observed {observed}"
            )

    page_width, page_height = A4
    left_margin = 19 * mm
    right_margin = 19 * mm
    top_margin = 21 * mm
    bottom_margin = 18 * mm
    body_width = page_width - left_margin - right_margin

    font_directory = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
    regular_font, bold_font, italic_font, bold_italic_font = (
        font_directory / "DejaVuSans.ttf",
        font_directory / "DejaVuSans-Bold.ttf",
        font_directory / "DejaVuSans-Oblique.ttf",
        font_directory / "DejaVuSans-BoldOblique.ttf",
    )
    if not all(
        path.is_file()
        for path in (regular_font, bold_font, italic_font, bold_italic_font)
    ):
        raise RuntimeError("Matplotlib's bundled DejaVu Sans fonts are absent")
    mono_font = font_directory / "DejaVuSansMono.ttf"
    if not mono_font.is_file():
        raise RuntimeError("Matplotlib's bundled DejaVu Sans Mono font is absent")
    pdfmetrics.registerFont(TTFont("RHRegular", regular_font))
    pdfmetrics.registerFont(TTFont("RHBold", bold_font))
    pdfmetrics.registerFont(TTFont("RHItalic", italic_font))
    pdfmetrics.registerFont(TTFont("RHBoldItalic", bold_italic_font))
    pdfmetrics.registerFont(TTFont("RHMono", mono_font))
    pdfmetrics.registerFontFamily(
        "RHRegular",
        normal="RHRegular",
        bold="RHBold",
        italic="RHItalic",
        boldItalic="RHBoldItalic",
    )

    ink = colors.HexColor("#122033")
    navy = colors.HexColor("#0A1730")
    blue = colors.HexColor("#2357A6")
    cyan = colors.HexColor("#64C9E8")
    muted = colors.HexColor("#536274")
    pale = colors.HexColor("#EFF4F8")
    line = colors.HexColor("#D3DCE6")
    white = colors.white

    sample = getSampleStyleSheet()
    styles: dict[str, ParagraphStyle] = {
        "Body": ParagraphStyle(
            "RHBody",
            parent=sample["BodyText"],
            fontName="RHRegular",
            fontSize=9.25,
            leading=13.35,
            textColor=ink,
            alignment=TA_JUSTIFY,
            spaceAfter=6.5,
            allowWidows=0,
            allowOrphans=0,
        ),
        "Heading1": ParagraphStyle(
            "RHHeading1",
            parent=sample["Heading1"],
            fontName="RHBold",
            fontSize=19,
            leading=23,
            textColor=navy,
            spaceBefore=14,
            spaceAfter=8,
            keepWithNext=True,
        ),
        "Heading2": ParagraphStyle(
            "RHHeading2",
            parent=sample["Heading2"],
            fontName="RHBold",
            fontSize=13.0,
            leading=16.2,
            textColor=blue,
            spaceBefore=10,
            spaceAfter=5,
            keepWithNext=True,
        ),
        "Heading3": ParagraphStyle(
            "RHHeading3",
            parent=sample["Heading3"],
            fontName="RHBold",
            fontSize=10.5,
            leading=13.5,
            textColor=ink,
            spaceBefore=8,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "Bullet": ParagraphStyle(
            "RHBullet",
            parent=sample["BodyText"],
            fontName="RHRegular",
            fontSize=9.1,
            leading=12.8,
            textColor=ink,
            leftIndent=13,
            firstLineIndent=0,
            spaceAfter=3.5,
        ),
        "Numbered": ParagraphStyle(
            "RHNumbered",
            parent=sample["BodyText"],
            fontName="RHRegular",
            fontSize=8.9,
            leading=12.4,
            textColor=ink,
            leftIndent=30,
            firstLineIndent=0,
            bulletIndent=0,
            bulletFontName="RHBold",
            bulletFontSize=8.2,
            bulletColor=blue,
            spaceAfter=4.2,
        ),
        "Quote": ParagraphStyle(
            "RHQuote",
            parent=sample["BodyText"],
            fontName="RHItalic",
            fontSize=9.3,
            leading=13.4,
            textColor=ink,
            spaceAfter=0,
        ),
        "Code": ParagraphStyle(
            "RHCode",
            parent=sample["Code"],
            fontName="RHMono",
            fontSize=7.6,
            leading=10.2,
            textColor=colors.HexColor("#EAF2FA"),
            leftIndent=4,
            rightIndent=4,
            spaceAfter=0,
        ),
        "Table": ParagraphStyle(
            "RHTable",
            parent=sample["BodyText"],
            fontName="RHRegular",
            fontSize=7.3,
            leading=9.8,
            textColor=ink,
        ),
        "TableHead": ParagraphStyle(
            "RHTableHead",
            parent=sample["BodyText"],
            fontName="RHBold",
            fontSize=7.4,
            leading=9.9,
            textColor=white,
        ),
        "CoverTitle": ParagraphStyle(
            "RHCoverTitle",
            parent=sample["Title"],
            fontName="RHBold",
            fontSize=33,
            leading=38,
            textColor=white,
            alignment=TA_LEFT,
            spaceAfter=12,
        ),
        "CoverDeck": ParagraphStyle(
            "RHCoverDeck",
            parent=sample["Heading2"],
            fontName="RHRegular",
            fontSize=16.5,
            leading=22,
            textColor=cyan,
            alignment=TA_LEFT,
            spaceAfter=22,
        ),
        "CoverSubtitle": ParagraphStyle(
            "RHCoverSubtitle",
            parent=sample["BodyText"],
            fontName="RHItalic",
            fontSize=13,
            leading=18,
            textColor=white,
            alignment=TA_LEFT,
            spaceAfter=18,
        ),
        "CoverMeta": ParagraphStyle(
            "RHCoverMeta",
            parent=sample["BodyText"],
            fontName="RHRegular",
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#B8C8DB"),
            alignment=TA_LEFT,
        ),
        "TocTitle": ParagraphStyle(
            "RHTocTitle",
            parent=sample["Heading1"],
            fontName="RHBold",
            fontSize=24,
            leading=28,
            textColor=navy,
            spaceAfter=18,
        ),
    }

    token_pattern = re.compile(r"@@RH_TOKEN_(\d+)@@")

    greek = {
        "Pi": "Π",
        "Psi": "Ψ",
        "psi": "ψ",
        "xi": "ξ",
        "Xi": "Ξ",
        "Sigma": "Σ",
        "nu": "ν",
        "chi": "χ",
        "alpha": "α",
        "beta": "β",
        "gamma": "γ",
        "Gamma": "Γ",
        "delta": "δ",
        "Delta": "Δ",
        "epsilon": "ε",
        "varepsilon": "ε",
        "eta": "η",
        "theta": "θ",
        "Theta": "Θ",
        "kappa": "κ",
        "Lambda": "Λ",
        "lambda": "λ",
        "mu": "μ",
        "Omega": "Ω",
        "omega": "ω",
        "Phi": "Φ",
        "phi": "φ",
        "varphi": "φ",
        "pi": "π",
        "rho": "ρ",
        "sigma": "σ",
        "tau": "τ",
        "zeta": "ζ",
    }

    def latex_to_plain(
        value: str, script_open: str = "(", script_close: str = ")"
    ) -> str:
        """Make short inline formulae legible in ReportLab paragraphs."""
        value = value.replace(r"\{", "\ufffb").replace(r"\}", "\ufffc")
        value = value.replace(r"\%", "%").replace(r"\!", "").replace(r"\,", " ")
        value = value.replace(r"\;", " ").replace(r"\quad", " ")
        value = value.replace(r"\qquad", "  ").replace(r"\ ", " ")
        value = value.replace(r"\AA", "Å")
        value = value.replace(r"\dagger", "†").replace(r"\star", "⋆")
        value = (
            value.replace(r"\Longleftrightarrow", "⇔")
            .replace(r"\Longrightarrow", "⇒")
            .replace(r"\longrightarrow", "→")
            .replace(r"\leftarrow", "←")
            .replace(r"\leftrightarrow", "↔")
        )
        value = value.replace(r"\to", "→").replace(r"\mapsto", "↦")
        value = value.replace(r"\implies", "⇒").replace(r"\Rightarrow", "⇒")
        value = value.replace(r"\iff", "⇔").replace(r"\Leftrightarrow", "⇔")
        value = value.replace(r"\gg", "≫").replace(r"\ll", "≪")
        value = re.sub(r"\\(?:geq|ge)(?![A-Za-z])", "≥", value)
        value = re.sub(r"\\(?:leq|le)(?![A-Za-z])", "≤", value)
        value = re.sub(r"\\(?:neq|ne)(?![A-Za-z])", "≠", value)
        value = (
            value.replace(r"\approx", "≈")
            .replace(r"\simeq", "≃")
            .replace(r"\sim", "∼")
            .replace(r"\equiv", "≡")
        )
        value = value.replace(r"\propto", "∝")
        value = re.sub(r"\\in(?![A-Za-z])", "∈", value).replace(r"\times", "×")
        value = re.sub(r"\\int(?![A-Za-z])", "∫", value)
        value = re.sub(r"\\oint(?![A-Za-z])", "∮", value)
        value = re.sub(r"\\sum(?![A-Za-z])", "∑", value)
        value = re.sub(r"\\prod(?![A-Za-z])", "∏", value)
        value = value.replace(r"\ell", "ℓ").replace(r"\odot", "⊙")
        value = value.replace(r"\ddots", "⋱").replace(r"\cdots", "⋯")
        value = value.replace(r"\ldots", "…").replace(r"\dots", "…")
        value = value.replace(r"\otimes", "⊗").replace(r"\cdot", "·")
        value = value.replace(r"\partial", "∂").replace(r"\infty", "∞")
        value = value.replace(r"\nabla", "∇")
        value = value.replace(r"\hbar", "ℏ").replace(r"\pm", "±").replace(r"\mp", "∓")
        value = value.replace(r"\Box", "□").replace(r"\square", "□")
        value = value.replace(r"\parallel", "∥").replace(r"\perp", "⊥")
        value = value.replace(r"\|", "‖").replace(r"\Vert", "‖")
        value = (
            value.replace(r"\lvert", "|")
            .replace(r"\rvert", "|")
            .replace(r"\vert", "|")
        )
        value = (
            value.replace(r"^{\prime\prime}", "″")
            .replace(r"^{\prime}", "′")
            .replace(r"^\prime", "′")
            .replace(r"\prime", "′")
        )
        value = (
            value.replace(r"^{\circ}", "°")
            .replace(r"^\circ", "°")
            .replace(r"\circ", "∘")
        )
        value = re.sub(
            r"\\(log|ln|exp|cosh|sinh|tanh|cos|sin|tan|sec|csc|cot|arcsin|arccos|arctan|atanh|artanh|min|max|sup|inf|lim|det|Tr|diag|sgn)(?=\\[A-Za-z])",
            r"\1 ",
            value,
        )
        value = re.sub(
            r"\\(log|ln|exp|cosh|sinh|tanh|cos|sin|tan|sec|csc|cot|arcsin|arccos|arctan|atanh|artanh|min|max|sup|inf|lim|det|Tr|diag|sgn)(?![A-Za-z])",
            r"\1",
            value,
        )
        for name, symbol in greek.items():
            value = value.replace(f"\\{name}", symbol)
        value = value.replace(r"\bar\psi", "ψ̄")
        value = re.sub(r"\\rm(?![A-Za-z])\s*", "", value)
        for _ in range(4):
            for command in (
                "mathrm",
                "mathbf",
                "boldsymbol",
                "mathbb",
                "mathcal",
                "operatorname",
                "text",
            ):
                value = re.sub(rf"\\{command}\{{([^{{}}]+)\}}", r"\1", value)
                value = re.sub(rf"\\{command}\s+([A-Za-z])", r"\1", value)
            value = re.sub(
                r"\\(?:overline|bar)\{([^{}]+)\}",
                lambda match: match.group(1) + "\u0304",
                value,
            )
            value = re.sub(
                r"\\bar\s*([A-Za-zΑ-Ωα-ω])",
                lambda match: match.group(1) + "\u0304",
                value,
            )
            value = re.sub(
                r"\\ddot\{([^{}]+)\}",
                lambda match: match.group(1) + "\u0308",
                value,
            )
            value = re.sub(
                r"\\ddot\s*([A-Za-zΑ-Ωα-ω])",
                lambda match: match.group(1) + "\u0308",
                value,
            )
            value = re.sub(
                r"\\dot\{([^{}]+)\}",
                lambda match: match.group(1) + "\u0307",
                value,
            )
            value = re.sub(
                r"\\dot\s*([A-Za-zΑ-Ωα-ω])",
                lambda match: match.group(1) + "\u0307",
                value,
            )
            value = re.sub(
                r"\\(?:widetilde|tilde)\{([^{}]+)\}",
                lambda match: match.group(1) + "\u0303",
                value,
            )
            value = re.sub(
                r"\\(?:widetilde|tilde)\s*([A-Za-zΑ-Ωα-ω])",
                lambda match: match.group(1) + "\u0303",
                value,
            )
            value = re.sub(
                r"\\(?:widehat|hat)\{([^{}]+)\}",
                lambda match: match.group(1) + "\u0302",
                value,
            )
            value = re.sub(
                r"\\(?:widehat|hat)\s*([A-Za-zΑ-Ωα-ω])",
                lambda match: match.group(1) + "\u0302",
                value,
            )
            value = re.sub(
                r"\\sqrt\{([^{}]+)\}",
                lambda match: f"√({match.group(1)})"
                if re.search(r"[+\-\s]", match.group(1))
                else f"√{match.group(1)}",
                value,
            )
            value = re.sub(
                r"\\(?:frac|tfrac|dfrac)([0-9])([0-9])", r"(\1)/(\2)", value
            )
            value = re.sub(
                r"\\(?:frac|tfrac|dfrac)\{([^{}]+)\}\{([^{}]+)\}",
                r"(\1)/(\2)",
                value,
            )
            value = re.sub(
                r"\\binom\{([^{}]+)\}\{([^{}]+)\}", r"C(\1,\2)", value
            )
            value = re.sub(
                r"_\{([^{}]+)\}",
                lambda match: f"_{script_open}{match.group(1)}{script_close}",
                value,
            )
            value = re.sub(
                r"\^\{([^{}]+)\}",
                lambda match: f"^{script_open}{match.group(1)}{script_close}",
                value,
            )
        value = value.replace(r"\sqrt", "√")
        value = re.sub(
            r"\\(?:mathrm|mathbf|boldsymbol|mathbb|mathcal|operatorname|text)(?![A-Za-z])\s*",
            "",
            value,
        )
        value = value.replace("{", "").replace("}", "")
        value = value.replace("\ufffb", "{").replace("\ufffc", "}")
        value = value.replace(r"\left", "").replace(r"\right", "")
        value = value.replace(r"\langle", "⟨").replace(r"\rangle", "⟩")
        value = value.replace("--", "–")
        value = re.sub(r"\s+([_^])", r"\1", value)
        return re.sub(r"\s+", " ", value).strip()

    def inline_math_markup(value: str) -> str:
        converted = latex_to_plain(
            value, script_open="\ufff9", script_close="\ufffa"
        )
        if "\\" in converted:
            raise ValueError(
                f"untranslated inline LaTeX in PDF build: {value!r} -> {converted!r}"
            )
        plain = html.escape(converted, quote=False)

        def script(match: re.Match[str]) -> str:
            tag = "sub" if match.group(1) == "_" else "super"
            return f"<{tag}>{match.group(2)}</{tag}>"

        plain = re.sub(r"([_^])([\w*⋆†±+∥⊥°∘∞×-])", script, plain)
        while re.search(r"([_^])\ufff9([^\ufff9\ufffa]*)\ufffa", plain):
            plain = re.sub(r"([_^])\ufff9([^\ufff9\ufffa]*)\ufffa", script, plain)
        return plain

    def inline_markup(value: str, is_header: bool = False) -> str:
        tokens: list[str] = []
        code_color = "#EAF2FA" if is_header else "#173D6B"
        link_color = "#EAF2FA" if is_header else "#2357A6"

        def reserve(markup: str) -> str:
            tokens.append(markup)
            return f"@@RH_TOKEN_{len(tokens) - 1}@@"

        def link_replacement(match: re.Match[str]) -> str:
            label = html.escape(match.group(1).strip("`"), quote=False)
            url = html.escape(match.group(2), quote=True)
            return reserve(f'<link href="{url}" color="{link_color}"><u>{label}</u></link>')

        value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_replacement, value)
        value = re.sub(
            r"`([^`]+)`",
            lambda match: reserve(
                f'<font name="Courier" color="{code_color}">'
                + html.escape(match.group(1), quote=False)
                + "</font>"
            ),
            value,
        )
        value = re.sub(
            r"\\\((.+?)\\\)",
            lambda match: reserve(
                '<font name="RHItalic">'
                + inline_math_markup(match.group(1))
                + "</font>"
            ),
            value,
        )
        value = re.sub(
            r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)",
            lambda match: reserve(
                '<font name="RHItalic">'
                + inline_math_markup(match.group(1))
                + "</font>"
            ),
            value,
        )
        value = html.escape(value, quote=False)
        if "\\" in value:
            raise ValueError(f"untranslated backslash in PDF prose: {value!r}")
        value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
        value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", value)
        value = value.replace("  ", " ")
        return token_pattern.sub(lambda match: tokens[int(match.group(1))], value)

    def table_flowable(lines: list[str]) -> Table:
        raw_rows = [
            [cell.strip() for cell in re.split(r"(?<!\\)\|", row.strip().strip("|"))]
            for row in lines
        ]
        if len(raw_rows) > 1 and all(
            re.fullmatch(r":?-{3,}:?", cell.replace(" ", ""))
            for cell in raw_rows[1]
        ):
            raw_rows.pop(1)
        columns = max(len(row) for row in raw_rows)
        lengths = []
        for column in range(columns):
            longest = max(
                (len(row[column]) if column < len(row) else 0) for row in raw_rows
            )
            lengths.append(max(8, min(longest, 42)))
        total = sum(lengths)
        widths = [body_width * length / total for length in lengths]
        if columns >= 3:
            widths = [min(width, body_width * 0.44) for width in widths]
            scale = body_width / sum(widths)
            widths = [width * scale for width in widths]

        rows = []
        for row_index, row in enumerate(raw_rows):
            style = styles["TableHead"] if row_index == 0 else styles["Table"]
            padded = row + [""] * (columns - len(row))
            rows.append(
                [
                    Paragraph(inline_markup(cell, is_header=(row_index == 0)), style)
                    for cell in padded
                ]
            )

        table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), blue),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("BOX", (0, 0), (-1, -1), 0.45, line),
                    ("INNERGRID", (0, 0), (-1, -1), 0.3, line),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4.5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4.5),
                    ("TOPPADDING", (0, 0), (-1, -1), 3.8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3.8),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, pale]),
                ]
            )
        )
        return table

    def quote_flowable(lines: list[str]) -> Table:
        source_lines = [line.removeprefix(">").strip() for line in lines]
        chunks = [
            " ".join(source_lines[index : index + 4])
            for index in range(0, len(source_lines), 4)
        ]
        quote = Table(
            [[Paragraph(inline_markup(chunk), styles["Quote"])] for chunk in chunks],
            colWidths=[body_width - 6],
            splitByRow=1,
        )
        quote.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), pale),
                    ("LINEBEFORE", (0, 0), (0, -1), 3, cyan),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, 0), 8),
                    ("BOTTOMPADDING", (0, -1), (-1, -1), 8),
                ]
            )
        )
        return quote

    def code_flowable(code: str) -> Table:
        block = XPreformatted(html.escape(code.rstrip(), quote=False), styles["Code"])
        table = Table([[block]], colWidths=[body_width], hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), navy),
                    ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#20395B")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        return table

    def equation_flowable(source_eq: str) -> object:
        expression = " ".join(
            line_val.strip() for line_val in source_eq.splitlines()
        ).strip()
        expression = re.sub(r"\\frac([0-9])([0-9])", r"\\frac{\1}{\2}", expression)
        expression = (
            expression.replace(r"\Box", "□")
            .replace(r"\square", "□")
            .replace(r"\Longleftrightarrow", r"\Leftrightarrow")
            .replace(r"\Longrightarrow", r"\Rightarrow")
            .replace(r"\text{--}", "-")
            .replace(r"\text{—}", "-")
        )
        expression = re.sub(r"\\text\{([^{}]+)\}", r"\\mathrm{\1}", expression)
        expression = re.sub(r"\\le(?![A-Za-z])", r"\\leq", expression)
        expression = re.sub(r"\\ge(?![A-Za-z])", r"\\geq", expression)
        expression = re.sub(r"\\ne(?![A-Za-z])", r"\\neq", expression)
        def unwrap_boxed(text: str) -> str:
            while r"\boxed{" in text:
                start_idx = text.index(r"\boxed{")
                brace_start = start_idx + len(r"\boxed")
                depth = 0
                end_idx = -1
                for idx in range(brace_start, len(text)):
                    if text[idx] == "{":
                        depth += 1
                    elif text[idx] == "}":
                        depth -= 1
                        if depth == 0:
                            end_idx = idx
                            break
                if end_idx == -1:
                    break
                text = (
                    text[:start_idx]
                    + text[brace_start + 1 : end_idx]
                    + text[end_idx + 1 :]
                )
            return text

        expression = unwrap_boxed(expression)
        expression = re.sub(
            r"\\(mathbb|mathcal|mathrm|mathbf)\s+([A-Za-z])",
            r"\\\1{\2}",
            expression,
        )
        segments = [
            segment.strip().rstrip(",")
            for segment in re.split(r"\\qquad", expression)
            if segment.strip().rstrip(",")
        ]
        rows = []
        for segment in segments:
            buffer = BytesIO()
            math_to_image(
                f"${segment}$",
                buffer,
                prop=FontProperties(size=12.5),
                dpi=220,
                format="png",
                color="#122033",
            )
            buffer.seek(0)
            rendered = Image(buffer)
            rendered._nsc_buffer = buffer
            rendered.drawWidth *= 72.0 / 220.0
            rendered.drawHeight *= 72.0 / 220.0
            maximum = body_width - 28
            if rendered.drawWidth > maximum:
                scale = maximum / rendered.drawWidth
                rendered.drawWidth *= scale
                rendered.drawHeight *= scale
            rendered.hAlign = "CENTER"
            rows.append([rendered])
        table = Table(rows, colWidths=[body_width], hAlign="CENTER")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), white),
                    ("BOX", (0, 0), (-1, -1), 0.45, line),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, 0), 8),
                    ("BOTTOMPADDING", (0, -1), (-1, -1), 8),
                ]
            )
        )
        return KeepTogether([Spacer(1, 3), table, Spacer(1, 7)])

    def parse_markdown(markdown: str) -> list[object]:
        lines = markdown.splitlines()
        start = next(
            (
                index
                for index, line_value in enumerate(lines)
                if line_value == "## Abstract"
            ),
            0,
        )
        lines = lines[start:]
        story: list[object] = []
        index = 0
        paragraph: list[str] = []

        def flush_paragraph() -> None:
            if paragraph:
                style = styles["Body"]
                story.append(
                    Paragraph(
                        inline_markup(" ".join(part.strip() for part in paragraph)),
                        style,
                    )
                )
                paragraph.clear()

        while index < len(lines):
            line_value = lines[index]
            stripped = line_value.strip()
            if not stripped:
                flush_paragraph()
                index += 1
                continue

            if stripped == "---":
                flush_paragraph()
                story.append(Spacer(1, 4))
                index += 1
                continue

            image_match = IMAGE_LINK.fullmatch(stripped)
            if image_match:
                flush_paragraph()
                path = local_image_path(source, image_match.group(2))
                rendered = Image(str(path))
                scale = min(
                    body_width / rendered.drawWidth,
                    510 / rendered.drawHeight,
                    1.0,
                )
                rendered.drawWidth *= scale
                rendered.drawHeight *= scale
                rendered.hAlign = "CENTER"
                caption_text = image_match.group(1).strip()
                if caption_text:
                    caption = Paragraph(
                        inline_markup(f"**Figure.** {caption_text}."),
                        styles["Body"],
                    )
                    story.append(
                        KeepTogether(
                            [Spacer(1, 5), rendered, Spacer(1, 4), caption, Spacer(1, 5)]
                        )
                    )
                else:
                    story.extend([Spacer(1, 5), rendered, Spacer(1, 5)])
                index += 1
                continue

            if stripped.startswith("<!--") and stripped.endswith("-->"):
                flush_paragraph()
                index += 1
                continue

            if stripped.startswith("```"):
                flush_paragraph()
                index += 1
                code_lines: list[str] = []
                while index < len(lines) and not lines[index].strip().startswith("```"):
                    code_lines.append(lines[index])
                    index += 1
                index += 1
                story.extend([code_flowable("\n".join(code_lines)), Spacer(1, 6)])
                continue

            if stripped == "$$":
                flush_paragraph()
                index += 1
                equation_lines: list[str] = []
                while index < len(lines) and lines[index].strip() != "$$":
                    equation_lines.append(lines[index])
                    index += 1
                if index >= len(lines):
                    raise RuntimeError("unclosed display-math block in manuscript")
                index += 1
                story.append(equation_flowable("\n".join(equation_lines)))
                continue

            if stripped.startswith("|"):
                flush_paragraph()
                table_lines: list[str] = []
                while index < len(lines) and lines[index].strip().startswith("|"):
                    table_lines.append(lines[index])
                    index += 1
                table = table_flowable(table_lines)
                if len(table_lines) <= 6:
                    story.append(KeepTogether([table, Spacer(1, 8)]))
                else:
                    story.extend([table, Spacer(1, 8)])
                continue

            if stripped.startswith(">"):
                flush_paragraph()
                quote_lines: list[str] = []
                while index < len(lines) and lines[index].strip().startswith(">"):
                    quote_lines.append(lines[index].strip())
                    index += 1
                story.extend([quote_flowable(quote_lines), Spacer(1, 8)])
                continue

            heading = re.match(r"^(#{1,3})\s+(.+)$", stripped)
            if heading:
                flush_paragraph()
                level = len(heading.group(1))
                story.append(
                    Paragraph(
                        inline_markup(heading.group(2)), styles[f"Heading{level}"]
                    )
                )
                index += 1
                continue

            if re.match(r"^[-*]\s+", stripped):
                flush_paragraph()
                items: list[ListItem] = []
                while index < len(lines) and re.match(r"^\s*[-*]\s+", lines[index]):
                    item_parts = [re.sub(r"^\s*[-*]\s+", "", lines[index]).strip()]
                    index += 1
                    while (
                        index < len(lines)
                        and lines[index].strip()
                        and re.match(r"^\s+\S", lines[index])
                        and not re.match(r"^\s*(?:[-*]|\d+\.)\s+", lines[index])
                        and lines[index].strip() != "$$"
                        and not lines[index]
                        .strip()
                        .startswith(("```", "|", ">", "#", "<!--"))
                    ):
                        item_parts.append(lines[index].strip())
                        index += 1
                    items.append(
                        ListItem(
                            Paragraph(
                                inline_markup(" ".join(item_parts)), styles["Bullet"]
                            )
                        )
                    )
                story.append(
                    ListFlowable(
                        items,
                        bulletType="bullet",
                        bulletFontName="RHRegular",
                        bulletFontSize=7,
                        leftIndent=15,
                        bulletColor=blue,
                        spaceAfter=5,
                    )
                )
                continue

            numbered = re.match(r"^(\d+)\.\s+(.+)$", stripped)
            if numbered:
                flush_paragraph()
                while index < len(lines):
                    match = re.match(r"^\s*(\d+)\.\s+(.+)$", lines[index])
                    if not match:
                        break
                    item_parts = [match.group(2).strip()]
                    index += 1
                    while (
                        index < len(lines)
                        and lines[index].strip()
                        and re.match(r"^\s+\S", lines[index])
                        and not re.match(r"^\s*(?:[-*]|\d+\.)\s+", lines[index])
                        and lines[index].strip() != "$$"
                        and not lines[index]
                        .strip()
                        .startswith(("```", "|", ">", "#", "<!--"))
                    ):
                        item_parts.append(lines[index].strip())
                        index += 1
                    story.append(
                        Paragraph(
                            inline_markup(" ".join(item_parts)),
                            styles["Numbered"],
                            bulletText=f"{match.group(1)}.",
                        )
                    )
                continue

            paragraph.append(line_value)
            index += 1

        flush_paragraph()
        return story

    class NestedSpaceDocTemplate(BaseDocTemplate):
        def afterFlowable(self, flowable: object) -> None:  # noqa: N802
            if isinstance(flowable, Paragraph):
                if flowable.style.name == "RHHeading1":
                    self.notify("TOCEntry", (0, flowable.getPlainText(), self.page))
                elif flowable.style.name == "RHHeading2":
                    self.notify("TOCEntry", (1, flowable.getPlainText(), self.page))
                elif flowable.style.name == "RHHeading3":
                    self.notify("TOCEntry", (2, flowable.getPlainText(), self.page))

    def draw_cover(canvas: object, document: object) -> None:
        canvas.saveState()
        canvas.setTitle(str(metadata["title"]) + ": " + str(metadata["subtitle"]))
        canvas.setAuthor(str(metadata["author"]))
        canvas.setSubject(
            "Force at Resolutions: Wave-Particle Duality, Helium at the Absolute-Zero Floor, and the Single Thermodynamic Pressure Gradient"
        )
        canvas.setKeywords(
            "nested-space cosmology, force at resolutions, wave-particle duality, superfluid helium, single force law, facet dilution, atomic shells, nuclear fission"
        )
        canvas.setFillColor(navy)
        canvas.rect(0, 0, page_width, page_height, fill=1, stroke=0)
        canvas.setStrokeColor(colors.HexColor("#16345D"))
        canvas.setLineWidth(1.0)
        for radius in (58, 95, 142, 205, 282):
            canvas.circle(
                page_width * 0.89, page_height * 0.18, radius, fill=0, stroke=1
            )
        canvas.setStrokeColor(cyan)
        canvas.setLineWidth(2.0)
        canvas.line(
            left_margin,
            page_height - 39 * mm,
            left_margin + 34 * mm,
            page_height - 39 * mm,
        )
        canvas.restoreState()

    def draw_body(canvas: object, document: object) -> None:
        canvas.saveState()
        canvas.setFont("RHRegular", 6.8)
        canvas.setFillColor(muted)
        canvas.drawString(
            left_margin, page_height - 11 * mm, str(metadata["project"]).upper()
        )
        right = f"{metadata['status']}  ·  {metadata.get('revision', metadata['version'])}"
        canvas.drawRightString(
            page_width - right_margin, page_height - 11 * mm, right
        )
        canvas.setStrokeColor(line)
        canvas.setLineWidth(0.5)
        canvas.line(
            left_margin,
            page_height - 13 * mm,
            page_width - right_margin,
            page_height - 13 * mm,
        )
        canvas.line(
            left_margin, 12 * mm, page_width - right_margin, 12 * mm
        )
        canvas.setFont("RHRegular", 7.2)
        canvas.drawString(
            left_margin, 8.2 * mm, "Douglas Ek · Force at Resolutions (Paper II)"
        )
        canvas.drawRightString(
            page_width - right_margin, 8.2 * mm, str(document.page)
        )
        canvas.restoreState()

    cover_frame = Frame(
        left_margin,
        25 * mm,
        body_width,
        page_height - 50 * mm,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
        id="cover-frame",
    )
    body_frame = Frame(
        left_margin,
        bottom_margin,
        body_width,
        page_height - top_margin - bottom_margin,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
        id="body-frame",
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    staging = output.parent / ".build"
    staging.mkdir(parents=True, exist_ok=True)
    temporary = staging / f"{output.name}.tmp"
    if temporary.exists():
        temporary.unlink()

    os.environ["SOURCE_DATE_EPOCH"] = str(metadata["source_date_epoch"])
    os.environ["TZ"] = "UTC"
    if hasattr(time, "tzset"):
        time.tzset()
    document = NestedSpaceDocTemplate(
        str(temporary),
        pagesize=A4,
        leftMargin=left_margin,
        rightMargin=right_margin,
        topMargin=top_margin,
        bottomMargin=bottom_margin,
        title=str(metadata["title"]),
        author=str(metadata["author"]),
        invariant=1,
    )
    document.addPageTemplates(
        [
            PageTemplate(id="Cover", frames=[cover_frame], onPage=draw_cover),
            PageTemplate(id="Body", frames=[body_frame], onPage=draw_body),
        ]
    )

    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(
            "RHTocLevel1",
            fontName="RHBold",
            fontSize=9.2,
            leading=13,
            textColor=ink,
            leftIndent=0,
            firstLineIndent=0,
            spaceBefore=3,
        ),
        ParagraphStyle(
            "RHTocLevel2",
            fontName="RHBold",
            fontSize=8.4,
            leading=11.8,
            textColor=blue,
            leftIndent=10,
            firstLineIndent=0,
            spaceBefore=2,
        ),
        ParagraphStyle(
            "RHTocLevel3",
            fontName="RHRegular",
            fontSize=7.8,
            leading=10.8,
            textColor=muted,
            leftIndent=22,
            firstLineIndent=0,
            spaceBefore=1,
        ),
    ]

    cover_story: list[object] = [
        Spacer(1, 28 * mm),
        Paragraph("NESTED-SPACE<br/>COSMOLOGY II", styles["CoverTitle"]),
        Paragraph(str(metadata["subtitle"]), styles["CoverDeck"]),
        Paragraph(
            "Wave–particle duality at the Absolute-Zero floor, finite Planck facets at the ceiling, and the single thermodynamic pressure gradient across all resolutions",
            styles["CoverSubtitle"],
        ),
        Spacer(1, 16 * mm),
        Paragraph(
            f"AUTHOR<br/>{str(metadata['author']).upper()}<br/><br/>"
            f"{str(metadata['project']).upper()}<br/>"
            f"VERSION {metadata['version']} · {str(metadata['date']).upper()}<br/><br/>"
            f"STATUS: {metadata['status']}",
            styles["CoverMeta"],
        ),
        NextPageTemplate("Body"),
        PageBreak(),
        Paragraph("Contents", styles["TocTitle"]),
        toc,
        PageBreak(),
    ]
    manuscript = source.read_text(encoding="utf-8").split("<!-- nsc-pdf-end -->", 1)[0]
    story = cover_story + parse_markdown(manuscript)
    with deterministic_pdf_compression():
        document.multiBuild(story)

    if not temporary.is_file() or temporary.stat().st_size < 20_000:
        raise RuntimeError("PDF build did not produce a plausible output file")
    with temporary.open("rb") as handle:
        if handle.read(5) != b"%PDF-":
            raise RuntimeError("generated file does not have a PDF signature")
    temporary.replace(output)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    return int(document.page), output.stat().st_size, digest


def write_build_manifest(
    source: Path,
    output: Path,
    metadata: dict[str, object],
    pages: int,
    size: int,
    digest: str,
) -> None:
    record = {
        "schema": "NSC-PAPER-2-BUILD-v1",
        "source": source.relative_to(REPOSITORY).as_posix(),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "metadata": METADATA.relative_to(REPOSITORY).as_posix(),
        "metadata_sha256": hashlib.sha256(METADATA.read_bytes()).hexdigest(),
        "output": output.relative_to(REPOSITORY).as_posix(),
        "pdf_sha256": digest,
        "pages": pages,
        "bytes": size,
        "version": metadata["version"],
        "scientific_build_inputs": scientific_build_inputs(source),
    }
    BUILD_MANIFEST.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def check_build(source: Path, output: Path, metadata: dict[str, object]) -> int:
    if not output.is_file() or not BUILD_MANIFEST.is_file():
        print("tracked PDF or build manifest is absent", file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory(prefix="nsc-paper2-check-") as directory:
        first = Path(directory) / "first.pdf"
        second = Path(directory) / "second.pdf"
        first_result = build_pdf(source, first, metadata)
        second_result = build_pdf(source, second, metadata)
        if first.read_bytes() != second.read_bytes():
            print("two identical paper builds produced different bytes", file=sys.stderr)
            return 1
        if first.read_bytes() != output.read_bytes():
            print(
                "tracked PDF does not match a fresh deterministic build",
                file=sys.stderr,
            )
            return 1
        manifest = json.loads(BUILD_MANIFEST.read_text(encoding="utf-8"))
        expected = {
            "scientific_build_inputs": scientific_build_inputs(source),
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "metadata_sha256": hashlib.sha256(METADATA.read_bytes()).hexdigest(),
            "pdf_sha256": first_result[2],
            "pages": first_result[0],
            "bytes": first_result[1],
        }
        for key, value in expected.items():
            if manifest.get(key) != value:
                print(f"build manifest mismatch for {key}", file=sys.stderr)
                return 1
    print(
        f"verified deterministic Paper II PDF: {output} "
        f"({first_result[0]} pages, {first_result[1]} bytes, sha256={first_result[2][:12]}...)"
    )
    return 0


def main() -> int:
    args = parse_args()
    if args.clean:
        return clean_output(args.output)
    metadata = load_metadata()
    if args.check:
        return check_build(args.source, args.output, metadata)
    pages, size, digest = build_pdf(args.source, args.output, metadata)
    write_build_manifest(args.source, args.output, metadata, pages, size, digest)
    print(
        f"Wrote {args.output} ({pages} pages, {size} bytes, sha256={digest[:12]}...)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
