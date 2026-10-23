# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_d6c6f979 = "dj0yfHN0ZXBzPXByb2ZpbGVfaG9zdCxhY3F1aXJlX3JlbW90ZSxkZWNvZGVfZW1iZWRkZWQsd3JpdGVfZmlsZSxkaXNwYXRjaF9wcm9jZXNzfGFkYXB0ZXI9cG93ZXJzaGVsbF9weXRob25faGFuZG9mZnxzdGFnZV9jb3VudD01fHN5bnRheD13YWxydXNfYmluZGluZ3xvYmZ1c2NhdGlvbj1leGNlcHRpb25fcm91dGluZ3xjYXJyaWVyPXB5MmV4ZV93aW5kb3dzX3NlcnZpY2V8d2luZG93c19jaGFpbj1zZXJ2aWNlX2Rlc2NyaXB0b3J8Y2FtcGFpZ25faWQ9Y2FtcGFpZ24tMDc1NjE0MDdhYXx1cmw9aHR0cHM6Ly8wNzU2MTQwN2FhLmV4YW1wbGUuaW52YWxpZC9kY2ZkNTgxMS5weXx1c2VyX2FnZW50PUh1bnRyZXNzUHl0aG9uLzA3NTYxNDA3YWF8ZmlsZV9wYXRoPUM6L1Byb2dyYW1EYXRhL0h1bnRyZXNzTGFiLy51cGRhdGUtMDc1NjE0MDdhYS5weXxpbnRlcnByZXRlcl9wYXRoPUM6L1Byb2dyYW1EYXRhL1B5dGhvbi0wNzU2MTQwN2FhL3B5dGhvbi5leGV8dGFza19uYW1lPVN5c3RlbVVwZGF0ZS0wNzU2MTQwN2FhfHByb3h5X2VuZHBvaW50PTEyNy4wLjAuMToxMTg3OHxuZXh0X3N0YWdlPXJlc291cmNlLXNhbXBsZS5wczE="
CODEC_d6c6f979 = "urlsafe_base64|identity|"

def load_d6c6f979():
    return base64.urlsafe_b64decode(MATERIAL_d6c6f979)

def decode_d6c6f979(EnCoDeD_Bytes):
    return bytes(EnCoDeD_Bytes)

def recover_d6c6f979():
    NeUtRaL = ":".join(("north", "south"))
    DeCoDe_Target = decode_d6c6f979
    DeCoDeD_Bytes = DeCoDe_Target(load_d6c6f979())
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_d6c6f979():
    return recover_d6c6f979()

def surface_d6c6f979():
    return surface if (surface := ("walrus_binding", "exception_routing", "py2exe_windows_service", "service_descriptor")) else ()

def obfuscation_d6c6f979():
    try:
        {}["missing"]
    except KeyError:
        return "exception_routing"

def plan_d6c6f979():
    fields = dict(item.split("=", 1) for item in inspect_d6c6f979().split("|"))
    analysis_surface = surface_d6c6f979()
    obfuscation_surface = obfuscation_d6c6f979()
    operation_plan = ("powershell_python_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_d6c6f979())

# reconstruction complete