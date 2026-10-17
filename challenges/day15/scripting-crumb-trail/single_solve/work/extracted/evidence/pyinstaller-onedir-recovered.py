#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_ebbf84aa = (110, 53, 42, 116, 107, 108, 93, 104, 107, 53, 91, 103, 100, 100, 93, 91, 108, 87, 100, 103, 91, 89, 100, 36, 93, 102, 91, 103, 92, 93, 87, 89, 106, 91, 96, 97, 110, 93, 36, 108, 106, 89, 102, 107, 101, 97, 108, 87, 106, 93, 101, 103, 108, 93, 116, 89, 92, 89, 104, 108, 93, 106, 53, 91, 93, 106, 108, 109, 108, 97, 100, 87, 89, 106, 91, 96, 97, 110, 93, 87, 104, 106, 93, 92, 93, 91, 93, 107, 107, 103, 106, 116, 107, 108, 89, 95, 93, 87, 91, 103, 109, 102, 108, 53, 41, 116, 107, 113, 102, 108, 89, 112, 53, 92, 97, 91, 108, 97, 103, 102, 89, 106, 113, 87, 92, 97, 107, 104, 89, 108, 91, 96, 116, 103, 90, 94, 109, 107, 91, 89, 108, 97, 103, 102, 53, 100, 89, 101, 90, 92, 89, 87, 97, 102, 92, 97, 106, 93, 91, 108, 97, 103, 102, 116, 91, 89, 106, 106, 97, 93, 106, 53, 104, 113, 97, 102, 107, 108, 89, 100, 100, 93, 106, 87, 103, 102, 93, 92, 97, 106, 116, 111, 97, 102, 92, 103, 111, 107, 87, 91, 96, 89, 97, 102, 53, 106, 109, 102, 92, 100, 100, 43, 42, 87, 104, 106, 93, 92, 93, 91, 93, 107, 107, 103, 106, 116, 91, 89, 101, 104, 89, 97, 95, 102, 87, 97, 92, 53, 91, 89, 101, 104, 89, 97, 95, 102, 37, 91, 42, 48, 91, 46, 89, 49, 92, 47, 49, 116, 109, 104, 100, 103, 89, 92, 87, 109, 106, 100, 53, 96, 108, 108, 104, 107, 50, 39, 39, 91, 42, 48, 91, 46, 89, 49, 92, 47, 49, 38, 93, 112, 89, 101, 104, 100, 93, 38, 97, 102, 110, 89, 100, 97, 92, 39, 109, 104, 100, 103, 89, 92, 116, 89, 106, 91, 96, 97, 110, 93, 87, 104, 89, 108, 96, 53, 59, 50, 39, 72, 106, 103, 95, 106, 89, 101, 60, 89, 108, 89, 39, 64, 109, 102, 108, 106, 93, 107, 107, 68, 89, 90, 39, 91, 89, 91, 96, 93, 37, 91, 42, 48, 91, 46, 89, 49, 92, 47, 49, 38, 114, 97, 104,)
    CODEC_ebbf84aa = "integer_tuple|subtract_modulo_256|08"

    def load_ebbf84aa():
        return bytes(MATERIAL_ebbf84aa)

    def decode_ebbf84aa(EnCoDeD_Bytes):
        return bytes((value + 8) % 256 for value in EnCoDeD_Bytes)

    def recover_ebbf84aa():
        NeUtRaL = "left" if 2 > 1 else "right"
        StAtE = "decode"
        while StAtE != "done":
            if StAtE == "decode":
                DeCoDeD_Bytes = decode_ebbf84aa(load_ebbf84aa())
                StAtE = "done"
        DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
        return DeScRiPtOr_Text

    def inspect_ebbf84aa():
        stream = io.BytesIO(recover_ebbf84aa().encode("ascii"))
        return stream.read().decode("ascii")

    def surface_ebbf84aa():
        routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}
        return routes["selected"]()

    def obfuscation_ebbf84aa():
        recover = lambda value: value
        return recover("lambda_indirection")

    def plan_ebbf84aa():
        fields = dict(item.split("=", 1) for item in inspect_ebbf84aa().split("|"))
        analysis_surface = surface_ebbf84aa()
        obfuscation_surface = obfuscation_ebbf84aa()
        operation_plan = ("certutil_archive_predecessor", fields["archive_path"], fields["upload_url"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_ebbf84aa())
