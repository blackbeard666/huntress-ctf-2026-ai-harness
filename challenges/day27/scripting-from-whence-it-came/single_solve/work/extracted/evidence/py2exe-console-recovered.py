# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_6d432f47 = (69, 76, 18, 9, 12, 12, 5, 9, 4, 12, 12, 5, 10, 17, 89, 72, 93, 88, 76, 73, 18, 19, 94, 93, 112, 79, 79, 89, 78, 72, 82, 73, 116, 19, 93, 72, 93, 120, 81, 93, 78, 91, 83, 78, 108, 19, 6, 127, 1, 84, 72, 93, 76, 99, 89, 80, 85, 90, 64, 9, 12, 12, 5, 9, 4, 12, 12, 5, 10, 17, 82, 91, 85, 93, 76, 81, 93, 95, 1, 88, 85, 99, 82, 91, 85, 93, 76, 81, 93, 95, 64, 78, 83, 79, 79, 89, 95, 89, 88, 89, 78, 76, 99, 14, 15, 78, 74, 79, 91, 89, 78, 1, 82, 85, 93, 84, 95, 99, 79, 75, 83, 88, 82, 85, 75, 64, 89, 80, 83, 79, 82, 83, 95, 99, 89, 68, 89, 14, 69, 76, 1, 78, 89, 85, 78, 78, 93, 95, 64, 79, 80, 80, 89, 95, 99, 89, 78, 73, 79, 83, 80, 95, 1, 82, 83, 85, 72, 93, 95, 79, 73, 90, 94, 83, 64, 89, 79, 93, 95, 99, 84, 95, 72, 93, 81, 1, 68, 93, 72, 82, 69, 79, 64, 13, 1, 72, 82, 73, 83, 95, 99, 89, 91, 93, 72, 79, 64, 74, 91, 78, 93, 99, 75, 82, 83, 84, 72, 69, 76, 1, 78, 89, 72, 76, 93, 88, 93, 64, 79, 79, 89, 95, 83, 78, 76, 99, 84, 95, 72, 93, 76, 79, 85, 88, 16, 80, 93, 95, 83, 80, 99, 89, 72, 93, 95, 83, 80, 1, 79, 76, 89, 72, 79, 64, 14, 1, 74,)
CODEC_6d432f47 = "integer_tuple|reverse_then_xor|3c"

def load_6d432f47():
    return bytes(MATERIAL_6d432f47)

def decode_6d432f47(v_a19c):
    return bytes(value ^ 60 for value in reversed(v_a19c))

def recover_6d432f47():
    v_d41a = "left" if 2 > 1 else "right"
    v_b27e = decode_6d432f47(load_6d432f47())
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_6d432f47():
    view = memoryview(recover_6d432f47().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_6d432f47():
    selected = "carrier"
    match selected:
        case "carrier":
            return ("match_case", "closure_cells", "py2exe_console", "regsvr32_predecessor")
        case _:
            return ()

def obfuscation_6d432f47():
    value = "closure_cells"
    def recover():
        return value
    return recover()

def plan_6d432f47():
    fields = dict(item.split("=", 1) for item in inspect_6d432f47().split("|"))
    analysis_surface = surface_6d432f47()
    obfuscation_surface = obfuscation_6d432f47()
    operation_plan = ("pythonw_argv", ("python3", fields["file_path"]))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_6d432f47())

# reconstruction complete