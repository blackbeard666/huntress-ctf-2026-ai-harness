# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_aa8a7995 = "dj0yfHN0ZXBzPWRlY29kZV9jb25maWd1cmF0aW9uLGxvY2F0ZV9pbnRlcnByZXRlcixkaXNwYXRjaF9uZXh0X3N0YWdlfGFkYXB0ZXI9cHl0aG9uX3RvX3Bvd2Vyc2hlbGx8c3RhZ2VfY291bnQ9M3xzeW50YXg9bGFtYmRhX2Rpc3BhdGNofG9iZnVzY2F0aW9uPXJldmVyc2VkX2ZyYWdtZW50c3xjYXJyaWVyPXppcGFwcF9weXp8d2luZG93c19jaGFpbj1jbWRfdG9fcHl0aG9ufGNhbXBhaWduX2lkPWNhbXBhaWduLWY5NTE0MTAwZmN8ZmlsZV9wYXRoPUM6L1Byb2dyYW1EYXRhL0h1bnRyZXNzTGFiLy51cGRhdGUtZjk1MTQxMDBmYy5weXxuZXh0X3N0YWdlPXB5YzM4LXJlY292ZXJlZC5weQ=="
CODEC_aa8a7995 = "urlsafe_base64|identity|"

def load_aa8a7995():
    return base64.urlsafe_b64decode(MATERIAL_aa8a7995)

def decode_aa8a7995(stored_bytes):
    return bytes(stored_bytes)

def recover_aa8a7995():
    harmless_value = ":".join(("north", "south"))
    try:
        recovered_bytes = decode_aa8a7995(load_aa8a7995())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_aa8a7995():
    stream = io.BytesIO(recover_aa8a7995().encode("ascii"))
    return stream.read().decode("ascii")

def surface_aa8a7995():
    dispatch = lambda *items: tuple(items)
    return dispatch("lambda_dispatch", "reversed_fragments", "zipapp_pyz", "cmd_to_python")

def obfuscation_aa8a7995():
    return "stnemgarf_desrever"[::-1]

def plan_aa8a7995():
    fields = dict(item.split("=", 1) for item in inspect_aa8a7995().split("|"))
    analysis_surface = surface_aa8a7995()
    obfuscation_surface = obfuscation_aa8a7995()
    operation_plan = ("python_to_powershell", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_aa8a7995())

# reconstruction complete