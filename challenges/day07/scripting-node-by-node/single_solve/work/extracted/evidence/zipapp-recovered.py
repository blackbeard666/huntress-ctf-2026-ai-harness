# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_b2e203fa = "98,41,30,104,95,96,81,92,95,41,80,81,79,91,80,81,75,79,91,90,82,85,83,97,94,77,96,85,91,90,24,88,91,79,77,96,81,75,85,90,96,81,94,92,94,81,96,81,94,24,80,85,95,92,77,96,79,84,75,90,81,100,96,75,95,96,77,83,81,104,77,80,77,92,96,81,94,41,92,101,96,84,91,90,75,96,91,75,92,101,96,84,91,90,104,95,96,77,83,81,75,79,91,97,90,96,41,31,104,95,101,90,96,77,100,41,88,77,89,78,80,77,75,80,85,95,92,77,96,79,84,104,91,78,82,97,95,79,77,96,85,91,90,41,94,81,98,81,94,95,81,80,75,82,94,77,83,89,81,90,96,95,104,79,77,94,94,85,81,94,41,102,85,92,77,92,92,75,92,101,102,104,99,85,90,80,91,99,95,75,79,84,77,85,90,41,79,89,80,75,96,91,75,92,101,96,84,91,90,104,79,77,89,92,77,85,83,90,75,85,80,41,79,77,89,92,77,85,83,90,25,32,28,31,32,82,80,77,78,29,29,104,82,85,88,81,75,92,77,96,84,41,47,38,27,60,94,91,83,94,77,89,48,77,96,77,27,52,97,90,96,94,81,95,95,56,77,78,27,26,97,92,80,77,96,81,25,32,28,31,32,82,80,77,78,29,29,26,92,101,104,90,81,100,96,75,95,96,77,83,81,41,92,101,79,31,36,25,94,81,79,91,98,81,94,81,80,26,92,101"
CODEC_b2e203fa = "decimal_csv|subtract_modulo_256|14"

def load_b2e203fa():
    return bytes(int(item) for item in MATERIAL_b2e203fa.split(","))

def decode_b2e203fa(e):
    return bytes((value + 20) % 256 for value in e)

def recover_b2e203fa():
    n = None
    try:
        d = decode_b2e203fa(load_b2e203fa())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    t = d.decode("ascii", "strict")
    return t

def inspect_b2e203fa():
    view = memoryview(recover_b2e203fa().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_b2e203fa():
    dispatch = lambda *items: tuple(items)
    return dispatch("lambda_dispatch", "reversed_fragments", "zipapp_pyz", "cmd_to_python")

def obfuscation_b2e203fa():
    return "stnemgarf_desrever"[::-1]

def plan_b2e203fa():
    fields = dict(item.split("=", 1) for item in inspect_b2e203fa().split("|"))
    analysis_surface = surface_b2e203fa()
    obfuscation_surface = obfuscation_b2e203fa()
    operation_plan = ("python_to_python", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_b2e203fa())

# reconstruction complete