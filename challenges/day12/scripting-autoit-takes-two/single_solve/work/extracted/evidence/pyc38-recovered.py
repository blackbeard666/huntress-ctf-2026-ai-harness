#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_96d1d475 = "79702e313136613038323862302d6574616470752e2f62614c73736572746e75482f617461446d6172676f72502f3a433d687461705f656c69667c313136613038323862302d6e676961706d61633d64695f6e676961706d61637c7265746572707265746e695f64656d616e65723d6e696168635f73776f646e69777c38335f6379705f64657361625f687361683d726569727261637c656c6261745f676e697274733d6e6f69746163737566626f7c646f6874656d6369746174735f7373616c633d7861746e79737c313d746e756f635f65676174737c6563616c7065725f656c6966706d65743d726574706164617c656c69665f65746972772c6465646465626d655f65646f6365643d73706574737c323d76"
    CODEC_96d1d475 = "hex_literal|reverse_bytes|"

    def load_96d1d475():
        return bytes.fromhex(MATERIAL_96d1d475)

    def decode_96d1d475(e):
        return bytes(reversed(e))

    def recover_96d1d475():
        n = ":".join(("north", "south"))
        s = "decode"
        while s != "done":
            if s == "decode":
                d = decode_96d1d475(load_96d1d475())
                s = "done"
        t = d.decode("ascii", "strict")
        return t

    def inspect_96d1d475():
        stream = io.BytesIO(recover_96d1d475().encode("ascii"))
        return stream.read().decode("ascii")

    class Surface_surface_96d1d475:
        @staticmethod
        def recover():
            return ("class_staticmethod", "string_table", "hash_based_pyc_38", "renamed_interpreter")

    def surface_96d1d475():
        return Surface_surface_96d1d475.recover()

    def obfuscation_96d1d475():
        table = ("strin", "g_table")
        return "".join(table)

    def plan_96d1d475():
        fields = dict(item.split("=", 1) for item in inspect_96d1d475().split("|"))
        analysis_surface = surface_96d1d475()
        obfuscation_surface = obfuscation_96d1d475()
        operation_plan = ("tempfile_replace", "decode", fields["file_path"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_96d1d475())
