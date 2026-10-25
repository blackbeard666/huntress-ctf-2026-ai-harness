#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_c74c3bac = "gMvEioWCk4aFy4WTmpOVgqmQn46Cg4STqZCfmpOF2oKEl5iFkJmEm6mVmYaP2oGEn4KTqYSTlZmAk4SPqZiZgpOKl5KXhoKThMuFnoOCn5qplZmGj6mGmpeYioWCl5GTqZWZg5iCy8eKhY+YgpeOy5KTlZmEl4KZhKmBhJeGhpOEipmUkIOFlZeCn5mYy5SPgpOFqYKEl5iFmpeCn5mYipWXhISfk4TLlY6pkISTk4yTqZOOk5WDgpeUmpOKgZ+YkpmBhamVnpefmMuFlZ6TkoOak5KpgpeFnamSk4WVhJ+GgpmEipWXm4aXn5GYqZ+Sy5WXm4aXn5GY28PFxMKVx8OTlZWKk46Ck5iFn5mYy9jDxcTClcfDk5WV2JqZlZ2TkoqYmYKTqZiXm5PLpLO1uaCzpNvDxcTClcfDk5WV2IKOgoqCl4SRk4KphJmZgsu1zNm+g5iChJOFhbqXlNnDxcTClcfDk5WV"
CODEC_c74c3bac = "base64_literal|single_byte_xor|f6"

def load_c74c3bac():
    return base64.b64decode(MATERIAL_c74c3bac)

def decode_c74c3bac(item1):
    return bytes(value ^ 246 for value in item1)

def recover_c74c3bac():
    item4 = None
    item6 = decode_c74c3bac
    item2 = item6(load_c74c3bac())
    item3 = item2.decode("ascii", "strict")
    return item3

def inspect_c74c3bac():
    return recover_c74c3bac()

def decorate_surface_c74c3bac(function):
    def wrapped():
        return tuple(function())
    return wrapped

@decorate_surface_c74c3bac
def surface_c74c3bac():
    return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")

def obfuscation_c74c3bac():
    return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")

def plan_c74c3bac():
    fields = dict(item.split("=", 1) for item in inspect_c74c3bac().split("|"))
    analysis_surface = surface_c74c3bac()
    obfuscation_surface = obfuscation_c74c3bac()
    operation_plan = ("shutil_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_c74c3bac())
