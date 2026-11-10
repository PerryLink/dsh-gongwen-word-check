#!/usr/bin/env python3
"""Generate the README visuals for dsh-gongwen-word-check.

Outputs (idempotent overwrite):
  docs/assets/dsh-gongwen-word-check-hero-{zh,en}-{light,dark}.webp
      1440x576 hero banner drawn with Pillow. Left column: kicker, two-line
      title, two value lines, one subtitle, one meta line, footer. The right
      column is this repository's own semantic figure: a document-number
      specimen annotated as 机关代字 / 〔年份〕 / 序号, the two literal
      differences the rule pack reports on that form, one real sample run
      (0 error / 1 warn / 0 info, one skipped GW-003), and the evidence-kind
      severity caps. Every number is taken from the run recorded in
      samples/quickstart/expected/result.json.
  docs/assets/dsh-gongwen-word-check-flow-v5-{light,dark}.svg
      1100x660 hand-written SVG. Grammar: a two-sided scope boundary, NOT a
      row of five nodes. Left of the boundary, the five canonical fields the
      register exposes and the seven rules mounted on them (docNo carries
      GW-001 and GW-006; title carries GW-005 and GW-007; docKind is the
      factory-empty list, so GW-003 reports itself in skipped). Right of the
      boundary, the four layout facts that only the document itself can show
      (typeface, type size, margins, seal), explicitly outside the check.
      Below the boundary, the report: one issue located at row 1 / column
      docNo plus the one skipped rule. The same pair is shared by all five
      README languages; the prose labels are English and the material
      literals stay as the plugin reports them.

Design parameters
-----------------
* GitHub renders the 1440px hero at ~880px. The title is 82px, the subtitle
  25px, the meta line 20px, so the displayed sizes stay above 48 / 15 / 12px.
  The 1100px SVG is checked at its native size in headless Chrome.
* Palette: light #f9f6fd -> #e4eaf8, dark #131a2a -> #0c1016; family accent
  #4B67B4 (dark #8496f5); radius 18-22; soft shadows.
* Fonts: msyh.ttc / msyhbd.ttc / consola.ttf (the family set). Every string
  is measured before drawing; an overflow raises instead of being clipped.
* Nothing is fabricated: the sample finding, locator, values and skipped
  reason are the real output of lib/index.mjs against the shipped fixture.

Run once:  python scripts/gen-readme-assets.py
Requires:  Python 3.10+, Pillow, and the Windows fonts above.
"""
from __future__ import annotations

import os
import re
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")
os.makedirs(OUT, exist_ok=True)

FONT_CJK = r"C:\Windows\Fonts\msyh.ttc"
FONT_CJK_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_MONO = r"C:\Windows\Fonts\consola.ttf"

for _path in (FONT_CJK, FONT_CJK_BOLD, FONT_MONO):
    if not os.path.exists(_path):
        raise SystemExit(f"FATAL: font missing: {_path}")

HERO_W, HERO_H = 1440, 576
NAME = "dsh-gongwen-word-check"

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
SKIN = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        card="#ffffff", card_edge="#e6e2ef",
        band="#f5f2fb", edge="#e7e4f0",
        text="#141419", sub="#4d5261", faint="#737a8c",
        accent="#4B67B4", accent_soft="#ece7f9",
        seg2="#0f766e",
        warn="#b45309", warn_bg="#fdf0e7", warn_edge="#f2d5bc",
        good="#15803d", good_bg="#e9f6ee",
        out_fill="#f4f2f8", out_edge="#cfc8e2", out_text="#7c8194",
        shadow=(28, 22, 54, 42), dot="#cfc8e2",
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        card="#1b2231", card_edge="#2e374b",
        band="#242d42", edge="#1e2636",
        text="#f0f3f9", sub="#a8b1c4", faint="#838ca0",
        accent="#8496f5", accent_soft="#242d42",
        seg2="#5eead4",
        warn="#e0a85a", warn_bg="#35271b", warn_edge="#5b4227",
        good="#4ade80", good_bg="#16301f",
        out_fill="#161c28", out_edge="#39445a", out_text="#7f889b",
        shadow=(0, 0, 0, 110), dot="#2a3448",
    ),
}

# ---------------------------------------------------------------------------
# Hero copy. The Chinese/English variants are the only localized assets.
# ---------------------------------------------------------------------------
HERO = {
    "zh": dict(
        lang="zh",
        kicker="DEEPSEEK HARNESS · dsh-gongwen-word-check",
        title_lines=["公文台账", "逐项核对"],
        value=["七条规则，逐栏核台账文字", "差异落到行号、栏名与改法"],
        sub="只列差异，不判合规；定性结论留给审核人。",
        meta="gongwen_word_check · GW-001…007 · JSON/YAML",
        foot="Apache-2.0 · 社区插件 · 无网络 · 不调模型",
        spec_kicker="样本 · 发文字号",
        spec_chip="GW-001 · warn",
        specimen=["某政发", "〔2026〕", "15号"],
        seg_labels=["机关代字", "〔年份〕", "序号"],
        diff_rows=[
            ("某政发[2026]15号", "某政发〔2026〕15号", "GW-001"),
            ("二〇二六年三月十日", "2026-03-10", "GW-002"),
        ],
        run_kicker="一次运行 · 样例",
        run_file="GW-001-unsafe.json",
        run_nums=["0", "1", "0"],
        run_labels=["error", "warn", "info"],
        run_locator="row 1 · column docNo",
        run_value="某政发[2026]15号",
        run_fix="→ 六角括号〔〕",
        run_skip="skipped 1 · GW-003",
        cap_kicker="证据 → 封顶",
        cap_rows=[
            ("derived-from-principle", "≤ warn"),
            ("institutional-configuration", "≤ info"),
            ("excerpt", "逐字引文"),
            ("skipped", "逐条写明"),
        ],
        cap_note="空 issues ≠ 通过",
        note="边界：只核对台账文字；字体、字号、页边距与印章只看正本。",
    ),
    "en": dict(
        lang="en",
        kicker="DEEPSEEK HARNESS · dsh-gongwen-word-check",
        title_lines=["Register", "check"],
        value=["Seven rules over the register's text", "Every difference gets a row + field"],
        sub="Differences only — the verdict stays yours.",
        meta="gongwen_word_check · GW-001…007 · JSON/YAML",
        foot="Apache-2.0 · community plugin · offline · no model calls",
        spec_kicker="SPECIMEN · DOCUMENT NUMBER",
        spec_chip="GW-001 · warn",
        specimen=["某政发", "〔2026〕", "15号"],
        seg_labels=["issuer code", "year in 〔〕", "serial no."],
        diff_rows=[
            ("某政发[2026]15号", "某政发〔2026〕15号", "GW-001"),
            ("二〇二六年三月十日", "2026-03-10", "GW-002"),
        ],
        run_kicker="ONE RUN · SAMPLE",
        run_file="GW-001-unsafe.json",
        run_nums=["0", "1", "0"],
        run_labels=["error", "warn", "info"],
        run_locator="row 1 · column docNo",
        run_value="某政发[2026]15号",
        run_fix="→ hexagonal brackets",
        run_skip="skipped 1 · GW-003",
        cap_kicker="EVIDENCE → CAP",
        cap_rows=[
            ("derived-from-principle", "≤ warn"),
            ("institutional-configuration", "≤ info"),
            ("excerpt", "verbatim"),
            ("skipped", "named"),
        ],
        cap_note="empty issues ≠ all clear",
        note="Boundary: register text only — typeface, size, margins and seal stay on the document.",
    ),
}

# ---------------------------------------------------------------------------
# Font helpers
# ---------------------------------------------------------------------------
_FONT_CACHE: dict[tuple[int, str], ImageFont.FreeTypeFont] = {}


def font(size: float, kind: str) -> ImageFont.FreeTypeFont:
    key = (max(1, int(round(size))), kind)
    if key not in _FONT_CACHE:
        path = {"cjk": FONT_CJK, "cjk_bold": FONT_CJK_BOLD, "mono": FONT_MONO}[kind]
        _FONT_CACHE[key] = ImageFont.truetype(path, key[0], index=0)
    return _FONT_CACHE[key]


def tw(text: str, size: float, kind: str) -> float:
    return font(size, kind).getlength(text)


def fit(text: str, kind: str, max_width: float, preferred: float, minimum: float) -> float:
    size = preferred
    while size > minimum and tw(text, size, kind) > max_width:
        size -= 0.5
    if tw(text, size, kind) > max_width:
        raise SystemExit(f"FATAL: text does not fit ({kind}, {max_width}px): {text!r}")
    return size


def require(text: str, size: float, kind: str, max_width: float, label: str) -> None:
    width = tw(text, size, kind)
    if width > max_width:
        raise SystemExit(f"FATAL: {label} overflows: {width:.1f} > {max_width}px: {text!r}")


def hx(color: str) -> str:
    return color


# ---------------------------------------------------------------------------
# Raster helpers
# ---------------------------------------------------------------------------
def gradient(width: int, height: int, top: str, bottom: str) -> Image.Image:
    top_rgb = tuple(int(top[i:i + 2], 16) for i in (1, 3, 5))
    bottom_rgb = tuple(int(bottom[i:i + 2], 16) for i in (1, 3, 5))
    strip = Image.new("RGB", (1, height))
    pixels = strip.load()
    for y in range(height):
        t = y / max(1, height - 1)
        pixels[0, y] = tuple(
            round(top_rgb[i] * (1 - t) + bottom_rgb[i] * t) for i in range(3)
        )
    return strip.resize((width, height)).convert("RGBA")


def glow(img: Image.Image, cx: int, cy: int, radius: int, color: str, alpha: int) -> Image.Image:
    rgb = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius], fill=(*rgb, alpha)
    )
    layer = layer.filter(ImageFilter.GaussianBlur(radius * 0.55))
    return Image.alpha_composite(img, layer)


def dots(img: Image.Image, step: int, color: str, alpha: int) -> Image.Image:
    rgb = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y in range(step // 2, img.height, step):
        for x in range(step // 2, img.width, step):
            d.ellipse([x, y, x + 1.7, y + 1.7], fill=(*rgb, alpha))
    return Image.alpha_composite(img, layer)


def card(
    img: Image.Image,
    box: tuple[int, int, int, int],
    radius: int,
    fill: str,
    edge: str,
    shadow: tuple[int, int, int, int],
    blur: int = 18,
    dy: int = 8,
) -> Image.Image:
    x0, y0, x1, y1 = box
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle(
        [x0, y0 + dy, x1, y1 + dy], radius, fill=shadow
    )
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    img = Image.alpha_composite(img, layer)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, radius, fill=hx(fill), outline=hx(edge), width=1)
    return img


def pill(
    d: ImageDraw.ImageDraw,
    x: float,
    y: float,
    text: str,
    size: float,
    kind: str,
    fg: str,
    bg: str,
    pad_x: float = 12,
    height: float | None = None,
) -> float:
    box_h = height if height is not None else round(size * 1.75)
    width = tw(text, size, kind) + pad_x * 2
    d.rounded_rectangle([x, y, x + width, y + box_h], box_h / 2, fill=hx(bg))
    d.text((x + pad_x, y + box_h / 2), text, font=font(size, kind), fill=hx(fg), anchor="lm")
    return width


# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
def hero(lang: str, skin: str) -> None:
    s = SKIN[skin]
    m = HERO[lang]
    img = gradient(HERO_W, HERO_H, s["bg_from"], s["bg_to"])
    img = dots(img, 30, s["dot"], 26 if skin == "light" else 32)
    img = glow(img, 1180, 70, 330, s["accent"], 16 if skin == "light" else 26)
    img = glow(img, 180, 560, 280, s["accent"], 9 if skin == "light" else 18)
    d = ImageDraw.Draw(img)

    left_x, left_w = 76, 606

    # ---- kicker -----------------------------------------------------------
    kicker_size = 17.5 if lang == "zh" else 16.5
    kicker_kind = "cjk_bold" if lang == "zh" else "cjk_bold"
    require(m["kicker"], kicker_size, kicker_kind, left_w - 32, "hero kicker")
    pill(d, left_x, 64, m["kicker"], kicker_size, kicker_kind,
         s["accent"], s["accent_soft"], pad_x=16, height=34)

    # ---- title ------------------------------------------------------------
    title_size = 82
    for line in m["title_lines"]:
        require(line, title_size, "cjk_bold", left_w, "hero title")
    d.text((left_x - 2, 108), m["title_lines"][0], font=font(title_size, "cjk_bold"),
           fill=hx(s["text"]))
    d.text((left_x - 2, 200), m["title_lines"][1], font=font(title_size, "cjk_bold"),
           fill=hx(s["text"]))
    if title_size * 880 / 1440 < 48:
        raise SystemExit("FATAL: hero title below 48px displayed")

    # ---- two value lines --------------------------------------------------
    value_size = min(
        fit(line, "cjk_bold", left_w, 29, 24) for line in m["value"]
    )
    for i, line in enumerate(m["value"]):
        require(line, value_size, "cjk_bold", left_w, f"hero value {i}")
        d.text((left_x, 306 + i * 40), line, font=font(value_size, "cjk_bold"),
               fill=hx(s["text"]))

    # ---- subtitle / meta / footer ----------------------------------------
    sub_size = fit(m["sub"], "cjk", left_w, 25, 24.5)
    require(m["sub"], sub_size, "cjk", left_w, "hero subtitle")
    d.text((left_x, 392), m["sub"], font=font(sub_size, "cjk"), fill=hx(s["sub"]))
    if sub_size * 880 / 1440 < 15:
        raise SystemExit("FATAL: hero subtitle below 15px displayed")

    meta_size = fit(m["meta"], "mono", left_w, 20, 20)
    require(m["meta"], meta_size, "mono", left_w, "hero meta")
    d.text((left_x, 438), m["meta"], font=font(meta_size, "mono"), fill=hx(s["sub"]))
    if meta_size * 880 / 1440 < 12:
        raise SystemExit("FATAL: hero meta below 12px displayed")

    d.line([left_x, 482, left_x + left_w - 8, 482], fill=hx(s["edge"]), width=1)
    require(m["foot"], 18, "cjk", left_w, "hero footer")
    d.text((left_x, 500), m["foot"], font=font(18, "cjk"), fill=hx(s["faint"]))

    # ---- specimen card ----------------------------------------------------
    img = card(img, (752, 60, 1368, 312), 22, s["card"], s["card_edge"], s["shadow"])
    d = ImageDraw.Draw(img)

    spec_kind = "cjk_bold" if lang == "zh" else "cjk_bold"
    d.text((772, 82), m["spec_kicker"], font=font(14.5, spec_kind), fill=hx(s["accent"]))
    chip_w = tw(m["spec_chip"], 10.5, "mono") + 20
    pill(d, 1348 - chip_w, 76, m["spec_chip"], 10.5, "mono", s["warn"], s["warn_bg"])

    # big specimen, segmented by meaning
    spec_size = 40
    x = 772.0
    colors = [s["accent"], s["seg2"], s["accent"]]
    seg_positions = []
    for index, (segment, label) in enumerate(zip(m["specimen"], m["seg_labels"])):
        seg_w = tw(segment, spec_size, "cjk_bold")
        d.text((x, 180), segment, font=font(spec_size, "cjk_bold"),
               fill=hx(colors[index]), anchor="ls")
        d.rounded_rectangle([x + 1, 190, x + seg_w - 1, 193], 1.5, fill=hx(colors[index]))
        require(label, 12, "cjk", 190, "specimen segment label")
        d.text((x + seg_w / 2, 213), label, font=font(12, "cjk"),
               fill=hx(s["faint"]), anchor="ms")
        seg_positions.append((x, x + seg_w))
        x += seg_w

    d.line([772, 228, 1348, 228], fill=hx(s["edge"]), width=1)

    # literal differences (the two forms the pack reports)
    for index, (bad, good, tag) in enumerate(m["diff_rows"]):
        y = 252 + index * 38
        d.ellipse([772, y - 5, 781, y + 4], fill=hx(s["warn"]))
        d.text((776.5, y + 0.5), "×", font=font(9, "cjk_bold"), fill="#ffffff", anchor="mm")
        bad_size = 14
        good_size = 14 if lang == "zh" else 13.5
        d.text((792, y), bad, font=font(bad_size, "cjk"), fill=hx(s["sub"]), anchor="lm")
        bad_w = tw(bad, bad_size, "cjk")
        d.text((792 + bad_w + 10, y), "→", font=font(13, "cjk"), fill=hx(s["faint"]), anchor="lm")
        d.text((792 + bad_w + 32, y), good, font=font(good_size, "cjk"),
               fill=hx(s["text"]), anchor="lm")
        require(bad + " → " + good, 14, "cjk", 470, "hero diff row")
        pill(d, 1300, y - 11, tag, 10, "mono", s["faint"], s["band"], pad_x=8, height=22)

    # ---- one-run + evidence-cap card (one wide card, two columns) ---------
    img = card(img, (752, 328, 1368, 512), 20, s["card"], s["card_edge"], s["shadow"])
    d = ImageDraw.Draw(img)
    d.line([1060, 344, 1060, 496], fill=hx(s["edge"]), width=1)

    d.text((772, 348), m["run_kicker"], font=font(11, "cjk_bold"), fill=hx(s["accent"]))
    d.text((1038, 348), m["run_file"], font=font(9.5, "mono"), fill=hx(s["faint"]), anchor="rm")

    for i, (num, label) in enumerate(zip(m["run_nums"], m["run_labels"])):
        nx = 772 + i * 88
        color = s["warn"] if label == "warn" else s["text"]
        d.text((nx, 384), num, font=font(28, "cjk_bold"), fill=hx(color), anchor="ls")
        d.text((nx, 402), label, font=font(10.5, "mono"), fill=hx(s["faint"]))

    d.line([772, 414, 1038, 414], fill=hx(s["edge"]), width=1)
    require(m["run_locator"], 10.5, "mono", 266, "run locator")
    d.text((772, 432), m["run_locator"], font=font(10.5, "mono"), fill=hx(s["sub"]))
    require(m["run_value"], 12.5, "cjk", 266, "run value")
    d.text((772, 452), m["run_value"], font=font(12.5, "cjk"), fill=hx(s["text"]))
    require(m["run_fix"], 11, "cjk", 266, "run fix")
    d.text((772, 472), m["run_fix"], font=font(11, "cjk"), fill=hx(s["accent"]))
    require(m["run_skip"], 10.5, "mono", 266, "run skipped")
    d.text((772, 492), m["run_skip"], font=font(10.5, "mono"), fill=hx(s["warn"]))

    d.text((1080, 348), m["cap_kicker"],
           font=font(11, "cjk_bold" if lang == "zh" else "mono"), fill=hx(s["accent"]))
    for i, (label, cap) in enumerate(m["cap_rows"]):
        y = 378 + i * 28
        require(label, 10.5, "mono", 190, "cap label")
        d.text((1080, y), label, font=font(10.5, "mono"), fill=hx(s["sub"]))
        d.text((1348, y), cap, font=font(11, "cjk_bold"), fill=hx(s["accent"]), anchor="ra")
    require(m["cap_note"], 11, "cjk_bold", 268, "cap note")
    d.text((1080, 488), m["cap_note"], font=font(11, "cjk_bold"), fill=hx(s["warn"]))

    # ---- boundary footnote (right of the left footer) ---------------------
    require(m["note"], 12, "cjk", 616, "hero boundary note")
    d.text((752, 534), m["note"], font=font(12, "cjk"), fill=hx(s["faint"]))

    path = os.path.join(OUT, f"{NAME}-hero-{lang}-{skin}.webp")
    img.convert("RGB").save(path, "WEBP", quality=90, method=6)
    print(f"wrote {os.path.basename(path)}")


# ---------------------------------------------------------------------------
# Flow SVG: scope boundary, five fields / seven rules | four layout facts
# ---------------------------------------------------------------------------
def svg_text(
    x: float,
    y: float,
    content: str,
    size: float,
    fill: str,
    *,
    anchor: str = "start",
    mono: bool = False,
    bold: bool = False,
    spacing: float | None = None,
    opacity: float | None = None,
    rotate: float | None = None,
) -> str:
    family = (
        "Consolas,'Microsoft YaHei',ui-monospace,monospace"
        if mono
        else "'Microsoft YaHei','Segoe UI','PingFang SC','Noto Sans CJK SC',sans-serif"
    )
    attrs = [
        f'x="{x:g}"', f'y="{y:g}"', f'fill="{fill}"',
        f'font-family="{family}"', f'font-size="{size:g}"',
    ]
    if anchor != "start":
        attrs.append(f'text-anchor="{anchor}"')
    if bold:
        attrs.append('font-weight="700"')
    if spacing is not None:
        attrs.append(f'letter-spacing="{spacing:g}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity:g}"')
    if rotate is not None:
        attrs.append(f'transform="rotate({rotate:g} {x:g} {y:g})"')
    return f"<text {' '.join(attrs)}>{escape(content)}</text>"


def rect(
    x: float, y: float, w: float, h: float, r: float, fill: str,
    stroke: str | None = None, width: float = 1, dash: str | None = None,
    extra: str = "",
) -> str:
    attrs = [f'x="{x:g}"', f'y="{y:g}"', f'width="{w:g}"', f'height="{h:g}"',
             f'rx="{r:g}"', f'fill="{fill}"']
    if stroke is not None:
        attrs += [f'stroke="{stroke}"', f'stroke-width="{width:g}"']
    if dash is not None:
        attrs.append(f'stroke-dasharray="{dash}"')
    if extra:
        attrs.append(extra)
    return f"<rect {' '.join(attrs)}/>"


def svg_pill(
    x: float, y: float, content: str, size: float, fg: str, bg: str,
    *, mono: bool = True, bold: bool = False, pad: float = 8,
    height: float = 21, stroke: str | None = None, dash: str | None = None,
) -> tuple[str, float]:
    width = tw(content, size, "mono" if mono else "cjk") + pad * 2
    shape = rect(x, y, width, height, height / 2, bg, stroke, 1, dash)
    label = svg_text(x + width / 2, y + height / 2 + size * 0.34, content, size, fg,
                     anchor="middle", mono=mono, bold=bold)
    return shape + label, width


def flow_svg(skin: str) -> str:
    s = SKIN[skin]
    s = dict(s)
    # SVG-specific aliases
    parts: list[str] = []
    W, H = 1100, 660

    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">'
    )
    parts.append(
        '<title id="title">dsh-gongwen-word-check — register-text scope boundary</title>'
    )
    parts.append(
        '<desc id="desc">A vertical scope boundary. In scope on the left: the register\'s five '
        'canonical fields (docNo, signedAt, docKind, recipient, title) and the seven rules that read '
        'them; docNo carries GW-001 and GW-006, title carries GW-005 and GW-007, and GW-003 is the '
        'factory-empty document-kind list, so it reports itself in skipped. Out of scope on the '
        'right: typeface, type size, margins and seal placement, which a register cannot show. Below: '
        'the report, one issue at row 1 column docNo and one skipped rule; empty issues is not all clear.</desc>'
    )
    parts.append("<defs>")
    parts.append(
        f'<linearGradient id="bg" x1="0" y1="0" x2="0.15" y2="1">'
        f'<stop offset="0" stop-color="{s["bg_from"]}"/>'
        f'<stop offset="1" stop-color="{s["bg_to"]}"/></linearGradient>'
    )
    parts.append(
        f'<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="{s["accent"]}" stop-opacity="0.16"/>'
        f'<stop offset="1" stop-color="{s["accent"]}" stop-opacity="0"/></radialGradient>'
    )
    parts.append(
        '<filter id="soft" x="-20%" y="-20%" width="140%" height="150%">'
        '<feDropShadow dx="0" dy="6" stdDeviation="9" flood-color="#241d38" flood-opacity="0.12"/>'
        "</filter>"
    )
    parts.append("</defs>")

    parts.append(rect(0, 0, W, H, 22, "url(#bg)"))
    parts.append(f'<circle cx="968" cy="74" r="270" fill="url(#glow)"/>')

    # ---- header -----------------------------------------------------------
    parts.append(svg_text(44, 58, NAME, 30, s["text"], mono=True, bold=True))
    parts.append(
        svg_text(44, 86,
                 "Seven rules read the text a register records. Layout is outside the boundary.",
                 14, s["sub"])
    )
    badge_text = "rules/gongwen-word-check.yaml · v2026.1"
    badge_w = tw(badge_text, 11, "mono") + 26
    parts.append(rect(1056 - badge_w, 34, badge_w, 28, 14, s["accent_soft"]))
    parts.append(svg_text(1056 - badge_w + 13, 52.4, badge_text, 11, s["accent"], mono=True))

    parts.append(
        svg_text(44, 112, "IN · rows[] · issuer / year / checkedAt · JSON or YAML",
                 11, s["faint"], mono=True)
    )
    parts.append(
        svg_text(1056, 112, "OUT · issues[] + skipped[] · markdown + reportJson",
                 11, s["faint"], mono=True, anchor="end")
    )
    parts.append(f'<line x1="44" y1="126" x2="1056" y2="126" stroke="{s["edge"]}" stroke-width="1"/>')

    # ---- left panel: in scope --------------------------------------------
    parts.append(rect(44, 150, 544, 390, 20, s["card"], s["card_edge"], 1.2,
                      extra='filter="url(#soft)"'))
    parts.append(
        svg_text(64, 181, "IN SCOPE · WHAT THE REGISTER RECORDS", 11, s["accent"],
                 bold=True, spacing=1.1)
    )
    parts.append(
        svg_text(568, 181, "5 fields · 7 rules", 11, s["faint"], mono=True, anchor="end")
    )

    # input strip
    parts.append(rect(60, 196, 512, 32, 10, s["band"], s["edge"], 1))
    parts.append(svg_text(74, 216.5, "rows[]", 11.5, s["text"], mono=True, bold=True))
    parts.append(svg_text(132, 216.5, "issuer · year · checkedAt", 11, s["sub"], mono=True))
    parts.append(svg_text(558, 216.5, "JSON | YAML", 11, s["faint"], mono=True, anchor="end"))

    fields = [
        ("docNo", "发文字号", [("GW-001", "pattern", "warn"), ("GW-006", "unique", "warn")], None),
        ("signedAt", "成文日期", [("GW-002", "date", "warn")], None),
        ("docKind", "文种", [("GW-003", "enum", "info")], "skipped"),
        ("recipient", "主送机关", [("GW-004", "presence", "warn")], None),
        ("title", "标题", [("GW-005", "length", "warn"), ("GW-007", "containsAny", "warn")], None),
    ]

    row_y = 242
    for index, (key, cn, rules, status) in enumerate(fields):
        y = row_y + index * 58
        parts.append(rect(60, y, 512, 50, 12, s["card"], s["edge"], 1))
        parts.append(svg_text(74, y + 21, key, 14, s["text"], mono=True, bold=True))
        parts.append(svg_text(74, y + 38, cn, 11, s["faint"]))
        chip_x = 236.0
        for rule_id, kind, sev in rules:
            chip_w = tw(rule_id, 13, "mono") + tw(kind, 11, "mono") + 40
            highlight = rule_id == "GW-001"
            fill = s["warn_bg"] if highlight else s["band"]
            edge = s["warn_edge"] if highlight else s["edge"]
            parts.append(rect(chip_x, y + 14, chip_w, 22, 11, fill, edge, 1))
            dot = s["warn"] if sev == "warn" else s["accent"]
            parts.append(f'<circle cx="{chip_x + 10:g}" cy="{y + 25:g}" r="2.6" fill="{dot}"/>')
            parts.append(
                svg_text(chip_x + 18, y + 27.4, rule_id, 13, s["text"], mono=True, bold=True)
            )
            id_w = tw(rule_id, 13, "mono")
            parts.append(
                svg_text(chip_x + 18 + id_w + 5, y + 27.4, f"· {kind}", 11, s["sub"], mono=True)
            )
            chip_x += chip_w + 6
        if status == "skipped":
            tag_w = tw("skipped", 11, "mono") + 14
            parts.append(rect(chip_x, y + 15, tag_w, 20, 10, s["accent_soft"], None, 0,
                              dash="3 2"))
            parts.append(
                svg_text(chip_x + tag_w / 2, y + 29, "skipped", 11, s["accent"],
                         mono=True, anchor="middle")
            )

    # ---- boundary ---------------------------------------------------------
    parts.append(
        f'<line x1="602" y1="150" x2="602" y2="540" stroke="{s["out_edge"]}" '
        f'stroke-width="1.5" stroke-dasharray="6 5" opacity="0.9"/>'
    )
    parts.append(
        svg_text(602, 345, "SCOPE BOUNDARY", 11, s["faint"], mono=True,
                 anchor="middle", spacing=1.4, rotate=-90)
    )

    # ---- right panel: out of scope ---------------------------------------
    parts.append(rect(616, 150, 440, 390, 20, s["out_fill"], s["out_edge"], 1.2))
    parts.append(
        svg_text(636, 181, "OUT OF SCOPE · DOCUMENT LAYOUT", 11, s["out_text"],
                 bold=True, spacing=1.1)
    )
    parts.append(
        svg_text(1040, 181, "no field in rows[]", 11, s["out_text"], mono=True, anchor="end")
    )

    layout_facts = [
        ("typeface", "字体", "标题小标宋 · §7.3.1", "Aa"),
        ("type size", "字号", "正文 3 号仿宋 · §5.2.2", "12"),
        ("margins", "页边距", "156mm × 225mm · §5", "▭"),
        ("seal", "印章", "印章位置 · §7.3.5.1", "◎"),
    ]
    for index, (en, cn, detail, glyph) in enumerate(layout_facts):
        y = 200 + index * 74
        parts.append(rect(632, y, 408, 64, 12, s["card"], s["out_edge"], 1,
                          dash="5 4"))
        parts.append(rect(646, y + 14, 36, 36, 10, s["band"], s["out_edge"], 1))
        parts.append(
            svg_text(664, y + 38, glyph, 15, s["out_text"], anchor="middle", bold=True)
        )
        parts.append(svg_text(694, y + 25, f"{en} · {cn}", 13.5, s["out_text"], bold=True))
        parts.append(svg_text(694, y + 45, detail, 11, s["faint"], mono=True))
        parts.append(
            svg_text(1024, y + 25, "not checked", 11, s["out_text"], mono=True, anchor="end")
        )
    parts.append(
        svg_text(636, 508, "A register records text; these four live on the document itself.",
                 11, s["out_text"])
    )
    parts.append(
        svg_text(636, 526, "The check never claims them, and the report never implies them.",
                 11, s["faint"])
    )

    # ---- report -----------------------------------------------------------
    parts.append(rect(44, 552, 640, 84, 16, s["card"], s["card_edge"], 1.2,
                      extra='filter="url(#soft)"'))
    parts.append(svg_text(64, 574, "OUT · issues[]", 11, s["accent"], mono=True, bold=True))
    warn_pill, warn_w = svg_pill(664 - 82, 560, "1 warn", 11, s["warn"], s["warn_bg"])
    parts.append(warn_pill)
    parts.append(
        svg_text(64, 596, "row 1 · column docNo", 11.5, s["sub"], mono=True)
    )
    parts.append(
        svg_text(64, 620, "某政发[2026]15号", 13, s["text"])
    )
    parts.append(svg_text(238, 620, "→", 13, s["faint"]))
    parts.append(svg_text(264, 620, "某政发〔2026〕15号", 13, s["accent"], bold=True))

    parts.append(rect(700, 552, 356, 84, 16, s["card"], s["card_edge"], 1.2,
                      extra='filter="url(#soft)"'))
    parts.append(svg_text(720, 574, "skipped[] · 1", 11, s["warn"], mono=True, bold=True))
    parts.append(svg_text(1036, 574, "GW-003", 11, s["faint"], mono=True, anchor="end"))
    parts.append(svg_text(720, 598, "values: []", 11.5, s["sub"], mono=True))
    parts.append(svg_text(812, 598, "→ document-kind list unset", 11.5, s["text"]))
    parts.append(svg_text(720, 622, "empty issues ≠ all clear", 12, s["warn"], bold=True))

    parts.append(
        svg_text(550, 646, "wording guard · no compliance verdict · the verdict stays with the reviewer",
                 11, s["faint"], anchor="middle")
    )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------------------
# Verification helpers
# ---------------------------------------------------------------------------
def verify_hero(path: str) -> None:
    with Image.open(path) as img:
        if img.size != (HERO_W, HERO_H):
            raise SystemExit(f"FATAL: {path} is {img.size}, expected {(HERO_W, HERO_H)}")
        if img.format != "WEBP":
            raise SystemExit(f"FATAL: {path} is {img.format}, expected WEBP")


def verify_flow(svg: str) -> None:
    ET.fromstring(svg)  # well-formed XML, not a string that merely looks like SVG
    if svg.count("<text") < 40:
        raise SystemExit("FATAL: flow SVG is missing labels")
    if 'width="1100"' not in svg or 'height="660"' not in svg:
        raise SystemExit("FATAL: flow SVG canvas is not 1100x660")
    sizes = [float(match) for match in re.findall(r'font-size="([0-9.]+)"', svg)]
    if not sizes or min(sizes) < 11:
        raise SystemExit(f"FATAL: flow text below 11px: {min(sizes)}")
    if sum(1 for size in sizes if size >= 13) < 10:
        raise SystemExit("FATAL: flow lacks enough >=13px node labels")
    for token in ("GW-001", "GW-003", "GW-006", "docKind", "skipped[]", "OUT OF SCOPE"):
        if token not in svg:
            raise SystemExit(f"FATAL: flow SVG is missing {token!r}")


def main() -> None:
    for lang in ("zh", "en"):
        for skin in ("light", "dark"):
            hero(lang, skin)
            verify_hero(os.path.join(OUT, f"{NAME}-hero-{lang}-{skin}.webp"))
    for skin in ("light", "dark"):
        svg = flow_svg(skin)
        verify_flow(svg)
        path = os.path.join(OUT, f"{NAME}-flow-v5-{skin}.svg")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(svg)
        print(f"wrote {os.path.basename(path)}")


if __name__ == "__main__":
    main()
