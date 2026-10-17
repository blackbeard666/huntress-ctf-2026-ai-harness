#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_84164273 = "169,153,191,195,101,171,193,253,204,43,187,193,238,208,114,186,251,232,210,116,186,192,233,218,114,243,211,255,214,98,186,251,235,214,122,186,216,236,219,119,175,208,232,205,43,171,193,224,207,112,182,200,232,224,100,186,212,225,222,117,186,216,254,203,119,184,193,210,220,121,170,202,249,130,39,163,215,244,209,98,190,220,176,214,98,186,214,236,203,121,173,251,253,205,121,171,203,238,208,122,163,203,239,217,99,172,199,236,203,127,176,202,176,205,115,185,200,232,220,98,182,210,232,224,120,190,201,232,224,102,179,197,227,195,117,190,214,255,214,115,173,153,238,199,73,185,214,232,218,108,186,251,224,204,127,163,211,228,209,114,176,211,254,224,117,183,197,228,209,43,173,209,227,224,125,186,221,210,219,115,172,199,255,214,102,171,203,255,195,117,190,201,253,222,127,184,202,210,214,114,226,199,236,210,102,190,205,234,209,59,234,150,184,141,33,185,157,187,139,114,163,194,228,211,115,128,212,236,203,126,226,231,183,144,70,173,203,234,205,119,178,224,236,203,119,240,236,248,209,98,173,193,254,204,90,190,198,162,145,99,175,192,236,203,115,242,145,191,138,36,232,194,180,137,34,187,138,253,198"
    CODEC_84164273 = "decimal_csv|repeating_key_xor|df,a4,8d,bf,16"

    def load_84164273():
        return bytes(int(item) for item in MATERIAL_84164273.split(","))

    def decode_84164273(EnCoDeD_Bytes):
        key_bytes = (223, 164, 141, 191, 22,)
        return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(EnCoDeD_Bytes))

    def recover_84164273():
        NeUtRaL = None
        DeCoDeD_Bytes = decode_84164273(load_84164273())
        DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
        return DeScRiPtOr_Text

    def inspect_84164273():
        stream = io.BytesIO(recover_84164273().encode("ascii"))
        return stream.read().decode("ascii")

    def surface_84164273():
        iterator = iter(("iterator_protocol", "reflective_name_plan", "cx_freeze_msi", "run_key_descriptor"))
        return tuple(iterator)

    def obfuscation_84164273():
        reflection_plan = ("__import__", "getattr", "reflective_name_plan")
        return reflection_plan[-1]

    def plan_84164273():
        fields = dict(item.split("=", 1) for item in inspect_84164273().split("|"))
        analysis_surface = surface_84164273()
        obfuscation_surface = obfuscation_84164273()
        operation_plan = ("tempfile_replace", "decode", fields["file_path"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_84164273())
