"""Fixture WRITER for the wav-deep chunk fields (stdlib `wave` for fmt+data, struct for BWF/INFO/cue/iXML/fact
per EBU Tech 3285 + the RIFF spec). Independent of lib.meta. Usage: python3 gen_wav_deep.py <outdir>"""
import io
import struct
import sys
import wave


def ck(cid, body):
    return cid + struct.pack("<I", len(body)) + body + (b"\x00" if len(body) & 1 else b"")


def pcm_base(rate=8000, n=801):
    bio = io.BytesIO()
    with wave.open(bio, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(bytes(range(256)) * (2 * n // 256) + b"\x00" * (2 * n % 256))
    b = bio.getvalue()
    return b[12:36], b[36:]          # "fmt " chunk, "data" chunk (wave writes fmt then data)


def riff(chunks, trailer=b""):
    body = b"WAVE" + b"".join(chunks)
    return b"RIFF" + struct.pack("<I", len(body)) + body + trailer


def bext(desc, orig, ref, date, time, tref, umid):
    b = desc.ljust(256, b"\0") + orig.ljust(32, b"\0") + ref.ljust(32, b"\0") + date + time
    b += struct.pack("<QH", tref, 1) + umid.ljust(64, b"\0") + b"\0" * 10 + b"\0" * 180
    return b + b"A=PCM,F=8000,W=16,M=mono,T=HuntressRec\r\n"


def info(tags):
    return b"INFO" + b"".join(ck(k, v + b"\0") for k, v in tags)


def cue(n):
    pts = b"".join(struct.pack("<II4sIII", i + 1, i * 100, b"data", 0, 0, i * 100) for i in range(n))
    return struct.pack("<I", n) + pts


def main(out):
    fmt, data = pcm_base()
    umid = bytes.fromhex("060a2b340101010501010d4313000000") + bytes.fromhex("a1b2c3d4e5f60718293a4b5c6d7e8f90")
    ixml = b'<?xml version="1.0" encoding="UTF-8"?><BWFXML><IXML_VERSION>1.61</IXML_VERSION>' \
           b'<PROJECT>Huntress</PROJECT><TAPE>T01</TAPE></BWFXML>'
    tags = [(b"INAM", b"Huntress audio evidence 3f9a1c0b7d2e"), (b"IART", b"Field Recorder 7"),
            (b"ICMT", b"exfil staged in trailer"), (b"ICRD", b"2026-10-17"), (b"ISFT", b"Lavf61.7.100")]
    payload = b"PK\x03\x04\x14\x00\x00\x00\x08\x00" + b"hidden-flag-payload" * 3
    bwf = riff([fmt, ck(b"bext", bext(b"Interview take 3 - evidence copy", b"HuntressRec v2.1", b"USHNT0000012345",
                                      b"2026-10-17", b"14:05:33", 864000123, umid)),
                ck(b"iXML", ixml), data, ck(b"LIST", info(tags)), ck(b"cue ", cue(3))], payload)
    open(f"{out}/bwf.bin", "wb").write(bwf)

    # A-law (format tag 6) + fact, odd-length INFO text, no bext/iXML/cue, no trailer, consistent RIFF size.
    al_fmt = ck(b"fmt ", struct.pack("<HHIIHHH", 6, 2, 22050, 44100, 2, 8, 0))
    al_data = ck(b"data", bytes(range(256)) * 4 + b"\x55" * 6)          # 1030 bytes -> 515 frames
    alaw = riff([al_fmt, ck(b"fact", struct.pack("<I", 515)), ck(b"LIST", info([(b"ISFT", b"sox 14.4.2"),
                                                                                (b"INAM", b"odd")])), al_data])
    open(f"{out}/alaw_fact.bin", "wb").write(alaw)

    # stdlib `wave` output (fmt + data last), payload appended AND the RIFF size patched to cover it (no mismatch):
    # the trailer is only visible as bytes after the data chunk.
    fmt2, data2 = pcm_base(rate=16000, n=500)
    tail = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00" + b"This program cannot be run" * 2
    patched = riff([fmt2, data2], tail)
    patched = patched[:4] + struct.pack("<I", len(patched) - 8) + patched[8:]
    open(f"{out}/patched.bin", "wb").write(patched)


if __name__ == "__main__":
    main(sys.argv[1])
