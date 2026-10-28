# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_786f40c6 = "763d327c73746570733d6465636f64655f656d6265646465642c77726974655f66696c657c616461707465723d696d706f72746c69625f7265736f757263655f77726974657c73746167655f636f756e743d317c73796e7461783d6974657261746f725f70726f746f636f6c7c6f62667573636174696f6e3d7265666c6563746976655f6e616d655f706c616e7c636172726965723d63785f667265657a655f6d73697c77696e646f77735f636861696e3d72756e5f6b65795f64657363726970746f727c63616d706169676e5f69643d63616d706169676e2d303132356234643738637c66696c655f706174683d433a2f50726f6772616d446174612f48756e74726573734c61622f2e7570646174652d303132356234643738632e7079"
CODEC_786f40c6 = "hex_literal|identity|"

def load_786f40c6():
    return bytes.fromhex(MATERIAL_786f40c6)

def decode_786f40c6(EnCoDeD_Bytes):
    return bytes(EnCoDeD_Bytes)

def recover_786f40c6():
    NeUtRaL = (3, 5, 8, 13)[1:3]
    try:
        DeCoDeD_Bytes = decode_786f40c6(load_786f40c6())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_786f40c6():
    return recover_786f40c6()

def surface_786f40c6():
    iterator = iter(("iterator_protocol", "reflective_name_plan", "cx_freeze_msi", "run_key_descriptor"))
    return tuple(iterator)

def obfuscation_786f40c6():
    reflection_plan = ("__import__", "getattr", "reflective_name_plan")
    return reflection_plan[-1]

def plan_786f40c6():
    fields = dict(item.split("=", 1) for item in inspect_786f40c6().split("|"))
    analysis_surface = surface_786f40c6()
    obfuscation_surface = obfuscation_786f40c6()
    operation_plan = ("importlib_resource_write", "decode", fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_786f40c6())

# reconstruction complete