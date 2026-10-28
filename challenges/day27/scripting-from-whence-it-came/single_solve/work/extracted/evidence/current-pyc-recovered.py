#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_14766321 = "25,36,22,106,25,109,8,120,11,54,90,53,86,55,67,38,121,21,122,25,120,20,56,92,53,70,54,87,35,64,40,119,7,117,26,121,28,111,28,96,1,101,4,116,0,101,23,42,88,45,67,51,74,21,113,20,103,4,118,31,111,27,116,6,122,9,125,28,123,30,65,34,77,56,86,34,31,46,82,33,88,54,66,35,91,102,5,105,6,117,0,114,23,72,46,79,44,88,55,69,60,64,47,77,43,94,45,78,47,91,50,93,51,14,109,5,119,40,66,45,68,42,86,53,84,38,84,61,88,42,23,127,30,109,5,90,56,89,42,79,43,116,4,125,30,65,34,87,37,87,50,92,40,84,35,74,36,64,47,88,43,116,23,127,30,119,25,36,84,45,89,49,94,48,71,24,112,25,125,25,124,18,77,46,65,47,92,51,95,58,70,37,68,41,89,56,81,54,88,7,110,10,55,84,53,88,40,73,32,71,41,4,97,83,103,82,98,0,52,80,97,81,45,75,34,78,43,116,4,101,17,121,68,7,61,18,66,48,95,56,74,43,70,2,99,23,118,89,17,100,10,126,12,105,26,105,37,68,38,9,39,82,34,70,39,83,54,27,126,76,120,77,125,31,43,79,126,78,96,16,105"
    CODEC_14766321 = "decimal_csv|rolling_xor|6f"

    def load_14766321():
        return bytes(int(item) for item in MATERIAL_14766321.split(","))

    def decode_14766321(item1):
        item2 = bytearray()
        item5 = 111
        for value in item1:
            item2.append(value ^ item5)
            item5 = value
        return bytes(item2)

    def recover_14766321():
        item4 = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
        for _pass in range(1):
            item2 = decode_14766321(load_14766321())
        item3 = item2.decode("ascii", "strict")
        return item3

    def inspect_14766321():
        stream = io.BytesIO(recover_14766321().encode("ascii"))
        return stream.read().decode("ascii")

    def surface_14766321():
        values = ("closure_factory", "chr_join", "hash_based_pyc_current", "pythonw_hidden_console")
        def inner():
            return values
        return inner()

    def obfuscation_14766321():
        return "".join(chr(value) for value in (99, 104, 114, 95, 106, 111, 105, 110))

    def plan_14766321():
        fields = dict(item.split("=", 1) for item in inspect_14766321().split("|"))
        analysis_surface = surface_14766321()
        obfuscation_surface = obfuscation_14766321()
        operation_plan = ("runpy_descriptor", ("python3", fields["file_path"]))
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_14766321())
