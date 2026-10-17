#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_a4931063 = "eXAuMDgwN2U1YjQwMS1ldGFkcHUuL2JhTHNzZXJ0bnVIL2F0YURtYXJnb3JQLzpDPWh0YXBfZWxpZnwwODA3ZTViNDAxL25vaHR5UHNzZXJ0bnVIPXRuZWdhX3Jlc3V8eXAuNzQwMDIzNjMvZGlsYXZuaS5lbHBtYXhlLjA4MDdlNWI0MDEvLzpzcHR0aD1scnV8MDgwN2U1YjQwMS1uZ2lhcG1hYz1kaV9uZ2lhcG1hY3xub2h0eXBfb3RfYXRoc209bmlhaGNfc3dvZG5pd3xlbGlmZW5vX3JlbGxhdHNuaXlwPXJlaXJyYWN8c3RuZW1nYXJmX2duaXJ0c2Y9bm9pdGFjc3VmYm98ZW5pbGVwaXBfcm90YXJlbmVnPXhhdG55c3wxPXRudW9jX2VnYXRzfGh0YXBfb3RfdG5laWxjX3B0dGg9cmV0cGFkYXxlbGlmX2V0aXJ3LGV0b21lcl9lcml1cWNhPXNwZXRzfDI9dg=="
CODEC_a4931063 = "base64_literal|reverse_bytes|"

def load_a4931063():
    return base64.b64decode(MATERIAL_a4931063)

def decode_a4931063(EnCoDeD_Bytes):
    return bytes(reversed(EnCoDeD_Bytes))

def recover_a4931063():
    NeUtRaL = 19 * 7 - 133
    StAtE = "decode"
    while StAtE != "done":
        if StAtE == "decode":
            DeCoDeD_Bytes = decode_a4931063(load_a4931063())
            StAtE = "done"
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_a4931063():
    stream = io.BytesIO(recover_a4931063().encode("ascii"))
    return stream.read().decode("ascii")

def surface_a4931063():
    stream = (item for item in ("generator_pipeline", "fstring_fragments", "pyinstaller_onefile", "mshta_to_python"))
    return tuple(stream)

def obfuscation_a4931063():
    left, right = "fstrin", "g_fragments"
    return f"{left}{right}"

def plan_a4931063():
    fields = dict(item.split("=", 1) for item in inspect_a4931063().split("|"))
    analysis_surface = surface_a4931063()
    obfuscation_surface = obfuscation_a4931063()
    operation_plan = ("http_client_to_path", fields["url"], fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_a4931063())
