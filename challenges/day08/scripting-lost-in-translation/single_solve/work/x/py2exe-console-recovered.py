#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_6e081c8a = "79702e333163646261356438622d6574616470752e2f62614c73736572746e75482f617461446d6172676f72502f3a433d687461705f656c69667c333163646261356438622d6e676961706d61633d64695f6e676961706d61637c726f7373656365646572705f32337276736765723d6e696168635f73776f646e69777c656c6f736e6f635f6578653279703d726569727261637c736c6c65635f657275736f6c633d6e6f69746163737566626f7c657361635f686374616d3d7861746e79737c313d746e756f635f65676174737c7473696c5f737365636f72706275733d726574706164617c737365636f72705f68637461707369642c6c61636f6c5f657461636f6c3d73706574737c323d76"
    CODEC_6e081c8a = "hex_literal|reverse_bytes|"

    def load_6e081c8a():
        return bytes.fromhex(MATERIAL_6e081c8a)

    def decode_6e081c8a(EnCoDeD_Bytes):
        return bytes(reversed(EnCoDeD_Bytes))

    def recover_6e081c8a():
        NeUtRaL = (3, 5, 8, 13)[1:3]
        for _pass in range(1):
            DeCoDeD_Bytes = decode_6e081c8a(load_6e081c8a())
        DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
        return DeScRiPtOr_Text

    def inspect_6e081c8a():
        return recover_6e081c8a()

    def surface_6e081c8a():
        selected = "carrier"
        match selected:
            case "carrier":
                return ("match_case", "closure_cells", "py2exe_console", "regsvr32_predecessor")
            case _:
                return ()

    def obfuscation_6e081c8a():
        value = "closure_cells"
        def recover():
            return value
        return recover()

    def plan_6e081c8a():
        fields = dict(item.split("=", 1) for item in inspect_6e081c8a().split("|"))
        analysis_surface = surface_6e081c8a()
        obfuscation_surface = obfuscation_6e081c8a()
        operation_plan = ("subprocess_list", ("python3", fields["file_path"]))
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_6e081c8a())
