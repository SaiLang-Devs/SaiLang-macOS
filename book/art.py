"""Illustrations for the SaiLang book, drawn with reportlab's canvas.

Everything is drawn with flat or gradient fills and thin ink outlines.
There are no drop shadows. Highlights are light shapes placed on top of a fill.
"""

import math
import random

from reportlab.lib.colors import HexColor, white

INK = HexColor("#1D2433")
PALETTE = ["#FF4FA3", "#FFD21F", "#22B573", "#2B7BEA", "#8A4FFF", "#FF8A00", "#1FC2C2", "#FF5A36"]


def rgb(hex_or_colour):
    if isinstance(hex_or_colour, str):
        return HexColor(hex_or_colour)
    return hex_or_colour


def mix(a, b, t):
    a, b = rgb(a), rgb(b)
    return HexColor("#%02X%02X%02X" % tuple(int((x + (y - x) * t) * 255) for x, y in
                                          ((a.red, b.red), (a.green, b.green), (a.blue, b.blue))))


def gradient_rect(c, x, y, w, h, r, top, bottom, steps=14, vertical=True):
    """A rounded rectangle filled with a smooth gradient (drawn as bands, clipped to the shape)."""
    c.saveState()
    path = c.beginPath()
    path.roundRect(x, y, w, h, r)
    c.clipPath(path, stroke=0, fill=0)
    for i in range(steps):
        t0 = i / steps
        colour = mix(top, bottom, t0)
        c.setFillColor(colour)
        if vertical:
            band_h = h / steps + 0.5
            c.rect(x, y + h - (i + 1) * h / steps, w, band_h, stroke=0, fill=1)
        else:
            band_w = w / steps + 0.5
            c.rect(x + i * w / steps, y, band_w, h, stroke=0, fill=1)
    c.restoreState()


def glow(c, x, y, radius, colour, alpha=0.35, rings=3):
    c.saveState()
    for i in range(rings, 0, -1):
        c.setFillColor(rgb(colour))
        c.setFillAlpha(alpha / rings)
        c.circle(x, y, radius * i / rings, stroke=0, fill=1)
    c.restoreState()


def highlight(c, x, y, w, h, alpha=0.55):
    c.saveState()
    c.setFillColor(white)
    c.setFillAlpha(alpha)
    c.ellipse(x, y, x + w, y + h, stroke=0, fill=1)
    c.restoreState()


# ----- Sai the robot ---------------------------------------------------------------
POSES = ("wave", "think", "cheer", "point", "cool")


def robot(c, cx, cy, s, pose="wave"):
    """Sai the robot. cx, cy is the centre of the body. s is the unit size.

    Total height is about 5.2 units, from cy - 2.9s (feet) to cy + 2.3s (antenna top).
    """
    ink_w = max(0.5, 0.13 * s)
    c.saveState()
    c.setStrokeColor(INK)
    c.setLineWidth(ink_w)
    c.setLineCap(1)

    # arms and hands, behind the body
    shoulder_l = (cx - 1.15 * s, cy - 0.35 * s)
    shoulder_r = (cx + 1.15 * s, cy - 0.35 * s)
    if pose == "wave":
        elbow_l, hand_l = (cx - 1.85 * s, cy - 0.7 * s), (cx - 2.25 * s, cy + 0.25 * s)
        elbow_r, hand_r = (cx + 1.9 * s, cy + 0.6 * s), (cx + 2.2 * s, cy + 1.7 * s)
    elif pose == "think":
        elbow_l, hand_l = (cx - 1.9 * s, cy - 0.7 * s), (cx - 1.7 * s, cy - 1.6 * s)
        elbow_r, hand_r = (cx + 1.5 * s, cy + 0.1 * s), (cx + 0.5 * s, cy + 1.0 * s)
    elif pose == "cheer":
        elbow_l, hand_l = (cx - 2.1 * s, cy + 0.6 * s), (cx - 2.0 * s, cy + 1.9 * s)
        elbow_r, hand_r = (cx + 2.1 * s, cy + 0.6 * s), (cx + 2.0 * s, cy + 1.9 * s)
    elif pose == "point":
        elbow_l, hand_l = (cx - 1.8 * s, cy - 0.9 * s), (cx - 2.1 * s, cy - 1.7 * s)
        elbow_r, hand_r = (cx + 2.0 * s, cy - 0.1 * s), (cx + 2.9 * s, cy + 0.1 * s)
    else:  # cool
        elbow_l, hand_l = (cx - 1.9 * s, cy - 0.5 * s), (cx - 1.6 * s, cy - 1.5 * s)
        elbow_r, hand_r = (cx + 1.9 * s, cy - 0.5 * s), (cx + 1.6 * s, cy - 1.5 * s)

    for shoulder, elbow, hand in ((shoulder_l, elbow_l, hand_l), (shoulder_r, elbow_r, hand_r)):
        c.setLineWidth(0.42 * s + ink_w * 2)
        c.setStrokeColor(INK)
        c.line(shoulder[0], shoulder[1], elbow[0], elbow[1])
        c.line(elbow[0], elbow[1], hand[0], hand[1])
        c.setLineWidth(0.36 * s)
        c.setStrokeColor(rgb("#CFF6FF"))
        c.line(shoulder[0], shoulder[1], elbow[0], elbow[1])
        c.line(elbow[0], elbow[1], hand[0], hand[1])
        c.setStrokeColor(INK)
        c.setLineWidth(ink_w)
    for hand in (hand_l, hand_r):
        gradient_rect(c, hand[0] - 0.36 * s, hand[1] - 0.36 * s, 0.72 * s, 0.72 * s, 0.36 * s,
                      "#FFFFFF", "#8FDFF5", steps=6)
        c.setStrokeColor(INK)
        c.circle(hand[0], hand[1], 0.36 * s, stroke=1, fill=0)
    if pose == "point":
        tip = (hand_r[0] + 0.6 * s, hand_r[1])
        c.setStrokeColor(INK)
        c.setLineWidth(ink_w)
        c.line(hand_r[0] + 0.25 * s, hand_r[1], tip[0], tip[1])

    # legs and feet
    for leg_x in (cx - 0.5 * s, cx + 0.5 * s):
        gradient_rect(c, leg_x - 0.27 * s, cy - 2.25 * s, 0.54 * s, 0.6 * s, 0.2 * s, "#5EEAF0", "#1C7ED6", steps=5)
        c.setStrokeColor(INK)
        c.setLineWidth(ink_w)
        c.roundRect(leg_x - 0.27 * s, cy - 2.25 * s, 0.54 * s, 0.6 * s, 0.2 * s, stroke=1, fill=0)
        gradient_rect(c, leg_x - 0.55 * s, cy - 2.9 * s, 1.1 * s, 0.48 * s, 0.22 * s, "#FFD21F", "#FF8A00", steps=4)
        c.setStrokeColor(INK)
        c.roundRect(leg_x - 0.55 * s, cy - 2.9 * s, 1.1 * s, 0.48 * s, 0.22 * s, stroke=1, fill=0)

    # neck
    c.setFillColor(rgb("#3AB7D6"))
    c.setStrokeColor(INK)
    c.rect(cx - 0.3 * s, cy - 0.2 * s, 0.6 * s, 0.45 * s, stroke=1, fill=1)

    # torso: metallic teal gradient with a rainbow chest panel
    gradient_rect(c, cx - 1.0 * s, cy - 1.95 * s, 2.0 * s, 2.0 * s, 0.55 * s, "#7DF3FF", "#0A6FE0", steps=18)
    c.setStrokeColor(INK)
    c.setLineWidth(ink_w)
    c.roundRect(cx - 1.0 * s, cy - 1.95 * s, 2.0 * s, 2.0 * s, 0.55 * s, stroke=1, fill=0)
    highlight(c, cx - 0.85 * s, cy - 0.3 * s, 0.32 * s, 1.1 * s, alpha=0.45)
    band_colours = ["#FF4FA3", "#FFD21F", "#22B573", "#2B7BEA"]
    for i, colour in enumerate(band_colours):
        c.setFillColor(rgb(colour))
        c.rect(cx - 0.62 * s, cy - 1.05 * s - i * 0.16 * s, 1.24 * s, 0.12 * s, stroke=0, fill=1)
    c.setStrokeColor(INK)
    c.setLineWidth(ink_w * 0.7)
    c.rect(cx - 0.62 * s, cy - 1.05 * s - 3 * 0.16 * s, 1.24 * s, 0.12 * s + 3 * 0.16 * s, stroke=1, fill=0)
    for bx, by in ((cx - 0.8 * s, cy - 1.7 * s), (cx + 0.8 * s, cy - 1.7 * s), (cx - 0.8 * s, cy - 0.3 * s),
                   (cx + 0.8 * s, cy - 0.3 * s)):
        c.setFillColor(rgb("#DDF8FF"))
        c.circle(bx, by, 0.09 * s, stroke=1, fill=1)

    # shoulder joints
    for sx, sy in (shoulder_l, shoulder_r):
        c.setFillColor(rgb("#FF8A00"))
        c.circle(sx, sy, 0.32 * s, stroke=1, fill=1)
        highlight(c, sx - 0.15 * s, sy + 0.05 * s, 0.14 * s, 0.1 * s, alpha=0.8)

    # head: glossy shell
    gradient_rect(c, cx - 1.2 * s, cy + 0.02 * s, 2.4 * s, 1.75 * s, 0.7 * s, "#A8F4FF", "#2B8CF0", steps=16)
    c.setStrokeColor(INK)
    c.setLineWidth(ink_w)
    c.roundRect(cx - 1.2 * s, cy + 0.02 * s, 2.4 * s, 1.75 * s, 0.7 * s, stroke=1, fill=0)
    highlight(c, cx - 0.95 * s, cy + 1.2 * s, 0.9 * s, 0.38 * s, alpha=0.6)

    # antenna with a glowing bulb
    c.setStrokeColor(INK)
    c.setLineWidth(ink_w)
    c.line(cx, cy + 1.77 * s, cx, cy + 2.2 * s)
    glow(c, cx, cy + 2.4 * s, 0.42 * s, "#FF4FA3", alpha=0.5)
    gradient_rect(c, cx - 0.2 * s, cy + 2.2 * s, 0.4 * s, 0.4 * s, 0.2 * s, "#FFB3DA", "#FF4FA3", steps=4)
    c.setStrokeColor(INK)
    c.circle(cx, cy + 2.4 * s, 0.2 * s, stroke=1, fill=0)

    # visor with gradient screen, glowing eyes and a grille
    gradient_rect(c, cx - 0.92 * s, cy + 0.95 * s, 1.84 * s, 0.8 * s, 0.32 * s, "#FF6BD6", "#6A3DFF", steps=10)
    c.setStrokeColor(INK)
    c.setLineWidth(ink_w)
    c.roundRect(cx - 0.92 * s, cy + 0.95 * s, 1.84 * s, 0.8 * s, 0.32 * s, stroke=1, fill=0)
    if pose == "cool":
        c.setFillColor(INK)
        for lx in (cx - 0.46 * s, cx + 0.46 * s):
            c.roundRect(lx - 0.42 * s, cy + 1.04 * s, 0.84 * s, 0.52 * s, 0.2 * s, stroke=1, fill=1)
        c.setStrokeColor(white)
        c.setLineWidth(ink_w * 0.8)
        c.line(cx - 0.9 * s, cy + 1.4 * s, cx - 0.6 * s, cy + 1.22 * s)
        c.line(cx + 0.1 * s, cy + 1.4 * s, cx + 0.4 * s, cy + 1.22 * s)
        c.setStrokeColor(INK)
        c.setLineWidth(ink_w)
    else:
        for ex in (cx - 0.46 * s, cx + 0.46 * s):
            glow(c, ex, cy + 1.35 * s, 0.34 * s, "#FFD21F", alpha=0.6)
            c.setFillColor(rgb("#FFF6A8"))
            c.setStrokeColor(INK)
            c.circle(ex, cy + 1.35 * s, 0.2 * s, stroke=1, fill=1)
            c.setFillColor(INK)
            c.circle(ex + 0.04 * s, cy + 1.36 * s, 0.09 * s, stroke=0, fill=1)
    c.setStrokeColor(INK)
    c.setLineWidth(ink_w)
    if pose == "cheer":
        c.arc(cx - 0.4 * s, cy + 0.25 * s, cx + 0.4 * s, cy + 0.85 * s, 200, 140)
    else:
        c.arc(cx - 0.4 * s, cy + 0.36 * s, cx + 0.4 * s, cy + 0.66 * s, 200, 140)
    c.restoreState()


# ----- scene icons ----------------------------------------------------------------
def _box(c, x, y, w, h, r, top, bottom):
    gradient_rect(c, x, y, w, h, r, top, bottom, steps=10)
    c.setStrokeColor(INK)
    c.setLineWidth(1.1)
    c.roundRect(x, y, w, h, r, stroke=1, fill=0)


def icon(c, name, x, y, s):
    """Draw a chapter icon with its bottom-left at (x, y). s is the unit size (about 1/10 of the icon)."""
    c.saveState()
    c.setStrokeColor(INK)
    c.setLineWidth(max(0.5, 0.11 * s))
    if name == "laptop":  # Chapter 1
        _box(c, x + 0.6 * s, y + 1.0 * s, 8 * s, 6 * s, 0.6 * s, "#7FE0FF", "#2B7BEA")
        c.setFillColor(rgb("#FFFFFF"))
        c.setFont("Mono-Bold", 1.4 * s)
        c.drawString(x + 1.6 * s, y + 4.4 * s, "say")
        _box(c, x, y, 9.2 * s, 1.0 * s, 0.4 * s, "#D6DEEE", "#8E9AB5")
    elif name == "box":  # Chapter 2
        _box(c, x + 1.0 * s, y + 0.2 * s, 7 * s, 6.2 * s, 0.6 * s, "#FFB86B", "#FF8A00")
        c.setFillColor(rgb("#FFF6A8"))
        c.roundRect(x + 2.4 * s, y + 3.0 * s, 4.2 * s, 1.8 * s, 0.4 * s, stroke=1, fill=1)
        c.setFillColor(INK)
        c.setFont("Mono-Bold", 1.3 * s)
        c.drawCentredString(x + 4.5 * s, y + 3.5 * s, "make")
        highlight(c, x + 1.4 * s, y + 5.0 * s, 1.4 * s, 0.7 * s, alpha=0.6)
    elif name == "signpost":  # Chapter 3
        c.setFillColor(rgb("#8E9AB5"))
        c.rect(x + 4.1 * s, y, 0.9 * s, 8.4 * s, stroke=1, fill=1)
        for i, (text, colour, dx) in enumerate((("when", "#2B7BEA", 0.0), ("otherwise", "#22B573", 0.6))):
            top_y = y + 6.4 * s - i * 2.6 * s
            p = c.beginPath()
            p.moveTo(x + 0.3 * s + dx, top_y)
            p.lineTo(x + 7.2 * s + dx, top_y)
            p.lineTo(x + 8.2 * s + dx, top_y + 0.9 * s)
            p.lineTo(x + 7.2 * s + dx, top_y + 1.8 * s)
            p.lineTo(x + 0.3 * s + dx, top_y + 1.8 * s)
            p.close()
            c.setFillColor(rgb(colour))
            c.drawPath(p, stroke=1, fill=1)
            c.setFillColor(white)
            c.setFont("Sans-Bold", 1.1 * s)
            c.drawString(x + 1.0 * s + dx, top_y + 0.6 * s, text)
    elif name == "loop":  # Chapter 4
        c.setLineWidth(1.3 * s)
        c.setStrokeColor(rgb("#FF4FA3"))
        c.arc(x + 0.8 * s, y + 0.8 * s, x + 8.2 * s, y + 8.2 * s, 30, 300)
        c.setStrokeColor(INK)
        c.setLineWidth(max(0.5, 0.11 * s))
        c.setFillColor(rgb("#FF4FA3"))
        cx, cy = x + 4.5 * s, y + 4.5 * s
        p = c.beginPath()
        p.moveTo(x + 8.4 * s, y + 4.6 * s)
        p.lineTo(x + 6.6 * s, y + 6.3 * s)
        p.lineTo(x + 6.6 * s, y + 3.0 * s)
        p.close()
        c.drawPath(p, stroke=1, fill=1)
        c.setFillColor(rgb("#FFD21F"))
        c.circle(cx, cy, 1.4 * s, stroke=1, fill=1)
        c.setFillColor(INK)
        c.setFont("Sans-Bold", 1.3 * s)
        c.drawCentredString(cx, cy - 0.45 * s, "3")
    elif name == "lockers":  # Chapter 5
        colours = ["#FF4FA3", "#FFD21F", "#22B573", "#2B7BEA"]
        for i, colour in enumerate(colours):
            lx = x + i * 2.2 * s
            _box(c, lx, y, 2.0 * s, 8.6 * s, 0.3 * s, "#FFFFFF", colour)
            c.setFillColor(INK)
            c.circle(lx + 1.0 * s, y + 4.3 * s, 0.22 * s, stroke=0, fill=1)
            c.setFont("Mono-Bold", 0.9 * s)
            c.drawCentredString(lx + 1.0 * s, y + 7.3 * s, str(i))
    elif name == "wand":  # Chapter 6
        c.setStrokeColor(INK)
        c.setLineWidth(max(0.5, 0.11 * s))
        gradient_rect(c, x + 0.9 * s, y + 0.5 * s, 1.0 * s, 1.0 * s, 0.4 * s, "#FFD21F", "#FF8A00", steps=4)
        c.setLineWidth(1.4 * s)
        c.setStrokeColor(rgb("#2B7BEA"))
        c.line(x + 1.6 * s, y + 1.4 * s, x + 6.4 * s, y + 6.2 * s)
        c.setStrokeColor(INK)
        c.setLineWidth(max(0.5, 0.11 * s))
        c.setFillColor(rgb("#FFD21F"))
        star(c, x + 7.0 * s, y + 7.0 * s, 1.9 * s, 0.8 * s, 5, "#FFD21F")
    elif name == "bug":  # Chapter 7
        c.setStrokeColor(INK)
        for dx in (-1.6, 1.6):
            for dy in (0.4, 2.4, 4.4):
                c.line(x + 4.5 * s, y + 4.6 * s + dy * 0.4 * s, x + 4.5 * s + dx * 1.6 * s, y + 4.5 * s + (dy - 1.5) * s)
        gradient_rect(c, x + 2.0 * s, y + 1.0 * s, 5.0 * s, 6.4 * s, 2.4 * s, "#FF6B6B", "#C81E1E", steps=10)
        c.setStrokeColor(INK)
        c.roundRect(x + 2.0 * s, y + 1.0 * s, 5.0 * s, 6.4 * s, 2.4 * s, stroke=1, fill=0)
        c.setFillColor(INK)
        c.circle(x + 4.5 * s, y + 8.1 * s, 1.0 * s, stroke=1, fill=1)
        c.line(x + 4.5 * s, y + 7.1 * s, x + 4.5 * s, y + 6.3 * s)
        for sx, sy in ((3.4, 4.6), (5.7, 3.0), (5.4, 6.2)):
            c.setFillColor(INK)
            c.circle(x + sx * s, y + sy * s, 0.6 * s, stroke=0, fill=1)
        c.setFillColor(rgb("#FFD21F"))
        c.circle(x + 6.8 * s, y + 8.6 * s, 0.7 * s, stroke=1, fill=1)
    elif name == "notebook":  # Chapter 8
        _box(c, x + 1.2 * s, y + 0.2 * s, 7.0 * s, 8.2 * s, 0.5 * s, "#FFFFFF", "#CFEFE0")
        c.setStrokeColor(rgb("#2B7BEA"))
        c.setLineWidth(max(0.4, 0.07 * s))
        for i in range(4):
            c.line(x + 2.2 * s, y + 6.0 * s - i * 1.2 * s, x + 7.2 * s, y + 6.0 * s - i * 1.2 * s)
        c.setStrokeColor(INK)
        c.setLineWidth(max(0.5, 0.11 * s))
        for i in range(5):
            c.setFillColor(rgb("#8E9AB5"))
            c.circle(x + 1.2 * s, y + 1.0 * s + i * 1.6 * s, 0.35 * s, stroke=1, fill=1)
    elif name == "window":  # Chapter 9
        _box(c, x + 0.4 * s, y + 0.4 * s, 8.4 * s, 7.0 * s, 0.5 * s, "#FFFFFF", "#D6E7FF")
        gradient_rect(c, x + 0.4 * s, y + 6.5 * s, 8.4 * s, 0.9 * s, 0.4 * s, "#2B7BEA", "#1B5BC0", steps=3)
        c.setFillColor(rgb("#FF4FA3"))
        c.roundRect(x + 2.2 * s, y + 2.2 * s, 4.6 * s, 1.5 * s, 0.5 * s, stroke=1, fill=1)
        c.setFillColor(INK)
        c.setFont("Sans-Bold", 0.9 * s)
        c.drawCentredString(x + 4.5 * s, y + 2.7 * s, "Hi!")
    elif name == "controller":  # Chapter 10
        gradient_rect(c, x + 0.4 * s, y + 2.0 * s, 8.4 * s, 4.6 * s, 2.2 * s, "#8A4FFF", "#4B1FB0", steps=8)
        c.setStrokeColor(INK)
        c.roundRect(x + 0.4 * s, y + 2.0 * s, 8.4 * s, 4.6 * s, 2.2 * s, stroke=1, fill=0)
        c.setFillColor(INK)
        c.rect(x + 2.0 * s, y + 4.0 * s, 1.0 * s, 0.4 * s, stroke=0, fill=1)
        c.rect(x + 1.5 * s, y + 4.5 * s, 0.4 * s, 1.0 * s, stroke=0, fill=1)
        c.rect(x + 1.3 * s, y + 4.3 * s, 1.4 * s, 0.4 * s, stroke=0, fill=1)
        for bx, by, colour in ((7.0, 5.6, "#FF4FA3"), (7.6, 4.8, "#FFD21F"), (6.4, 4.8, "#22B573"), (7.0, 4.0, "#2B7BEA")):
            c.setFillColor(rgb(colour))
            c.circle(x + bx * s, y + by * s, 0.4 * s, stroke=1, fill=1)
    c.restoreState()


def star(c, cx, cy, r_out, r_in, points, colour):
    p = c.beginPath()
    for i in range(points * 2):
        radius = r_out if i % 2 == 0 else r_in
        angle = math.pi / 2 + i * math.pi / points
        px, py = cx + radius * math.cos(angle), cy + radius * math.sin(angle)
        if i == 0:
            p.moveTo(px, py)
        else:
            p.lineTo(px, py)
    p.close()
    c.saveState()
    c.setFillColor(rgb(colour))
    c.setStrokeColor(INK)
    c.setLineWidth(0.6)
    c.drawPath(p, stroke=1, fill=1)
    c.restoreState()


def starburst(c, cx, cy, r_out, r_in, points, colour):
    c.saveState()
    p = c.beginPath()
    for i in range(points * 2):
        radius = r_out if i % 2 == 0 else r_in
        angle = i * math.pi / points
        px, py = cx + radius * math.cos(angle), cy + radius * math.sin(angle)
        if i == 0:
            p.moveTo(px, py)
        else:
            p.lineTo(px, py)
    p.close()
    c.setFillColor(rgb(colour))
    c.drawPath(p, stroke=0, fill=1)
    c.restoreState()


def confetti(c, x, y, w, h, count, seed=1, colours=PALETTE):
    rng = random.Random(seed)
    c.saveState()
    for _ in range(count):
        px, py = x + rng.random() * w, y + rng.random() * h
        colour = rgb(colours[rng.randrange(len(colours))])
        c.setFillColor(colour)
        kind = rng.random()
        if kind < 0.4:
            c.saveState()
            c.translate(px, py)
            c.rotate(rng.random() * 90)
            c.rect(-1.2, -0.5, 2.4, 1.0, stroke=0, fill=1)
            c.restoreState()
        elif kind < 0.7:
            c.circle(px, py, 0.7 + rng.random() * 0.6, stroke=0, fill=1)
        else:
            star(c, px, py, 2.0, 0.9, 5, colours[rng.randrange(len(colours))])
    c.restoreState()


def rainbow(c, cx, cy, r_outer, thickness, colours=("#FF4FA3", "#FF8A00", "#FFD21F", "#22B573", "#2B7BEA", "#8A4FFF")):
    c.saveState()
    for i, colour in enumerate(colours):
        radius = r_outer - i * thickness
        c.setStrokeColor(rgb(colour))
        c.setLineWidth(thickness * 0.98)
        c.arc(cx - radius, cy - radius, cx + radius, cy + radius, 0, 180)
    c.restoreState()


def doodle(c, x, y, kind, colour):
    c.saveState()
    if kind == "star":
        star(c, x, y, 2.6, 1.1, 5, colour)
    elif kind == "squiggle":
        c.setStrokeColor(rgb(colour))
        c.setLineWidth(1.2)
        p = c.beginPath()
        p.moveTo(x, y)
        for i in range(1, 9):
            p.lineTo(x + i * 1.2, y + (1.6 if i % 2 else -1.6))
        c.drawPath(p, stroke=1, fill=0)
    else:
        c.setFillColor(rgb(colour))
        c.circle(x, y, 1.4, stroke=0, fill=1)
    c.restoreState()


def outlined_text(c, x, y, text, font, size, fill, stroke_colour, stroke_w, align="centre"):
    """Text with a thick ink outline, no shadow."""
    c.saveState()
    c.setLineWidth(stroke_w)
    c.setStrokeColor(rgb(stroke_colour))
    t = c.beginText()
    t.setTextRenderMode(2)
    t.setFont(font, size)
    t.setFillColor(rgb(fill))
    width = c.stringWidth(text, font, size)
    start = x - width / 2 if align == "centre" else x
    t.setTextOrigin(start, y)
    t.textOut(text)
    c.drawText(t)
    c.restoreState()
