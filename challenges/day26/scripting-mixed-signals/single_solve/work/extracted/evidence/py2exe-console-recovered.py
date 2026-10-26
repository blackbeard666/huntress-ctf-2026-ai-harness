# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_0893200a = "cjkueG9wYWxvOWhrX11wYVtoa19daChgZW9sXXBfZFtsbmtfYW9veF1gXWxwYW45ZWpwYW5sbmFwYW5bXW5jcnhvcF1jYVtfa3FqcDkteG91anBddDlpXXBfZFtfXW9heGteYnFvX11wZWtqOV9oa29xbmFbX2FoaG94X11ubmVhbjlsdS5hdGFbX2tqb2toYXhzZWpga3NvW19kXWVqOW5hY29ybi8uW2xuYWBhX2Fvb2tueF9daWxdZWNqW2VgOV9daWxdZWNqKWEzNGExL2JdXV14YmVoYVtsXXBkOT82K0xua2NuXWlAXXBdK0RxanBuYW9vSF1eKypxbGBdcGEpYTM0YTEvYl1dXSpsdQ=="
CODEC_0893200a = "base64_literal|subtract_modulo_256|04"

def load_0893200a():
    return base64.b64decode(MATERIAL_0893200a)

def decode_0893200a(e):
    return bytes((value + 4) % 256 for value in e)

def recover_0893200a():
    n = (3, 5, 8, 13)[1:3]
    for _pass in range(1):
        d = decode_0893200a(load_0893200a())
    t = d.decode("ascii", "strict")
    return t

def inspect_0893200a():
    view = memoryview(recover_0893200a().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_0893200a():
    selected = "carrier"
    match selected:
        case "carrier":
            return ("match_case", "closure_cells", "py2exe_console", "regsvr32_predecessor")
        case _:
            return ()

def obfuscation_0893200a():
    value = "closure_cells"
    def recover():
        return value
    return recover()

def plan_0893200a():
    fields = dict(item.split("=", 1) for item in inspect_0893200a().split("|"))
    analysis_surface = surface_0893200a()
    obfuscation_surface = obfuscation_0893200a()
    operation_plan = ("interpreter_argv", ("python3", fields["file_path"]))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_0893200a())

# reconstruction complete