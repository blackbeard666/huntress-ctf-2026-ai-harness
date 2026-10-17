# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_7b7ab488 = "72392e786f70616c6f39686b5f5d70615b686b5f5d682860656f6c5d705f645b6c6e6b5f616f6f785d605d6c70616e39656a70616e6c6e6170616e5b5d6e6372786f705d63615b5f6b716a70392d786f756a705d7439695d705f645b5f5d6f61786b5e62716f5f5d70656b6a395f686b6f716e615b5f6168686f785f5d6e6e65616e396c752e6174615b5f6b6a6f6b68617873656a606b736f5b5f645d656a396e61636f726e2f2e5b6c6e6160615f616f6f6b6e785f5d696c5d65636a5b6560395f5d696c5d65636a295e2f2e2e5e5e6261613378626568615b6c5d7064393f362b4c6e6b636e5d69405d705d2b44716a706e616f6f485d5e2b2a716c605d7061295e2f2e2e5e5e626161332a6c75"
CODEC_7b7ab488 = "hex_literal|subtract_modulo_256|04"

def load_7b7ab488():
    return bytes.fromhex(MATERIAL_7b7ab488)

def decode_7b7ab488(item1):
    return bytes((value + 4) % 256 for value in item1)

def recover_7b7ab488():
    item4 = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    _pass = 0
    while _pass < 1:
        item2 = decode_7b7ab488(load_7b7ab488())
        _pass += 1
    item3 = item2.decode("ascii", "strict")
    return item3

def inspect_7b7ab488():
    view = memoryview(recover_7b7ab488().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_7b7ab488():
    selected = "carrier"
    match selected:
        case "carrier":
            return ("match_case", "closure_cells", "py2exe_console", "regsvr32_predecessor")
        case _:
            return ()

def obfuscation_7b7ab488():
    value = "closure_cells"
    def recover():
        return value
    return recover()

def plan_7b7ab488():
    fields = dict(item.split("=", 1) for item in inspect_7b7ab488().split("|"))
    analysis_surface = surface_7b7ab488()
    obfuscation_surface = obfuscation_7b7ab488()
    operation_plan = ("interpreter_argv", ("python3", fields["file_path"]))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_7b7ab488())

# reconstruction complete