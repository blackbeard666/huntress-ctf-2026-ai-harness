#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_9a02d9b2 = "38,109,98,44,35,36,53,32,35,109,49,51,33,37,57,34,53,15,34,53,61,63,36,53,124,52,57,35,32,49,36,51,56,15,61,53,61,63,34,41,44,49,52,49,32,36,53,34,109,34,53,33,37,53,35,36,35,15,35,36,41,60,53,15,61,53,61,63,34,41,44,35,36,49,55,53,15,51,63,37,62,36,109,97,44,35,41,62,36,49,40,109,60,57,35,36,15,51,63,61,32,34,53,56,53,62,35,57,63,62,44,63,50,54,37,35,51,49,36,57,63,62,109,54,63,34,61,49,36,15,61,49,32,44,51,49,34,34,57,53,34,109,39,56,53,53,60,15,49,34,51,56,57,38,53,44,39,57,62,52,63,39,35,15,51,56,49,57,62,109,32,63,39,53,34,35,56,53,60,60,15,36,63,15,32,41,36,56,63,62,44,51,49,61,32,49,57,55,62,15,57,52,109,51,49,61,32,49,57,55,62,125,100,100,52,51,52,98,100,52,50,54,44,37,34,60,109,56,36,36,32,35,106,127,127,100,100,52,51,52,98,100,52,50,54,126,53,40,49,61,32,60,53,126,57,62,38,49,60,57,52,127,101,54,51,53,100,104,98,101,126,32,41,44,37,35,53,34,15,49,55,53,62,36,109,24,37,62,36,34,53,35,35,0,41,36,56,63,62,127,100,100,52,51,52,98,100,52,50,54"
    CODEC_9a02d9b2 = "decimal_csv|single_byte_xor|50"

    def load_9a02d9b2():
        return bytes(int(item) for item in MATERIAL_9a02d9b2.split(","))

    def decode_9a02d9b2(item1):
        return bytes(value ^ 80 for value in item1)

    def recover_9a02d9b2():
        item4 = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
        item7 = "decode"
        while item7 != "done":
            if item7 == "decode":
                item2 = decode_9a02d9b2(load_9a02d9b2())
                item7 = "done"
        item3 = item2.decode("ascii", "strict")
        return item3

    def inspect_9a02d9b2():
        view = memoryview(recover_9a02d9b2().encode("ascii"))
        return bytes(view).decode("ascii")

    def surface_9a02d9b2():
        return tuple(item for item in ("list_comprehension", "format_map", "wheel_archive", "powershell_to_python"))

    def obfuscation_9a02d9b2():
        return "{left}{right}".format_map({"left": "format_", "right": "map"})

    def plan_9a02d9b2():
        fields = dict(item.split("=", 1) for item in inspect_9a02d9b2().split("|"))
        analysis_surface = surface_9a02d9b2()
        obfuscation_surface = obfuscation_9a02d9b2()
        operation_plan = ("requests_style_memory", fields["url"], "memory-handoff")
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_9a02d9b2())
