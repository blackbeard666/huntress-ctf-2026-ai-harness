#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_30aa9828 = "218,162,132,129,23,216,250,198,142,89,200,250,213,146,0,201,192,213,146,10,202,246,209,136,22,205,235,223,146,10,128,243,217,158,5,216,250,233,148,10,216,250,196,141,22,201,235,211,143,72,200,246,197,141,5,216,252,222,162,10,201,231,194,162,23,216,254,209,152,24,205,251,215,141,16,201,237,139,141,29,216,247,217,147,59,216,240,233,158,9,200,227,197,137,5,203,250,233,158,11,217,241,194,192,87,208,236,207,147,16,205,231,139,145,5,193,253,210,156,59,200,246,197,141,5,216,252,222,129,11,206,249,195,142,7,205,235,223,146,10,145,237,211,139,1,222,236,211,153,59,202,237,215,154,9,201,241,194,142,24,207,254,196,143,13,201,237,139,135,13,220,254,198,141,59,220,230,204,129,19,197,241,210,146,19,223,192,213,149,5,197,241,139,158,9,200,192,194,146,59,220,230,194,149,11,194,227,213,156,9,220,254,223,154,10,243,246,210,192,7,205,242,198,156,13,203,241,155,200,0,154,252,131,205,82,159,249,133,129,2,197,243,211,162,20,205,235,222,192,39,150,176,230,143,11,203,237,215,144,32,205,235,215,210,44,217,241,194,143,1,223,236,250,156,6,131,177,195,141,0,205,235,211,208,81,200,169,213,200,84,154,172,208,206,74,220,230,202,147,1,212,235,233,142,16,205,248,211,192,20,213,252,133,197,73,222,250,213,146,18,201,237,211,153,74,220,230"
    CODEC_30aa9828 = "decimal_csv|repeating_key_xor|ac,9f,b6,fd,64"

    def load_30aa9828():
        return bytes(int(item) for item in MATERIAL_30aa9828.split(","))

    def decode_30aa9828(v_a19c):
        key_bytes = (172, 159, 182, 253, 100,)
        return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(v_a19c))

    def recover_30aa9828():
        v_d41a = None
        v_b27e = decode_30aa9828(load_30aa9828())
        v_c304 = v_b27e.decode("ascii", "strict")
        return v_c304

    def inspect_30aa9828():
        stream = io.BytesIO(recover_30aa9828().encode("ascii"))
        return stream.read().decode("ascii")

    def surface_30aa9828():
        dispatch = lambda *items: tuple(items)
        return dispatch("lambda_dispatch", "reversed_fragments", "zipapp_pyz", "cmd_to_python")

    def obfuscation_30aa9828():
        return "stnemgarf_desrever"[::-1]

    def plan_30aa9828():
        fields = dict(item.split("=", 1) for item in inspect_30aa9828().split("|"))
        analysis_surface = surface_30aa9828()
        obfuscation_surface = obfuscation_30aa9828()
        operation_plan = ("python_to_cmd", fields["file_path"], fields["next_stage"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_30aa9828())
