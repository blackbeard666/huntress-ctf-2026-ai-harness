#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_0cd92186 = [119, 110, 44, 53, 46, 47, 100, 96, 98, 46, 100, 100, 96, 43, 99, 114, 95, 98, 110, 115, 44, 45, 96, 95, 74, 113, 113, 99, 112, 114, 108, 115, 70, 45, 95, 114, 95, 66, 107, 95, 112, 101, 109, 112, 78, 45, 56, 65, 59, 102, 114, 95, 110, 93, 99, 106, 103, 100, 122, 53, 46, 47, 100, 96, 98, 46, 100, 100, 96, 43, 108, 101, 103, 95, 110, 107, 95, 97, 59, 98, 103, 93, 108, 101, 103, 95, 110, 107, 95, 97, 122, 112, 109, 114, 110, 103, 112, 97, 113, 99, 98, 93, 119, 99, 105, 93, 108, 115, 112, 59, 108, 103, 95, 102, 97, 93, 113, 117, 109, 98, 108, 103, 117, 122, 103, 113, 107, 93, 99, 120, 99, 99, 112, 100, 93, 118, 97, 59, 112, 99, 103, 112, 112, 95, 97, 122, 108, 95, 106, 110, 93, 99, 107, 95, 108, 93, 99, 116, 103, 114, 97, 99, 106, 100, 99, 112, 59, 108, 109, 103, 114, 95, 97, 113, 115, 100, 96, 109, 122, 106, 109, 97, 109, 114, 109, 112, 110, 93, 112, 109, 114, 95, 112, 99, 114, 103, 59, 118, 95, 114, 108, 119, 113, 122, 47, 59, 114, 108, 115, 109, 97, 93, 99, 101, 95, 114, 113, 122, 113, 99, 114, 119, 96, 93, 99, 114, 103, 112, 117, 93, 102, 114, 95, 110, 59, 112, 99, 114, 110, 95, 98, 95, 122, 99, 106, 103, 100, 93, 99, 114, 103, 112, 117, 42, 98, 99, 98, 98, 99, 96, 107, 99, 93, 99, 98, 109, 97, 99, 98, 59, 113, 110, 99, 114, 113, 122, 48, 59, 116]
    CODEC_0cd92186 = "reversed_integer_list|subtract_modulo_256|02"

    def load_0cd92186():
        return bytes(reversed(MATERIAL_0cd92186))

    def decode_0cd92186(e):
        return bytes((value + 2) % 256 for value in e)

    def recover_0cd92186():
        n = (3, 5, 8, 13)[1:3]
        s = "decode"
        while s != "done":
            if s == "decode":
                d = decode_0cd92186(load_0cd92186())
                s = "done"
        t = d.decode("ascii", "strict")
        return t

    def inspect_0cd92186():
        return recover_0cd92186()

    def surface_0cd92186():
        iterator = iter(("iterator_protocol", "reflective_name_plan", "cx_freeze_msi", "run_key_descriptor"))
        return tuple(iterator)

    def obfuscation_0cd92186():
        reflection_plan = ("__import__", "getattr", "reflective_name_plan")
        return reflection_plan[-1]

    def plan_0cd92186():
        fields = dict(item.split("=", 1) for item in inspect_0cd92186().split("|"))
        analysis_surface = surface_0cd92186()
        obfuscation_surface = obfuscation_0cd92186()
        operation_plan = ("path_write_bytes", "decode", fields["file_path"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_0cd92186())
