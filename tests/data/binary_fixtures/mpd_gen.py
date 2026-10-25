""".NET twin patch-diff fixtures (lib.binary.dotnet_patch_diff): same-length hand patches of the cached D03/D22/D23
sample dlls (no dotnet build). A = vulnerable (patched copy), B = corrected (the original build). Byte surgery is
pefile RVA->offset + asserted literal byte runs only.
usage (repo root): python3 tests/data/binary_fixtures/mpd_gen.py D03.dll D22.dll D23.dll"""
import pathlib, sys
import pefile

d03, d22, d23 = (pathlib.Path(p).read_bytes() for p in sys.argv[1:4])
OUT = pathlib.Path(__file__).resolve().parent


def off(data, rva):
    return pefile.PE(data=data, fast_load=True).get_offset_from_rva(rva)


def patch(data, at, old, new):
    assert len(old) == len(new) and data[at:at + len(old)] == old, (hex(at), data[at:at + len(old)].hex())
    return data[:at] + new + data[at + len(old):]


def save(name, a, b):
    (OUT / f"mpd_{name}_a.bin").write_bytes(a)
    (OUT / f"mpd_{name}_b.bin").write_bytes(b)


main23 = off(d23, 0x21B8) + 12   # Huntress.Binary.Day23.Program::Main, fat header 12
# checked arithmetic: A's loop counter uses plain `add`, B (original) `add.ovf`
save("ovf", patch(d23, main23 + 0x24, bytes.fromhex("110617d61306"), bytes.fromhex("110617581306")), d23)
# null guard: A drops `dup; brtrue.s +6; pop` (env var ?? "workstation" -> always "workstation"), B keeps it
save("nullguard", patch(d23, main23 + 0x0A, bytes.fromhex("252d0626"), bytes.fromhex("26000000")), d23)
# exception handling: A's Program::Campaign loses its try/finally (fat header MoreSects 0x08 cleared), B keeps it
camp = off(d03, 0x2368)
save("try", patch(d03, camp, bytes([d03[camp]]), bytes([d03[camp] & ~0x08])) if d03[camp] & 0x08 else None, d03)
# bounds check: A's decode loop compares against a hard-coded 380, B (original) against get_arr@1().Length
main22 = off(d22, 0x2108) + 12
save("bounds", patch(d22, main22 + 0xD1, d22[main22 + 0xD1:main22 + 0xD8], bytes.fromhex("207c0100000000")), d22)
# DECOY: same IL, only the Module MVID (#GUID heap) and the PE TimeDateStamp differ
pe = pefile.PE(data=d23)
ts = pe.FILE_HEADER.get_file_offset() + 4
g = d23.find(b"#GUID\0")
assert g > 0
mvid = d23.find(bytes.fromhex("f04b83cbdb7f7c42b2bd5588b8f660b1"))   # cb834bf0-7fdb-427c-b2bd-5588b8f660b1 (LE)
assert mvid > 0
dec = patch(d23, ts, d23[ts:ts + 4], b"\x01\x02\x03\x04")
dec = patch(dec, mvid, dec[mvid:mvid + 16], bytes(range(0x10, 0x20)))
save("decoy_mvid", d23, dec)
# DECOY: B is a truncated copy (headers only) -> no CLI metadata -> None
save("decoy_trunc", d23, d23[:1024])
