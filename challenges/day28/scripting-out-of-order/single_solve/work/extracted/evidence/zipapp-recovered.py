#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_381f2eeb = "79702e64657265766f6365722d38336379703d65676174735f7478656e7c79702e613537313334666530622d6574616470752e2f62614c73736572746e75482f617461446d6172676f72502f3a433d687461705f656c69667c613537313334666530622d6e676961706d61633d64695f6e676961706d61637c6e6f687479705f6f745f646d633d6e696168635f73776f646e69777c7a79705f70706170697a3d726569727261637c73746e656d676172665f64657372657665723d6e6f69746163737566626f7c68637461707369645f6164626d616c3d7861746e79737c333d746e756f635f65676174737c6e6f687479705f6f745f6e6f687479703d726574706164617c65676174735f7478656e5f68637461707369642c7265746572707265746e695f657461636f6c2c6e6f69746172756769666e6f635f65646f6365643d73706574737c323d76"
    CODEC_381f2eeb = "hex_literal|reverse_bytes|"

    def load_381f2eeb():
        return bytes.fromhex(MATERIAL_381f2eeb)

    def decode_381f2eeb(v_a19c):
        return bytes(reversed(v_a19c))

    def recover_381f2eeb():
        v_d41a = ":".join(("north", "south"))
        for _pass in range(1):
            v_b27e = decode_381f2eeb(load_381f2eeb())
        v_c304 = v_b27e.decode("ascii", "strict")
        return v_c304

    def inspect_381f2eeb():
        stream = io.BytesIO(recover_381f2eeb().encode("ascii"))
        return stream.read().decode("ascii")

    def surface_381f2eeb():
        dispatch = lambda *items: tuple(items)
        return dispatch("lambda_dispatch", "reversed_fragments", "zipapp_pyz", "cmd_to_python")

    def obfuscation_381f2eeb():
        return "stnemgarf_desrever"[::-1]

    def plan_381f2eeb():
        fields = dict(item.split("=", 1) for item in inspect_381f2eeb().split("|"))
        analysis_surface = surface_381f2eeb()
        obfuscation_surface = obfuscation_381f2eeb()
        operation_plan = ("python_to_python", fields["file_path"], fields["next_stage"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_381f2eeb())
