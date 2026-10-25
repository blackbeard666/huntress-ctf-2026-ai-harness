"""Offline generator for the ascii-art fixtures (figlet banners + 5x7 dot matrix). Writers: pyfiglet 1.0.4 / figlet.js
(npm figlet 1.x) / luma.core.legacy text() on a Pillow image; oracles: the OTHER figlet implementation re-renders the plain
and must match byte-for-byte (after rstrip per row), Pillow pixel readback for the dot matrix. Never imports lib.*.
Run: PYTHONPATH=tools/pyfig python3 tests/data/warmups_fixtures/asciiart_mkfixtures.py"""
import json
import subprocess
from pathlib import Path

import pyfiglet
from PIL import Image, ImageDraw
from luma.core.legacy import text as luma_text
from luma.core.legacy.font import LCD_FONT

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
NODE = str(ROOT / "tools/node/bin/node")
FIGJS = str(ROOT / "tools/npm-figlet/node_modules/figlet")
S = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: {}"


def figjs(plain, font, width=None):
    opts = {"font": font} | ({"width": width, "whitespaceBreak": True} if width else {})
    js = f"const f=require({json.dumps(FIGJS)});process.stdout.write(f.textSync(process.argv[1],{json.dumps(opts)}))"
    return subprocess.run([NODE, "-e", js, plain], capture_output=True, text=True, check=True).stdout


def norm(t):
    return "\n".join(x.rstrip() for x in t.split("\n")).rstrip("\n")


def luma_img(plain):
    img = Image.new("1", (8 * len(plain), 8))
    luma_text(ImageDraw.Draw(img), (0, 0), plain, fill=1, font=LCD_FONT)
    return img


def rows_of(img, on="#", off="."):
    w, h = img.size
    return ["".join(on if img.getpixel((x, y)) else off for x in range(w)) for y in range(h)]


def write(name, d):
    (OUT / f"{name}.json").write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
    print(name, d.get("expected"))


# 1. figlet standard, pyfiglet default width 80 (wrapped into 6-row blocks); oracle figlet.js re-render, no wrap per block
p = S.format("amber-falcon-42")
enc = pyfiglet.figlet_format(p, font="standard")
blocks = enc.rstrip("\n").split("\n")
# oracle: figlet.js renders each wrapped line's words separately (pyfiglet breaks at a blank, the blank dropped); its
# 1-column left margin removed, the stacked blocks must equal pyfiglet's output row for row
rem, stack, blk = p, [], 0
nb = len(blocks) // 6
while rem:
    want = norm("\n".join(blocks[6 * blk:6 * blk + 6]))
    cuts = [i for i in range(len(rem), 0, -1) if i == len(rem) or rem[i] == " "]
    cuts += [i for i in range(len(rem) - 1, 0, -1) if i not in cuts]   # a word wider than the line: cut mid-word
    for k in cuts:
        got = norm("\n".join(x[1:] for x in figjs(rem[:k], "Standard").split("\n")))
        if got == want:
            stack.append(rem[:k])
            rem, blk = rem[k:].removeprefix(" "), blk + 1
            break
    else:
        raise SystemExit(f"figlet.js oracle: block {blk} not reproduced")
assert blk == nb, (blk, nb)
write("asciiart-figlet-standard-amber", {
    "codec": "figlet-standard", "plain": p, "encoded": enc,
    "generator_cmd": "PYTHONPATH=tools/pyfig python3 -c 'import pyfiglet,sys; sys.stdout.write(pyfiglet.figlet_format(sys.argv[1], font=\"standard\"))' \"$plain\"  # pyfiglet 1.0.4, width 80",
    "oracle_cmd": "for each wrapped line L: tools/node/bin/node -e 'const f=require(\"./tools/npm-figlet/node_modules/figlet\");process.stdout.write(f.textSync(process.argv[1],{font:\"Standard\"}))' \"$L\" | cut -c2-  # figlet.js (independent JS FIGlet driver) per line, stacked == encoded (rows rstripped); lines: " + " | ".join(stack),
    "oracle_plain": p, "expected": "match"})

# 2. figlet banner, no wrap, written by figlet.js; oracle pyfiglet width=10000
p = S.format("jade-otter-7731")
enc = figjs(p, "Banner") + "\n"
assert norm("\n".join(x[1:] for x in enc.split("\n"))) == norm(pyfiglet.figlet_format(p, font="banner", width=10000)), "figlet.js vs pyfiglet banner differ"
write("asciiart-figlet-banner-jade", {
    "codec": "figlet-banner-nowrap", "plain": p, "encoded": enc,
    "generator_cmd": "tools/node/bin/node -e 'const f=require(\"./tools/npm-figlet/node_modules/figlet\");process.stdout.write(f.textSync(process.argv[1],{font:\"Banner\"}))' \"$plain\"  # figlet.js, no wrap",
    "oracle_cmd": "PYTHONPATH=tools/pyfig python3 -c 'import pyfiglet,sys; print(pyfiglet.figlet_format(sys.argv[1], font=\"banner\", width=10000))' \"$plain\"  # pyfiglet re-render == encoded minus its margin column (rows rstripped)",
    "oracle_plain": p, "expected": "match"})

# 3. figlet big, written by figlet.js (no wrap: its width option smushes wrapped lines vertically); oracle pyfiglet
p = S.format("cobalt-heron-58")
enc = figjs(p, "Big") + "\n"
ok = norm("\n".join(x[1:] for x in enc.split("\n"))) == norm(pyfiglet.figlet_format(p, font="big", width=10000))
assert ok, "figlet.js vs pyfiglet big differ"
write("asciiart-figlet-big-cobalt", {
    "codec": "figlet-big-nowrap", "plain": p, "encoded": enc,
    "generator_cmd": "tools/node/bin/node -e 'const f=require(\"./tools/npm-figlet/node_modules/figlet\");process.stdout.write(f.textSync(process.argv[1],{font:\"Big\"}))' \"$plain\"  # figlet.js, no wrap, 1-col left margin kept",
    "oracle_cmd": "PYTHONPATH=tools/pyfig python3 -c 'import pyfiglet,sys; print(pyfiglet.figlet_format(sys.argv[1], font=\"big\", width=10000))' \"$plain\"  # pyfiglet re-render == encoded minus its margin column (rows rstripped)",
    "oracle_plain": p, "expected": "match"})

# 4. 5x7 dot matrix as #/. rows: luma.core legacy text() (8-px pitch, 8 rows) on a Pillow image
p = S.format("maple-lynx-19")
img = luma_img(p)
enc = "\n".join(rows_of(img))
# oracle: independent Pillow readback of the same image, glyph j = columns 8j..8j+4, matched against LCD_FONT columns
inv = {tuple(LCD_FONT[c][:5]): chr(c) for c in range(0x20, 0x7f)}
back = "".join(inv.get(tuple(sum((img.getpixel((8 * j + k, y)) and 1 or 0) << y for y in range(8)) for k in range(5)), "?")
               for j in range(len(p)))
assert back == p
write("asciiart-dotmatrix-rows-maple", {
    "codec": "dotmatrix5x7-luma-rows", "plain": p, "encoded": enc,
    "generator_cmd": "PYTHONPATH=tools/pyfig python3 -c 'from luma.core.legacy import text; from luma.core.legacy.font import LCD_FONT; from PIL import Image, ImageDraw; ...'  # luma.core text() into an 8-row Pillow image, pixels -> #/. (asciiart_mkfixtures.py)",
    "oracle_cmd": "Pillow getpixel readback of the luma image, 5 column bytes per 8-px cell looked up in luma LCD_FONT (asciiart_mkfixtures.py)",
    "oracle_plain": back, "expected": "match"})

# 5. 5x7 dot matrix as hex row bytes (7 per char, 5-bit MSB = left), from the luma image rows
p = S.format("clover-ibis-604")
img = luma_img(p)
enc = " ".join(f"{sum((1 if img.getpixel((8 * j + k, y)) else 0) << (4 - k) for k in range(5)):02x}"
               for j in range(len(p)) for y in range(7))
back = "".join(inv.get(tuple(sum(((int(enc.split()[7 * j + y], 16) >> (4 - k)) & 1) << y for y in range(7)) for k in range(5)), "?")
               for j in range(len(p)))
assert back == p
write("asciiart-dotmatrix-hexrows-clover", {
    "codec": "dotmatrix5x7-hexrows", "plain": p, "encoded": enc,
    "generator_cmd": "luma.core text() into a Pillow image, each 8-px cell's 7 rows -> 5-bit row bytes as lowercase hex (asciiart_mkfixtures.py)",
    "oracle_cmd": "python3 transpose of each 7-byte group back to 5 column bytes, looked up in luma LCD_FONT (asciiart_mkfixtures.py)",
    "oracle_plain": back, "expected": "match"})

# 6. decoy: figlet 'slant' (a font NOT vendored) -> the figlet decoder must not answer
p = S.format("amber-falcon-42")
write("asciiart-decoy-figlet-slant", {
    "codec": "figlet-slant*", "plain": None, "encoded": pyfiglet.figlet_format(p, font="slant"), "decoy": True,
    "generator_cmd": "PYTHONPATH=tools/pyfig python3 -c 'import pyfiglet,sys; print(pyfiglet.figlet_format(sys.argv[1], font=\"slant\"))' \"$plain\"",
    "oracle_cmd": "pyfiglet.FigletFont('slant') glyph rows differ from standard/banner/big -> not one of the vendored fonts",
    "oracle_plain": p, "expected": "none"})

# 7. decoy: plain hex of the sentence (bytes 0x20-0x7a): not 5x7 glyph bytes
p = S.format("jade-otter-7731")
hx = subprocess.run(["xxd", "-p", "-c", "1000"], input=p.encode(), capture_output=True, check=True).stdout.decode().strip()
write("asciiart-decoy-plain-hex", {
    "codec": "hex*", "plain": None, "encoded": " ".join(hx[i:i + 2] for i in range(0, len(hx), 2)), "decoy": True,
    "generator_cmd": "printf %s \"$plain\" | xxd -p -c 1000 | sed 's/../& /g'",
    "oracle_cmd": "printf %s \"$encoded\" | xxd -r -p  # -> the plain sentence (ordinary hex, not glyph rows)",
    "oracle_plain": p, "expected": "none"})
