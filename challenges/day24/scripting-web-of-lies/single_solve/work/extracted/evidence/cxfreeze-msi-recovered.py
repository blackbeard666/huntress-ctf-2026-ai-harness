#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_d1fa7143 = [107, 98, 32, 84, 87, 37, 34, 39, 84, 37, 38, 37, 39, 31, 87, 102, 83, 86, 98, 103, 32, 33, 84, 83, 62, 101, 101, 87, 100, 102, 96, 103, 58, 33, 83, 102, 83, 54, 95, 83, 100, 89, 97, 100, 66, 33, 44, 53, 47, 90, 102, 83, 98, 81, 87, 94, 91, 88, 110, 84, 87, 37, 34, 39, 84, 37, 38, 37, 39, 31, 96, 89, 91, 83, 98, 95, 83, 85, 47, 86, 91, 81, 96, 89, 91, 83, 98, 95, 83, 85, 110, 100, 97, 102, 98, 91, 100, 85, 101, 87, 86, 81, 107, 87, 93, 81, 96, 103, 100, 47, 96, 91, 83, 90, 85, 81, 101, 105, 97, 86, 96, 91, 105, 110, 91, 101, 95, 81, 87, 108, 87, 87, 100, 88, 81, 106, 85, 47, 100, 87, 91, 100, 100, 83, 85, 110, 96, 83, 94, 98, 81, 87, 95, 83, 96, 81, 87, 104, 91, 102, 85, 87, 94, 88, 87, 100, 47, 96, 97, 91, 102, 83, 85, 101, 103, 88, 84, 97, 110, 94, 97, 85, 97, 102, 97, 100, 98, 81, 100, 97, 102, 83, 100, 87, 102, 91, 47, 106, 83, 102, 96, 107, 101, 110, 35, 47, 102, 96, 103, 97, 85, 81, 87, 89, 83, 102, 101, 110, 87, 102, 91, 100, 105, 81, 87, 85, 100, 103, 97, 101, 87, 100, 81, 84, 91, 94, 102, 100, 97, 98, 95, 91, 47, 100, 87, 102, 98, 83, 86, 83, 110, 87, 94, 91, 88, 81, 87, 102, 91, 100, 105, 30, 86, 87, 86, 86, 87, 84, 95, 87, 81, 87, 86, 97, 85, 87, 86, 47, 101, 98, 87, 102, 101, 110, 36, 47, 104]
    CODEC_d1fa7143 = "reversed_integer_list|subtract_modulo_256|0e"

    def load_d1fa7143():
        return bytes(reversed(MATERIAL_d1fa7143))

    def decode_d1fa7143(v_a19c):
        return bytes((value + 14) % 256 for value in v_a19c)

    def recover_d1fa7143():
        v_d41a = None
        try:
            v_b27e = decode_d1fa7143(load_d1fa7143())
        except (TypeError, ValueError) as error:
            raise RuntimeError("configuration recovery failed") from error
        v_c304 = v_b27e.decode("ascii", "strict")
        return v_c304

    def inspect_d1fa7143():
        view = memoryview(recover_d1fa7143().encode("ascii"))
        return bytes(view).decode("ascii")

    def surface_d1fa7143():
        iterator = iter(("iterator_protocol", "reflective_name_plan", "cx_freeze_msi", "run_key_descriptor"))
        return tuple(iterator)

    def obfuscation_d1fa7143():
        reflection_plan = ("__import__", "getattr", "reflective_name_plan")
        return reflection_plan[-1]

    def plan_d1fa7143():
        fields = dict(item.split("=", 1) for item in inspect_d1fa7143().split("|"))
        analysis_surface = surface_d1fa7143()
        obfuscation_surface = obfuscation_d1fa7143()
        operation_plan = ("importlib_resource_write", "decode", fields["file_path"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_d1fa7143())
