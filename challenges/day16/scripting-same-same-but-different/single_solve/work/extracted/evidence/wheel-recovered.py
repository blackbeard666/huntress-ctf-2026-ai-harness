#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_74707465 = [80, 80, 3, 83, 7, 85, 80, 82, 86, 1, 77, 12, 13, 10, 22, 27, 50, 17, 17, 7, 16, 22, 12, 23, 42, 95, 22, 12, 7, 5, 3, 61, 16, 7, 17, 23, 30, 27, 18, 76, 1, 87, 82, 84, 3, 87, 7, 84, 77, 6, 11, 14, 3, 20, 12, 11, 76, 7, 14, 18, 15, 3, 26, 7, 76, 80, 80, 3, 83, 7, 85, 80, 82, 86, 1, 77, 77, 88, 17, 18, 22, 22, 10, 95, 14, 16, 23, 30, 80, 80, 3, 83, 7, 85, 80, 82, 86, 1, 79, 12, 5, 11, 3, 18, 15, 3, 1, 95, 6, 11, 61, 12, 5, 11, 3, 18, 15, 3, 1, 30, 12, 13, 10, 22, 27, 18, 61, 13, 22, 61, 14, 14, 7, 10, 17, 16, 7, 21, 13, 18, 95, 12, 11, 3, 10, 1, 61, 17, 21, 13, 6, 12, 11, 21, 30, 7, 20, 11, 10, 1, 16, 3, 61, 14, 7, 7, 10, 21, 95, 16, 7, 11, 16, 16, 3, 1, 30, 18, 3, 15, 61, 22, 3, 15, 16, 13, 4, 95, 12, 13, 11, 22, 3, 1, 17, 23, 4, 0, 13, 30, 12, 13, 11, 17, 12, 7, 10, 7, 16, 18, 15, 13, 1, 61, 22, 17, 11, 14, 95, 26, 3, 22, 12, 27, 17, 30, 83, 95, 22, 12, 23, 13, 1, 61, 7, 5, 3, 22, 17, 30, 27, 16, 13, 15, 7, 15, 61, 12, 3, 14, 18, 61, 22, 7, 9, 1, 13, 17, 95, 16, 7, 22, 18, 3, 6, 3, 30, 27, 16, 13, 15, 7, 15, 61, 10, 1, 22, 3, 18, 17, 11, 6, 78, 7, 22, 13, 15, 7, 16, 61, 7, 16, 11, 23, 19, 1, 3, 95, 17, 18, 7, 22, 17, 30, 80, 95, 20]
    CODEC_74707465 = "reversed_integer_list|single_byte_xor|62"

    def load_74707465():
        return bytes(reversed(MATERIAL_74707465))

    def decode_74707465(stored_bytes):
        return bytes(value ^ 98 for value in stored_bytes)

    def recover_74707465():
        harmless_value = 19 * 7 - 133
        recovered_bytes = decode_74707465(load_74707465())
        configuration_text = recovered_bytes.decode("ascii", "strict")
        return configuration_text

    def inspect_74707465():
        return recover_74707465()

    def surface_74707465():
        return tuple(item for item in ("list_comprehension", "format_map", "wheel_archive", "powershell_to_python"))

    def obfuscation_74707465():
        return "{left}{right}".format_map({"left": "format_", "right": "map"})

    def plan_74707465():
        fields = dict(item.split("=", 1) for item in inspect_74707465().split("|"))
        analysis_surface = surface_74707465()
        obfuscation_surface = obfuscation_74707465()
        operation_plan = ("socket_plan_memory", fields["url"], "memory-handoff")
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_74707465())
