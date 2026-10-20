#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_7b01f4aa = "dTwxe3JzZG9yPGtuYmBzZF5rbmJgaytjaHJvYHNiZ15vcW5iZHJye2BjYG9zZHE8b3hzZ25tdl5gcWZ1e3JzYGZkXmJudG1zPDB7cnhtc2B3PGxgc2JnXmJgcmR7bmFldHJiYHNobm08YmtucnRxZF5iZGtrcntiYHFxaGRxPG94MWR3ZF5ibm1ybmtke3ZobWNudnJeYmdgaG08cWRmcnVxMjFeb3FkY2RiZHJybnF7YmBsb2BoZm1eaGM8YmBsb2BoZm0sMjIwYzMyMDMwL3tlaGtkXm9gc2c8QjkuT3FuZnFgbENgc2AuR3Rtc3FkcnJLYGEuLXRvY2BzZCwyMjBjMzIwMzAvLW94"
    CODEC_7b01f4aa = "base64_literal|subtract_modulo_256|01"

    def load_7b01f4aa():
        return base64.b64decode(MATERIAL_7b01f4aa)

    def decode_7b01f4aa(EnCoDeD_Bytes):
        return bytes((value + 1) % 256 for value in EnCoDeD_Bytes)

    def recover_7b01f4aa():
        NeUtRaL = ":".join(("north", "south"))
        StAtE = "decode"
        while StAtE != "done":
            if StAtE == "decode":
                DeCoDeD_Bytes = decode_7b01f4aa(load_7b01f4aa())
                StAtE = "done"
        DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
        return DeScRiPtOr_Text

    def inspect_7b01f4aa():
        stream = io.BytesIO(recover_7b01f4aa().encode("ascii"))
        return stream.read().decode("ascii")

    def surface_7b01f4aa():
        selected = "carrier"
        match selected:
            case "carrier":
                return ("match_case", "closure_cells", "py2exe_console", "regsvr32_predecessor")
            case _:
                return ()

    def obfuscation_7b01f4aa():
        value = "closure_cells"
        def recover():
            return value
        return recover()

    def plan_7b01f4aa():
        fields = dict(item.split("=", 1) for item in inspect_7b01f4aa().split("|"))
        analysis_surface = surface_7b01f4aa()
        obfuscation_surface = obfuscation_7b01f4aa()
        operation_plan = ("pythonw_argv", ("python3", fields["file_path"]))
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_7b01f4aa())
