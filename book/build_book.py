"""Build the printable A5 book: book/build/Learn-to-Code-with-SaiLang-A5.pdf

Run from the project folder:  python book/build_book.py
The examples and mission starters are checked first; the build stops if any is wrong.
"""

import os
import random
import sys

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily, stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Flowable, Frame, KeepTogether, NextPageTemplate, PageBreak,
    PageTemplate, Paragraph, Spacer, Table, TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(HERE, "content"))
sys.path.insert(0, HERE)

# ----- fonts (registered before art.py draws any text) ----------------------------
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("Sans", os.path.join(FONT_DIR, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("Sans-Bold", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Sans-Oblique", os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf")))
pdfmetrics.registerFont(TTFont("Mono", os.path.join(FONT_DIR, "DejaVuSansMono.ttf")))
pdfmetrics.registerFont(TTFont("Mono-Bold", os.path.join(FONT_DIR, "DejaVuSansMono-Bold.ttf")))
registerFontFamily("Sans", normal="Sans", bold="Sans-Bold", italic="Sans-Oblique", boldItalic="Sans-Bold")

from sailang.lexer import KEYWORDS  # noqa: E402
from sailang.stdlib import BUILTINS  # noqa: E402
import art  # noqa: E402
import check_examples  # noqa: E402
from part1 import CHAPTERS_1_5, FRONT_WELCOME, FRONT_HOWTO, FRONT_SETUP  # noqa: E402
from part2 import CHAPTERS_6_10, GLOSSARY, WHERE_NEXT  # noqa: E402
from part3 import EXTRAS, QUOTES  # noqa: E402

OUT_DIR = os.path.join(HERE, "build")
OUT_PDF = os.path.join(OUT_DIR, "Learn-to-Code-with-SaiLang-A5.pdf")

# ----- colours --------------------------------------------------------------------
INK = HexColor("#1D2433")
YELLOW = HexColor("#FFD21F")
ORANGE = HexColor("#FF8A00")
GREEN = HexColor("#22B573")
BLUE = HexColor("#2B7BEA")
PURPLE = HexColor("#8A4FFF")
PINK = HexColor("#FF4FA3")
TEAL = HexColor("#1FC2C2")
RED = HexColor("#FF5A36")
MUTED = HexColor("#5A6275")
CODE_BG = HexColor("#F1F4FA")
OUT_BG = HexColor("#EAF7EF")
OUT_LINE = HexColor("#1E9E5A")
ERR_BG = HexColor("#FDECEC")
ERR_LINE = HexColor("#C62828")
KW_COL = HexColor("#2446C8")
BI_COL = HexColor("#00857A")
STR_COL = HexColor("#15803D")
NUM_COL = HexColor("#D9480F")
COM_COL = HexColor("#7A8194")

CALLOUT_COLOUR = {"tip": GREEN, "watch": RED, "fun": PURPLE, "learn": BLUE, "joke": YELLOW,
                  "mission": PINK, "quiz": TEAL}
CALLOUT_ICON = {"try": "\u25B6", "tip": "\u2713", "watch": "!", "fun": "\u2665", "learn": "\u2192",
                "joke": "\u263A", "mission": "\u2605", "quiz": "?"}
CALLOUT_TITLE = {"tip": "Top tip", "watch": "Watch out!", "fun": "Did you know?", "joke": "Sai's joke",
                 "quiz": "Quick quiz"}
POSES = art.POSES
SCENES = {1: "laptop", 2: "box", 3: "signpost", 4: "loop", 5: "lockers", 6: "wand", 7: "bug",
          8: "notebook", 9: "window", 10: "controller"}


def darker(colour, factor=0.72):
    """A darker shade of a colour, for readable headings."""
    return art.mix(colour, "#000000", 1 - factor)


# ----- styles ---------------------------------------------------------------------
BODY = ParagraphStyle("body", fontName="Sans", fontSize=10, leading=14.6, textColor=INK, spaceAfter=5.5)
SMALL = ParagraphStyle("small", parent=BODY, fontSize=9.2, leading=13.2, spaceAfter=3)
BULLET = ParagraphStyle("bullet", parent=BODY, leftIndent=12, bulletIndent=1, spaceAfter=3)
TOC1 = ParagraphStyle("toc1", fontName="Sans-Bold", fontSize=11.5, leading=20, textColor=INK)
H_BIG = ParagraphStyle("hbig", fontName="Sans-Bold", fontSize=22, leading=26, textColor=PINK, spaceAfter=8)


def heading_style(colour):
    return ParagraphStyle("h", fontName="Sans-Bold", fontSize=12.6, leading=16, textColor=darker(colour),
                          spaceBefore=9, spaceAfter=5, keepWithNext=1,
                          backColor=art.mix(colour, "#FFFFFF", 0.78), borderPadding=(2, 4, 2, 4))


# ----- inline flowables ---------------------------------------------------------------
_pose_counter = [0]


def next_pose():
    """Sai changes pose from one speech bubble to the next."""
    pose = POSES[_pose_counter[0] % len(POSES)]
    _pose_counter[0] += 1
    return pose


class Bubble(Flowable):
    """Speech bubble from Sai the robot. The robot alternates between the left and the right."""

    def __init__(self, text, colour, pose, side="left"):
        Flowable.__init__(self)
        self.text = text
        self.colour = colour
        self.pose = pose
        self.side = side
        self.pad = 4 * mm
        self.scale = 4.4 * mm
        self.robot_room = 31 * mm

    def wrap(self, aw, ah):
        self.W = aw
        self.para = Paragraph(self.text, ParagraphStyle("bub", parent=BODY, fontSize=10.4, leading=15.2,
                                                        spaceAfter=0))
        _, ph = self.para.wrap(aw - self.robot_room - 2 * self.pad, 10000)
        self.ph = ph
        self.H = max(ph + 2 * self.pad, 34 * mm)
        return aw, self.H

    def draw(self):
        c = self.canv
        mid = self.H / 2
        left = self.side == "left"
        box_x = self.robot_room if left else 0
        box_w = self.W - self.robot_room
        tail_x = box_x if left else box_x + box_w
        tail_dx = -4.4 * mm if left else 4.4 * mm
        c.saveState()
        c.setFillColor(white)
        c.setStrokeColor(self.colour)
        c.setLineWidth(2.2)
        c.roundRect(box_x, 0, box_w, self.H, 4.5 * mm, stroke=1, fill=1)
        p = c.beginPath()
        p.moveTo(tail_x + (0.6 if left else -0.6), mid + 3.2 * mm)
        p.lineTo(tail_x + tail_dx, mid)
        p.lineTo(tail_x + (0.6 if left else -0.6), mid - 3.2 * mm)
        p.close()
        c.drawPath(p, stroke=0, fill=1)
        c.line(tail_x, mid + 3.2 * mm, tail_x + tail_dx, mid)
        c.line(tail_x + tail_dx, mid, tail_x, mid - 3.2 * mm)
        self.para.drawOn(c, box_x + self.pad, (self.H - self.ph) / 2)
        c.restoreState()
        s = self.scale
        robot_x = 13 * mm if left else self.W - 13 * mm
        art.robot(c, robot_x, mid - 0.6 * s, s, self.pose)


class Callout(Flowable):
    """A box with an icon and a title. It can be tilted like a sticker, dashed, or burst-shaped."""

    def __init__(self, kind, title, paragraphs, colour=None, tilt=0, dashed=False, burst=False):
        Flowable.__init__(self)
        self.kind = kind
        self.title = title
        self.paragraphs = paragraphs
        self.colour = colour or CALLOUT_COLOUR.get(kind, BLUE)
        self.pad = 3.4 * mm
        self.icon = CALLOUT_ICON.get(kind, "\u25B6")
        self.tilt = tilt
        self.dashed = dashed
        self.burst = burst

    def wrap(self, aw, ah):
        self.W = aw
        self.inner = aw - 2 * self.pad - 9 * mm
        self.heights = []
        total = self.pad + 6.5 * mm
        for text in self.paragraphs:
            para = Paragraph(text, SMALL)
            _, ph = para.wrap(self.inner, 10000)
            self.heights.append((para, ph))
            total += ph + 1.4 * mm
        self.H = total + self.pad - 1.4 * mm
        return aw, self.H

    def draw(self):
        c = self.canv
        c.saveState()
        if self.tilt:
            c.translate(self.W / 2, self.H / 2)
            c.rotate(self.tilt)
            c.translate(-self.W / 2, -self.H / 2)
        c.setFillColor(HexColor("#FFF9D6") if self.kind == "joke" else white)
        c.setStrokeColor(self.colour)
        c.setLineWidth(1.8)
        if self.dashed:
            c.setDash(5, 3)
        c.roundRect(0, 0, self.W, self.H, 3.5 * mm, stroke=1, fill=1)
        c.setDash()
        cx, cy = self.pad + 3.5 * mm, self.H - self.pad - 3.5 * mm
        if self.burst:
            art.starburst(c, cx, cy, 5.6 * mm, 4.6 * mm, 12, self.colour)
        c.setFillColor(self.colour)
        c.setStrokeColor(INK)
        c.setLineWidth(0.8)
        c.circle(cx, cy, 3.6 * mm, stroke=1, fill=1)
        c.setFillColor(INK if self.colour == YELLOW else white)
        c.setFont("Sans-Bold", 9)
        c.drawCentredString(cx, cy - 3.2, self.icon)
        dark_text = self.colour in (YELLOW, TEAL)
        c.setFillColor(darker(self.colour, 0.55) if dark_text else darker(self.colour))
        c.setFont("Sans-Bold", 10.5)
        c.drawString(self.pad + 9 * mm, self.H - self.pad - 4.2, self.title)
        y = self.H - self.pad - 6.5 * mm
        for para, ph in self.heights:
            para.drawOn(c, self.pad + 9 * mm, y - ph)
            y -= ph + 1.4 * mm
        c.restoreState()


class Quote(Flowable):
    """A large pull quote from Sai, with a thick coloured bar and a big quote mark."""

    def __init__(self, text, colour):
        Flowable.__init__(self)
        self.text = text
        self.colour = colour

    def wrap(self, aw, ah):
        self.W = aw
        style = ParagraphStyle("pq", fontName="Sans-Bold", fontSize=13.5, leading=18.5, textColor=darker(self.colour, 0.8),
                               leftIndent=14 * mm)
        self.para = Paragraph(self.text, style)
        _, ph = self.para.wrap(aw, 10000)
        self.H = max(ph, 14 * mm) + 3 * mm
        return aw, self.H

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(self.colour)
        c.roundRect(0, 0, 2.6 * mm, self.H, 1.2 * mm, stroke=0, fill=1)
        c.setFont("Sans-Bold", 40)
        c.drawString(3.5 * mm, self.H - 10 * mm, "\u201C")
        self.para.drawOn(c, 0, (self.H - self.para.height) / 2)
        c.restoreState()


class CodeBlock(Flowable):
    """A SaiLang program with coloured keywords, then its output, its error, or a window note."""

    def __init__(self, src, transcript="", error=None, gui=False, note=None, label=None, label_colour=None):
        Flowable.__init__(self)
        self.label = label
        self.label_colour = label_colour or PINK
        self.lines = src.split("\n")
        self.out_lines = transcript.rstrip().split("\n") if transcript.strip() else []
        self.err_lines = error.split("\n") if error else []
        self.gui = gui
        self.note = note
        self.pad = 3 * mm

    def _segments(self, line):
        segs, pos = [], 0
        for match in check_examples.TOKEN_RE.finditer(line):
            if match.start() > pos:
                segs.append((line[pos:match.start()], INK, "Mono"))
            word = match.group(0)
            if word[0] == "#":
                segs.append((word, COM_COL, "Mono"))
            elif word[0] == '"':
                segs.append((word, STR_COL, "Mono"))
            elif word[0].isdigit():
                segs.append((word, NUM_COL, "Mono"))
            elif word in KEYWORDS:
                segs.append((word, KW_COL, "Mono-Bold"))
            elif word in BUILTINS:
                segs.append((word, BI_COL, "Mono"))
            else:
                segs.append((word, INK, "Mono"))
            pos = match.end()
        if pos < len(line):
            segs.append((line[pos:], INK, "Mono"))
        return segs

    def wrap(self, aw, ah):
        self.W = aw
        inner = aw - 2 * self.pad
        all_lines = self.lines + self.out_lines + self.err_lines
        widest = max([stringWidth(line, "Mono", 8.4) for line in all_lines] or [0])
        self.size = 8.4 if widest <= inner else max(6.6, 8.4 * inner / widest)
        self.lead = self.size * 1.45
        self.code_h = 2 * self.pad + len(self.lines) * self.lead
        h = self.code_h
        self.out_h = 2 * self.pad + 4.2 * mm + len(self.out_lines) * self.lead if self.out_lines else 0
        self.err_h = 2 * self.pad + 4.2 * mm + len(self.err_lines) * self.lead if self.err_lines else 0
        if self.out_lines:
            h += 2 * mm + self.out_h
        if self.err_lines:
            h += 2 * mm + self.err_h
        if self.gui:
            texts = ["Window example. Type it in and press F5 in SaiLang IDLE. A window opens."]
            if self.note:
                texts.append(self.note)
            self.note_paras = [Paragraph(t, SMALL) for t in texts]
            heights = [para.wrap(inner, 1000)[1] for para in self.note_paras]
            self.note_h = 2 * self.pad + sum(heights) + 1.5 * mm * (len(heights) - 1)
            h += 2 * mm + self.note_h
        self.H = h
        return aw, h

    def draw(self):
        c = self.canv
        top = self.H
        c.saveState()
        c.setFillColor(CODE_BG)
        c.roundRect(0, top - self.code_h, self.W, self.code_h, 2.5 * mm, stroke=0, fill=1)
        for i, line in enumerate(self.lines):
            baseline = top - self.pad - i * self.lead - self.size * 0.95
            x = self.pad
            for text, colour, font in self._segments(line):
                c.setFont(font, self.size)
                c.setFillColor(colour)
                c.drawString(x, baseline, text)
                x += stringWidth(text, font, self.size)
        self._draw_label(top)
        y = top - self.code_h
        if self.out_lines:
            y -= 2 * mm
            self._box(y - self.out_h, self.out_h, OUT_BG, OUT_LINE, "OUTPUT", self.out_lines, INK)
            y -= self.out_h
        if self.err_lines:
            y -= 2 * mm
            self._box(y - self.err_h, self.err_h, ERR_BG, ERR_LINE, "ERROR", self.err_lines,
                      HexColor("#8B0000"))
            y -= self.err_h
        if self.gui:
            y -= 2 * mm
            c.setFillColor(HexColor("#E8F3FF"))
            c.setStrokeColor(BLUE)
            c.setLineWidth(1)
            c.roundRect(0, y - self.note_h, self.W, self.note_h, 2.5 * mm, stroke=1, fill=1)
            ty = y - self.pad
            for para in self.note_paras:
                ty -= para.height
                para.drawOn(c, self.pad, ty)
                ty -= 1.5 * mm
        c.restoreState()

    def _draw_label(self, top):
        if not self.label:
            return
        c = self.canv
        c.saveState()
        c.setFont("Sans-Bold", 7.6)
        width = stringWidth(self.label, "Sans-Bold", 7.6) + 6 * mm
        x = self.W - width - 2 * mm
        c.translate(x + width / 2, top - 1.5 * mm)
        c.rotate(3)
        c.setFillColor(self.label_colour)
        c.setStrokeColor(INK)
        c.setLineWidth(0.9)
        c.roundRect(-width / 2, -2.6 * mm, width, 5.2 * mm, 2.6 * mm, stroke=1, fill=1)
        c.setFillColor(white if self.label_colour not in (YELLOW,) else INK)
        c.drawCentredString(0, -1.3 * mm, self.label)
        c.restoreState()

    def _box(self, bottom, height, fill, line, label, lines, text_colour):
        c = self.canv
        c.saveState()
        c.setFillColor(fill)
        c.setStrokeColor(line)
        c.setLineWidth(1)
        c.roundRect(0, bottom, self.W, height, 2.5 * mm, stroke=1, fill=1)
        c.setFillColor(line)
        c.setFont("Sans-Bold", 7)
        c.drawString(self.pad, bottom + height - self.pad - 2.6, label)
        base = bottom + height - self.pad - 4.2 * mm - self.size * 0.95
        for i, text in enumerate(lines):
            c.setFont("Mono", self.size)
            c.setFillColor(text_colour)
            c.drawString(self.pad, base - i * self.lead, text)
        c.restoreState()


class ChapterOpener(Flowable):
    """A bright banner with stripes, confetti, a number, a title and a scene or a robot."""

    def __init__(self, num, title, colour, scene=None, toc=False, height=60 * mm, pose=None, seed=1,
                 pattern="stripes"):
        Flowable.__init__(self)
        self.pattern = pattern
        self.num = num
        self.title = title
        self.colour = colour
        self.scene = scene
        self.height_mm = height
        self.pose = pose
        self.seed = seed
        self.toc_text = (f"{num}&nbsp;&nbsp;{title}" if num else title) if toc else None

    def wrap(self, aw, ah):
        self.W = aw
        self.H = self.height_mm
        return aw, self.H

    def draw(self):
        c = self.canv
        W, H = self.W, self.H
        c.saveState()
        path = c.beginPath()
        path.roundRect(0, 0, W, H, 5 * mm)
        c.clipPath(path, stroke=0, fill=0)
        c.setFillColor(self.colour)
        c.rect(0, 0, W, H, stroke=0, fill=1)
        rng = random.Random(self.seed * 97)
        if self.pattern == "stripes":
            c.setStrokeColor(white)
            c.setLineWidth(9)
            c.setStrokeAlpha(0.14)
            for k in range(-4, 16):
                x = k * 14 * mm
                c.line(x, 0, x + H, H)
        elif self.pattern == "dots":
            c.setFillColor(white)
            c.setFillAlpha(0.22)
            for i in range(0, int(W / (5 * mm)) + 1):
                for j in range(0, int(H / (5 * mm)) + 1):
                    c.circle(i * 5 * mm + (j % 2) * 2.5 * mm, j * 5 * mm, 0.9 * mm, stroke=0, fill=1)
        elif self.pattern == "zigzag":
            c.setFillColor(white)
            c.setFillAlpha(0.25)
            p = c.beginPath()
            p.moveTo(0, 0)
            for i in range(0, int(W / (6 * mm)) + 2):
                p.lineTo(i * 6 * mm, 12 * mm if i % 2 else 4 * mm)
            p.lineTo(W, 0)
            p.close()
            c.drawPath(p, stroke=0, fill=1)
        else:  # circles
            for _ in range(7):
                c.setFillColor(white)
                c.setFillAlpha(0.13)
                c.circle(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(6, 16) * mm, stroke=0, fill=1)
        c.setStrokeAlpha(1)
        c.setFillAlpha(1)
        art.confetti(c, 0, 0, W, H, 26, seed=self.seed * 13 + 5,
                     colours=["#FFFFFF", "#FFD21F", "#FF4FA3", "#22B573", "#2B7BEA"])
        c.restoreState()

        text_x = 10 * mm
        if self.num:
            cx, cy = 19 * mm, H - 25 * mm
            art.starburst(c, cx, cy, 15 * mm, 11.5 * mm, 12, "#FFFFFF")
            c.saveState()
            c.setFillColor(self.colour)
            c.circle(cx, cy, 7.5 * mm, stroke=0, fill=1)
            c.setFillColor(white)
            c.setFont("Sans-Bold", 20)
            c.drawCentredString(cx, cy - 7, str(self.num))
            c.restoreState()
            text_x = 37 * mm
        style = ParagraphStyle("ot", fontName="Sans-Bold", fontSize=17.5, leading=21, textColor=white)
        para = Paragraph(self.title, style)
        right_limit = W - 30 * mm if (self.scene or self.pose) else W - 8 * mm
        _, ph = para.wrap(right_limit - text_x, 1000)
        para.drawOn(c, text_x, H - 12 * mm - ph)
        if self.scene:
            art.icon(c, self.scene, W - 26 * mm, 8 * mm, 1.9 * mm)
        elif self.pose:
            art.robot(c, W - 15 * mm, 12 * mm, 2.6 * mm, self.pose)


def mission_parts(mission):
    """A mission callout with its starter code, kept together on one page."""
    parts = [Callout("mission", mission["title"], [mission["goal"]]), Spacer(1, 2 * mm)]
    if mission.get("starter"):
        parts.append(CodeBlock(mission["starter"]))
    return parts


def table_block(rows, width):
    left = ParagraphStyle("tl", parent=SMALL, fontName="Mono-Bold", fontSize=8.8, leading=12)
    right = ParagraphStyle("tr", parent=SMALL)
    data = [[Paragraph(a, left), Paragraph(b, right)] for a, b in rows]
    table = Table(data, colWidths=[width * 0.36, width * 0.64], hAlign="LEFT")
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.8, HexColor("#D5DBE8")),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


# ----- document -----------------------------------------------------------------------
class BookDoc(BaseDocTemplate):
    def afterFlowable(self, flowable):
        text = getattr(flowable, "toc_text", None)
        if text:
            self.notify("TOCEntry", (0, text, self.page))


def draw_cover(c, doc):
    W, H = A5
    c.saveState()
    c.setFillColor(PINK)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    art.confetti(c, 0, 0, W, H, 70, seed=21)
    art.starburst(c, W / 2, 128 * mm, 74 * mm, 56 * mm, 18, "#FFD21F")
    art.rainbow(c, W / 2, 6 * mm, 64 * mm, 5 * mm)

    art.outlined_text(c, W / 2, 164 * mm, "LEARN TO CODE", "Sans-Bold", 24, "#FFFFFF", INK, 2.2)

    c.saveState()
    c.translate(W / 2, 137 * mm)
    c.rotate(5)
    c.setFillColor(BLUE)
    c.setStrokeColor(INK)
    c.setLineWidth(2.4)
    c.roundRect(-64 * mm, -17 * mm, 128 * mm, 34 * mm, 8 * mm, stroke=1, fill=1)
    art.outlined_text(c, 0, -5.2 * mm, "with SaiLang", "Sans-Bold", 30, "#FFFFFF", INK, 1.6)
    c.restoreState()

    c.saveState()
    c.setFillColor(white)
    c.setStrokeColor(INK)
    c.setLineWidth(1.4)
    c.roundRect(W / 2 - 57 * mm, 106 * mm, 114 * mm, 11 * mm, 5.5 * mm, stroke=1, fill=1)
    c.setFillColor(INK)
    c.setFont("Sans-Bold", 9.6)
    c.drawCentredString(W / 2, 109.4 * mm, "A fun first book for beginners!")
    c.restoreState()

    c.saveState()
    c.translate(W - 22 * mm, H - 24 * mm)
    c.rotate(10)
    art.star(c, 0, 0, 14 * mm, 10.5 * mm, 12, "#FF8A00")
    c.setFillColor(INK)
    c.setFont("Sans-Bold", 8.5)
    c.drawCentredString(0, -1.6 * mm, "AGES 9+")
    c.restoreState()

    art.robot(c, W / 2, 6 * mm + 2.9 * 8.6 * mm, 8.6 * mm, "cheer")
    c.saveState()
    c.setFillColor(white)
    c.setFont("Sans-Bold", 7.5)
    c.drawString(9 * mm, H - 9 * mm, "FIRST EDITION")
    c.restoreState()
    c.restoreState()


def draw_body(c, doc):
    W, H = A5
    colours = ["#FF4FA3", "#FFD21F", "#22B573", "#2B7BEA", "#8A4FFF", "#FF8A00"]
    c.saveState()
    c.setFillColor(MUTED)
    c.setFont("Sans", 7)
    c.drawString(14 * mm, H - 10 * mm, "Learn to Code with SaiLang")
    c.drawRightString(W - 14 * mm, 9 * mm, str(doc.page))
    c.restoreState()
    rng = random.Random(doc.page * 31 + 7)
    for _ in range(5):                       # stars and squiggles in the side margins
        side = rng.choice([-1, 1])
        x = (W - 6 * mm) if side > 0 else 6 * mm
        y = rng.uniform(20 * mm, H - 20 * mm)
        colour = colours[rng.randrange(len(colours))]
        if rng.random() < 0.6:
            c.saveState()
            c.translate(x, y)
            c.rotate(rng.uniform(-30, 30))
            art.star(c, 0, 0, rng.uniform(2.2, 3.2), 1.1, 5, colour)
            c.restoreState()
        else:
            art.doodle(c, x, y, "squiggle", colour)


LABELS = [("Type this!", PINK), ("Try me!", ORANGE), ("Watch it run!", GREEN), ("Copy me!", BLUE)]
TILTS = [-2.5, 2, -1.5, 2.5, -2, 1.5]
PATTERNS = ["stripes", "dots", "zigzag", "circles"]


def build_story(transcripts):
    story = []
    body_w = A5[0] - 28 * mm
    state = {"bubble": 0, "code": 0, "tilt": 0}

    def add_block(block, colour):
        kind = block["type"]
        if kind == "p":
            story.append(Paragraph(block["text"], BODY))
        elif kind == "h":
            story.append(Paragraph(block["text"], heading_style(colour)))
        elif kind == "bubble":
            side = "left" if state["bubble"] % 2 == 0 else "right"
            story.append(Bubble(block["text"], colour, next_pose(), side=side))
            state["bubble"] += 1
            story.append(Spacer(1, 4 * mm))
        elif kind == "code":
            transcript, error = transcripts.get(id(block), ("", None))
            shows_output = "out" in block or "error" in block
            if block.get("gui"):
                label, label_colour = "Make a window!", PURPLE
            elif "error" in block:
                label, label_colour = "Oops!", RED
            else:
                label, label_colour = LABELS[state["code"] % len(LABELS)]
                state["code"] += 1
            story.append(CodeBlock(
                block["src"],
                transcript=transcript if shows_output else "",
                error=error if "error" in block else None,
                gui=block.get("gui", False),
                note=block.get("gui_note"),
                label=label, label_colour=label_colour,
            ))
            story.append(Spacer(1, 4 * mm))
        elif kind == "try":
            steps = [f"<b>{i}.</b> {s}" for i, s in enumerate(block["steps"], 1)]
            story.append(Callout("try", block["title"], steps, colour=colour, dashed=True))
            story.append(Spacer(1, 4 * mm))
        elif kind in ("tip", "watch", "fun"):
            tilt = TILTS[state["tilt"] % len(TILTS)] if kind == "fun" else 0
            state["tilt"] += 1
            story.append(Callout(kind, CALLOUT_TITLE[kind], [block["text"]], tilt=tilt, burst=(kind == "fun")))
            story.append(Spacer(1, 4 * mm))
        elif kind == "list":
            for item in block["items"]:
                story.append(Paragraph(item, BULLET, bulletText="\u2022"))
        elif kind == "table":
            story.append(table_block(block["rows"], body_w))
            story.append(Spacer(1, 4 * mm))
        else:
            raise ValueError(f"unknown block type {kind}")

    story.append(Spacer(1, 1 * mm))
    story.append(NextPageTemplate("body"))
    story.append(PageBreak())

    story.append(Paragraph("Contents", H_BIG))
    toc = TableOfContents()
    toc.levelStyles = [TOC1]
    story.append(toc)
    story.append(PageBreak())

    fronts = [(FRONT_WELCOME, "wave", None, "stripes"), (FRONT_HOWTO, "cheer", None, "dots"),
              (FRONT_SETUP, None, "laptop", "circles")]
    for index, (front, pose, scene, pattern) in enumerate(fronts):
        story.append(ChapterOpener(None, front["title"], BLUE, scene=scene, pose=pose, height=40 * mm,
                                   seed=index + 2, pattern=pattern))
        story.append(Spacer(1, 4 * mm))
        for block in front["blocks"]:
            add_block(block, BLUE)
        story.append(PageBreak())

    for chapter in CHAPTERS_1_5 + CHAPTERS_6_10:
        num = chapter["num"]
        colour = HexColor(chapter["colour"])
        pattern = PATTERNS[(num - 1) % len(PATTERNS)]
        story.append(ChapterOpener(num, chapter["title"], colour, scene=SCENES[num], toc=True, seed=num,
                                   pattern=pattern))
        story.append(Spacer(1, 5 * mm))
        learn_items = [f"\u2022&nbsp;&nbsp;{item}" for item in chapter["learn"]]
        story.append(Callout("learn", "What you will learn", learn_items, colour=colour, tilt=-1))
        story.append(Spacer(1, 3 * mm))
        extra = EXTRAS.get(num, {})
        if QUOTES.get(num):
            story.append(Quote(QUOTES[num], colour))
            story.append(Spacer(1, 4 * mm))
        for block in chapter["blocks"]:
            add_block(block, colour)
        if extra.get("joke"):
            story.append(Callout("joke", "Sai's joke", [extra["joke"]], tilt=TILTS[num % len(TILTS)]))
            story.append(Spacer(1, 4 * mm))
        if extra.get("mission"):
            story.append(KeepTogether(mission_parts(extra["mission"])))
            story.append(Spacer(1, 4 * mm))
        if extra.get("quiz"):
            questions = [f"<b>Q{i}.</b> {q}" for i, (q, _a) in enumerate(extra["quiz"], 1)]
            story.append(KeepTogether([Callout("quiz", "Quick quiz", questions, tilt=-1.5)]))
        story.append(PageBreak())

    story.append(ChapterOpener(None, "Glossary", PURPLE, toc=True, height=40 * mm, pose="think", seed=31,
                               pattern="dots"))
    story.append(Spacer(1, 4 * mm))
    rows = [(f"<b>{term}</b>", definition) for term, definition in GLOSSARY]
    story.append(table_block(rows, body_w))
    story.append(PageBreak())

    story.append(ChapterOpener(None, "Answers to the quizzes", TEAL, toc=True, height=40 * mm, pose="cool",
                               seed=32, pattern="zigzag"))
    story.append(Spacer(1, 4 * mm))
    for chapter in CHAPTERS_1_5 + CHAPTERS_6_10:
        extra = EXTRAS.get(chapter["num"], {})
        if not extra.get("quiz"):
            continue
        story.append(Paragraph(f"Chapter {chapter['num']}: {chapter['title']}",
                               heading_style(HexColor(chapter["colour"]))))
        for i, (_question, answer) in enumerate(extra["quiz"], 1):
            story.append(Paragraph(f"<b>Q{i}.</b> {answer}", BULLET, bulletText="\u2022"))
    story.append(PageBreak())

    story.append(ChapterOpener(None, "Where next?", GREEN, toc=True, height=40 * mm, pose="cheer", seed=33,
                               pattern="circles"))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("You have finished the book. Here are some ideas to keep going:", BODY))
    for idea in WHERE_NEXT:
        story.append(Paragraph(idea, BULLET, bulletText="\u2022"))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("Keep your programs in one folder, share them with friends, and never stop asking "
                           "\u201cwhat happens if I change this?\u201d", BODY))
    return story


def collect_transcripts(chapters):
    """Run every example once and remember what the book should display."""
    results = {}
    blocks = [b for ch in chapters for b in ch["blocks"]]
    blocks += [b for front in (FRONT_WELCOME, FRONT_HOWTO, FRONT_SETUP) for b in front["blocks"]]
    for block in blocks:
        if block["type"] == "code" and not block.get("gui"):
            results[id(block)] = check_examples.transcript_for(block)
    return results


def check_extras(chapters):
    """Mission starter code must parse, and every chapter needs a quiz."""
    from sailang.errors import SaiError
    from sailang.parser import parse
    problems = []
    for chapter in chapters:
        extra = EXTRAS.get(chapter["num"], {})
        mission = extra.get("mission")
        if mission and mission.get("starter"):
            try:
                parse(mission["starter"], "mission.sai")
            except SaiError as err:
                problems.append(f"chapter {chapter['num']} mission starter: {err.format()}")
        if not extra.get("quiz"):
            problems.append(f"chapter {chapter['num']} has no quiz")
    return problems


def main():
    chapters = CHAPTERS_1_5 + CHAPTERS_6_10
    checked, problems = check_examples.run_all(chapters, windows=bool(os.environ.get("DISPLAY")))
    problems += check_extras(chapters)
    if problems:
        print("Examples have problems. The book was not built:")
        for problem in problems:
            print(" -", problem)
        return 1
    os.makedirs(OUT_DIR, exist_ok=True)
    transcripts = collect_transcripts(chapters)
    story = build_story(transcripts)

    doc = BookDoc(OUT_PDF, pagesize=A5, leftMargin=14 * mm, rightMargin=14 * mm,
                  topMargin=16 * mm, bottomMargin=16 * mm,
                  title="Learn to Code with SaiLang", author="SaiLang contributors")
    cover_frame = Frame(0, 0, A5[0], A5[1], leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
                        id="cover")
    body_frame = Frame(14 * mm, 16 * mm, A5[0] - 28 * mm, A5[1] - 32 * mm, id="body")
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[cover_frame], onPage=draw_cover),
        PageTemplate(id="body", frames=[body_frame], onPage=draw_body),
    ])
    doc.multiBuild(story)
    print(f"Checked {checked} examples and all mission starters. Wrote {OUT_PDF}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
