# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_4decfd17 = ("k1pPmZCRgo2QWoGCgIyBgnyCin+CgYGCgUmUj4aRgnyDhomCmX6Bfo2Rgo9akYKKjYOGiYJ8j4KNiX6AgpmQkX6EgnyAj"
    "JKLkVpOmZCWi5F+lVqGkYKPfpGMj3yNj4yRjICMiZmMf4OSkIB+kYaMi1qPgoOJgoCRhpOCfIt+ioJ8jYl+i5mAfo+Pho"
    "KPWoCVfIOPgoKXgnyKkIaZlIaLgYyUkHyAhX6Gi1qPkot8iIKWfIGCkICPho2RjI+ZgH6KjX6GhIt8hoFagH6KjX6GhIt"
    "KVlNPVoFRgoKAU5mDhomCfI1+kYVaYFdMbY+MhI9+imF+kX5MZZKLkY+CkJBpfn9MS5KNgX6RgkpWU09WgVGCgoBTS42W")
CODEC_4decfd17 = "base64_chunks|add_modulo_256|1d"

def load_4decfd17():
    return base64.b64decode(MATERIAL_4decfd17)

def decode_4decfd17(v_a19c):
    return bytes((value - 29) % 256 for value in v_a19c)

def recover_4decfd17():
    v_d41a = "left" if 2 > 1 else "right"
    v_b27e = decode_4decfd17(load_4decfd17())
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_4decfd17():
    return recover_4decfd17()

def surface_4decfd17():
    iterator = iter(("iterator_protocol", "reflective_name_plan", "cx_freeze_msi", "run_key_descriptor"))
    return tuple(iterator)

def obfuscation_4decfd17():
    reflection_plan = ("__import__", "getattr", "reflective_name_plan")
    return reflection_plan[-1]

def plan_4decfd17():
    fields = dict(item.split("=", 1) for item in inspect_4decfd17().split("|"))
    analysis_surface = surface_4decfd17()
    obfuscation_surface = obfuscation_4decfd17()
    operation_plan = ("tempfile_replace", "decode", fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_4decfd17())

# reconstruction complete