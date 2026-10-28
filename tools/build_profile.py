"""Builds the GitHub profile README images: banner, buttons and app windows.

Every app is drawn as a small browser window whose address bar holds the app's
real address, so the picture itself says where to go.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SHOTS = sys.argv[1]
OUT = sys.argv[2]
FONTS = os.path.expanduser("~/.claude/skills/canvas-design/canvas-fonts")
os.makedirs(f"{OUT}/cards", exist_ok=True)


def font(name, size):
    return ImageFont.truetype(f"{FONTS}/{name}.ttf", size)


DISPLAY = lambda s: font("BricolageGrotesque-Bold", s)
BODY = lambda s: font("InstrumentSans-Regular", s)
BODY_B = lambda s: font("InstrumentSans-Bold", s)
MONO = lambda s: font("GeistMono-Regular", s)
MONO_B = lambda s: font("GeistMono-Bold", s)

INK = (22, 22, 26)
INK2 = (85, 85, 94)
INK3 = (110, 110, 120)
PAPER = (250, 250, 250)
LINE = (229, 229, 238)
CYAN = (0, 196, 223)
VIOLET = (139, 92, 246)
DEEP_A = (14, 116, 144)
DEEP_B = (109, 40, 217)


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    """t of a over b."""
    return tuple(round(a[i] * t + b[i] * (1 - t)) for i in range(3))


def gradient(size, a, b, angle_h=True):
    w, h = size
    g = Image.new("RGB", size)
    px = g.load()
    for x in range(w):
        for y in range(h):
            t = (x / max(w - 1, 1)) * 0.75 + (y / max(h - 1, 1)) * 0.25 if angle_h else y / (h - 1)
            px[x, y] = mix(b, a, t)
    return g


def fit(draw, text, f, width):
    if draw.textlength(text, font=f) <= width:
        return text
    while text and draw.textlength(text + "…", font=f) > width:
        text = text[:-1]
    return text.rstrip() + "…"


def glyph(size, initials, accent, card=(255, 255, 255), radius=None):
    """The portal's initials square: a wash of the accent, initials in it."""
    radius = radius or round(size * 0.28)
    g = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    top = mix(accent, card, 0.18)
    bottom = mix(accent, card, 0.07)
    fill = gradient((size, size), top, bottom, angle_h=False)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size - 1, size - 1), radius, fill=255)
    g.paste(fill, (0, 0), mask)
    d = ImageDraw.Draw(g)
    d.rounded_rectangle((0, 0, size - 1, size - 1), radius, outline=mix(accent, card, 0.25) + (255,), width=max(2, size // 40))
    ink = mix((0, 0, 0), accent, 0.14)
    f = MONO_B(round(size * 0.36))
    d.text((size / 2, size / 2), initials, font=f, fill=ink, anchor="mm")
    return g


def shadowed(img, pad, radius, strength=60):
    """Place img on a transparent canvas with a soft drop shadow."""
    w, h = img.size
    canvas = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((pad, pad + pad // 3, pad + w, pad + h + pad // 3), radius, fill=(20, 20, 40, strength))
    sh = sh.filter(ImageFilter.GaussianBlur(pad / 2.2))
    canvas.alpha_composite(sh)
    canvas.alpha_composite(img, (pad, pad))
    return canvas


def window(width, address, accent, shot=None, shot_h=None, body=None, body_h=0):
    """A rounded browser window: accent strip, traffic lights, address, content."""
    s = width / 816  # scale relative to the card canvas
    bar = round(66 * s)
    strip = max(3, round(5 * s))
    radius = round(30 * s)
    sh = shot_h if shot is not None else 0
    h = strip + bar + sh + body_h
    win = Image.new("RGBA", (width, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(win)
    d.rectangle((0, 0, width, strip), fill=accent)
    d.rectangle((0, strip, width, strip + bar), fill=(247, 247, 250))
    d.line((0, strip + bar - 1, width, strip + bar - 1), fill=LINE, width=max(1, round(2 * s)))
    cy = strip + bar / 2
    for i, c in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):
        cx = round((34 + i * 30) * s)
        r = round(8.5 * s)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=c)
    pill_w = min(round(width * 0.56), round(width - 260 * s))
    pill_h = round(40 * s)
    px0 = (width - pill_w) / 2
    d.rounded_rectangle((px0, cy - pill_h / 2, px0 + pill_w, cy + pill_h / 2), pill_h / 2, fill=(255, 255, 255), outline=LINE, width=max(1, round(2 * s)))
    f = MONO(round(22 * s))
    d.text((width / 2, cy), fit(d, address, f, pill_w - 30 * s), font=f, fill=INK2, anchor="mm")
    y = strip + bar
    if shot is not None:
        win.paste(shot.convert("RGB").resize((width, sh), Image.LANCZOS), (0, y))
        y += sh
    if body is not None:
        win.alpha_composite(body, (0, y))
    mask = Image.new("L", win.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, width - 1, h - 1), radius, fill=255)
    out = Image.new("RGBA", win.size, (0, 0, 0, 0))
    out.paste(win, (0, 0), mask)
    ImageDraw.Draw(out).rounded_rectangle((0, 0, width - 1, h - 1), radius, outline=(222, 222, 232, 255), width=max(2, round(2 * s)))
    return out


def caption(width, name, line, initials, accent, tag):
    s = width / 816
    h = round(176 * s)
    c = Image.new("RGBA", (width, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(c)
    gs = round(96 * s)
    gx, gy = round(30 * s), (h - gs) // 2
    c.alpha_composite(glyph(gs, initials, accent), (gx, gy))
    tx = gx + gs + round(24 * s)
    avail = width - tx - round(30 * s)
    ft = MONO(round(22 * s))
    tag_w = d.textlength(tag, font=ft)
    d.text((width - round(30 * s), gy + round(8 * s)), tag, font=ft, fill=INK3, anchor="ra")
    d.text((tx, gy - round(4 * s)), fit(d, name, DISPLAY(round(50 * s)), avail - tag_w - 16 * s), font=DISPLAY(round(50 * s)), fill=INK, anchor="la")
    d.text((tx, gy + round(58 * s)), fit(d, line, BODY(round(37 * s)), avail), font=BODY(round(37 * s)), fill=INK2, anchor="la")
    return c


def card(slug, name, line, initials, accent, address, shot_path, tag, width=816):
    acc = hexrgb(accent)
    shot = Image.open(shot_path)
    shot_h = round(width * 10 / 16)
    body = caption(width, name, line, initials, acc, tag)
    w = window(width, address, acc, shot=shot, shot_h=shot_h, body=body, body_h=body.size[1])
    out = shadowed(w, round(26 * width / 816), round(30 * width / 816), 46)
    out.save(f"{OUT}/cards/{slug}.webp", "WEBP", quality=82, method=6)
    return out.size


def store_card(slug, name, line, initials, accent, store, tag, width=816):
    acc = hexrgb(accent)
    body = caption(width, name, line, initials, acc, tag)
    w = window(width, store, acc, body=body, body_h=body.size[1])
    out = shadowed(w, 26, 30, 40)
    out.save(f"{OUT}/cards/{slug}.webp", "WEBP", quality=86, method=6)
    return out.size


# ── Data — mirrors lib/apps.ts in msrx-portal ─────────────────────────────────
WEB = [
    # group, slug, name, initials, accent, url, line, shot
    ("study", "planner", "MSRX Planner", "MP", "#15803D", "planner.msrx.co.in", "Plans the student's week with them", "planner.png"),
    ("study", "storyquest", "MSRX StoryQuest", "SQ", "#A21CAF", "story.msrx.co.in", "222 STEM missions, real equations", "story.png"),
    ("study", "jee-hyperlab", "JEE HyperLab", "JH", "#4338CA", "lab.msrx.co.in", "204 live PCM simulations for JEE", "lab.png"),
    ("create", "graphiq", "MSRX GraphIQ", "GQ", "#9333EA", "graph.msrx.co.in", "Spreadsheet in, 2D and 3D charts out", "graphiq.png"),
    ("create", "canvasiq", "MSRX CanvasIQ", "CQ", "#1D4ED8", "canvas.msrx.co.in", "Paint, vectors and 3D with a copilot", "canvasiq.png"),
    ("create", "qr-studio", "MSRX QR Studio", "QS", "#0E7490", "qr.msrx.co.in", "22 QR types, with scan-health scores", "qrstudio.png"),
    ("work", "invoice", "MSRX Invoice", "IV", "#4338CA", "invoice.msrx.co.in", "39 invoice templates, nothing saved", "invoice.png"),
    ("work", "meeting", "MSRX Meeting", "MM", "#2563EB", "meeting.msrx.co.in", "Encrypted rooms with live captions", "meeting.png"),
    ("work", "incognitocv", "IncognitoCV", "IC", "#8A5F1C", "cv.msrx.co.in", "Score a CV without uploading it", "cv.png"),
    ("work", "easy-peasy-gantt", "Easy-Peasy Gantt", "EG", "#4F46E5", "gantt.msrx.co.in", "Presentation-ready Gantt charts", "gantt.png"),
    ("work", "security", "MSRX Security", "SC", "#0F766E", "security.msrx.co.in", "Website security scored out of 10", "security.png"),
    ("everyday", "tools", "MSRX Tools", "MT", "#0F766E", "tools.msrx.co.in", "238 tools, no file ever uploaded", "tools.png"),
    ("everyday", "split", "MSRX Split", "SP", "#6A28B8", "split.msrx.co.in", "Trip costs, nothing on a server", "split.png"),
    ("everyday", "gluconexa", "MSRX GlucoNexa", "GN", "#0A66C2", "gluconexa.msrx.co.in", "A private, offline diabetes log", "gluconexa-pane.jpg"),
    ("everyday", "flight", "MSRX Flights", "FL", "#0A6E70", "flight.msrx.co.in", "Cheapest flights, day and hour", "flight.png"),
    ("everyday", "diwali", "MSRX Diwali Cards", "DW", "#B4440A", "diwali.msrx.co.in", "63 Diwali cards in 13 languages", "diwali.png"),
    ("everyday", "weatherwatch", "MSRX WeatherWatch", "WW", "#0369A1", "weather.msrx.co.in", "Weather and hazards in 19 languages", "weather.png"),
    ("everyday", "upi-desk", "MSRX UPI Desk", "UD", "#5B45B0", "upi.msrx.co.in", "22 UPI tools, 22 Indian languages", "upi.png"),
    ("everyday", "pulsenet", "OrionPulseNet", "PN", "#7C3AED", "pulsenet.msrx.co.in", "Speed tests and 16 diagnostics", "pulsenet-old.jpg"),
]
MAC = [
    ("canvas-ai", "MSRX Canvas AI", "CA", "#5B21B6", "Annotate screenshots, on-device AI"),
    ("orionseek", "OrionSeek", "OS", "#166534", "Find anything on your Mac, fast"),
    ("orionshield", "MSRX Shield", "MS", "#C2410C", "Privacy protection, out of the way"),
    ("orion-process-explorer", "Orion Process Explorer", "PE", "#BE123C", "See exactly what your Mac is doing"),
    ("orionclean", "MSRX Clean", "MC", "#115E59", "Reclaim space, keep what matters"),
    ("pulsenet-mac", "OrionPulseNet", "PN", "#7C3AED", "The network toolkit, native"),
]
IOS = [
    ("guardtrack-pro", "GuardTrack Pro", "GT", "#3730A3", "Patrols, incidents and reports"),
    ("numly", "MSRX AI Calculator", "AC", "#B45309", "A calculator that reads English"),
    ("pdf-compressor", "MSRX PDF Compressor", "PC", "#7C3AED", "Shrink PDFs, keep text as text"),
    ("passportfast", "MSRX PassportFast", "PF", "#047857", "Passport and ID photos, measured"),
]
PLAY = [
    ("highway-rash", "Highway Rash", "HR", "#C2410C", "msrx.co.in/games/highway-rash", "A 3D motorbike brawl, in the browser", "highway.png", "GAME"),
    ("dave-trophy-run", "Dave's Trophy Run", "DT", "#1D4ED8", "msrx.co.in/games/dave-trophy-run", "An EGA-style platformer, six levels", "dave.png", "GAME"),
    ("articles", "MSRX Articles", "AR", "#6D28D9", "articles.msrx.co.in", "AI explained twice: plain words, then maths", "articles.png", "READ"),
    ("news", "MSRX News", "NW", "#0E7490", "news.msrx.co.in", "Short, sourced briefs on AI and technology", "news.png", "READ"),
]


def main():
    sizes = {}
    for _, slug, name, ini, acc, url, line, shot in WEB:
        sizes[slug] = card(slug, name, line, ini, acc, url, f"{SHOTS}/{shot}", "WEB · MAC" if slug == "pulsenet" else "WEB")
    for slug, name, ini, acc, line in MAC:
        sizes[slug] = store_card(slug, name, line, ini, acc, "Mac App Store", "MAC")
    for slug, name, ini, acc, line in IOS:
        sizes[slug] = store_card(slug, name, line, ini, acc, "App Store", "iOS")
    for slug, name, ini, acc, url, line, shot, tag in PLAY:
        sizes[slug] = card(slug, name, line, ini, acc, url, f"{SHOTS}/{shot}", tag)
    sizes["portal"] = card("portal", "MSRX", "All 28 apps in one place. Install it as one icon.", "MX", "#6D28D9", "www.msrx.co.in", f"{SHOTS}/portal.png", "WEB", width=1632)
    sizes["library"] = card("library", "Mana Jardin Children's Library", "A real library platform, open source under MIT", "MJ", "#BE185D", "library.msrx.co.in", f"{SHOTS}/library.png", "COMMUNITY", width=1632)
    for k, v in sizes.items():
        print(k, v)


if __name__ == "__main__":
    main()


# ── Banner ─────────────────────────────────────────────────────────────────────
def logo(height):
    """The MSRX mark from components/MsrxLogo.tsx, viewBox 100 × 115."""
    k = height / 115
    W, H = round(100 * k), height
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    left = gradient((W, H), (126, 232, 248), (0, 170, 200), angle_h=False)
    right = gradient((W, H), (196, 181, 253), (124, 58, 237), angle_h=False)

    def poly(points, src=None, rgba=None, alpha=255):
        mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mask).polygon([(x * k, y * k) for x, y in points], fill=alpha)
        if src is not None:
            im.paste(src, (0, 0), Image.composite(mask, Image.new("L", (W, H), 0), mask))
        else:
            layer = Image.new("RGBA", (W, H), rgba)
            la = Image.new("L", (W, H), 0)
            la.paste(mask, (0, 0))
            layer.putalpha(Image.eval(la, lambda v: v * rgba[3] // 255))
            im.alpha_composite(layer)

    poly([(5, 110), (5, 12), (22, 12), (22, 110)], left)
    poly([(22, 12), (50, 58), (50, 78), (22, 46)], left, alpha=204)
    poly([(5, 12), (50, 12), (50, 22), (22, 22)], rgba=(200, 248, 255, 102))
    poly([(22, 46), (50, 78), (78, 46), (78, 62), (50, 94), (22, 62)], rgba=(0, 0, 30, 71))
    poly([(78, 12), (50, 58), (50, 78), (78, 46)], right, alpha=204)
    poly([(78, 12), (95, 12), (95, 110), (78, 110)], right)
    poly([(50, 12), (95, 12), (78, 22), (50, 22)], rgba=(220, 210, 255, 97))
    poly([(5, 12), (22, 12), (50, 58), (78, 12), (95, 12), (95, 20), (78, 20), (50, 68), (22, 20), (5, 20)], rgba=(255, 255, 255, 46))
    return im


def bloom(size, center, radius, color, alpha):
    layer = Image.new("RGBA", size, color + (0,))
    m = Image.new("L", size, 0)
    cx, cy = center
    ImageDraw.Draw(m).ellipse((cx - radius, cy - radius * 0.8, cx + radius, cy + radius * 0.8), fill=alpha)
    layer.putalpha(m.filter(ImageFilter.GaussianBlur(radius / 2.2)))
    return layer


def banner(theme):
    dark = theme == "dark"
    W, H = 1680, 600
    bg = (11, 11, 18) if dark else (250, 250, 252)
    card = (23, 23, 31) if dark else (255, 255, 255)
    ink = (245, 245, 248) if dark else INK
    ink2 = (168, 168, 184) if dark else INK2
    ink3 = (133, 133, 154) if dark else INK3
    im = Image.new("RGBA", (W, H), bg + (255,))
    im.alpha_composite(bloom((W, H), (1380, 120), 520, VIOLET, 70 if dark else 46))
    im.alpha_composite(bloom((W, H), (180, 40), 420, CYAN, 52 if dark else 40))
    d = ImageDraw.Draw(im)

    # Left: who and what
    x = 96
    mk = logo(64)
    im.alpha_composite(mk, (x, 92))
    d.text((x + mk.width + 18, 124), "M S R X", font=BODY_B(34), fill=ink, anchor="lm")
    d.text((x, 214), "FUTURE. INTELLIGENCE. IMPACT.", font=MONO(22), fill=ink3, anchor="lm")
    d.text((x, 250), "Mrinal Singh Raja", font=DISPLAY(96), fill=ink, anchor="la")
    sub = BODY(36)
    d.text((x, 392), "28 free apps for the web, Mac and iPhone.", font=sub, fill=ink2, anchor="la")
    d.text((x, 440), "No paid tier, anywhere. Most need no sign-up.", font=sub, fill=ink2, anchor="la")
    d.text((x, 516), "BENGALURU · WWW.MSRX.CO.IN", font=MONO(20), fill=ink3, anchor="la")

    # Right: the whole catalog as a mosaic, in catalog order
    order = [(w[3], hexrgb(w[4])) for w in WEB] + [(m[2], hexrgb(m[3])) for m in MAC[:5]] + [(i[2], hexrgb(i[3])) for i in IOS]
    cols, rows = 6, 5
    g, gap = 76, 14
    gx0 = W - 96 - (cols * g + (cols - 1) * gap)
    gy0 = (H - (rows * g + (rows - 1) * gap)) // 2 - 10
    for n, (ini, acc) in enumerate(order):
        r, c = divmod(n, cols)
        tile = glyph(g, ini, acc, card=card)
        if dark:
            # Dark: lift the initials toward white, as the portal does.
            t = Image.new("RGBA", (g, g), (0, 0, 0, 0))
            m = Image.new("L", (g, g), 0)
            ImageDraw.Draw(m).rounded_rectangle((0, 0, g - 1, g - 1), 21, fill=255)
            t.paste(gradient((g, g), mix(acc, card, 0.30), mix(acc, card, 0.14), angle_h=False), (0, 0), m)
            td = ImageDraw.Draw(t)
            td.rounded_rectangle((0, 0, g - 1, g - 1), 21, outline=mix(acc, card, 0.45) + (255,), width=2)
            td.text((g / 2, g / 2), ini, font=MONO_B(27), fill=mix((255, 255, 255), acc, 0.55), anchor="mm")
            tile = t
        im.alpha_composite(tile, (gx0 + c * (g + gap), gy0 + r * (g + gap)))
    cap_y = gy0 + rows * g + (rows - 1) * gap + 26
    d.text((gx0 + (cols * g + (cols - 1) * gap) / 2, cap_y), "19 WEB  ·  6 MAC  ·  4 IPHONE", font=MONO(19), fill=ink3, anchor="ma")

    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, W - 1, H - 1), 36, fill=255)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    ImageDraw.Draw(out).rounded_rectangle((0, 0, W - 1, H - 1), 36, outline=(40, 40, 54, 255) if dark else (226, 226, 236, 255), width=2)
    out.save(f"{OUT}/banner-{theme}.webp", "WEBP", quality=90, method=6)


# ── Buttons ────────────────────────────────────────────────────────────────────
BUTTONS = [
    ("catalog", "Open all 28 apps", True),
    ("launcher", "Install the launcher", False),
    ("appstore", "App Store", False),
    ("portfolio", "Portfolio", False),
    ("email", "Email me", False),
]


def button(slug, label, primary, theme):
    dark = theme == "dark"
    f = BODY_B(30)
    tw = ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(label, font=f)
    w, h = round(tw + 72 + (34 if primary else 0)), 84
    b = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=255)
    if primary:
        b.paste(gradient((w, h), DEEP_A, DEEP_B), (0, 0), m)
        fg = (255, 255, 255)
    else:
        b.paste(Image.new("RGB", (w, h), (23, 23, 31) if dark else (255, 255, 255)), (0, 0), m)
        ImageDraw.Draw(b).rounded_rectangle((0, 0, w - 1, h - 1), h // 2, outline=(52, 52, 68) if dark else (218, 218, 228), width=2)
        fg = (242, 242, 247) if dark else INK
    d = ImageDraw.Draw(b)
    d.text((36, h / 2), label, font=f, fill=fg, anchor="lm")
    if primary:
        ax = 36 + tw + 16
        d.line((ax, h / 2, ax + 20, h / 2), fill=fg, width=4)
        d.line((ax + 11, h / 2 - 9, ax + 20, h / 2), fill=fg, width=4)
        d.line((ax + 11, h / 2 + 9, ax + 20, h / 2), fill=fg, width=4)
    b.save(f"{OUT}/btn-{slug}-{theme}.webp", "WEBP", quality=92, method=6)
    return w // 2


if __name__ == "__main__" and len(sys.argv) > 3 and sys.argv[3] == "chrome":
    for t in ("light", "dark"):
        banner(t)
        for s, l, p in BUTTONS:
            print(s, button(s, l, p, t))
