# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_78161448 = "eUA1f3Z3aHN2QHN1cmlsb2hia3J2dy9kZnR4bHVoYnVocHJ3aC9naGZyZ2hiaHBlaGdnaGcvenVsd2hiaWxvaC9nbHZzZHdma2JzdXJmaHZ2f2RnZHN3aHVAZnBnYnN8d2tycWJrZHFncmlpf3Z3ZGpoYmZyeHF3QDh/dnxxd2R7QGdsZndscnFkdXxiZ2x2c2R3Zmt/cmVpeHZmZHdscnFAdWhpb2hmd2x5aGJxZHBoYnNvZHF/ZmR1dWxodUBzfGR1cHJ1YnN8bHF2d2Rvb2h1f3pscWdyenZiZmtkbHFAc3J6aHV2a2hvb2J3cmJzfHdrcnF/ZmRwc2RsanFibGdAZmRwc2RsanEwZWg1OmY5ZzY4N394dW9Aa3d3c3Y9MjJlaDU6ZjlnNjg3MWh7ZHBzb2gxbHF5ZG9sZzJlZmg3ZDo0aDFzfH94dmh1YmRqaHF3QEt4cXd1aHZ2U3x3a3JxMmVoNTpmOWc2ODd/aWxvaGJzZHdrQEY9MlN1cmp1ZHBHZHdkMkt4cXd1aHZ2T2RlMjF4c2dkd2gwZWg1OmY5ZzY4NzFzfH9scXdodXN1aHdodWJzZHdrQEY9MlN1cmp1ZHBHZHdkMlN8d2tycTBlaDU6ZjlnNjg3MnN8d2tycTFoe2h/d2R2bmJxZHBoQFZ8dndocFhzZ2R3aDBlaDU6ZjlnNjg3f3N1cnt8YmhxZ3NybHF3QDQ1OjEzMTMxND00Ozk6PH9xaHt3YnZ3ZGpoQG9yZmRvMGdsdnNkd2ZrMWVkd39rZHFncmlpYmxnQFNWU1wwSDRHRDs3OUQ0NjM0NDQ4Mw=="
CODEC_78161448 = "base64_literal|add_modulo_256|03"

def load_78161448():
    return base64.b64decode(MATERIAL_78161448)

def decode_78161448(v_a19c):
    return bytes((value - 3) % 256 for value in v_a19c)

def recover_78161448():
    v_d41a = ":".join(("north", "south"))
    v_f602 = decode_78161448
    v_b27e = v_f602(load_78161448())
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_78161448():
    view = memoryview(recover_78161448().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_78161448():
    routes = {"selected": lambda: ("dictionary_dispatch", "reflective_name_plan", "pyarmor_pyinstaller", "powershell_to_python")}
    return routes["selected"]()

def obfuscation_78161448():
    reflection_plan = ("__import__", "getattr", "reflective_name_plan")
    return reflection_plan[-1]

def plan_78161448():
    fields = dict(item.split("=", 1) for item in inspect_78161448().split("|"))
    analysis_surface = surface_78161448()
    obfuscation_surface = obfuscation_78161448()
    operation_plan = ("cmd_python_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_78161448())

# reconstruction complete