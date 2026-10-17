# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_a75fb070 = "dj0yfHN0ZXBzPXByb2ZpbGVfaG9zdCxhY3F1aXJlX3JlbW90ZSxkZWNvZGVfZW1iZWRkZWQsd3JpdGVfZmlsZSxkaXNwYXRjaF9wcm9jZXNzfGFkYXB0ZXI9cHJveHlfY2xpZW50X2hhbmRvZmZ8c3RhZ2VfY291bnQ9NXxzeW50YXg9d2FscnVzX2JpbmRpbmd8b2JmdXNjYXRpb249ZXhjZXB0aW9uX3JvdXRpbmd8Y2Fycmllcj1weTJleGVfd2luZG93c19zZXJ2aWNlfHdpbmRvd3NfY2hhaW49c2VydmljZV9kZXNjcmlwdG9yfGNhbXBhaWduX2lkPWNhbXBhaWduLWEzNDFmMjAyNTR8dXJsPWh0dHBzOi8vYTM0MWYyMDI1NC5leGFtcGxlLmludmFsaWQvMzNkMmNmODIucHl8dXNlcl9hZ2VudD1IdW50cmVzc1B5dGhvbi9hMzQxZjIwMjU0fGZpbGVfcGF0aD1DOi9Qcm9ncmFtRGF0YS9IdW50cmVzc0xhYi8udXBkYXRlLWEzNDFmMjAyNTQucHl8aW50ZXJwcmV0ZXJfcGF0aD1DOi9Qcm9ncmFtRGF0YS9QeXRob24tYTM0MWYyMDI1NC9weXRob24uZXhlfHRhc2tfbmFtZT1TeXN0ZW1VcGRhdGUtYTM0MWYyMDI1NHxwcm94eV9lbmRwb2ludD0xMjcuMC4wLjE6MTE3OTN8bmV4dF9zdGFnZT1yZXNvdXJjZS1zYW1wbGUucHMx"
CODEC_a75fb070 = "base64_literal|identity|"

def load_a75fb070():
    return base64.b64decode(MATERIAL_a75fb070)

def decode_a75fb070(e):
    return bytes(e)

def recover_a75fb070():
    n = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    for _pass in range(1):
        d = decode_a75fb070(load_a75fb070())
    t = d.decode("ascii", "strict")
    return t

def inspect_a75fb070():
    view = memoryview(recover_a75fb070().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_a75fb070():
    return surface if (surface := ("walrus_binding", "exception_routing", "py2exe_windows_service", "service_descriptor")) else ()

def obfuscation_a75fb070():
    try:
        {}["missing"]
    except KeyError:
        return "exception_routing"

def plan_a75fb070():
    fields = dict(item.split("=", 1) for item in inspect_a75fb070().split("|"))
    analysis_surface = surface_a75fb070()
    obfuscation_surface = obfuscation_a75fb070()
    operation_plan = ("proxy_client_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_a75fb070())

# reconstruction complete