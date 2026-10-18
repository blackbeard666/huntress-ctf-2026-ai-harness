#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_421916e0 = [116, 107, 41, 48, 93, 43, 50, 44, 45, 43, 96, 92, 44, 40, 96, 111, 92, 95, 107, 112, 41, 42, 93, 92, 71, 110, 110, 96, 109, 111, 105, 112, 67, 42, 92, 111, 92, 63, 104, 92, 109, 98, 106, 109, 75, 42, 53, 62, 56, 99, 111, 92, 107, 90, 96, 103, 100, 97, 119, 48, 93, 43, 50, 44, 45, 43, 96, 92, 44, 40, 105, 98, 100, 92, 107, 104, 92, 94, 56, 95, 100, 90, 105, 98, 100, 92, 107, 104, 92, 94, 119, 109, 96, 111, 96, 109, 107, 109, 96, 111, 105, 100, 90, 95, 96, 104, 92, 105, 96, 109, 56, 105, 100, 92, 99, 94, 90, 110, 114, 106, 95, 105, 100, 114, 119, 51, 46, 90, 94, 116, 107, 90, 95, 96, 110, 92, 93, 90, 99, 110, 92, 99, 56, 109, 96, 100, 109, 109, 92, 94, 119, 96, 103, 93, 92, 111, 90, 98, 105, 100, 109, 111, 110, 56, 105, 106, 100, 111, 92, 94, 110, 112, 97, 93, 106, 119, 95, 106, 99, 111, 96, 104, 94, 100, 111, 92, 111, 110, 90, 110, 110, 92, 103, 94, 56, 115, 92, 111, 105, 116, 110, 119, 44, 56, 111, 105, 112, 106, 94, 90, 96, 98, 92, 111, 110, 119, 96, 111, 100, 109, 114, 90, 96, 94, 109, 112, 106, 110, 96, 109, 90, 93, 100, 103, 111, 109, 106, 107, 104, 100, 56, 109, 96, 111, 107, 92, 95, 92, 119, 96, 103, 100, 97, 90, 96, 111, 100, 109, 114, 39, 95, 96, 95, 95, 96, 93, 104, 96, 90, 96, 95, 106, 94, 96, 95, 56, 110, 107, 96, 111, 110, 119, 45, 56, 113]
    CODEC_421916e0 = "reversed_integer_list|subtract_modulo_256|05"

    def load_421916e0():
        return bytes(reversed(MATERIAL_421916e0))

    def decode_421916e0(v_a19c):
        return bytes((value + 5) % 256 for value in v_a19c)

    def recover_421916e0():
        v_d41a = None
        v_a702 = "decode"
        while v_a702 != "done":
            if v_a702 == "decode":
                v_b27e = decode_421916e0(load_421916e0())
                v_a702 = "done"
        v_c304 = v_b27e.decode("ascii", "strict")
        return v_c304

    def inspect_421916e0():
        view = memoryview(recover_421916e0().encode("ascii"))
        return bytes(view).decode("ascii")

    class Surface_surface_421916e0:
        @staticmethod
        def recover():
            return ("class_staticmethod", "string_table", "hash_based_pyc_38", "renamed_interpreter")

    def surface_421916e0():
        return Surface_surface_421916e0.recover()

    def obfuscation_421916e0():
        table = ("strin", "g_table")
        return "".join(table)

    def plan_421916e0():
        fields = dict(item.split("=", 1) for item in inspect_421916e0().split("|"))
        analysis_surface = surface_421916e0()
        obfuscation_surface = obfuscation_421916e0()
        operation_plan = ("importlib_resource_write", "decode", fields["file_path"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_421916e0())
