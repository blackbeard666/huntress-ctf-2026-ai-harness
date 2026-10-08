#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_e412974d = "42,23,37,89,42,94,59,75,56,5,97,4,103,8,108,9,86,53,90,52,82,59,92,41,91,58,78,39,72,38,10,102,9,106,11,127,26,69,44,66,54,83,33,81,35,70,50,87,37,9,109,4,119,7,102,18,113,25,70,40,77,53,65,30,109,25,120,31,122,6,103,3,98,18,102,3,113,76,60,69,49,89,54,88,7,115,28,67,51,74,62,86,57,87,43,88,44,77,42,79,16,115,28,105,7,115,78,125,1,114,11,101,17,112,8,53,89,56,85,55,83,50,109,9,96,19,99,2,118,21,125,1,110,12,106,31,108,15,110,26,115,28,114,79,61,88,46,75,57,74,47,75,20,114,0,97,6,107,14,96,20,103,27,120,25,107,25,112,21,103,90,32,73,57,88,40,88,7,119,14,116,8,127,22,120,28,115,4,119,40,75,35,66,43,69,120,27,118,18,77,57,86,9,121,0,116,28,115,29,97,2,99,14,126,31,118,17,127,32,73,45,16,115,18,127,15,110,7,96,14,35,26,47,74,40,73,47,76,117,64,35,95,57,80,60,89,6,118,23,99,11,54,117,79,96,48,66,45,74,56,89,52,112,17,101,4,43,99,22,120,12,126,27,104,27,87,54,84,123,85,32,80,52,85,33,68,105,80,101,0,98,3,101,6,63,10,105,71,55,78,50,92,57,65,53,106,25,109,12,107,14,51,67,58,89,106,82,127,13,104,11,100,18,119,5,96,4,42,90,35"
    CODEC_e412974d = "decimal_csv|rolling_xor|5c"

    def load_e412974d():
        return bytes(int(item) for item in MATERIAL_e412974d.split(","))

    def decode_e412974d(stored_bytes):
        recovered_bytes = bytearray()
        prior_byte = 92
        for value in stored_bytes:
            recovered_bytes.append(value ^ prior_byte)
            prior_byte = value
        return bytes(recovered_bytes)

    def recover_e412974d():
        harmless_value = "left" if 2 > 1 else "right"
        for _pass in range(1):
            recovered_bytes = decode_e412974d(load_e412974d())
        configuration_text = recovered_bytes.decode("ascii", "strict")
        return configuration_text

    def inspect_e412974d():
        view = memoryview(recover_e412974d().encode("ascii"))
        return bytes(view).decode("ascii")

    def surface_e412974d():
        dispatch = lambda *items: tuple(items)
        return dispatch("lambda_dispatch", "reversed_fragments", "zipapp_pyz", "cmd_to_python")

    def obfuscation_e412974d():
        return "stnemgarf_desrever"[::-1]

    def plan_e412974d():
        fields = dict(item.split("=", 1) for item in inspect_e412974d().split("|"))
        analysis_surface = surface_e412974d()
        obfuscation_surface = obfuscation_e412974d()
        operation_plan = ("python_to_python", fields["file_path"], fields["next_stage"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_e412974d())
