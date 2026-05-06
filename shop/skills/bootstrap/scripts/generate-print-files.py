#!/usr/bin/env python3
"""
Génère les 10 print-ready PNG (transparent, 300 DPI) pour Printful DTG.

Spécifications par produit type :
- Tee chest / Hoodie chest / Hoodie back : 4500 x 5400 (15" x 18" @ 300 DPI)
- Tee hem (ourlet) : 4500 x 1200 (15" x 4" @ 300 DPI, format horizontal)
- Mug side : 1200 x 1050 (4" x 3.5" @ 300 DPI)
- Mug wrap : 2475 x 1050 (8.25" x 3.5" @ 300 DPI)

Police : Instrument Serif Italic (italique violet) + Geist Mono (mono noir/violet selon design).
Couleur violet brand : #7C4DFF

Sortie : store/products/designs/print/<slug>.png (et <slug>-back.png si 2-sided).
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "products" / "designs" / "print"
OUT.mkdir(parents=True, exist_ok=True)

ITAL = "/tmp/InstrumentSerif-Italic.ttf"
SERIF = "/tmp/InstrumentSerif-Regular.ttf"
MONO = "/tmp/GeistMono-Regular.ttf"

VIOLET = (124, 77, 255, 255)  # #7C4DFF
INK = (31, 29, 36, 255)  # #1F1D24
TRANSPARENT = (0, 0, 0, 0)


def measure(text, font):
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0], bbox[3] - bbox[1], bbox[0], bbox[1]


def center_x(canvas_w, text_w, anchor_x=0):
    return (canvas_w - text_w) // 2 - anchor_x


# === 1. Tee Mojo (chest, simple "mojo" italic violet) ===
def tee_mojo():
    img = Image.new("RGBA", (4500, 5400), TRANSPARENT)
    draw = ImageDraw.Draw(img)
    # Big "mojo" italic violet, centered upper-third (chest area)
    font = ImageFont.truetype(ITAL, 1400)
    text = "mojo"
    w, h, ax, ay = measure(text, font)
    x = (4500 - w) // 2 - ax
    y = (5400 // 3) - h // 2 - ay  # vertical position = upper third = chest
    draw.text((x, y), text, font=font, fill=VIOLET)
    img.save(OUT / "tee-mojo.png", "PNG")
    print(f"  tee-mojo.png : {w}x{h} 'mojo' italic violet centered")


# === 2. Tee Quatre Verbes (hem, horizontal, "construire" violet) ===
def tee_quatre_verbes():
    canvas_w, canvas_h = 4500, 1200
    img = Image.new("RGBA", (canvas_w, canvas_h), TRANSPARENT)
    draw = ImageDraw.Draw(img)
    parts = [
        ("Cadrer", MONO, INK),
        (" · ", MONO, INK),
        ("construire", ITAL, VIOLET),
        (" · ", MONO, INK),
        ("déployer", MONO, INK),
        (" · ", MONO, INK),
        ("itérer", MONO, INK),
    ]
    fs = 220
    target_w = int(canvas_w * 0.92)
    fonts = [(ImageFont.truetype(p[1], fs), p[0], p[2]) for p in parts]
    total_w = sum(measure(t, f)[0] for f, t, c in fonts)
    if total_w > target_w:
        fs = int(fs * target_w / total_w)
        fonts = [(ImageFont.truetype(p[1], fs), p[0], p[2]) for p in parts]
        total_w = sum(measure(t, f)[0] for f, t, c in fonts)
    x = (canvas_w - total_w) // 2
    y = canvas_h // 2 - fs // 2 - 30
    for f, t, c in fonts:
        w, _, ax, _ = measure(t, f)
        draw.text((x - ax, y), t, font=f, fill=c)
        x += w
    img.save(OUT / "tee-quatre-verbes.png", "PNG")
    print(f"  tee-quatre-verbes.png : hem horizontal, fs={fs}, total_w={total_w}/{canvas_w}")


# === 3. Tee Ship It (chest, 2 lignes, mix mono + italic violet) ===
def tee_ship_it():
    img = Image.new("RGBA", (4500, 5400), TRANSPARENT)
    draw = ImageDraw.Draw(img)
    # Line 1 : "SHIP IT." en Geist Mono uppercase noir, gros
    f1 = ImageFont.truetype(MONO, 800)
    t1 = "SHIP IT."
    w1, h1, ax1, ay1 = measure(t1, f1)
    # Line 2 : "/ Then iterate." en Instrument Serif italique violet
    f2 = ImageFont.truetype(ITAL, 600)
    t2 = "/ Then iterate."
    w2, h2, ax2, ay2 = measure(t2, f2)
    # Position : centré, alignement gauche, upper-third chest
    x_start = (4500 - max(w1, w2)) // 2
    y_start = 5400 // 3 - (h1 + h2 + 150) // 2
    draw.text((x_start - ax1, y_start - ay1), t1, font=f1, fill=INK)
    draw.text((x_start - ax2, y_start + h1 + 100 - ay2), t2, font=f2, fill=VIOLET)
    img.save(OUT / "tee-ship-it.png", "PNG")
    print(f"  tee-ship-it.png : 2-line chest")


# === 4. Tee Loop Forever (chest, /loop /forever/) ===
def tee_loop():
    img = Image.new("RGBA", (4500, 5400), TRANSPARENT)
    draw = ImageDraw.Draw(img)
    f1 = ImageFont.truetype(MONO, 850)
    t1 = "/loop"
    w1, h1, ax1, ay1 = measure(t1, f1)
    f2 = ImageFont.truetype(ITAL, 600)
    t2 = "/forever/"
    w2, h2, ax2, ay2 = measure(t2, f2)
    x_start = (4500 - max(w1, w2)) // 2
    y_start = 5400 // 3 - (h1 + h2 + 100) // 2
    draw.text((x_start - ax1, y_start - ay1), t1, font=f1, fill=(245, 243, 247, 255))  # cream sur fond noir tee
    draw.text((x_start - ax2, y_start + h1 + 80 - ay2), t2, font=f2, fill=VIOLET)
    img.save(OUT / "tee-loop-forever.png", "PNG")
    print(f"  tee-loop-forever.png : /loop blanc + /forever/ violet (sur tee noir)")


# === 5. Mug Mojo (side print, simple "mojo" italic violet) ===
def mug_mojo():
    img = Image.new("RGBA", (1200, 1050), TRANSPARENT)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(ITAL, 600)
    text = "mojo"
    w, h, ax, ay = measure(text, font)
    x = (1200 - w) // 2 - ax
    y = (1050 - h) // 2 - ay
    draw.text((x, y), text, font=font, fill=VIOLET)
    img.save(OUT / "mug-mojo.png", "PNG")
    print(f"  mug-mojo.png : 1200x1050 side print")


# === 6. Mug Quatre Verbes (wrap horizontal, ruban) ===
def mug_quatre_verbes():
    canvas_w, canvas_h = 2475, 1050
    img = Image.new("RGBA", (canvas_w, canvas_h), TRANSPARENT)
    draw = ImageDraw.Draw(img)
    parts = [
        ("Cadrer", MONO, INK),
        (" · ", MONO, INK),
        ("construire", ITAL, VIOLET),
        (" · ", MONO, INK),
        ("déployer", MONO, INK),
        (" · ", MONO, INK),
        ("itérer", MONO, INK),
    ]
    fs = 130
    target_w = int(canvas_w * 0.92)
    fonts = [(ImageFont.truetype(p[1], fs), p[0], p[2]) for p in parts]
    total_w = sum(measure(t, f)[0] for f, t, c in fonts)
    if total_w > target_w:
        fs = int(fs * target_w / total_w)
        fonts = [(ImageFont.truetype(p[1], fs), p[0], p[2]) for p in parts]
        total_w = sum(measure(t, f)[0] for f, t, c in fonts)
    x = (canvas_w - total_w) // 2
    y = canvas_h // 2 - fs // 2 - 10
    for f, t, c in fonts:
        w, _, ax, _ = measure(t, f)
        draw.text((x - ax, y), t, font=f, fill=c)
        x += w
    img.save(OUT / "mug-quatre-verbes.png", "PNG")
    print(f"  mug-quatre-verbes.png : wrap, fs={fs}, total_w={total_w}/{canvas_w}")


# === 7. Mug Git Commit (side print, mono avec "vibe" italic violet) ===
def mug_git_commit():
    img = Image.new("RGBA", (1200, 1050), TRANSPARENT)
    draw = ImageDraw.Draw(img)
    parts = [
        ('git commit -m "', MONO, (245, 243, 247, 255)),  # cream sur mug noir
        ("vibe", ITAL, VIOLET),
        ('"', MONO, (245, 243, 247, 255)),
    ]
    fs = 110
    fonts = [(ImageFont.truetype(p[1], fs), p[0], p[2]) for p in parts]
    total_w = sum(measure(t, f)[0] for f, t, c in fonts)
    x = (1200 - total_w) // 2
    y = 1050 // 2 - fs // 2
    for f, t, c in fonts:
        w, _, ax, _ = measure(t, f)
        draw.text((x - ax, y), t, font=f, fill=c)
        x += w
    img.save(OUT / "mug-git-commit-vibe.png", "PNG")
    print(f"  mug-git-commit-vibe.png : `git commit \"vibe\"` cream/violet (sur mug noir)")


# === 8. Mug Todo (side print, mono + italic violet) ===
def mug_todo():
    img = Image.new("RGBA", (1200, 1050), TRANSPARENT)
    draw = ImageDraw.Draw(img)
    f1 = ImageFont.truetype(MONO, 220)
    t1 = "TODO: get"
    w1, h1, ax1, ay1 = measure(t1, f1)
    f2 = ImageFont.truetype(ITAL, 320)
    t2 = "mojo"
    w2, h2, ax2, ay2 = measure(t2, f2)
    x1 = (1200 - w1) // 2 - ax1
    y1 = 1050 // 2 - (h1 + h2 + 50) // 2 - ay1
    x2 = (1200 - w2) // 2 - ax2
    y2 = y1 + h1 + 30 - ay2
    draw.text((x1, y1), t1, font=f1, fill=INK)
    draw.text((x2, y2), t2, font=f2, fill=VIOLET)
    img.save(OUT / "mug-todo-mojo.png", "PNG")
    print(f"  mug-todo-mojo.png : TODO: get mojo")


# === 9. Hoodie Mojo (back print, GROS "mojo" italic violet 60% width) ===
def hoodie_mojo():
    img = Image.new("RGBA", (4500, 5400), TRANSPARENT)
    draw = ImageDraw.Draw(img)
    # Trouver la bonne taille pour que "mojo" fasse ~60% des 4500px
    target_w = int(4500 * 0.7)
    fs = 100
    while True:
        font = ImageFont.truetype(ITAL, fs)
        w, _, _, _ = measure("mojo", font)
        if w >= target_w:
            break
        fs += 50
    font = ImageFont.truetype(ITAL, fs)
    text = "mojo"
    w, h, ax, ay = measure(text, font)
    x = (4500 - w) // 2 - ax
    y = (5400 - h) // 2 - ay
    draw.text((x, y), text, font=font, fill=VIOLET)
    img.save(OUT / "hoodie-mojo-back.png", "PNG")
    print(f"  hoodie-mojo-back.png : MOJO gros 60% width, fontsize={fs}")


# === 10. Hoodie Construire (front "Construire" + back séquence verbes) ===
def hoodie_construire():
    # FRONT : "Construire" italic violet centre poitrine
    img_front = Image.new("RGBA", (4500, 5400), TRANSPARENT)
    draw = ImageDraw.Draw(img_front)
    font = ImageFont.truetype(ITAL, 1100)
    text = "Construire"
    w, h, ax, ay = measure(text, font)
    x = (4500 - w) // 2 - ax
    y = 5400 // 3 - h // 2 - ay
    draw.text((x, y), text, font=font, fill=VIOLET)
    img_front.save(OUT / "hoodie-construire-front.png", "PNG")
    # BACK : séquence Cadrer · construire · déployer · itérer en Geist Mono petit corps
    img_back = Image.new("RGBA", (4500, 5400), TRANSPARENT)
    draw_back = ImageDraw.Draw(img_back)
    parts = [
        ("Cadrer", MONO, (245, 243, 247, 255)),  # cream sur hoodie noir
        (" · ", MONO, (245, 243, 247, 255)),
        ("construire", ITAL, VIOLET),
        (" · ", MONO, (245, 243, 247, 255)),
        ("déployer", MONO, (245, 243, 247, 255)),
        (" · ", MONO, (245, 243, 247, 255)),
        ("itérer", MONO, (245, 243, 247, 255)),
    ]
    fs = 200
    fonts = [(ImageFont.truetype(p[1], fs), p[0], p[2]) for p in parts]
    total_w = sum(measure(t, f)[0] for f, t, c in fonts)
    if total_w > 4200:
        # reduce fs to fit
        ratio = 4200 / total_w
        fs = int(fs * ratio)
        fonts = [(ImageFont.truetype(p[1], fs), p[0], p[2]) for p in parts]
        total_w = sum(measure(t, f)[0] for f, t, c in fonts)
    x = (4500 - total_w) // 2
    y = 5400 // 4  # haut du dos
    for f, t, c in fonts:
        w, _, ax, _ = measure(t, f)
        draw_back.text((x - ax, y), t, font=f, fill=c)
        x += w
    img_back.save(OUT / "hoodie-construire-back.png", "PNG")
    print(f"  hoodie-construire-front.png + back.png : 2-sided")


def main():
    print(f"Génération des print files dans {OUT}")
    tee_mojo()
    tee_quatre_verbes()
    tee_ship_it()
    tee_loop()
    mug_mojo()
    mug_quatre_verbes()
    mug_git_commit()
    mug_todo()
    hoodie_mojo()
    hoodie_construire()
    print(f"\nTerminé. {len(list(OUT.glob('*.png')))} fichiers PNG transparents prêts pour Printful DTG.")


if __name__ == "__main__":
    main()
