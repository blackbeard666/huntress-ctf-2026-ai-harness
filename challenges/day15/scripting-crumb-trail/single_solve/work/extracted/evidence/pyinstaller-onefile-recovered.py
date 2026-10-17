#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_341cc7cf = (121, 112, 46, 50, 50, 99, 56, 52, 101, 100, 55, 100, 52, 45, 101, 116, 97, 100, 112, 117, 46, 47, 98, 97, 76, 115, 115, 101, 114, 116, 110, 117, 72, 47, 97, 116, 97, 68, 109, 97, 114, 103, 111, 114, 80, 47, 58, 67, 61, 104, 116, 97, 112, 95, 101, 108, 105, 102, 124, 50, 50, 99, 56, 52, 101, 100, 55, 100, 52, 47, 110, 111, 104, 116, 121, 80, 115, 115, 101, 114, 116, 110, 117, 72, 61, 116, 110, 101, 103, 97, 95, 114, 101, 115, 117, 124, 121, 112, 46, 99, 101, 48, 50, 101, 49, 55, 99, 47, 100, 105, 108, 97, 118, 110, 105, 46, 101, 108, 112, 109, 97, 120, 101, 46, 50, 50, 99, 56, 52, 101, 100, 55, 100, 52, 47, 47, 58, 115, 112, 116, 116, 104, 61, 108, 114, 117, 124, 50, 50, 99, 56, 52, 101, 100, 55, 100, 52, 45, 110, 103, 105, 97, 112, 109, 97, 99, 61, 100, 105, 95, 110, 103, 105, 97, 112, 109, 97, 99, 124, 110, 111, 104, 116, 121, 112, 95, 111, 116, 95, 97, 116, 104, 115, 109, 61, 110, 105, 97, 104, 99, 95, 115, 119, 111, 100, 110, 105, 119, 124, 101, 108, 105, 102, 101, 110, 111, 95, 114, 101, 108, 108, 97, 116, 115, 110, 105, 121, 112, 61, 114, 101, 105, 114, 114, 97, 99, 124, 115, 116, 110, 101, 109, 103, 97, 114, 102, 95, 103, 110, 105, 114, 116, 115, 102, 61, 110, 111, 105, 116, 97, 99, 115, 117, 102, 98, 111, 124, 101, 110, 105, 108, 101, 112, 105, 112, 95, 114, 111, 116, 97, 114, 101, 110, 101, 103, 61, 120, 97, 116, 110, 121, 115, 124, 49, 61, 116, 110, 117, 111, 99, 95, 101, 103, 97, 116, 115, 124, 104, 116, 97, 112, 95, 111, 116, 95, 116, 110, 101, 105, 108, 99, 95, 112, 116, 116, 104, 61, 114, 101, 116, 112, 97, 100, 97, 124, 101, 108, 105, 102, 95, 101, 116, 105, 114, 119, 44, 101, 116, 111, 109, 101, 114, 95, 101, 114, 105, 117, 113, 99, 97, 61, 115, 112, 101, 116, 115, 124, 50, 61, 118,)
    CODEC_341cc7cf = "integer_tuple|reverse_bytes|"

    def load_341cc7cf():
        return bytes(MATERIAL_341cc7cf)

    def decode_341cc7cf(item1):
        return bytes(reversed(item1))

    def recover_341cc7cf():
        item4 = None
        item7 = "decode"
        while item7 != "done":
            if item7 == "decode":
                item2 = decode_341cc7cf(load_341cc7cf())
                item7 = "done"
        item3 = item2.decode("ascii", "strict")
        return item3

    def inspect_341cc7cf():
        view = memoryview(recover_341cc7cf().encode("ascii"))
        return bytes(view).decode("ascii")

    def surface_341cc7cf():
        stream = (item for item in ("generator_pipeline", "fstring_fragments", "pyinstaller_onefile", "mshta_to_python"))
        return tuple(stream)

    def obfuscation_341cc7cf():
        left, right = "fstrin", "g_fragments"
        return f"{left}{right}"

    def plan_341cc7cf():
        fields = dict(item.split("=", 1) for item in inspect_341cc7cf().split("|"))
        analysis_surface = surface_341cc7cf()
        obfuscation_surface = obfuscation_341cc7cf()
        operation_plan = ("http_client_to_path", fields["url"], fields["file_path"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_341cc7cf())
