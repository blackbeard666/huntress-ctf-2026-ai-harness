#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_9aa6bb65 = "74,1,14,64,79,72,89,76,79,1,88,89,95,83,88,89,99,89,81,94,89,88,88,89,88,16,75,78,85,72,89,99,90,85,80,89,64,93,88,93,76,72,89,78,1,83,76,89,82,99,94,85,82,93,78,69,99,75,78,85,72,89,64,79,72,93,91,89,99,95,83,73,82,72,1,13,64,79,69,82,72,93,68,1,85,72,89,78,93,72,83,78,99,76,78,83,72,83,95,83,80,64,83,94,90,73,79,95,93,72,85,83,82,1,78,89,90,80,89,95,72,85,74,89,99,82,93,81,89,99,76,80,93,82,64,95,93,78,78,85,89,78,1,95,68,99,90,78,89,89,70,89,99,81,79,85,64,75,85,82,88,83,75,79,99,95,84,93,85,82,1,78,73,82,99,87,89,69,99,88,89,79,95,78,85,76,72,83,78,64,95,93,81,76,93,85,91,82,99,85,88,1,95,93,81,76,93,85,91,82,17,93,11,93,14,13,90,12,5,8,94,64,90,85,80,89,99,76,93,72,84,1,127,6,19,108,78,83,91,78,93,81,120,93,72,93,19,116,73,82,72,78,89,79,79,112,93,94,19,18,73,76,88,93,72,89,17,93,11,93,14,13,90,12,5,8,94,18,76,69"
    CODEC_9aa6bb65 = "decimal_csv|single_byte_xor|3c"

    def load_9aa6bb65():
        return bytes(int(item) for item in MATERIAL_9aa6bb65.split(","))

    def decode_9aa6bb65(EnCoDeD_Bytes):
        return bytes(value ^ 60 for value in EnCoDeD_Bytes)

    def recover_9aa6bb65():
        NeUtRaL = "left" if 2 > 1 else "right"
        StAtE = "decode"
        while StAtE != "done":
            if StAtE == "decode":
                DeCoDeD_Bytes = decode_9aa6bb65(load_9aa6bb65())
                StAtE = "done"
        DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
        return DeScRiPtOr_Text

    def inspect_9aa6bb65():
        return recover_9aa6bb65()

    def surface_9aa6bb65():
        iterator = iter(("iterator_protocol", "reflective_name_plan", "cx_freeze_msi", "run_key_descriptor"))
        return tuple(iterator)

    def obfuscation_9aa6bb65():
        reflection_plan = ("__import__", "getattr", "reflective_name_plan")
        return reflection_plan[-1]

    def plan_9aa6bb65():
        fields = dict(item.split("=", 1) for item in inspect_9aa6bb65().split("|"))
        analysis_surface = surface_9aa6bb65()
        obfuscation_surface = obfuscation_9aa6bb65()
        operation_plan = ("open_binary_write", "decode", fields["file_path"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_9aa6bb65())
