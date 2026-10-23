# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_9ac01a91 = "82493e887f80717c7f49787b6f6d80716b787b6f6d783870757f7c6d806f746b7c7e7b6f717f7f886d706d7c80717e497f816e7c7e7b6f717f7f6b78757f80887f806d73716b6f7b817a80493d887f857a806d84496f787b7f817e716b726d6f807b7e85887b6e72817f6f6d80757b7a496f747e6b767b757a886f6d7e7e75717e49746d7f746b6e6d7f71706b7c856f6b6f817e7e717a808883757a707b837f6b6f746d757a497c8580747b7a836b74757070717a6b6f7b7a7f7b7871886f6d797c6d75737a6b7570496f6d797c6d75737a393e42724542414542456e88727578716b7c6d8074494f463b5c7e7b737e6d79506d806d3b54817a807e717f7f586d6e3b3a817c706d8071393e42724542414542456e3a7c85"
CODEC_9ac01a91 = "hex_literal|add_modulo_256|0c"

def load_9ac01a91():
    return bytes.fromhex(MATERIAL_9ac01a91)

def decode_9ac01a91(v_a19c):
    return bytes((value - 12) % 256 for value in v_a19c)

def recover_9ac01a91():
    v_d41a = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    v_a702 = "decode"
    while v_a702 != "done":
        if v_a702 == "decode":
            v_b27e = decode_9ac01a91(load_9ac01a91())
            v_a702 = "done"
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_9ac01a91():
    view = memoryview(recover_9ac01a91().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_9ac01a91():
    values = ("closure_factory", "chr_join", "hash_based_pyc_current", "pythonw_hidden_console")
    def inner():
        return values
    return inner()

def obfuscation_9ac01a91():
    return "".join(chr(value) for value in (99, 104, 114, 95, 106, 111, 105, 110))

def plan_9ac01a91():
    fields = dict(item.split("=", 1) for item in inspect_9ac01a91().split("|"))
    analysis_surface = surface_9ac01a91()
    obfuscation_surface = obfuscation_9ac01a91()
    operation_plan = ("subprocess_list", ("python3", fields["file_path"]))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_9ac01a91())

# reconstruction complete