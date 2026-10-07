"""lib/codec.py: every (rep, transform) pair seen in the D3-D6 script-analysis evidence decodes to its plan.
Run: python3 tests/test_codec.py"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib import codec  # noqa: E402

fails = 0


def check(name, cond):
    global fails
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    fails += 0 if cond else 1


samples = json.loads((ROOT / "tests" / "data" / "codec_samples.json").read_text())
bad = [s for s in samples if not (codec.decode(s["material"], s["rep"], s["transform"], s["key"]) or "")
       .startswith(s["plain_prefix"])]
check(f"{len(samples)} real samples (all reps x transforms seen D3-D6) decode to their plan", not bad)
for s in bad[:5]:
    print("     ", s["file"], s["rep"], s["transform"])

os.environ["HCTF_CODEC_MAX_DAY"] = "5"
d6 = [s for s in samples if codec.REPS.get(s["rep"]) == 6]
check("pre-day view (HCTF_CODEC_MAX_DAY=5) hides day-6 reps",
      d6 and all(codec.decode(s["material"], s["rep"], s["transform"], s["key"]) is None for s in d6))
del os.environ["HCTF_CODEC_MAX_DAY"]

check("unknown rep/transform -> None, never raises",
      codec.decode("abc", "brand_new_rep", "identity") is None and codec.decode("abc", "hex_pairs", "new_tx") is None)
check("int_array: hex tokens, explicit radix, any separator",
      codec.int_array("0x17,0x07") == [23, 7] and codec.int_array("23-7", 10) == [23, 7]
      and codec.int_array("17:07", 16) == [23, 7])
check("b64: urlsafe alphabet + missing padding", codec.b64("dj0x_-8") == b"v=1\xff\xef")
check("plan_kv splits on | and first =", codec.plan_kv("v=1|url=http://x/?a=b")["url"] == "http://x/?a=b")
bat = 'rem HUNTRESS-CODEC:base64_literal|identity\nrem HUNTRESS-MATERIAL:djE9MXxzdGVwcz1h\n'
check("find_codecs: batch HUNTRESS-CODEC/MATERIAL pair", codec.find_codecs(bat)[0]["plain"] == "v1=1|steps=a")
vbs = 'Const Material_ab12 = "76" & _\n  "3d31"\nConst Codec_ab12 = "hex_pairs|identity|"\n'
check("find_codecs: VBS `& _` continuation joined", (codec.find_codecs(vbs)[0]["plain"] or "") == "v=1")
sh = "readonly Material_cd_a='76:3d'\nreadonly Material_cd_b=':31'\nreadonly Codec_cd='hex_colon|identity|'\n"
check("find_codecs: bash split _a/_b parts joined in order", (codec.find_codecs(sh)[0]["plain"] or "") == "v=1")

print(f"\n{'all passed' if not fails else f'{fails} failed'}")
sys.exit(1 if fails else 0)
