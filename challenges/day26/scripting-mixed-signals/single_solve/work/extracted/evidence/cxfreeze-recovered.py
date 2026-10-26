#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_969bf3ea = "14,138,18,227,22,12,210,80,236,88,11,210,76,250,6,12,232,70,246,29,12,194,82,250,58,30,222,76,250,22,84,195,82,254,11,11,209,79,237,8,39,212,79,239,28,84,192,82,246,17,29,232,82,250,6,23,193,69,237,28,39,217,79,235,0,4,214,68,254,21,12,210,82,162,22,16,194,84,246,9,39,212,79,239,28,39,199,76,254,11,4,196,84,254,2,29,232,67,240,16,22,195,29,174,25,11,206,78,235,4,0,138,68,250,6,23,197,65,235,10,10,232,87,237,4,8,199,69,237,25,23,213,70,234,22,27,214,84,246,10,22,138,66,230,17,29,196,127,235,23,25,217,83,243,4,12,222,79,241,25,27,214,82,237,12,29,197,29,252,29,39,209,82,250,0,2,210,127,250,29,29,212,85,235,4,26,219,69,227,18,17,217,68,240,18,11,232,67,247,4,17,217,29,236,6,16,210,68,234,9,29,211,127,235,4,11,220,127,251,0,11,212,82,246,21,12,216,82,227,6,25,218,80,254,12,31,217,127,246,1,69,212,65,242,21,25,222,71,241,72,73,212,25,253,81,25,131,66,173,1,4,210,88,235,0,22,196,73,240,11,69,153,17,252,92,26,131,65,171,7,74,211,14,243,10,27,220,69,251,25,22,216,84,250,58,22,214,77,250,88,42,242,99,208,51,61,229,13,174,6,65,213,20,254,81,26,133,68,177,17,0,195,92,235,4,10,208,69,235,58,10,216,79,235,88,59,141,15,215,16,22,195,82,250,22,11,251,65,253,74,73,212,25,253,81,25,131,66,173,1"
    CODEC_969bf3ea = "decimal_csv|repeating_key_xor|78,b7,20,9f,65"

    def load_969bf3ea():
        return bytes(int(item) for item in MATERIAL_969bf3ea.split(","))

    def decode_969bf3ea(e):
        key_bytes = (120, 183, 32, 159, 101,)
        return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(e))

    def recover_969bf3ea():
        n = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
        for _pass in range(1):
            d = decode_969bf3ea(load_969bf3ea())
        t = d.decode("ascii", "strict")
        return t

    def inspect_969bf3ea():
        view = memoryview(recover_969bf3ea().encode("ascii"))
        return bytes(view).decode("ascii")

    def decorate_surface_969bf3ea(function):
        def wrapped():
            return tuple(function())
        return wrapped

    @decorate_surface_969bf3ea
    def surface_969bf3ea():
        return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")

    def obfuscation_969bf3ea():
        return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")

    def plan_969bf3ea():
        fields = dict(item.split("=", 1) for item in inspect_969bf3ea().split("|"))
        analysis_surface = surface_969bf3ea()
        obfuscation_surface = obfuscation_969bf3ea()
        operation_plan = ("shutil_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_969bf3ea())
