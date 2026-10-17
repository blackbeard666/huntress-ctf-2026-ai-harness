# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_dc3dac5e = ("2tONwZabxZbBkZLClI7G18LH09aNjMHC79DQxtHXzdbrjMLXwufOwtHEzNHzjJngnsvXwtP8xs/Kxd/BlpvFlsGRksKUjs"
    "3EysLTzsLAnsfK/M3EysLTzsLA38bPzNDNzMD8zcbHx8rL/NTNzMvX2tOezcrCy8D80NTMx83K1N/XzcbR0dbA/MDa0/zH"
    "xtDCwfzL0MLLntHGytHRwsDfzcrMyfzRy8CezczK18LA0NbFwczf2tHM18DCxfzG0dbQzM/AntvC183a0N+SntfN1szA/M"
    "bEwtfQ39HM19PK0cDQxsf82tPN1tGe0cbX08LHwt/Q0MbAzNHT/MvA18LT0MrHj8/CwMzP/MbXwsDMz57Q08bX0N+RntU=")
CODEC_dc3dac5e = "base64_chunks|reverse_then_xor|a3"

def load_dc3dac5e():
    return base64.b64decode(MATERIAL_dc3dac5e)

def decode_dc3dac5e(v_a19c):
    return bytes(value ^ 163 for value in reversed(v_a19c))

def recover_dc3dac5e():
    v_d41a = 19 * 7 - 133
    v_a702 = "decode"
    while v_a702 != "done":
        if v_a702 == "decode":
            v_b27e = decode_dc3dac5e(load_dc3dac5e())
            v_a702 = "done"
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_dc3dac5e():
    stream = io.BytesIO(recover_dc3dac5e().encode("ascii"))
    return stream.read().decode("ascii")

def surface_dc3dac5e():
    values = ("closure_factory", "chr_join", "hash_based_pyc_current", "pythonw_hidden_console")
    def inner():
        return values
    return inner()

def obfuscation_dc3dac5e():
    return "".join(chr(value) for value in (99, 104, 114, 95, 106, 111, 105, 110))

def plan_dc3dac5e():
    fields = dict(item.split("=", 1) for item in inspect_dc3dac5e().split("|"))
    analysis_surface = surface_dc3dac5e()
    obfuscation_surface = obfuscation_dc3dac5e()
    operation_plan = ("runpy_descriptor", ("python3", fields["file_path"]))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_dc3dac5e())

# reconstruction complete