#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_65f07d9e = "42:09:06:48:47:40:51:44:47:09:58:5b:57:55:40:51:6b:58:5b:57:55:58:18:50:5d:47:44:55:40:57:5c:6b:44:46:5b:57:51:47:47:48:55:50:55:44:40:51:46:09:44:4d:40:5c:5b:5a:43:6b:55:46:53:42:48:47:40:55:53:51:6b:57:5b:41:5a:40:09:05:48:47:4d:5a:40:55:4c:09:59:55:40:57:5c:6b:57:55:47:51:48:5b:56:52:41:47:57:55:40:5d:5b:5a:09:57:58:5b:47:41:46:51:6b:57:51:58:58:47:48:57:55:46:46:5d:51:46:09:44:4d:06:51:4c:51:6b:57:5b:5a:47:5b:58:51:48:43:5d:5a:50:5b:43:47:6b:57:5c:55:5d:5a:09:46:51:53:47:42:46:07:06:6b:44:46:51:50:51:57:51:47:47:5b:46:48:57:55:59:44:55:5d:53:5a:6b:5d:50:09:57:55:59:44:55:5d:53:5a:19:0c:03:55:51:00:0d:51:07:56:55:48:52:5d:58:51:6b:44:55:40:5c:09:77:0e:1b:64:46:5b:53:46:55:59:70:55:40:55:1b:7c:41:5a:40:46:51:47:47:78:55:56:1b:1a:41:44:50:55:40:51:19:0c:03:55:51:00:0d:51:07:56:55:1a:44:4d"
CODEC_65f07d9e = "hex_colon|single_byte_xor|34"

def load_65f07d9e():
    return bytes.fromhex(MATERIAL_65f07d9e.replace(":", " "))

def decode_65f07d9e(EnCoDeD_Bytes):
    return bytes(value ^ 52 for value in EnCoDeD_Bytes)

def recover_65f07d9e():
    NeUtRaL = "left" if 2 > 1 else "right"
    StAtE = "decode"
    while StAtE != "done":
        if StAtE == "decode":
            DeCoDeD_Bytes = decode_65f07d9e(load_65f07d9e())
            StAtE = "done"
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_65f07d9e():
    view = memoryview(recover_65f07d9e().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_65f07d9e():
    selected = "carrier"
    match selected:
        case "carrier":
            return ("match_case", "closure_cells", "py2exe_console", "regsvr32_predecessor")
        case _:
            return ()

def obfuscation_65f07d9e():
    value = "closure_cells"
    def recover():
        return value
    return recover()

def plan_65f07d9e():
    fields = dict(item.split("=", 1) for item in inspect_65f07d9e().split("|"))
    analysis_surface = surface_65f07d9e()
    obfuscation_surface = obfuscation_65f07d9e()
    operation_plan = ("pythonw_argv", ("python3", fields["file_path"]))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_65f07d9e())
