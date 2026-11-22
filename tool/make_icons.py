"""Render the Nishchit mark (nishchit/assets/favicon.svg) into Android + iOS launcher icons."""
import json, os, sys
from PIL import Image, ImageDraw

# Usage: python3 tool/make_icons.py   (needs Pillow)
root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..")
BLUE = (0x1D, 0x4E, 0xD8, 255)
WHITE = (255, 255, 255, 255)
SS = 8  # supersampling


def draw_glyph(img, scale, off):
    """favicon.svg glyph, in its 34x34 units, scaled and offset, composited onto img."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    def p(x, y):
        return (off + x * scale, off + y * scale)

    def line(x1, x2, w):
        r = w * scale / 2
        (ax, ay), (bx, _) = p(x1, 17), p(x2, 17)
        d.rectangle([ax, ay - r, bx, ay + r], fill=WHITE)
        for cx in (ax, bx):
            d.ellipse([cx - r, ay - r, cx + r, ay + r], fill=WHITE)

    line(8, 13, 3)
    line(21, 26, 3)
    cx, cy = p(17, 17)
    ro, ri = (3.2 + 1.1) * scale, (3.2 - 1.1) * scale
    d.ellipse([cx - ro, cy - ro, cx + ro, cy + ro], fill=WHITE)
    d.ellipse([cx - ri, cy - ri, cx + ri, cy + ri], fill=(0, 0, 0, 0))
    img.alpha_composite(layer)


def render(size, mode):
    n = size * SS
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if mode == "square":  # iOS: full bleed, iOS rounds it
        d.rectangle([0, 0, n, n], fill=BLUE)
        draw_glyph(img, n / 34, 0)
    elif mode == "rounded":  # legacy Android launcher
        d.rounded_rectangle([0, 0, n - 1, n - 1], radius=n * 9 / 34, fill=BLUE)
        draw_glyph(img, n / 34, 0)
    elif mode == "fg":  # adaptive foreground: 108dp canvas, icon fills the 72dp visible area
        icon = n * 72 / 108
        draw_glyph(img, icon / 34, (n - icon) / 2)
    img = img.resize((size, size), Image.LANCZOS)
    if mode == "square":
        img = img.convert("RGB")  # App Store rejects alpha
    return img


res = os.path.join(root, "android/app/src/main/res")
for dpi, s in {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}.items():
    render(s, "rounded").save(f"{res}/mipmap-{dpi}/ic_launcher.png")
    render(s * 108 // 48, "fg").save(f"{res}/mipmap-{dpi}/ic_launcher_foreground.png")

os.makedirs(f"{res}/mipmap-anydpi-v26", exist_ok=True)
with open(f"{res}/mipmap-anydpi-v26/ic_launcher.xml", "w") as f:
    f.write('''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/ic_launcher_background" />
    <foreground android:drawable="@mipmap/ic_launcher_foreground" />
    <monochrome android:drawable="@mipmap/ic_launcher_foreground" />
</adaptive-icon>
''')
with open(f"{res}/values/ic_launcher_background.xml", "w") as f:
    f.write('''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="ic_launcher_background">#1D4ED8</color>
</resources>
''')

ios = os.path.join(root, "ios/Runner/Assets.xcassets/AppIcon.appiconset")
for im in json.load(open(f"{ios}/Contents.json"))["images"]:
    w = float(im["size"].split("x")[0])
    px = round(w * int(im["scale"].rstrip("x")))
    render(px, "square").save(f"{ios}/{im['filename']}")
print("done")
