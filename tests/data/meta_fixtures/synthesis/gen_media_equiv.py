"""Generator (libsndfile via soundfile + mutagen tag writer + stdlib zipfile): audio members for the cross-recording
equivalence fixtures.  usage: python3 gen_media_equiv.py OUTDIR  -> OUTDIR/{equiv.zip, noaudio.zip, lone.wav}"""
import math, os, struct, sys, zipfile
import numpy as np
import soundfile as sf
from mutagen.id3 import ID3, TIT2

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
tone = lambda f, secs, rate: (0.4 * np.sin(2 * math.pi * f * np.arange(int(secs * rate)) / rate) * 32767).astype("<i2")
A, B, C = tone(440, 0.5, 8000), tone(660, 0.6, 8000), tone(300, 0.7, 8000)
files = {}


def write(name, pcm, fmt, sub, title=None, rate=8000):
    p = os.path.join(out, name)
    with sf.SoundFile(p, "w", samplerate=rate, channels=1, format=fmt, subtype=sub) as f:
        if title and fmt != "MP3":
            f.title = title
        f.write(pcm)
    if title and fmt == "MP3":
        t = ID3(); t.add(TIT2(encoding=3, text=title)); t.save(p)
    files[name] = open(p, "rb").read()


write("rec-a.wav", A, "WAV", "PCM_16", "Huntress audio evidence 1a2b3c4d5e6f")
write("rec-a.flac", A, "FLAC", "PCM_16", "Huntress audio evidence 1a2b3c4d5e6f")
write("rec-a-copy.wav", A, "WAV", "PCM_16")                      # untitled: links to rec-a by PCM content only
write("rec-b.wav", B, "WAV", "PCM_16", "Huntress audio evidence 0f9e8d7c6b5a")
write("rec-b.ogg", B, "OGG", "VORBIS", "Huntress audio evidence 0f9e8d7c6b5a")
write("rec-b.mp3", B, "MP3", "MPEG_LAYER_III", "Huntress audio evidence 0f9e8d7c6b5a")
write("odd.wav", C, "WAV", "PCM_16", "Huntress audio evidence 99aa88bb77cc")
files["note.txt"] = b"Evidence note: recordings collected from the shared drive.\n"
with zipfile.ZipFile(os.path.join(out, "equiv.zip"), "w") as z:
    for n in ("note.txt", "rec-b.ogg", "rec-a.wav", "odd.wav", "rec-a-copy.wav", "rec-a.flac", "rec-b.wav", "rec-b.mp3"):
        z.writestr(zipfile.ZipInfo(n, (2026, 10, 17, 12, 0, 0)), files[n])
with zipfile.ZipFile(os.path.join(out, "noaudio.zip"), "w") as z:
    z.writestr(zipfile.ZipInfo("note.txt", (2026, 10, 17, 12, 0, 0)), files["note.txt"])
    z.writestr(zipfile.ZipInfo("readme.md", (2026, 10, 17, 12, 0, 0)), b"# no audio here\n")
open(os.path.join(out, "lone.wav"), "wb").write(files["rec-a.wav"])
