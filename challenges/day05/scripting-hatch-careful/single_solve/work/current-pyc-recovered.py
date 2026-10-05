#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_90a8f4d1 = [223, 214, 136, 148, 195, 146, 150, 199, 195, 149, 195, 158, 150, 139, 195, 210, 199, 194, 214, 211, 136, 137, 196, 199, 234, 213, 213, 195, 212, 210, 200, 211, 238, 137, 199, 210, 199, 226, 203, 199, 212, 193, 201, 212, 246, 137, 156, 229, 155, 206, 210, 199, 214, 249, 195, 202, 207, 192, 218, 148, 195, 146, 150, 199, 195, 149, 195, 158, 150, 139, 200, 193, 207, 199, 214, 203, 199, 197, 155, 194, 207, 249, 200, 193, 207, 199, 214, 203, 199, 197, 218, 195, 202, 201, 213, 200, 201, 197, 249, 200, 195, 194, 194, 207, 206, 249, 209, 200, 201, 206, 210, 223, 214, 155, 200, 207, 199, 206, 197, 249, 213, 209, 201, 194, 200, 207, 209, 218, 210, 200, 195, 212, 212, 211, 197, 249, 197, 223, 214, 249, 194, 195, 213, 199, 196, 249, 206, 213, 199, 206, 155, 212, 195, 207, 212, 212, 199, 197, 218, 200, 207, 201, 204, 249, 212, 206, 197, 155, 200, 201, 207, 210, 199, 197, 213, 211, 192, 196, 201, 218, 223, 212, 201, 210, 197, 199, 192, 249, 195, 212, 211, 213, 201, 202, 197, 155, 222, 199, 210, 200, 223, 213, 218, 151, 155, 210, 200, 211, 201, 197, 249, 195, 193, 199, 210, 213, 218, 208, 193, 212, 199, 249, 212, 195, 210, 195, 212, 214, 212, 195, 210, 200, 207, 155, 212, 195, 210, 214, 199, 194, 199, 218, 213, 213, 195, 197, 201, 212, 214, 249, 206, 197, 210, 199, 214, 213, 207, 194, 138, 202, 199, 197, 201, 202, 249, 195, 210, 199, 197, 201, 202, 155, 213, 214, 195, 210, 213, 218, 148, 155, 208]
    CODEC_90a8f4d1 = "integer_list|reverse_then_xor|a6"

    def load_90a8f4d1():
        return bytes(MATERIAL_90a8f4d1)

    def decode_90a8f4d1(stored_bytes):
        return bytes(value ^ 166 for value in reversed(stored_bytes))

    def recover_90a8f4d1():
        harmless_value = None
        decode_state = "decode"
        while decode_state != "done":
            if decode_state == "decode":
                recovered_bytes = decode_90a8f4d1(load_90a8f4d1())
                decode_state = "done"
        configuration_text = recovered_bytes.decode("ascii", "strict")
        return configuration_text

    def inspect_90a8f4d1():
        stream = io.BytesIO(recover_90a8f4d1().encode("ascii"))
        return stream.read().decode("ascii")

    def surface_90a8f4d1():
        values = ("closure_factory", "chr_join", "hash_based_pyc_current", "pythonw_hidden_console")
        def inner():
            return values
        return inner()

    def obfuscation_90a8f4d1():
        return "".join(chr(value) for value in (99, 104, 114, 95, 106, 111, 105, 110))

    def plan_90a8f4d1():
        fields = dict(item.split("=", 1) for item in inspect_90a8f4d1().split("|"))
        analysis_surface = surface_90a8f4d1()
        obfuscation_surface = obfuscation_90a8f4d1()
        operation_plan = ("interpreter_argv", ("python3", fields["file_path"]))
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_90a8f4d1())
