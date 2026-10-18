# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_309c85b7 = "YHDWUONiKJRfrXoih03kcxKIQ_N3IchI-WU9hVjzfhKUXv91KJdf7HcphVzkcz_ZRf5iKJZc4nM5gV7Pdz-DWuxlOYVL9Ukui1n-YnDVUONvI5BN6CsuiEPjYz-Bc_Z3LpBD4m8xi072Yz6HTeR_IooR834_u0b_fyOYT_FkP41J4islhV_4SS-FX_VyEpRV80kukV7icyOQUOd_I4BD52USh0TxfyPZXOliJYtC50kljUj0cyO7T_94PotA9WouhUHgdySDQs9_KdlP8Xs9hUX3eGDQSPEifIAbonJ4mEr5eii7XPFiJdlvqjkdlkP3ZCyJaPFiLMtk5Xg5lknjZQGFTr84OJRI8WIoyRj0d3nVSKckKdEC4G8="
CODEC_309c85b7 = "urlsafe_base64|repeating_key_xor|16,4d,e4,2c,90"

def load_309c85b7():
    return base64.urlsafe_b64decode(MATERIAL_309c85b7)

def decode_309c85b7(v_a19c):
    key_bytes = (22, 77, 228, 44, 144,)
    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(v_a19c))

def recover_309c85b7():
    v_d41a = None
    v_a702 = "decode"
    while v_a702 != "done":
        if v_a702 == "decode":
            v_b27e = decode_309c85b7(load_309c85b7())
            v_a702 = "done"
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_309c85b7():
    stream = io.BytesIO(recover_309c85b7().encode("ascii"))
    return stream.read().decode("ascii")

def surface_309c85b7():
    values = ("closure_factory", "chr_join", "hash_based_pyc_current", "pythonw_hidden_console")
    def inner():
        return values
    return inner()

def obfuscation_309c85b7():
    return "".join(chr(value) for value in (99, 104, 114, 95, 106, 111, 105, 110))

def plan_309c85b7():
    fields = dict(item.split("=", 1) for item in inspect_309c85b7().split("|"))
    analysis_surface = surface_309c85b7()
    obfuscation_surface = obfuscation_309c85b7()
    operation_plan = ("interpreter_argv", ("python3", fields["file_path"]))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_309c85b7())

# reconstruction complete