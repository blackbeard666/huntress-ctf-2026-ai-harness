#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_0fe21cea = [209, 216, 134, 156, 159, 202, 205, 159, 204, 144, 202, 153, 206, 133, 205, 220, 201, 204, 216, 221, 134, 135, 202, 201, 228, 219, 219, 205, 218, 220, 198, 221, 224, 135, 201, 220, 201, 236, 197, 201, 218, 207, 199, 218, 248, 135, 146, 235, 149, 192, 220, 201, 216, 247, 205, 196, 193, 206, 212, 156, 159, 202, 205, 159, 204, 144, 202, 153, 206, 135, 198, 199, 192, 220, 209, 248, 219, 219, 205, 218, 220, 198, 221, 224, 149, 220, 198, 205, 207, 201, 247, 218, 205, 219, 221, 212, 209, 216, 134, 202, 152, 154, 158, 145, 201, 156, 158, 135, 204, 193, 196, 201, 222, 198, 193, 134, 205, 196, 216, 197, 201, 208, 205, 134, 156, 159, 202, 205, 159, 204, 144, 202, 153, 206, 135, 135, 146, 219, 216, 220, 220, 192, 149, 196, 218, 221, 212, 156, 159, 202, 205, 159, 204, 144, 202, 153, 206, 133, 198, 207, 193, 201, 216, 197, 201, 203, 149, 204, 193, 247, 198, 207, 193, 201, 216, 197, 201, 203, 212, 198, 199, 192, 220, 209, 216, 247, 199, 220, 247, 201, 220, 192, 219, 197, 149, 198, 193, 201, 192, 203, 247, 219, 223, 199, 204, 198, 193, 223, 212, 205, 196, 193, 206, 205, 198, 199, 247, 218, 205, 196, 196, 201, 220, 219, 198, 193, 209, 216, 149, 218, 205, 193, 218, 218, 201, 203, 212, 219, 220, 198, 205, 197, 207, 201, 218, 206, 247, 207, 198, 193, 218, 220, 219, 206, 149, 198, 199, 193, 220, 201, 203, 219, 221, 206, 202, 199, 212, 205, 198, 193, 196, 205, 216, 193, 216, 247, 218, 199, 220, 201, 218, 205, 198, 205, 207, 149, 208, 201, 220, 198, 209, 219, 212, 153, 149, 220, 198, 221, 199, 203, 247, 205, 207, 201, 220, 219, 212, 192, 220, 201, 216, 247, 199, 220, 247, 197, 201, 205, 218, 220, 219, 247, 220, 219, 205, 221, 217, 205, 218, 149, 218, 205, 220, 216, 201, 204, 201, 212, 205, 196, 193, 206, 247, 205, 220, 193, 218, 223, 132, 205, 220, 199, 197, 205, 218, 247, 205, 218, 193, 221, 217, 203, 201, 149, 219, 216, 205, 220, 219, 212, 154, 149, 222]
    CODEC_0fe21cea = "reversed_integer_list|single_byte_xor|a8"

    def load_0fe21cea():
        return bytes(reversed(MATERIAL_0fe21cea))

    def decode_0fe21cea(e):
        return bytes(value ^ 168 for value in e)

    def recover_0fe21cea():
        n = ":".join(("north", "south"))
        for _pass in range(1):
            d = decode_0fe21cea(load_0fe21cea())
        t = d.decode("ascii", "strict")
        return t

    def inspect_0fe21cea():
        view = memoryview(recover_0fe21cea().encode("ascii"))
        return bytes(view).decode("ascii")

    def surface_0fe21cea():
        stream = (item for item in ("generator_pipeline", "fstring_fragments", "pyinstaller_onefile", "mshta_to_python"))
        return tuple(stream)

    def obfuscation_0fe21cea():
        left, right = "fstrin", "g_fragments"
        return f"{left}{right}"

    def plan_0fe21cea():
        fields = dict(item.split("=", 1) for item in inspect_0fe21cea().split("|"))
        analysis_surface = surface_0fe21cea()
        obfuscation_surface = obfuscation_0fe21cea()
        operation_plan = ("request_stream_to_path", fields["url"], fields["file_path"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_0fe21cea())
