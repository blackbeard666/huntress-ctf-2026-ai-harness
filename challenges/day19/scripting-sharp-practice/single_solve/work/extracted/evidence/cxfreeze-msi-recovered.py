#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_e2475c7c = "2b:60:6f:21:2e:29:38:2d:2e:60:39:38:3e:32:39:38:02:38:30:3f:38:39:39:38:39:71:2a:2f:34:29:38:02:3b:34:31:38:21:3c:39:3c:2d:29:38:2f:60:34:30:2d:32:2f:29:31:34:3f:02:2f:38:2e:32:28:2f:3e:38:02:2a:2f:34:29:38:21:2e:29:3c:3a:38:02:3e:32:28:33:29:60:6c:21:2e:24:33:29:3c:25:60:34:29:38:2f:3c:29:32:2f:02:2d:2f:32:29:32:3e:32:31:21:32:3f:3b:28:2e:3e:3c:29:34:32:33:60:2f:38:3b:31:38:3e:29:34:2b:38:02:33:3c:30:38:02:2d:31:3c:33:21:3e:3c:2f:2f:34:38:2f:60:3e:25:02:3b:2f:38:38:27:38:02:30:2e:34:21:2a:34:33:39:32:2a:2e:02:3e:35:3c:34:33:60:2f:28:33:02:36:38:24:02:39:38:2e:3e:2f:34:2d:29:32:2f:21:3e:3c:30:2d:3c:34:3a:33:02:34:39:60:3e:3c:30:2d:3c:34:3a:33:70:6c:39:3b:68:39:3b:6f:3e:68:65:21:3b:34:31:38:02:2d:3c:29:35:60:1e:67:72:0d:2f:32:3a:2f:3c:30:19:3c:29:3c:72:15:28:33:29:2f:38:2e:2e:11:3c:3f:72:73:28:2d:39:3c:29:38:70:6c:39:3b:68:39:3b:6f:3e:68:65:73:2d:24"
    CODEC_e2475c7c = "hex_colon|single_byte_xor|5d"

    def load_e2475c7c():
        return bytes.fromhex(MATERIAL_e2475c7c.replace(":", " "))

    def decode_e2475c7c(EnCoDeD_Bytes):
        return bytes(value ^ 93 for value in EnCoDeD_Bytes)

    def recover_e2475c7c():
        NeUtRaL = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
        try:
            DeCoDeD_Bytes = decode_e2475c7c(load_e2475c7c())
        except (TypeError, ValueError) as error:
            raise RuntimeError("configuration recovery failed") from error
        DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
        return DeScRiPtOr_Text

    def inspect_e2475c7c():
        return recover_e2475c7c()

    def surface_e2475c7c():
        iterator = iter(("iterator_protocol", "reflective_name_plan", "cx_freeze_msi", "run_key_descriptor"))
        return tuple(iterator)

    def obfuscation_e2475c7c():
        reflection_plan = ("__import__", "getattr", "reflective_name_plan")
        return reflection_plan[-1]

    def plan_e2475c7c():
        fields = dict(item.split("=", 1) for item in inspect_e2475c7c().split("|"))
        analysis_surface = surface_e2475c7c()
        obfuscation_surface = obfuscation_e2475c7c()
        operation_plan = ("importlib_resource_write", "decode", fields["file_path"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_e2475c7c())
