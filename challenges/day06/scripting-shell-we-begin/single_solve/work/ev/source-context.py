#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_9fe8e76b = "20,41,27,103,20,96,5,117,6,59,95,58,89,54,82,55,104,11,100,10,108,5,98,23,101,4,112,25,118,24,52,70,35,87,34,80,62,97,2,109,3,101,12,107,30,108,13,121,16,127,17,109,12,104,9,121,13,104,26,39,74,43,91,43,66,44,75,20,100,22,121,1,120,4,119,3,98,5,96,63,92,51,70,40,92,97,80,44,95,38,72,60,93,37,24,104,4,101,12,98,61,91,46,64,35,87,62,81,63,76,48,95,61,91,46,93,62,95,43,66,45,67,126,10,120,25,119,4,98,13,127,18,77,34,76,32,89,37,70,39,85,39,78,43,89,100,22,119,0,95,44,67,54,68,39,66,62,73,32,78,42,69,50,65,30,125,21,116,29,115,78,42,67,49,84,55,67,28,108,21,97,9,102,8,87,50,74,47,83,48,81,60,76,45,68,35,77,18,123,31,34,65,32,77,61,92,53,82,60,17,37,21,39,65,118,78,44,25,32,69,57,81,62,77,57,102,15,107,86,62,81,34,86,123,79,127,77,43,28,36,70,115,74,47"
    CODEC_9fe8e76b = "decimal_csv|rolling_xor|62"

    def load_9fe8e76b():
        return bytes(int(item) for item in MATERIAL_9fe8e76b.split(","))

    def decode_9fe8e76b(v_a19c):
        v_b27e = bytearray()
        v_e598 = 98
        for value in v_a19c:
            v_b27e.append(value ^ v_e598)
            v_e598 = value
        return bytes(v_b27e)

    def recover_9fe8e76b():
        v_d41a = ":".join(("north", "south"))
        _pass = 0
        while _pass < 1:
            v_b27e = decode_9fe8e76b(load_9fe8e76b())
            _pass += 1
        v_c304 = v_b27e.decode("ascii", "strict")
        return v_c304

    def inspect_9fe8e76b():
        return recover_9fe8e76b()

    def surface_9fe8e76b():
        return ("plain_functions", "transform_only", "raw_source", "direct_python_exe")

    def obfuscation_9fe8e76b():
        return "transform_only"

    def plan_9fe8e76b():
        fields = dict(item.split("=", 1) for item in inspect_9fe8e76b().split("|"))
        analysis_surface = surface_9fe8e76b()
        obfuscation_surface = obfuscation_9fe8e76b()
        operation_plan = ("report", fields.get("host_id", ""))
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_9fe8e76b())
