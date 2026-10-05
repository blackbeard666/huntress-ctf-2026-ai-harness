#!/usr/bin/env python3
"""Adversarial self-test for the hardening helpers (reference/HARDENING.md).

Generates HARDENED synthetic fixtures on the fly and asserts each new capability recovers the planted
answer — so a regression is caught here, before a live drop, rather than during one.

Run:  source bin/env.sh && python3 tests/test_hardening.py      (exit 0 = all pass)
"""
import io
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PASS, FAIL = [], []


def check(name, cond):
    (PASS if cond else FAIL).append(name)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")


def test_android(tmp):
    """APK with the answer MOVED out of huntress_puzzle.json into a dex string (zero obfuscation break)."""
    from lib import android
    apk = tmp / "moved.apk"
    with zipfile.ZipFile(apk, "w") as z:
        z.writestr("AndroidManifest.xml", b"\x03\x00\x08\x00")  # stub (manifest parse is a separate path)
        z.writestr("classes.dex", b"dex\n035\x00" + b"\x00ANS-DEADBEEF12345678\x00")
        z.writestr("assets/other.json", b"{}")
    check("android: answer recovered from dex (not puzzle-json)",
          android.extract_answer(str(apk)) == "ANS-DEADBEEF12345678")


def test_binary(tmp):
    """Stripped-Go function-name recovery from .gopclntab (names survive stripping)."""
    from lib import binary
    go = ROOT / "challenges/day04/binary-go-fish/single_solve/work/d04--variant-000.elf"
    if go.exists():
        fns = binary.go_pclntab_funcs(go.read_bytes())
        check("binary: stripped-Go names via .gopclntab (main.main present)",
              any(f == "main.main" for f in fns))
        check("binary: go_buildinfo version detected", bool(binary.go_buildinfo(go.read_bytes())))
    else:
        print("  [SKIP] binary: Day4 Go sample not on disk")
    check("binary: packer_info entropy gate on random (packed) data",
          binary.packer_info(bytes(range(256)) * 200)["entropy"] > 7.0)


def test_ciphers(tmp):
    from lib import ciphers as C
    pt = b"the quick brown fox jumps over the lazy dog many times over and over again now"
    k, dec, _ = C.xor_crack(C.repeating_key_xor(pt, "KEY"))[0]
    check("ciphers: repeating-key XOR crack (KEY)", dec.encode("latin-1") == pt)
    check("ciphers: atbash roundtrip", C.atbash(C.atbash("Hello")) == "Hello")
    check("ciphers: morse", C.morse_decode(".... . .-.. .-.. ---") == "HELLO")
    check("ciphers: base58", C.base58_decode("StV1DL6CwTryKyV") == b"hello world")
    check("ciphers: quoted-printable", C.quoted_printable_decode("Hi=20there=21") == "Hi there!")
    msg = "attack at dawn when the guards are asleep and the gate is open wide"
    check("ciphers: caesar_all recovers plaintext", C.caesar_all(C.caesar(msg, 7))[0][1] == msg)


def test_stego(tmp):
    try:
        import numpy as np
        from PIL import Image
    except ImportError:
        print("  [SKIP] stego: PIL/numpy missing")
        return
    from lib import stego
    secret = b"ANS-CAFEBABE12345678 hidden"
    bits = np.unpackbits(np.frombuffer(secret, dtype=np.uint8))
    arr = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
    r = arr[:, :, 0].reshape(-1)
    r[:len(bits)] = (r[:len(bits)] & 0xFE) | bits
    arr[:, :, 0] = r.reshape(50, 50)
    img = tmp / "lsb.png"
    Image.fromarray(arr).save(img)
    v = stego.lsb_variants(str(img))
    check("stego: LSB-R extraction finds the hidden ANS",
          any("ANS-CAFEBABE12345678" in s for s in stego.printable_runs(v.get("lsb-R", b""))))
    trail = tmp / "trail.png"
    trail.write_bytes(img.read_bytes() + b"PK\x03\x04APPENDED")
    check("stego: trailing_data carve", stego.trailing_data(str(trail)).startswith(b"PK\x03\x04"))
    try:
        import pyzipper
        ez = tmp / "enc.zip"
        with pyzipper.AESZipFile(ez, "w", encryption=pyzipper.WZ_AES) as z:
            z.pwd = b"huntress"
            z.writestr("f.txt", "x")
        check("stego: crack_zip (wordlist)", stego.crack_zip(str(ez)) == "huntress")
    except ImportError:
        print("  [SKIP] stego: pyzipper missing")


def test_pyc(tmp):
    import py_compile
    from lib import pyc
    src = tmp / "s.py"
    src.write_text('def f():\n    return "ANS-PYCTEST0000"\n')
    pycf = tmp / "s.pyc"
    py_compile.compile(str(src), str(pycf))
    check("pyc: recover surfaces the constant (decompyle3 or dis)",
          "ANS-PYCTEST0000" in pyc.decompile_pyc(str(pycf)))


def main():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        for t in (test_android, test_binary, test_ciphers, test_stego, test_pyc):
            print(f"== {t.__name__} ==")
            try:
                t(tmp)
            except Exception as e:  # noqa: BLE001
                FAIL.append(f"{t.__name__}: EXCEPTION {e}")
                print(f"  [FAIL] {t.__name__}: EXCEPTION {e}")
    print(f"\n=== {len(PASS)} passed, {len(FAIL)} failed ===")
    if FAIL:
        print("FAILURES:", FAIL)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
