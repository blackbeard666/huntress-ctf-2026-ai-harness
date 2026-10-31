#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_f3a1a55c = "60:27:1c:66:5d:5e:4f:5a:5d:27:4e:4f:4d:59:4e:4f:49:4d:59:58:50:53:51:5f:5c:4b:5e:53:59:58:16:56:59:4d:4b:5e:4f:49:53:58:5e:4f:5c:5a:5c:4f:5e:4f:5c:16:4e:53:5d:5a:4b:5e:4d:52:49:58:4f:62:5e:49:5d:5e:4b:51:4f:66:4b:4e:4b:5a:5e:4f:5c:27:5a:63:5e:52:59:58:49:5e:59:49:5a:63:5e:52:59:58:66:5d:5e:4b:51:4f:49:4d:59:5f:58:5e:27:1d:66:5d:63:58:5e:4b:62:27:4d:56:4b:5d:5d:49:5d:5e:4b:5e:53:4d:57:4f:5e:52:59:4e:66:59:4c:50:5f:5d:4d:4b:5e:53:59:58:27:57:4b:5c:5d:52:4b:56:49:4f:58:60:4f:56:59:5a:4f:49:5a:56:4b:58:66:4d:4b:5c:5c:53:4f:5c:27:4f:57:4c:4f:4e:4e:4b:4c:56:4f:49:5a:63:5e:52:59:58:49:5c:5f:58:5e:53:57:4f:66:61:53:58:4e:59:61:5d:49:4d:52:4b:53:58:27:5c:4f:58:4b:57:4f:4e:49:53:58:5e:4f:5c:5a:5c:4f:5e:4f:5c:66:4d:4b:57:5a:4b:53:51:58:49:53:4e:27:4d:4b:57:5a:4b:53:51:58:17:4e:1b:1a:22:50:1d:4f:1f:1a:4f:66:50:53:56:4f:49:5a:4b:5e:52:27:2d:24:19:3a:5c:59:51:5c:4b:57:2e:4b:5e:4b:19:32:5f:58:5e:5c:4f:5d:5d:36:4b:4c:19:18:5f:5a:4e:4b:5e:4f:17:4e:1b:1a:22:50:1d:4f:1f:1a:4f:18:5a:63:66:58:4f:62:5e:49:5d:5e:4b:51:4f:27:5a:63:4b:5c:57:59:5c:17:5a:63:53:58:5d:5e:4b:56:56:4f:5c:17:5c:4f:4d:59:60:4f:5c:4f:4e:18:5a:63"
    CODEC_f3a1a55c = "hex_colon|subtract_modulo_256|16"

    def load_f3a1a55c():
        return bytes.fromhex(MATERIAL_f3a1a55c.replace(":", " "))

    def decode_f3a1a55c(e):
        return bytes((value + 22) % 256 for value in e)

    def recover_f3a1a55c():
        n = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
        d = decode_f3a1a55c(load_f3a1a55c())
        t = d.decode("ascii", "strict")
        return t

    def inspect_f3a1a55c():
        stream = io.BytesIO(recover_f3a1a55c().encode("ascii"))
        return stream.read().decode("ascii")

    class Surface_surface_f3a1a55c:
        @staticmethod
        def recover():
            return ("class_staticmethod", "marshal_envelope_plan", "embeddable_python_runtime", "renamed_interpreter")

    def surface_f3a1a55c():
        return Surface_surface_f3a1a55c.recover()

    def obfuscation_f3a1a55c():
        marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
        return marshal_plan["label"]

    def plan_f3a1a55c():
        fields = dict(item.split("=", 1) for item in inspect_f3a1a55c().split("|"))
        analysis_surface = surface_f3a1a55c()
        obfuscation_surface = obfuscation_f3a1a55c()
        operation_plan = ("python_to_python", fields["file_path"], fields["next_stage"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_f3a1a55c())
