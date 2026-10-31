#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_cec77891 = "67:2e:23:6d:64:65:56:61:64:2e:5d:60:54:52:65:56:50:5d:60:54:52:5d:1d:55:5a:64:61:52:65:54:59:50:61:63:60:54:56:64:64:6d:52:55:52:61:65:56:63:2e:5a:5f:65:56:63:61:63:56:65:56:63:50:52:63:58:67:6d:64:65:52:58:56:50:54:60:66:5f:65:2e:22:6d:64:6a:5f:65:52:69:2e:54:5d:60:64:66:63:56:50:57:52:54:65:60:63:6a:6d:60:53:57:66:64:54:52:65:5a:60:5f:2e:54:59:63:50:5b:60:5a:5f:6d:54:52:63:63:5a:56:63:2e:59:52:64:59:50:53:52:64:56:55:50:61:6a:54:50:54:66:63:63:56:5f:65:6d:68:5a:5f:55:60:68:64:50:54:59:52:5a:5f:2e:61:6a:65:59:60:5f:68:50:59:5a:55:55:56:5f:50:54:60:5f:64:60:5d:56:6d:54:52:5e:61:52:5a:58:5f:50:5a:55:2e:54:52:5e:61:52:5a:58:5f:1e:23:56:53:57:53:2a:28:54:55:55:6d:57:5a:5d:56:50:61:52:65:59:2e:34:2b:20:41:63:60:58:63:52:5e:35:52:65:52:20:39:66:5f:65:63:56:64:64:3d:52:53:20:1f:66:61:55:52:65:56:1e:23:56:53:57:53:2a:28:54:55:55:1f:61:6a"
CODEC_cec77891 = "hex_colon|subtract_modulo_256|0f"

def load_cec77891():
    return bytes.fromhex(MATERIAL_cec77891.replace(":", " "))

def decode_cec77891(v_a19c):
    return bytes((value + 15) % 256 for value in v_a19c)

def recover_cec77891():
    v_d41a = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    try:
        v_b27e = decode_cec77891(load_cec77891())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_cec77891():
    view = memoryview(recover_cec77891().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_cec77891():
    values = ("closure_factory", "chr_join", "hash_based_pyc_current", "pythonw_hidden_console")
    def inner():
        return values
    return inner()

def obfuscation_cec77891():
    return "".join(chr(value) for value in (99, 104, 114, 95, 106, 111, 105, 110))

def plan_cec77891():
    fields = dict(item.split("=", 1) for item in inspect_cec77891().split("|"))
    analysis_surface = surface_cec77891()
    obfuscation_surface = obfuscation_cec77891()
    operation_plan = ("interpreter_argv", ("python3", fields["file_path"]))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_cec77891())
