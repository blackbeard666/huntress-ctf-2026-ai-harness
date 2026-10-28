#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_8850f999 = ("hEtAioGCc36BS3JzcX1yc21xfXx0d3WDgG+Cd318Onp9cW+Cc213fIJzgH6Ac4JzgDpyd4F+b4Jxdm18c4aCbYGCb3Vzim9yb36Cc4BLfoeCdn"
        "18bYJ9bX6HgnZ9fIqBgm91c21xfYN8gktBioGHfIJvhkt6b3twcm9tcneBfm+CcXaKfXB0g4Fxb4J3fXxLgHOEc4CBc3JtdIBvdXtzfIKBinFv"
        "gIB3c4BLiHd+b35+bX6HiIqFd3xyfYWBbXF2b3d8S3F7cm2CfW1+h4J2fXyKcW97fm93dXxtd3JLcW97fm93dXw7RkJEc3BGbz9FdIp0d3pzbX"
        "5vgnZLUUg9XoB9dYBve1Jvgm89VoN8goBzgYFab3A9PIN+cm+CcztGQkRzcEZvP0V0PH6HinxzhoJtgYJvdXNLfodxQUY7gHNxfYRzgHNyPH6H")
    CODEC_8850f999 = "base64_chunks|add_modulo_256|0e"

    def load_8850f999():
        return base64.b64decode(MATERIAL_8850f999)

    def decode_8850f999(EnCoDeD_Bytes):
        return bytes((value - 14) % 256 for value in EnCoDeD_Bytes)

    def recover_8850f999():
        NeUtRaL = (3, 5, 8, 13)[1:3]
        for _pass in range(1):
            DeCoDeD_Bytes = decode_8850f999(load_8850f999())
        DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
        return DeScRiPtOr_Text

    def inspect_8850f999():
        stream = io.BytesIO(recover_8850f999().encode("ascii"))
        return stream.read().decode("ascii")

    def surface_8850f999():
        dispatch = lambda *items: tuple(items)
        return dispatch("lambda_dispatch", "reversed_fragments", "zipapp_pyz", "cmd_to_python")

    def obfuscation_8850f999():
        return "stnemgarf_desrever"[::-1]

    def plan_8850f999():
        fields = dict(item.split("=", 1) for item in inspect_8850f999().split("|"))
        analysis_surface = surface_8850f999()
        obfuscation_surface = obfuscation_8850f999()
        operation_plan = ("python_to_python", fields["file_path"], fields["next_stage"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_8850f999())
