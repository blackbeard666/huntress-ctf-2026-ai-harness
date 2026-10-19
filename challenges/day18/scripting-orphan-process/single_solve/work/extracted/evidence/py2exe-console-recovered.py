# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_739eb8f0 = ("PjhNiuY8YA+FqCRqHJfhLVoTmfYpaVOS/Dt1HoL2IFoPhPorYAyF6SlhHobhLXdCn/s8YA2G5y1xGoTKKXcYgOk7cR6"
    "R8BdmEIP7PDhOiuYxawuX7XVoHoL2IFocl+YteRCU8z12HJfhIWoRy/YkagyD5y1aHJP5JHYDlfQ6dxaT53V1BsTwMG"
    "AglfomdhCa8DRyFpjxJ3IMqfYgZBaYqDpgGIXjOjZNqeU6YBuT9i12DJnnNGYem+UpbBiYyiFhQpX0JXUen/ImKEaQ9"
    "H8xR8WgfTwDkPwkYCCG9DxtQrWvZ1UNmfI6ZBKy9DxkUL7gJnENk+Y7SR6UumZwD5L0PGBSz/MpMkvOpn0wRtjlMQ==")
CODEC_739eb8f0 = "base64_chunks|repeating_key_xor|48,05,7f,f6,95"

def load_739eb8f0():
    return base64.b64decode(MATERIAL_739eb8f0)

def decode_739eb8f0(EnCoDeD_Bytes):
    key_bytes = (72, 5, 127, 246, 149,)
    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(EnCoDeD_Bytes))

def recover_739eb8f0():
    NeUtRaL = "left" if 2 > 1 else "right"
    DeCoDeD_Bytes = decode_739eb8f0(load_739eb8f0())
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_739eb8f0():
    return recover_739eb8f0()

def surface_739eb8f0():
    selected = "carrier"
    match selected:
        case "carrier":
            return ("match_case", "closure_cells", "py2exe_console", "regsvr32_predecessor")
        case _:
            return ()

def obfuscation_739eb8f0():
    value = "closure_cells"
    def recover():
        return value
    return recover()

def plan_739eb8f0():
    fields = dict(item.split("=", 1) for item in inspect_739eb8f0().split("|"))
    analysis_surface = surface_739eb8f0()
    obfuscation_surface = obfuscation_739eb8f0()
    operation_plan = ("interpreter_argv", ("python3", fields["file_path"]))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_739eb8f0())

# reconstruction complete