# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_55f9ea97 = "M2JhMjYzZmQ0NC9iYUxzc2VydG51SC86Qz10b29yX3RlZ3JhdHx0eHQuM2JhMjYzZmQ0NC1SRVZPQ0VSPWVtYW5fZXRvbnxkZWtjb2wuM2JhMjYzZmQ0NC49bm9pc25ldHhlfDNiYTI2M2ZkNDQtbmdpYXBtYWM9ZGlfbmdpYXBtYWN8cm90cGlyY3NlZF9rc2F0X2RlbHVkZWhjcz1uaWFoY19zd29kbml3fGVsYmF0dWNleGVfZXplZXJmX3hjPXJlaXJyYWN8bm9pdGFsc25hcnRfc2V0eWI9bm9pdGFjc3VmYm98cmVwcGFyd19yb3Rhcm9jZWQ9eGF0bnlzfDE9dG51b2NfZWdhdHN8bmFscF95cG9jX2JpbGh0YXA9cmV0cGFkYXxldG9uX3lyZXZvY2VyX2V0aXJ3LHlwb2NfbXJvZnNuYXJ0LHNlbGlmX2VydXR4aWZfdGNlbGVzPXNwZXRzfDI9dg=="
CODEC_55f9ea97 = "base64_literal|reverse_bytes|"

def load_55f9ea97():
    return base64.b64decode(MATERIAL_55f9ea97)

def decode_55f9ea97(item1):
    return bytes(reversed(item1))

def recover_55f9ea97():
    item4 = 19 * 7 - 133
    try:
        item2 = decode_55f9ea97(load_55f9ea97())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    item3 = item2.decode("ascii", "strict")
    return item3

def inspect_55f9ea97():
    stream = io.BytesIO(recover_55f9ea97().encode("ascii"))
    return stream.read().decode("ascii")

def decorate_surface_55f9ea97(function):
    def wrapped():
        return tuple(function())
    return wrapped

@decorate_surface_55f9ea97
def surface_55f9ea97():
    return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")

def obfuscation_55f9ea97():
    return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")

def plan_55f9ea97():
    fields = dict(item.split("=", 1) for item in inspect_55f9ea97().split("|"))
    analysis_surface = surface_55f9ea97()
    obfuscation_surface = obfuscation_55f9ea97()
    operation_plan = ("pathlib_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_55f9ea97())

# reconstruction complete