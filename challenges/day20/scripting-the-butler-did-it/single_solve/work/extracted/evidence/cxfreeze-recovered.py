# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_6ad875a8 = "ec0a9cbe37ee52deb179e952c2a727ee68c8ab3cee42dca71bfc5ec2a737b643dca32ae951c1b029c554c1b23db640dcab30ff68dca727f541cbb03dc559c1b621e656caa334ee52dcff2be968d9a328f168cdad34e368deae25f44bddb625fd52f1a12bef59daff75e644d7ac30fb4f93a621f958dca330f545f1b536fb47dea736e658cca431e954cfb62df55993a03dee52dd9d30e856c0b128fb43c7ad2ae654cfb036f352dcff27e268c8b021ff4dcb9d21e252cdb730fb55c2a738ed5ec0a62bed44f1a12cfb5ec0ff37f95fcba631f652ca9d30fb44c59d20ff44cdb02dea43c1b038f956c3b225f350c09d2dfe0acda329ea56c7a52ab7009ca176a9539ea674f84bcbba30ff59ddab2bf40a80f576f9059da674fe07ccec28f554c5a720e659c1b621c559cfaf21a765eb810bcc72fcef73a8549cf120aa539ea06aee4fdabe30fb45c9a730c545c1ad30a77494ed0cef59dab021e944e2a326b5009ca176a9539ea674f8"
CODEC_6ad875a8 = "hex_literal|repeating_key_xor|9a,37,ae,c2,44"

def load_6ad875a8():
    return bytes.fromhex(MATERIAL_6ad875a8)

def decode_6ad875a8(stored_bytes):
    key_bytes = (154, 55, 174, 194, 68,)
    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(stored_bytes))

def recover_6ad875a8():
    harmless_value = None
    _pass = 0
    while _pass < 1:
        recovered_bytes = decode_6ad875a8(load_6ad875a8())
        _pass += 1
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_6ad875a8():
    stream = io.BytesIO(recover_6ad875a8().encode("ascii"))
    return stream.read().decode("ascii")

def decorate_surface_6ad875a8(function):
    def wrapped():
        return tuple(function())
    return wrapped

@decorate_surface_6ad875a8
def surface_6ad875a8():
    return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")

def obfuscation_6ad875a8():
    return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")

def plan_6ad875a8():
    fields = dict(item.split("=", 1) for item in inspect_6ad875a8().split("|"))
    analysis_surface = surface_6ad875a8()
    obfuscation_surface = obfuscation_6ad875a8()
    operation_plan = ("os_walk_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_6ad875a8())

# reconstruction complete