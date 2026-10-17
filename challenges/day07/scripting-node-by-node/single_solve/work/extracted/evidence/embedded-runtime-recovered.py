#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_ea652008 = ("dj0yfHN0ZXBzPWRlY29kZV9jb25maWd1cmF0aW9uLGxvY2F0ZV9pbnRlcnByZXRlcixkaXNwYXRjaF9uZXh0X3N0YWdlfGFkYXB0ZXI9cHl0aG9uX3RvX3dzY3Jp"
        "cHR8c3RhZ2VfY291bnQ9M3xzeW50YXg9Y2xhc3Nfc3RhdGljbWV0aG9kfG9iZnVzY2F0aW9uPW1hcnNoYWxfZW52ZWxvcGVfcGxhbnxjYXJyaWVyPWVtYmVkZGFi"
        "bGVfcHl0aG9uX3J1bnRpbWV8d2luZG93c19jaGFpbj1yZW5hbWVkX2ludGVycHJldGVyfGNhbXBhaWduX2lkPWNhbXBhaWduLWRiYjA1ODU0OTB8ZmlsZV9wYXRo"
        "PUM6L1Byb2dyYW1EYXRhL0h1bnRyZXNzTGFiLy51cGRhdGUtZGJiMDU4NTQ5MC5weXxuZXh0X3N0YWdlPXB5YXJtb3ItcHlpbnN0YWxsZXItcmVjb3ZlcmVkLnB5")
    CODEC_ea652008 = "base64_chunks|identity|"

    def load_ea652008():
        return base64.b64decode(MATERIAL_ea652008)

    def decode_ea652008(item1):
        return bytes(item1)

    def recover_ea652008():
        item4 = None
        item6 = decode_ea652008
        item2 = item6(load_ea652008())
        item3 = item2.decode("ascii", "strict")
        return item3

    def inspect_ea652008():
        stream = io.BytesIO(recover_ea652008().encode("ascii"))
        return stream.read().decode("ascii")

    class Surface_surface_ea652008:
        @staticmethod
        def recover():
            return ("class_staticmethod", "marshal_envelope_plan", "embeddable_python_runtime", "renamed_interpreter")

    def surface_ea652008():
        return Surface_surface_ea652008.recover()

    def obfuscation_ea652008():
        marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
        return marshal_plan["label"]

    def plan_ea652008():
        fields = dict(item.split("=", 1) for item in inspect_ea652008().split("|"))
        analysis_surface = surface_ea652008()
        obfuscation_surface = obfuscation_ea652008()
        operation_plan = ("python_to_wscript", fields["file_path"], fields["next_stage"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_ea652008())
