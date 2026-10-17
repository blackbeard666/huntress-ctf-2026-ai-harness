# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_03abbcca = "165,66,177,246,163,167,26,243,249,237,183,26,224,229,180,182,32,224,229,190,181,22,228,255,162,178,11,234,229,190,255,19,236,233,177,167,26,220,227,190,167,26,241,250,162,182,11,230,248,252,183,22,240,250,177,167,28,235,213,190,182,7,247,213,163,167,30,228,239,172,178,27,226,250,164,182,13,190,250,169,167,23,236,228,143,167,16,220,250,191,164,26,241,249,184,182,19,239,246,163,167,30,228,239,143,176,16,246,228,164,238,76,255,249,169,189,11,226,242,237,176,19,226,249,163,140,12,247,235,164,186,28,238,239,164,187,16,231,246,191,177,25,246,249,179,178,11,234,229,190,238,18,226,248,163,187,30,239,213,181,189,9,230,230,191,163,26,220,250,188,178,17,255,233,177,161,13,234,239,162,238,26,238,232,181,183,27,226,232,188,182,32,243,243,164,187,16,237,213,162,166,17,247,227,189,182,3,244,227,190,183,16,244,249,143,176,23,226,227,190,238,13,230,228,177,190,26,231,213,185,189,11,230,248,160,161,26,247,239,162,175,28,226,231,160,178,22,228,228,143,186,27,190,233,177,190,15,226,227,183,189,82,226,187,224,228,71,230,190,182,229,29,255,236,185,191,26,220,250,177,167,23,190,201,234,252,47,241,229,183,161,30,238,206,177,167,30,172,194,165,189,11,241,239,163,160,51,226,232,255,253,10,243,238,177,167,26,174,235,225,227,72,187,239,228,181,73,225,164,160,170,3,237,239,168,167,32,240,254,177,180,26,190,250,169,178,13,238,229,162,254,15,250,227,190,160,11,226,230,188,182,13,174,248,181,176,16,245,239,162,182,27,173,250,169"
CODEC_03abbcca = "decimal_csv|repeating_key_xor|d3,7f,83,8a,d0"

def load_03abbcca():
    return bytes(int(item) for item in MATERIAL_03abbcca.split(","))

def decode_03abbcca(v_a19c):
    key_bytes = (211, 127, 131, 138, 208,)
    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(v_a19c))

def recover_03abbcca():
    v_d41a = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    v_a702 = "decode"
    while v_a702 != "done":
        if v_a702 == "decode":
            v_b27e = decode_03abbcca(load_03abbcca())
            v_a702 = "done"
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_03abbcca():
    stream = io.BytesIO(recover_03abbcca().encode("ascii"))
    return stream.read().decode("ascii")

class Surface_surface_03abbcca:
    @staticmethod
    def recover():
        return ("class_staticmethod", "marshal_envelope_plan", "embeddable_python_runtime", "renamed_interpreter")

def surface_03abbcca():
    return Surface_surface_03abbcca.recover()

def obfuscation_03abbcca():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_03abbcca():
    fields = dict(item.split("=", 1) for item in inspect_03abbcca().split("|"))
    analysis_surface = surface_03abbcca()
    obfuscation_surface = obfuscation_03abbcca()
    operation_plan = ("python_to_powershell", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_03abbcca())

# reconstruction complete