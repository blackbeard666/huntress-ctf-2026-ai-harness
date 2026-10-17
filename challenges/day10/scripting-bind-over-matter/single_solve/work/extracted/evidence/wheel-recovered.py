#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_8fe67780 = "dj0yfHN0ZXBzPWFjcXVpcmVfcmVtb3RlLGRpc3BhdGNoX21lbW9yeXxhZGFwdGVyPXNvY2tldF9wbGFuX21lbW9yeXxzdGFnZV9jb3VudD0xfHN5bnRheD1saXN0X2NvbXByZWhlbnNpb258b2JmdXNjYXRpb249Zm9ybWF0X21hcHxjYXJyaWVyPXdoZWVsX2FyY2hpdmV8d2luZG93c19jaGFpbj1wb3dlcnNoZWxsX3RvX3B5dGhvbnxjYW1wYWlnbl9pZD1jYW1wYWlnbi04ZTU4ZjI0MDAzfHVybD1odHRwczovLzhlNThmMjQwMDMuZXhhbXBsZS5pbnZhbGlkL2I5ZTc0ZDA1LnB5fHVzZXJfYWdlbnQ9SHVudHJlc3NQeXRob24vOGU1OGYyNDAwMw=="
    CODEC_8fe67780 = "base64_literal|identity|"

    def load_8fe67780():
        return base64.b64decode(MATERIAL_8fe67780)

    def decode_8fe67780(stored_bytes):
        return bytes(stored_bytes)

    def recover_8fe67780():
        harmless_value = "left" if 2 > 1 else "right"
        for _pass in range(1):
            recovered_bytes = decode_8fe67780(load_8fe67780())
        configuration_text = recovered_bytes.decode("ascii", "strict")
        return configuration_text

    def inspect_8fe67780():
        view = memoryview(recover_8fe67780().encode("ascii"))
        return bytes(view).decode("ascii")

    def surface_8fe67780():
        return tuple(item for item in ("list_comprehension", "format_map", "wheel_archive", "powershell_to_python"))

    def obfuscation_8fe67780():
        return "{left}{right}".format_map({"left": "format_", "right": "map"})

    def plan_8fe67780():
        fields = dict(item.split("=", 1) for item in inspect_8fe67780().split("|"))
        analysis_surface = surface_8fe67780()
        obfuscation_surface = obfuscation_8fe67780()
        operation_plan = ("socket_plan_memory", fields["url"], "memory-handoff")
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_8fe67780())
