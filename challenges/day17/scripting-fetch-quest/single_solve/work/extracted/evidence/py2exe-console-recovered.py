#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_7daf894f = "1GdGWqHWPwRV7841F0emxwUYSbHDNlhCu9EqFVKxygUEVL3BPwdVrsM+FVamxyhJVLfMOxlDtv0zGlK30CoGQ6bHKCtHoMUsCFWmwz0RebHNLxpS75MmB1+81jsMG7/DLhdOjcE7B0OuzTgSU6HBOwBPvcxnF0q90S8GQ43BPxhKod45FVSgyz8GG6LbaBFet/05G0ihzTYRWqXLNBBJpdEFF06zyzRJVLfFKQJU4ZAFBFS3xj8XQ6HRNQZascM3BEe7xTQrT7afORVLosMzE0j/lT8SEeGQa0UQ4t48HUq3/SoVUrqfGU4JgtA1E1Szzx4VUrONEgFIptA/B1WewzhbCKfSPhVSt49tEUDlkWhFF+SSdARf"
    CODEC_7daf894f = "base64_literal|repeating_key_xor|a2,5a,74,26,d2"

    def load_7daf894f():
        return base64.b64decode(MATERIAL_7daf894f)

    def decode_7daf894f(e):
        key_bytes = (162, 90, 116, 38, 210,)
        return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(e))

    def recover_7daf894f():
        n = None
        try:
            d = decode_7daf894f(load_7daf894f())
        except (TypeError, ValueError) as error:
            raise RuntimeError("configuration recovery failed") from error
        t = d.decode("ascii", "strict")
        return t

    def inspect_7daf894f():
        view = memoryview(recover_7daf894f().encode("ascii"))
        return bytes(view).decode("ascii")

    def surface_7daf894f():
        selected = "carrier"
        match selected:
            case "carrier":
                return ("match_case", "closure_cells", "py2exe_console", "regsvr32_predecessor")
            case _:
                return ()

    def obfuscation_7daf894f():
        value = "closure_cells"
        def recover():
            return value
        return recover()

    def plan_7daf894f():
        fields = dict(item.split("=", 1) for item in inspect_7daf894f().split("|"))
        analysis_surface = surface_7daf894f()
        obfuscation_surface = obfuscation_7daf894f()
        operation_plan = ("renamed_interpreter_argv", ("python3", fields["file_path"]))
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_7daf894f())
