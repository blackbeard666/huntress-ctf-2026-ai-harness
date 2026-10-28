#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_bb92dc72 = [51, 56, 51, 51, 98, 100, 56, 97, 48, 57, 45, 116, 115, 111, 104, 61, 100, 105, 95, 116, 115, 111, 104, 124, 51, 56, 51, 51, 98, 100, 56, 97, 48, 57, 45, 110, 103, 105, 97, 112, 109, 97, 99, 61, 100, 105, 95, 110, 103, 105, 97, 112, 109, 97, 99, 124, 101, 120, 101, 95, 110, 111, 104, 116, 121, 112, 95, 116, 99, 101, 114, 105, 100, 61, 110, 105, 97, 104, 99, 95, 115, 119, 111, 100, 110, 105, 119, 124, 101, 99, 114, 117, 111, 115, 95, 119, 97, 114, 61, 114, 101, 105, 114, 114, 97, 99, 124, 121, 108, 110, 111, 95, 109, 114, 111, 102, 115, 110, 97, 114, 116, 61, 110, 111, 105, 116, 97, 99, 115, 117, 102, 98, 111, 124, 115, 110, 111, 105, 116, 99, 110, 117, 102, 95, 110, 105, 97, 108, 112, 61, 120, 97, 116, 110, 121, 115, 124, 49, 61, 116, 110, 117, 111, 99, 95, 101, 103, 97, 116, 115, 124, 101, 99, 97, 112, 115, 101, 109, 97, 110, 95, 101, 115, 114, 97, 112, 103, 114, 97, 61, 114, 101, 116, 112, 97, 100, 97, 124, 110, 111, 105, 116, 97, 114, 117, 103, 105, 102, 110, 111, 99, 95, 110, 114, 117, 116, 101, 114, 44, 110, 111, 105, 116, 97, 114, 117, 103, 105, 102, 110, 111, 99, 95, 101, 100, 111, 99, 101, 100, 61, 115, 112, 101, 116, 115, 124, 50, 61, 118]
    CODEC_bb92dc72 = "reversed_integer_list|identity|"

    def load_bb92dc72():
        return bytes(reversed(MATERIAL_bb92dc72))

    def decode_bb92dc72(v_a19c):
        return bytes(v_a19c)

    def recover_bb92dc72():
        v_d41a = ":".join(("north", "south"))
        v_f602 = decode_bb92dc72
        v_b27e = v_f602(load_bb92dc72())
        v_c304 = v_b27e.decode("ascii", "strict")
        return v_c304

    def inspect_bb92dc72():
        view = memoryview(recover_bb92dc72().encode("ascii"))
        return bytes(view).decode("ascii")

    def surface_bb92dc72():
        return ("plain_functions", "transform_only", "raw_source", "direct_python_exe")

    def obfuscation_bb92dc72():
        return "transform_only"

    def plan_bb92dc72():
        fields = dict(item.split("=", 1) for item in inspect_bb92dc72().split("|"))
        analysis_surface = surface_bb92dc72()
        obfuscation_surface = obfuscation_bb92dc72()
        operation_plan = ("report", fields.get("host_id", ""))
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_bb92dc72())
