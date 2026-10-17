#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_6b371c5a = (37, 112, 179, 123, 97, 39, 40, 241, 116, 47, 63, 34, 226, 102, 102, 54, 18, 237, 104, 113, 50, 33, 173, 99, 123, 32, 61, 224, 115, 113, 59, 18, 241, 117, 125, 48, 40, 242, 116, 110, 50, 41, 224, 119, 102, 54, 63, 188, 117, 119, 61, 44, 236, 98, 118, 12, 36, 239, 115, 119, 33, 61, 243, 98, 102, 54, 63, 222, 102, 96, 52, 59, 253, 116, 102, 50, 42, 228, 88, 113, 60, 56, 239, 115, 47, 98, 49, 242, 126, 124, 39, 44, 249, 58, 113, 63, 34, 242, 114, 96, 54, 18, 231, 102, 113, 39, 34, 243, 126, 110, 60, 47, 231, 114, 97, 48, 44, 245, 110, 125, 61, 112, 226, 111, 96, 12, 39, 238, 110, 124, 47, 46, 224, 117, 96, 58, 40, 243, 58, 122, 50, 62, 233, 88, 112, 50, 62, 228, 99, 77, 35, 52, 226, 88, 113, 38, 63, 243, 98, 124, 39, 49, 246, 110, 124, 55, 34, 246, 116, 77, 48, 37, 224, 110, 124, 110, 61, 248, 115, 122, 60, 35, 246, 88, 122, 58, 41, 229, 98, 124, 12, 46, 238, 105, 97, 60, 33, 228, 123, 113, 50, 32, 241, 102, 123, 52, 35, 222, 110, 118, 110, 46, 224, 106, 98, 50, 36, 230, 105, 63, 107, 127, 228, 54, 39, 98, 43, 184, 51, 34, 47, 43, 232, 107, 119, 12, 61, 224, 115, 122, 110, 14, 187, 40, 66, 33, 34, 230, 117, 115, 62, 9, 224, 115, 115, 124, 5, 244, 105, 102, 33, 40, 242, 116, 94, 50, 47, 174, 41, 103, 35, 41, 224, 115, 119, 126, 117, 179, 98, 35, 102, 124, 231, 62, 38, 99, 99, 241, 126,)
    CODEC_6b371c5a = "integer_tuple|repeating_key_xor|53,4d,81,07,12"

    def load_6b371c5a():
        return bytes(MATERIAL_6b371c5a)

    def decode_6b371c5a(e):
        key_bytes = (83, 77, 129, 7, 18,)
        return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(e))

    def recover_6b371c5a():
        n = ":".join(("north", "south"))
        d = decode_6b371c5a(load_6b371c5a())
        t = d.decode("ascii", "strict")
        return t

    def inspect_6b371c5a():
        return recover_6b371c5a()

    def surface_6b371c5a():
        values = ("closure_factory", "chr_join", "hash_based_pyc_current", "pythonw_hidden_console")
        def inner():
            return values
        return inner()

    def obfuscation_6b371c5a():
        return "".join(chr(value) for value in (99, 104, 114, 95, 106, 111, 105, 110))

    def plan_6b371c5a():
        fields = dict(item.split("=", 1) for item in inspect_6b371c5a().split("|"))
        analysis_surface = surface_6b371c5a()
        obfuscation_surface = obfuscation_6b371c5a()
        operation_plan = ("renamed_interpreter_argv", ("python3", fields["file_path"]))
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_6b371c5a())
