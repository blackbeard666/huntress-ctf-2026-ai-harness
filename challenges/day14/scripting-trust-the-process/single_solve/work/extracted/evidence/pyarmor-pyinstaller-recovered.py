# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_71409347 = "dj0yfHN0ZXBzPXByb2ZpbGVfaG9zdCxhY3F1aXJlX3JlbW90ZSxkZWNvZGVfZW1iZWRkZWQsd3JpdGVfZmlsZSxkaXNwYXRjaF9wcm9jZXNzfGFkYXB0ZXI9cG93ZXJzaGVsbF9weXRob25faGFuZG9mZnxzdGFnZV9jb3VudD01fHN5bnRheD1kaWN0aW9uYXJ5X2Rpc3BhdGNofG9iZnVzY2F0aW9uPXJlZmxlY3RpdmVfbmFtZV9wbGFufGNhcnJpZXI9cHlhcm1vcl9weWluc3RhbGxlcnx3aW5kb3dzX2NoYWluPXBvd2Vyc2hlbGxfdG9fcHl0aG9ufGNhbXBhaWduX2lkPWNhbXBhaWduLWY3MmI3MDA1ZTZ8dXJsPWh0dHBzOi8vZjcyYjcwMDVlNi5leGFtcGxlLmludmFsaWQvZTNmYmI4NzkucHl8dXNlcl9hZ2VudD1IdW50cmVzc1B5dGhvbi9mNzJiNzAwNWU2fGZpbGVfcGF0aD1DOi9Qcm9ncmFtRGF0YS9IdW50cmVzc0xhYi8udXBkYXRlLWY3MmI3MDA1ZTYucHl8aW50ZXJwcmV0ZXJfcGF0aD1DOi9Qcm9ncmFtRGF0YS9QeXRob24tZjcyYjcwMDVlNi9weXRob24uZXhlfHRhc2tfbmFtZT1TeXN0ZW1VcGRhdGUtZjcyYjcwMDVlNnxwcm94eV9lbmRwb2ludD0xMjcuMC4wLjE6MzMyNzV8bmV4dF9zdGFnZT1sb2NhbC1kaXNwYXRjaC5iYXR8aGFuZG9mZl9pZD1QU1BZLTcyN0Y2NUQ3Qzc4MTc0MTI="
CODEC_71409347 = "urlsafe_base64|identity|"

def load_71409347():
    return base64.urlsafe_b64decode(MATERIAL_71409347)

def decode_71409347(stored_bytes):
    return bytes(stored_bytes)

def recover_71409347():
    harmless_value = None
    decoder_function = decode_71409347
    recovered_bytes = decoder_function(load_71409347())
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_71409347():
    view = memoryview(recover_71409347().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_71409347():
    routes = {"selected": lambda: ("dictionary_dispatch", "reflective_name_plan", "pyarmor_pyinstaller", "powershell_to_python")}
    return routes["selected"]()

def obfuscation_71409347():
    reflection_plan = ("__import__", "getattr", "reflective_name_plan")
    return reflection_plan[-1]

def plan_71409347():
    fields = dict(item.split("=", 1) for item in inspect_71409347().split("|"))
    analysis_surface = surface_71409347()
    obfuscation_surface = obfuscation_71409347()
    operation_plan = ("powershell_python_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_71409347())

# reconstruction complete