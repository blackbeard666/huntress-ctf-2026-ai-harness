"""Generator for the vba_ovba_* fixtures (run offline, NOT part of the gate):
    PYTHONPATH=tools/pyvba .venv/bin/python tests/data/script_fixtures/vba_ovba_gen.py <xlsxwriter examples/vbaProject.bin>
Template = XlsxWriter's shipped vbaProject.bin (real Excel output). The Module1 source is replaced: p-code kept up to
MODULEOFFSET (read by oletools' VBA_Project), then the new source compressed by ovba_compress() below (MS-OVBA spec, checked by oletools'
decompress_stream); the OLE container is rewritten by the `ms_cfb` pip package. Plans / materials are encoded with stdlib only.
Oracle: .venv/bin/olevba --decode <out> (prints the module source); the material is decoded by a stdlib one-liner."""
import base64
import gzip
import io
import json
import os
import sys
import tempfile
import zipfile

import olefile
from ms_cfb.ole_file import OleFile
from ms_cfb.Models.Directories.root_directory import RootDirectory
from ms_cfb.Models.Directories.storage_directory import StorageDirectory
from ms_cfb.Models.Directories.stream_directory import StreamDirectory
from oletools.olevba import VBA_Project, decompress_stream

# ms_ovba_compression 1.0.1 is broken past ~1 KiB (maxLength computed as `0xFFFF << bitCount + 3`; bad raw-chunk
# headers), so the container is written here straight from MS-OVBA 2.4.1.3.6-2.4.1.3.19 (greedy matcher, one
# CompressedChunk per 4096 bytes), and every output must round-trip through oletools' decompress_stream (the oracle).
def ovba_compress(raw):
    out = bytearray(b"\x01")
    for cs in range(0, len(raw), 4096):
        chunk, body, pos = raw[cs:cs + 4096], bytearray(), 0
        while pos < len(chunk):
            flag_at, flag = len(body), 0
            body.append(0)
            for bit in range(8):
                if pos >= len(chunk):
                    break
                bc = max((pos - 1).bit_length(), 4) if pos else 4
                maxlen, best, boff = (0xFFFF >> bc) + 3, 0, 0
                for off in range(1, min(pos, 1 << bc) + 1):
                    n = 0
                    while n < maxlen and pos + n < len(chunk) and chunk[pos + n] == chunk[pos + n - off]:
                        n += 1
                    if n > best:
                        best, boff = n, off
                if best >= 3:
                    body += (((boff - 1) << (16 - bc)) | (best - 3)).to_bytes(2, "little")
                    flag |= 1 << bit
                    pos += best
                else:
                    body.append(chunk[pos])
                    pos += 1
            body[flag_at] = flag
        assert len(body) <= 4096
        out += (0xB000 | (len(body) - 1)).to_bytes(2, "little") + body
    return bytes(out)


HERE = os.path.dirname(os.path.abspath(__file__))


def build(template, source):
    ole = olefile.OleFileIO(template)
    proj = VBA_Project(ole, "VBA/", "PROJECT", "VBA/dir")
    for _ in proj.parse_modules():
        pass
    offs = {m.streamname: m.textoffset for m in proj.modules}
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "VBA"))
    for ent in ole.listdir():
        data = ole.openstream(ent).read()
        if ent == ["VBA", "Module1"]:
            raw = source.replace("\n", "\r\n").encode("latin-1")
            comp = ovba_compress(raw)
            # the pip compressor is not trusted blindly: both independent decompressors must give the source back
            assert bytes(decompress_stream(bytearray(comp))) == raw
            data = data[:offs["Module1"]] + comp
        with open(os.path.join(tmp, *ent), "wb") as f:
            f.write(data)
    root = RootDirectory()
    for name in sorted(os.listdir(tmp)):
        p = os.path.join(tmp, name)
        if os.path.isdir(p):
            st = StorageDirectory(name)
            for sub in sorted(os.listdir(p)):
                st.add_directory(StreamDirectory(sub, os.path.join(p, sub)))
            root.add_directory(st)
        else:
            root.add_directory(StreamDirectory(name, p))
    of = OleFile()
    of.root_directory = root
    out = os.path.join(tmp, "out.bin")
    of.create_file(out)
    return open(out, "rb").read()


def wrap(material, width=60):
    parts = [material[i:i + width] for i in range(0, len(material), width)]
    return " & _\n    ".join(f'"{p}"' for p in parts)


def module(name, ident, material, spec, filler=0, attr=True):
    words = ["ledger", "accrual", "variance", "forecast", "region", "margin", "audit", "quota", "rebate", "freight"]
    pad = "".join(f"    s = s & \"{words[i * 7 % 10]} {i * 7919 % 10007} {words[i * 3 % 10]}\" & Chr({65 + i % 26})\n"
                  for i in range(filler))
    return ((f'Attribute VB_Name = "Module1"\n' if attr else "") + f"Option Explicit\n' {name}\n"
            f"Private Const Codec_{ident} As String = \"{spec}\"\n"
            f"Private Const Material_{ident} As String = {wrap(material)}\n\n"
            f"Sub AutoOpen()\n    Dim s As String\n{pad}    Debug.Print Len(s)\nEnd Sub\n")


def main(template):
    fx = {}
    # 1. raw vbaProject.bin: base64(xor 0x5a) material split over `& _` continuation lines
    p1 = ("v=1|language=vba|role=dropper|attack=T1059.005|steps=decode_payload,write_file,run|"
          "campaign_id=VBA-ovba11|url=https://vba-ovba11.example.invalid/stage.bin|file=%TEMP%\\upd.exe")
    m1 = base64.b64encode(bytes(c ^ 0x5A for c in p1.encode())).decode()
    fx["vba_ovba_bin_b64xor"] = (build(template, module("macro loader", "a11", m1, "base64|xor|0x5a")), p1,
                                 "base64|xor|0x5a")
    # 2. .xlsm (XlsxWriter) whose module source spans several 4 KiB OVBA chunks (gzip+base64 material at the end)
    p2 = ("v=1|language=vba|role=loader|attack=T1204.002|steps=decode_payload,inflate_stage,run|"
          "campaign_id=VBA-ovba22|url=https://vba-ovba22.example.invalid/q3.dat|mutex=Global\\ovba22")
    m2 = base64.b64encode(gzip.compress(p2.encode(), mtime=0)).decode()
    src2 = module("multi-chunk", "b22", m2, "gzip_base64|identity|", filler=260)
    bin2 = build(template, src2)
    import xlsxwriter
    tmp = tempfile.mkdtemp()
    with open(os.path.join(tmp, "vbaProject.bin"), "wb") as f:
        f.write(bin2)
    wb = xlsxwriter.Workbook(os.path.join(tmp, "q3.xlsm"))
    wb.add_worksheet().write("A1", "Q3 totals")
    wb.add_vba_project(os.path.join(tmp, "vbaProject.bin"))
    wb.close()
    fx["vba_ovba_xlsm_multichunk"] = (open(os.path.join(tmp, "q3.xlsm"), "rb").read(), p2, "gzip_base64|identity|")
    # 3. DECOY: same container shape and codec spec, but the material is a benign non-plan string (field absent)
    m3 = base64.b64encode(bytes(c ^ 0x5A for c in b"Q3 totals reconciled for EMEA; variance under 2 percent, see ledger")).decode()
    fx["vba_ovba_decoy_noplan"] = (build(template, module("decoy", "c33", m3, "base64|xor|0x5a")), None,
                                     "base64|xor|0x5a")
    # 4. no `Attribute VB_` header in the source (hand-built / stripped project): only MODULEOFFSET from the dir stream
    #    locates it. hex material, add 7 transform
    p4 = ("v=1|language=vba|role=persistence|attack=T1547.001|steps=decode_payload,set_run_key|campaign_id=VBA-ovba44|"
          "regkey=HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\Q3Sync")
    m4 = bytes((c + 7) & 0xFF for c in p4.encode()).hex()
    fx["vba_ovba_bin_noattr_hexadd"] = (build(template, module("no attribute header", "d44", m4, "hex|add|7",
                                                               attr=False)), p4, "hex|add|7")
    for name, (data, plain, spec) in fx.items():
        ext = "xlsm" if name.endswith("multichunk") else "bin"
        with open(os.path.join(HERE, name + "." + ext), "wb") as f:
            f.write(data)
        rep = spec.split("|")
        oracle = {"xor": "base64 -d | python3 -c 'import sys; print(bytes(c ^ 0x5a for c in sys.stdin.buffer.read()).decode())'",
                  "add": "xxd -r -p | python3 -c 'import sys; print(bytes((c - 7) % 256 for c in sys.stdin.buffer.read()).decode())'"
                  }.get(rep[1], "base64 -d | gunzip")
        doc = {"text": data.decode("latin-1"), "expected_plain": plain, "decoy": plain is None,
               "_doc": f"latin-1 text of {name}.{ext}: MS-OVBA compressed VBA module source in VBA/Module1 "
                       f"(Codec spec {spec!r}); find_codecs must read it through the OLE dir stream / OVBA chunks",
               "generator_cmd": "PYTHONPATH=tools/pyvba .venv/bin/python tests/data/script_fixtures/vba_ovba_gen.py "
                                ".run/tmp/vbadl/xlsxwriter-3.2.9/examples/vbaProject.bin  (MS-OVBA spec compressor in the script, round-tripped by oletools decompress_stream; "
                                "ms_cfb pip OLE writer; XlsxWriter add_vba_project for the .xlsm)",
               "oracle_cmd": f".venv/bin/olevba --decode {name}.{ext} | sed -n '/Material_/,/^$/p' | grep -o '\"[^\"]*\"'"
                             f" | tr -d '\"\\n' | {oracle}" + ("  # benign sentence, no v=1 plan" if plain is None else "")}
        with open(os.path.join(HERE, name + ".json"), "w") as f:
            json.dump(doc, f, indent=1)
        print(name, len(data))


if __name__ == "__main__":
    main(sys.argv[1])
