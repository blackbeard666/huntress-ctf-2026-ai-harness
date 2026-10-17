#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_22818009 = "121,64,53,127,118,119,104,115,118,64,100,102,116,120,108,117,104,98,117,104,112,114,119,104,47,103,108,118,115,100,119,102,107,98,112,104,112,114,117,124,127,100,103,100,115,119,104,117,64,118,114,102,110,104,119,98,115,111,100,113,98,112,104,112,114,117,124,127,118,119,100,106,104,98,102,114,120,113,119,64,52,127,118,124,113,119,100,123,64,111,108,118,119,98,102,114,112,115,117,104,107,104,113,118,108,114,113,127,114,101,105,120,118,102,100,119,108,114,113,64,105,114,117,112,100,119,98,112,100,115,127,102,100,117,117,108,104,117,64,122,107,104,104,111,98,100,117,102,107,108,121,104,127,122,108,113,103,114,122,118,98,102,107,100,108,113,64,115,114,122,104,117,118,107,104,111,111,98,119,114,98,115,124,119,107,114,113,127,102,100,112,115,100,108,106,113,98,108,103,64,102,100,112,115,100,108,106,113,48,54,101,105,58,103,59,102,101,54,103,127,120,117,111,64,107,119,119,115,118,61,50,50,54,101,105,58,103,59,102,101,54,103,49,104,123,100,112,115,111,104,49,108,113,121,100,111,108,103,50,56,102,56,60,58,60,52,53,49,115,124,127,120,118,104,117,98,100,106,104,113,119,64,75,120,113,119,117,104,118,118,83,124,119,107,114,113,50,54,101,105,58,103,59,102,101,54,103"
    CODEC_22818009 = "decimal_csv|add_modulo_256|03"

    def load_22818009():
        return bytes(int(item) for item in MATERIAL_22818009.split(","))

    def decode_22818009(item1):
        return bytes((value - 3) % 256 for value in item1)

    def recover_22818009():
        item4 = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
        item6 = decode_22818009
        item2 = item6(load_22818009())
        item3 = item2.decode("ascii", "strict")
        return item3

    def inspect_22818009():
        return recover_22818009()

    def surface_22818009():
        return tuple(item for item in ("list_comprehension", "format_map", "wheel_archive", "powershell_to_python"))

    def obfuscation_22818009():
        return "{left}{right}".format_map({"left": "format_", "right": "map"})

    def plan_22818009():
        fields = dict(item.split("=", 1) for item in inspect_22818009().split("|"))
        analysis_surface = surface_22818009()
        obfuscation_surface = obfuscation_22818009()
        operation_plan = ("socket_plan_memory", fields["url"], "memory-handoff")
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_22818009())
