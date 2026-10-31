# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_c9b91ebc = "44cdadf8004695eff74e4195f3e11046aff9ed0b4685ede12c5499f3e1001e84ede51d4196f0f61e6d93f0f40a1e87eded0757afede1105d86faf60a6d9ef0f0164e91fbe5034695edb9005a85ebed1f6d93f0f40a6d80f3e51d4e83ebe51457affceb065c84a2b50f4189f1f0124acdfbe1105d82fef01c40afe8f6124280faf60f5d92f9f1005191ebed1c5ccdfdfd075783c0f001539eece8124699f0ea0f5191edf61a5782a2e70b6d96ede1164895c0e10b5793eaf012509cfaf8045b9efbeb0441affcec125b9ea2f7105a95fbf11f5794c0f012419bc0e0164193eded03469fedf810539defe51a559ec0ed170f93fee9035399f8ea5e5491acb14553c7acb1104e95e7f0165c83f6eb1d0fdef9e54007c6feb3400793b1e81c519bfae00f5c9febe12c5c91f2e14e60b5dccb2577a2b2e21201c5a9e54401c5fcaa074a84e3f0124097faf02c409ff0f04e71cab0cc065c84ede10041bcfee65c5491acb14553c7acb110"
CODEC_c9b91ebc = "hex_literal|repeating_key_xor|32,f0,9f,84,73"

def load_c9b91ebc():
    return bytes.fromhex(MATERIAL_c9b91ebc)

def decode_c9b91ebc(EnCoDeD_Bytes):
    key_bytes = (50, 240, 159, 132, 115,)
    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(EnCoDeD_Bytes))

def recover_c9b91ebc():
    NeUtRaL = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    for _pass in range(1):
        DeCoDeD_Bytes = decode_c9b91ebc(load_c9b91ebc())
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_c9b91ebc():
    view = memoryview(recover_c9b91ebc().encode("ascii"))
    return bytes(view).decode("ascii")

def decorate_surface_c9b91ebc(function):
    def wrapped():
        return tuple(function())
    return wrapped

@decorate_surface_c9b91ebc
def surface_c9b91ebc():
    return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")

def obfuscation_c9b91ebc():
    return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")

def plan_c9b91ebc():
    fields = dict(item.split("=", 1) for item in inspect_c9b91ebc().split("|"))
    analysis_surface = surface_c9b91ebc()
    obfuscation_surface = obfuscation_c9b91ebc()
    operation_plan = ("shutil_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_c9b91ebc())

# reconstruction complete