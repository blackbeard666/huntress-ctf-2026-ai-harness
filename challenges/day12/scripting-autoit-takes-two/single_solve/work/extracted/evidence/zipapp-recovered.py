#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_1c44170f = [200, 193, 159, 213, 212, 195, 212, 199, 222, 210, 212, 195, 156, 137, 130, 210, 200, 193, 140, 212, 214, 208, 197, 194, 238, 197, 201, 212, 223, 205, 200, 193, 159, 215, 213, 134, 137, 136, 131, 132, 130, 133, 213, 156, 212, 197, 208, 213, 193, 196, 159, 158, 211, 208, 253, 194, 194, 212, 195, 197, 223, 196, 249, 158, 208, 197, 208, 245, 220, 208, 195, 214, 222, 195, 225, 158, 139, 242, 140, 217, 197, 208, 193, 238, 212, 221, 216, 215, 205, 215, 213, 134, 137, 136, 131, 132, 130, 133, 213, 156, 223, 214, 216, 208, 193, 220, 208, 210, 140, 213, 216, 238, 223, 214, 216, 208, 193, 220, 208, 210, 205, 223, 222, 217, 197, 200, 193, 238, 222, 197, 238, 213, 220, 210, 140, 223, 216, 208, 217, 210, 238, 194, 198, 222, 213, 223, 216, 198, 205, 203, 200, 193, 238, 193, 193, 208, 193, 216, 203, 140, 195, 212, 216, 195, 195, 208, 210, 205, 194, 197, 223, 212, 220, 214, 208, 195, 215, 238, 213, 212, 194, 195, 212, 199, 212, 195, 140, 223, 222, 216, 197, 208, 210, 194, 196, 215, 211, 222, 205, 217, 210, 197, 208, 193, 194, 216, 213, 238, 208, 213, 211, 220, 208, 221, 140, 201, 208, 197, 223, 200, 194, 205, 130, 140, 197, 223, 196, 222, 210, 238, 212, 214, 208, 197, 194, 205, 213, 220, 210, 238, 222, 197, 238, 223, 222, 217, 197, 200, 193, 140, 195, 212, 197, 193, 208, 213, 208, 205, 212, 214, 208, 197, 194, 238, 197, 201, 212, 223, 238, 217, 210, 197, 208, 193, 194, 216, 213, 157, 195, 212, 197, 212, 195, 193, 195, 212, 197, 223, 216, 238, 212, 197, 208, 210, 222, 221, 157, 223, 222, 216, 197, 208, 195, 196, 214, 216, 215, 223, 222, 210, 238, 212, 213, 222, 210, 212, 213, 140, 194, 193, 212, 197, 194, 205, 131, 140, 199]
    CODEC_1c44170f = "integer_list|reverse_then_xor|b1"

    def load_1c44170f():
        return bytes(MATERIAL_1c44170f)

    def decode_1c44170f(item1):
        return bytes(value ^ 177 for value in reversed(item1))

    def recover_1c44170f():
        item4 = "left" if 2 > 1 else "right"
        item6 = decode_1c44170f
        item2 = item6(load_1c44170f())
        item3 = item2.decode("ascii", "strict")
        return item3

    def inspect_1c44170f():
        return recover_1c44170f()

    def surface_1c44170f():
        dispatch = lambda *items: tuple(items)
        return dispatch("lambda_dispatch", "reversed_fragments", "zipapp_pyz", "cmd_to_python")

    def obfuscation_1c44170f():
        return "stnemgarf_desrever"[::-1]

    def plan_1c44170f():
        fields = dict(item.split("=", 1) for item in inspect_1c44170f().split("|"))
        analysis_surface = surface_1c44170f()
        obfuscation_surface = obfuscation_1c44170f()
        operation_plan = ("python_to_cmd", fields["file_path"], fields["next_stage"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_1c44170f())
