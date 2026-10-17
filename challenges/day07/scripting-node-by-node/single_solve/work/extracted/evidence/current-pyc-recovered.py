#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_3ccbdff1 = "5e:25:1a:64:5b:5c:4d:58:5b:25:54:57:4b:49:5c:4d:47:54:57:4b:49:54:14:4c:51:5b:58:49:5c:4b:50:47:58:5a:57:4b:4d:5b:5b:64:49:4c:49:58:5c:4d:5a:25:58:61:5c:50:57:56:5f:47:49:5a:4f:5e:64:5b:5c:49:4f:4d:47:4b:57:5d:56:5c:25:19:64:5b:61:56:5c:49:60:25:4b:54:57:5b:5d:5a:4d:47:4e:49:4b:5c:57:5a:61:64:57:4a:4e:5d:5b:4b:49:5c:51:57:56:25:4b:50:5a:47:52:57:51:56:64:4b:49:5a:5a:51:4d:5a:25:50:49:5b:50:47:4a:49:5b:4d:4c:47:58:61:4b:47:4b:5d:5a:5a:4d:56:5c:64:5f:51:56:4c:57:5f:5b:47:4b:50:49:51:56:25:58:61:5c:50:57:56:5f:47:50:51:4c:4c:4d:56:47:4b:57:56:5b:57:54:4d:64:4b:49:55:58:49:51:4f:56:47:51:4c:25:4b:49:55:58:49:51:4f:56:15:1d:4b:21:4e:4d:1b:1f:49:20:4c:64:4e:51:54:4d:47:58:49:5c:50:25:2b:22:17:38:5a:57:4f:5a:49:55:2c:49:5c:49:17:30:5d:56:5c:5a:4d:5b:5b:34:49:4a:17:16:5d:58:4c:49:5c:4d:15:1d:4b:21:4e:4d:1b:1f:49:20:4c:16:58:61"
    CODEC_3ccbdff1 = "hex_colon|subtract_modulo_256|18"

    def load_3ccbdff1():
        return bytes.fromhex(MATERIAL_3ccbdff1.replace(":", " "))

    def decode_3ccbdff1(EnCoDeD_Bytes):
        return bytes((value + 24) % 256 for value in EnCoDeD_Bytes)

    def recover_3ccbdff1():
        NeUtRaL = ":".join(("north", "south"))
        for _pass in range(1):
            DeCoDeD_Bytes = decode_3ccbdff1(load_3ccbdff1())
        DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
        return DeScRiPtOr_Text

    def inspect_3ccbdff1():
        return recover_3ccbdff1()

    def surface_3ccbdff1():
        values = ("closure_factory", "chr_join", "hash_based_pyc_current", "pythonw_hidden_console")
        def inner():
            return values
        return inner()

    def obfuscation_3ccbdff1():
        return "".join(chr(value) for value in (99, 104, 114, 95, 106, 111, 105, 110))

    def plan_3ccbdff1():
        fields = dict(item.split("=", 1) for item in inspect_3ccbdff1().split("|"))
        analysis_surface = surface_3ccbdff1()
        obfuscation_surface = obfuscation_3ccbdff1()
        operation_plan = ("pythonw_argv", ("python3", fields["file_path"]))
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_3ccbdff1())
