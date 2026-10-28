#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_6278587b = "d9d08ec392c4939997c5c299c28dc5d4c1c4d0d58e8fc2c1ecd3d3c5d2d4ced5e88fc1d4c1e4cdc1d2c7cfd2f08f9ae39dc8d4c1d0ffc5ccc9c6dcc392c4939997c5c299c28dcec7c9c1d0cdc1c39dc4c9ffcec7c9c1d0cdc1c3dcd2cfd4d0c9d2c3d3c5c4ffd9c5cbffced5d29dcec9c1c8c3ffd3d7cfc4cec9d7dcc9d3cdffc5dac5c5d2c6ffd8c39dd2c5c9d2d2c1c3dccec1ccd0ffc5cdc1ceffc5d6c9d4c3c5ccc6c5d29dcecfc9d4c1c3d3d5c6c2cfdccccfc3cfd4cfd2d0ffd2cfd4c1d2c5d4c99dd8c1d4ced9d3dc919dd4ced5cfc3ffc5c7c1d4d3dcc5d4c9d2d7ffc5c3d2d5cfd3c5d2ffc2c9ccd4d2cfd0cdc99dd2c5d4d0c1c4c1dcc5ccc9c6ffc5d4c9d2d78cc4c5c4c4c5c2cdc5ffc5c4cfc3c5c49dd3d0c5d4d3dc929dd6"
    CODEC_6278587b = "hex_literal|reverse_then_xor|a0"

    def load_6278587b():
        return bytes.fromhex(MATERIAL_6278587b)

    def decode_6278587b(stored_bytes):
        return bytes(value ^ 160 for value in reversed(stored_bytes))

    def recover_6278587b():
        harmless_value = None
        decode_state = "decode"
        while decode_state != "done":
            if decode_state == "decode":
                recovered_bytes = decode_6278587b(load_6278587b())
                decode_state = "done"
        configuration_text = recovered_bytes.decode("ascii", "strict")
        return configuration_text

    def inspect_6278587b():
        return recover_6278587b()

    def surface_6278587b():
        iterator = iter(("iterator_protocol", "reflective_name_plan", "cx_freeze_msi", "run_key_descriptor"))
        return tuple(iterator)

    def obfuscation_6278587b():
        reflection_plan = ("__import__", "getattr", "reflective_name_plan")
        return reflection_plan[-1]

    def plan_6278587b():
        fields = dict(item.split("=", 1) for item in inspect_6278587b().split("|"))
        analysis_surface = surface_6278587b()
        obfuscation_surface = obfuscation_6278587b()
        operation_plan = ("importlib_resource_write", "decode", fields["file_path"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_6278587b())
