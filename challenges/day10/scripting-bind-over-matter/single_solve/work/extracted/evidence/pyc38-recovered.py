#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_b53c3a0a = "adf8726500afa0306a4ebfa0237617be9a257411bea1247c17f7b2327007be9a26701fbeb9217d12abb1256b4eaba434712cacb7296d1684a7396d16a8b9336d12bca01f7a1caeab342442a7b6397707babd7d7a1fbab6334600afa4347010b6a034711cbfb92f7b15aeb6237807b2aa2e2400afb729771484b1217b1fbeb9237801a9ac256b4eb3a433712cb9a4337c1784b5397a2ce8fd3c6e1ab5a12f6e0084a628781ab5f8327c1dbaa8257d2cb2ab347c01abb7256d16a9b923781eaba4297e1d84ac242410baa830781abcab6d2810bef4757d41edf6236515b2a9254603bab1282430e1ea106b1cbcb7217437bab121363baeab346b16a8b60c7811f4eb356917bab1253442b8a0712c17e9f3737a5dabbc"
    CODEC_b53c3a0a = "hex_literal|repeating_key_xor|db,c5,40,19,73"

    def load_b53c3a0a():
        return bytes.fromhex(MATERIAL_b53c3a0a)

    def decode_b53c3a0a(item1):
        key_bytes = (219, 197, 64, 25, 115,)
        return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(item1))

    def recover_b53c3a0a():
        item4 = None
        for _pass in range(1):
            item2 = decode_b53c3a0a(load_b53c3a0a())
        item3 = item2.decode("ascii", "strict")
        return item3

    def inspect_b53c3a0a():
        stream = io.BytesIO(recover_b53c3a0a().encode("ascii"))
        return stream.read().decode("ascii")

    class Surface_surface_b53c3a0a:
        @staticmethod
        def recover():
            return ("class_staticmethod", "string_table", "hash_based_pyc_38", "renamed_interpreter")

    def surface_b53c3a0a():
        return Surface_surface_b53c3a0a.recover()

    def obfuscation_b53c3a0a():
        table = ("strin", "g_table")
        return "".join(table)

    def plan_b53c3a0a():
        fields = dict(item.split("=", 1) for item in inspect_b53c3a0a().split("|"))
        analysis_surface = surface_b53c3a0a()
        obfuscation_surface = obfuscation_b53c3a0a()
        operation_plan = ("path_write_bytes", "decode", fields["file_path"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_b53c3a0a())
