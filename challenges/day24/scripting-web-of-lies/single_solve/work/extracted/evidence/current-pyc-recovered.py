#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_5a92e298 = "69:30:25:6f:66:67:58:63:66:30:5f:62:56:54:67:58:52:5f:62:56:54:5f:1f:57:5c:66:63:54:67:56:5b:52:63:65:62:56:58:66:66:6f:54:57:54:63:67:58:65:30:5c:61:67:58:65:63:65:58:67:58:65:52:54:65:5a:69:6f:66:67:54:5a:58:52:56:62:68:61:67:30:24:6f:66:6c:61:67:54:6b:30:56:5f:62:66:68:65:58:52:59:54:56:67:62:65:6c:6f:62:55:59:68:66:56:54:67:5c:62:61:30:56:5b:65:52:5d:62:5c:61:6f:56:54:65:65:5c:58:65:30:5b:54:66:5b:52:55:54:66:58:57:52:63:6c:56:52:56:68:65:65:58:61:67:6f:6a:5c:61:57:62:6a:66:52:56:5b:54:5c:61:30:63:6c:67:5b:62:61:6a:52:5b:5c:57:57:58:61:52:56:62:61:66:62:5f:58:6f:56:54:60:63:54:5c:5a:61:52:5c:57:30:56:54:60:63:54:5c:5a:61:20:26:2b:57:27:25:25:23:26:28:54:6f:59:5c:5f:58:52:63:54:67:5b:30:36:2d:22:43:65:62:5a:65:54:60:37:54:67:54:22:3b:68:61:67:65:58:66:66:3f:54:55:22:21:68:63:57:54:67:58:20:26:2b:57:27:25:25:23:26:28:54:21:63:6c"
CODEC_5a92e298 = "hex_colon|subtract_modulo_256|0d"

def load_5a92e298():
    return bytes.fromhex(MATERIAL_5a92e298.replace(":", " "))

def decode_5a92e298(stored_bytes):
    return bytes((value + 13) % 256 for value in stored_bytes)

def recover_5a92e298():
    harmless_value = 19 * 7 - 133
    _pass = 0
    while _pass < 1:
        recovered_bytes = decode_5a92e298(load_5a92e298())
        _pass += 1
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_5a92e298():
    view = memoryview(recover_5a92e298().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_5a92e298():
    values = ("closure_factory", "chr_join", "hash_based_pyc_current", "pythonw_hidden_console")
    def inner():
        return values
    return inner()

def obfuscation_5a92e298():
    return "".join(chr(value) for value in (99, 104, 114, 95, 106, 111, 105, 110))

def plan_5a92e298():
    fields = dict(item.split("=", 1) for item in inspect_5a92e298().split("|"))
    analysis_surface = surface_5a92e298()
    obfuscation_surface = obfuscation_5a92e298()
    operation_plan = ("interpreter_argv", ("python3", fields["file_path"]))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_5a92e298())
