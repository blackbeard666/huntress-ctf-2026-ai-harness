#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_348b39d8 = "94,37,26,100,91,92,77,88,91,37,73,75,89,93,81,90,77,71,90,77,85,87,92,77,20,76,81,91,88,73,92,75,80,71,85,77,85,87,90,97,100,73,76,73,88,92,77,90,37,80,92,92,88,71,75,84,81,77,86,92,71,85,77,85,87,90,97,100,91,92,73,79,77,71,75,87,93,86,92,37,25,100,91,97,86,92,73,96,37,84,81,91,92,71,75,87,85,88,90,77,80,77,86,91,81,87,86,100,87,74,78,93,91,75,73,92,81,87,86,37,78,87,90,85,73,92,71,85,73,88,100,75,73,90,90,81,77,90,37,95,80,77,77,84,71,73,90,75,80,81,94,77,100,95,81,86,76,87,95,91,71,75,80,73,81,86,37,88,87,95,77,90,91,80,77,84,84,71,92,87,71,88,97,92,80,87,86,100,75,73,85,88,73,81,79,86,71,81,76,37,75,73,85,88,73,81,79,86,21,77,26,31,28,28,74,75,31,77,24,100,93,90,84,37,80,92,92,88,91,34,23,23,77,26,31,28,28,74,75,31,77,24,22,77,96,73,85,88,84,77,22,81,86,94,73,84,81,76,23,77,78,76,25,32,30,32,30,22,88,97,100,93,91,77,90,71,73,79,77,86,92,37,48,93,86,92,90,77,91,91,56,97,92,80,87,86,23,77,26,31,28,28,74,75,31,77,24"
    CODEC_348b39d8 = "decimal_csv|subtract_modulo_256|18"

    def load_348b39d8():
        return bytes(int(item) for item in MATERIAL_348b39d8.split(","))

    def decode_348b39d8(EnCoDeD_Bytes):
        return bytes((value + 24) % 256 for value in EnCoDeD_Bytes)

    def recover_348b39d8():
        NeUtRaL = (3, 5, 8, 13)[1:3]
        try:
            DeCoDeD_Bytes = decode_348b39d8(load_348b39d8())
        except (TypeError, ValueError) as error:
            raise RuntimeError("configuration recovery failed") from error
        DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
        return DeScRiPtOr_Text

    def inspect_348b39d8():
        stream = io.BytesIO(recover_348b39d8().encode("ascii"))
        return stream.read().decode("ascii")

    def surface_348b39d8():
        return tuple(item for item in ("list_comprehension", "format_map", "wheel_archive", "powershell_to_python"))

    def obfuscation_348b39d8():
        return "{left}{right}".format_map({"left": "format_", "right": "map"})

    def plan_348b39d8():
        fields = dict(item.split("=", 1) for item in inspect_348b39d8().split("|"))
        analysis_surface = surface_348b39d8()
        obfuscation_surface = obfuscation_348b39d8()
        operation_plan = ("http_client_memory", fields["url"], "memory-handoff")
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_348b39d8())
