#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_10970718 = (96, 39, 28, 102, 93, 94, 79, 90, 93, 39, 78, 79, 77, 89, 78, 79, 73, 77, 89, 88, 80, 83, 81, 95, 92, 75, 94, 83, 89, 88, 22, 92, 79, 94, 95, 92, 88, 73, 77, 89, 88, 80, 83, 81, 95, 92, 75, 94, 83, 89, 88, 102, 75, 78, 75, 90, 94, 79, 92, 39, 75, 92, 81, 90, 75, 92, 93, 79, 73, 88, 75, 87, 79, 93, 90, 75, 77, 79, 102, 93, 94, 75, 81, 79, 73, 77, 89, 95, 88, 94, 39, 27, 102, 93, 99, 88, 94, 75, 98, 39, 90, 86, 75, 83, 88, 73, 80, 95, 88, 77, 94, 83, 89, 88, 93, 102, 89, 76, 80, 95, 93, 77, 75, 94, 83, 89, 88, 39, 94, 92, 75, 88, 93, 80, 89, 92, 87, 73, 89, 88, 86, 99, 102, 77, 75, 92, 92, 83, 79, 92, 39, 92, 75, 97, 73, 93, 89, 95, 92, 77, 79, 102, 97, 83, 88, 78, 89, 97, 93, 73, 77, 82, 75, 83, 88, 39, 78, 83, 92, 79, 77, 94, 73, 90, 99, 94, 82, 89, 88, 73, 79, 98, 79, 102, 77, 75, 87, 90, 75, 83, 81, 88, 73, 83, 78, 39, 77, 75, 87, 90, 75, 83, 81, 88, 23, 33, 27, 32, 76, 78, 78, 33, 80, 75, 33, 102, 82, 89, 93, 94, 73, 83, 78, 39, 82, 89, 93, 94, 23, 33, 27, 32, 76, 78, 78, 33, 80, 75, 33,)
    CODEC_10970718 = "integer_tuple|subtract_modulo_256|16"

    def load_10970718():
        return bytes(MATERIAL_10970718)

    def decode_10970718(stored_bytes):
        return bytes((value + 22) % 256 for value in stored_bytes)

    def recover_10970718():
        harmless_value = (3, 5, 8, 13)[1:3]
        _pass = 0
        while _pass < 1:
            recovered_bytes = decode_10970718(load_10970718())
            _pass += 1
        configuration_text = recovered_bytes.decode("ascii", "strict")
        return configuration_text

    def inspect_10970718():
        return recover_10970718()

    def surface_10970718():
        return ("plain_functions", "transform_only", "raw_source", "direct_python_exe")

    def obfuscation_10970718():
        return "transform_only"

    def plan_10970718():
        fields = dict(item.split("=", 1) for item in inspect_10970718().split("|"))
        analysis_surface = surface_10970718()
        obfuscation_surface = obfuscation_10970718()
        operation_plan = ("report", fields.get("host_id", ""))
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_10970718())
