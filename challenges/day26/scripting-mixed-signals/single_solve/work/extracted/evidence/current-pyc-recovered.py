# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_dbcc1f06 = "763d327c73746570733d6c6f636174655f6c6f63616c2c64697370617463685f70726f636573737c616461707465723d707974686f6e775f617267767c73746167655f636f756e743d317c73796e7461783d636c6f737572655f666163746f72797c6f62667573636174696f6e3d6368725f6a6f696e7c636172726965723d686173685f62617365645f7079635f63757272656e747c77696e646f77735f636861696e3d707974686f6e775f68696464656e5f636f6e736f6c657c63616d706169676e5f69643d63616d706169676e2d613061393632363062317c66696c655f706174683d433a2f50726f6772616d446174612f48756e74726573734c61622f2e7570646174652d613061393632363062312e7079"
CODEC_dbcc1f06 = "hex_literal|identity|"

def load_dbcc1f06():
    return bytes.fromhex(MATERIAL_dbcc1f06)

def decode_dbcc1f06(stored_bytes):
    return bytes(stored_bytes)

def recover_dbcc1f06():
    harmless_value = 19 * 7 - 133
    _pass = 0
    while _pass < 1:
        recovered_bytes = decode_dbcc1f06(load_dbcc1f06())
        _pass += 1
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_dbcc1f06():
    view = memoryview(recover_dbcc1f06().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_dbcc1f06():
    values = ("closure_factory", "chr_join", "hash_based_pyc_current", "pythonw_hidden_console")
    def inner():
        return values
    return inner()

def obfuscation_dbcc1f06():
    return "".join(chr(value) for value in (99, 104, 114, 95, 106, 111, 105, 110))

def plan_dbcc1f06():
    fields = dict(item.split("=", 1) for item in inspect_dbcc1f06().split("|"))
    analysis_surface = surface_dbcc1f06()
    obfuscation_surface = obfuscation_dbcc1f06()
    operation_plan = ("pythonw_argv", ("python3", fields["file_path"]))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_dbcc1f06())

# reconstruction complete