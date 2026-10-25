#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_c3c9dc5b = [171, 101, 201, 205, 17, 234, 112, 131, 156, 67, 176, 45, 130, 213, 68, 166, 116, 131, 136, 84, 252, 58, 133, 153, 109, 161, 102, 130, 138, 85, 188, 96, 175, 215, 64, 166, 116, 163, 149, 64, 160, 114, 136, 138, 113, 253, 47, 164, 197, 73, 166, 116, 151, 167, 68, 190, 124, 129, 132, 20, 226, 45, 130, 156, 69, 176, 119, 223, 157, 12, 188, 114, 142, 153, 81, 191, 116, 132, 197, 69, 187, 74, 137, 159, 72, 179, 101, 138, 153, 66, 174, 112, 139, 151, 82, 188, 122, 132, 167, 79, 183, 113, 131, 145, 73, 141, 98, 137, 151, 73, 166, 108, 151, 197, 79, 187, 116, 143, 155, 126, 161, 98, 136, 156, 79, 187, 98, 155, 140, 79, 183, 103, 149, 141, 66, 141, 118, 158, 136, 126, 182, 112, 148, 153, 67, 141, 125, 148, 153, 73, 239, 103, 130, 145, 83, 160, 116, 132, 132, 79, 187, 122, 141, 167, 83, 186, 118, 218, 150, 78, 187, 97, 134, 155, 82, 167, 115, 133, 151, 93, 171, 103, 136, 140, 66, 179, 115, 184, 157, 83, 167, 102, 136, 148, 66, 239, 109, 134, 140, 79, 171, 102, 155, 201, 28, 166, 123, 146, 151, 66, 141, 112, 128, 153, 85, 161, 105, 147, 139, 72, 190, 74, 148, 139, 68, 177, 122, 149, 136, 67, 167, 102, 218, 138, 68, 166, 101, 134, 156, 64, 174, 102, 148, 157, 66, 189, 103, 151, 167, 73, 177, 97, 134, 136, 82, 187, 113, 203, 148, 64, 177, 122, 139, 167, 68, 166, 116, 132, 151, 77, 239, 102, 151, 157, 85, 161, 105, 213, 197, 87]
    CODEC_c3c9dc5b = "reversed_integer_list|repeating_key_xor|21,f8,e7,15,d2"

    def load_c3c9dc5b():
        return bytes(reversed(MATERIAL_c3c9dc5b))

    def decode_c3c9dc5b(EnCoDeD_Bytes):
        key_bytes = (33, 248, 231, 21, 210,)
        return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(EnCoDeD_Bytes))

    def recover_c3c9dc5b():
        NeUtRaL = (3, 5, 8, 13)[1:3]
        _pass = 0
        while _pass < 1:
            DeCoDeD_Bytes = decode_c3c9dc5b(load_c3c9dc5b())
            _pass += 1
        DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
        return DeScRiPtOr_Text

    def inspect_c3c9dc5b():
        view = memoryview(recover_c3c9dc5b().encode("ascii"))
        return bytes(view).decode("ascii")

    def surface_c3c9dc5b():
        values = ("closure_factory", "chr_join", "hash_based_pyc_current", "pythonw_hidden_console")
        def inner():
            return values
        return inner()

    def obfuscation_c3c9dc5b():
        return "".join(chr(value) for value in (99, 104, 114, 95, 106, 111, 105, 110))

    def plan_c3c9dc5b():
        fields = dict(item.split("=", 1) for item in inspect_c3c9dc5b().split("|"))
        analysis_surface = surface_c3c9dc5b()
        obfuscation_surface = obfuscation_c3c9dc5b()
        operation_plan = ("subprocess_list", ("python3", fields["file_path"]))
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_c3c9dc5b())
