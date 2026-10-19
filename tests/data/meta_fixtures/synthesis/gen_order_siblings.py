"""Generator (ffmpeg 7.0.2 lavfi sine/testsrc -> pcm WAV / libmp3lame MP3 / FLAC / libx264 MP4 with creation_time,
Pillow JPEG + EXIF DateTimeOriginal, Pillow PNG renamed .jpg, pypdf PdfWriter /CreationDate, RFC 5322 .eml, stdlib
zipfile with explicit ZipInfo DOS date_time per member): the synthesis order/group sibling fixtures.
usage: python3 gen_order_siblings.py OUTDIR  -> OUTDIR/{order.zip, dated.zip, textonly.zip}"""
import io, os, subprocess, sys, zipfile
from PIL import Image

F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../../tools/imageio_ffmpeg_pkg/imageio_ffmpeg/"
                 "binaries/ffmpeg-linux-x86_64-v7.0.2")
out = sys.argv[1]
os.makedirs(out, exist_ok=True)


def ff(name, *a):
    p = os.path.join(out, name)
    subprocess.run([F, "-y", "-loglevel", "error", *a, p], check=True)
    return open(p, "rb").read()


m = {}
m["clip-a.wav"] = ff("clip-a.wav", "-f", "lavfi", "-i", "sine=frequency=440:duration=2", "-ar", "8000", "-c:a", "pcm_s16le")
m["clip-b.mp3"] = ff("clip-b.mp3", "-f", "lavfi", "-i", "sine=frequency=330:duration=1", "-c:a", "libmp3lame",
                     "-b:a", "64k")
m["clip-c.flac"] = ff("clip-c.flac", "-f", "lavfi", "-i", "sine=frequency=220:duration=3", "-c:a", "flac")
m["clip-d.mp4"] = ff("clip-d.mp4", "-f", "lavfi", "-i", "testsrc=size=160x120:rate=10:duration=1.5", "-c:v",
                     "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
                     "-metadata", "creation_time=2024-03-05T08:00:00Z")
im = Image.new("RGB", (64, 48), (200, 30, 30))
ex = Image.Exif()
ex.get_ifd(0x8769)[0x9003] = "2024:01:02 03:04:05"
b = io.BytesIO(); im.save(b, "JPEG", exif=ex.tobytes()); m["photo.jpg"] = b.getvalue()
b = io.BytesIO(); Image.new("RGB", (8, 8), (0, 0, 255)).save(b, "PNG"); m["thumb.jpg"] = b.getvalue()
from pypdf import PdfWriter
w = PdfWriter(); w.add_blank_page(72, 72); w.add_metadata({"/Producer": "pypdf", "/CreationDate": "D:20240210120000+02'00'"})
b = io.BytesIO(); w.write(b); m["report.pdf"] = b.getvalue()
m["mail.eml"] = (b"From: a@example.org\r\nTo: b@example.org\r\nSubject: hi\r\nDate: Mon, 01 Jan 2024 00:00:00 +0000\r\n"
                 b"Message-ID: <x1@example.org>\r\n\r\nbody\r\n")
m["note.txt"] = b"Evidence note: ordering siblings.\n"
zb = io.BytesIO(); zipfile.ZipFile(zb, "w").writestr("a.txt", "x"); m["invoice.pdf"] = zb.getvalue()
times = {"clip-a.wav": (2023, 5, 1, 10, 0, 0), "clip-b.mp3": (2023, 4, 1, 9, 30, 0), "clip-c.flac": (2023, 6, 1, 8, 0, 0),
         "clip-d.mp4": (2022, 12, 31, 23, 59, 58), "photo.jpg": (2023, 4, 1, 9, 30, 0), "thumb.jpg": (2021, 1, 1, 0, 0, 0),
         "report.pdf": (2023, 7, 7, 7, 7, 6), "mail.eml": (2023, 2, 2, 2, 2, 2), "note.txt": (2024, 9, 9, 9, 9, 8),
         "invoice.pdf": (2020, 3, 3, 3, 3, 4)}
order = ["note.txt", "clip-a.wav", "clip-b.mp3", "clip-c.flac", "clip-d.mp4", "photo.jpg", "thumb.jpg", "report.pdf",
         "mail.eml", "invoice.pdf"]
with zipfile.ZipFile(os.path.join(out, "order.zip"), "w", zipfile.ZIP_DEFLATED) as z:
    for n in order:
        z.writestr(zipfile.ZipInfo(n, times[n]), m[n])
with zipfile.ZipFile(os.path.join(out, "dated.zip"), "w") as z:
    for n in ("report.pdf", "clip-d.mp4", "mail.eml", "photo.jpg"):
        z.writestr(zipfile.ZipInfo(n, times[n]), m[n])
with zipfile.ZipFile(os.path.join(out, "textonly.zip"), "w") as z:
    z.writestr(zipfile.ZipInfo("readme.txt", (2023, 1, 1, 0, 0, 0)), "plain text\n")
    z.writestr(zipfile.ZipInfo("notes.csv", (2023, 1, 2, 0, 0, 0)), "a,b\n1,2\n")
