#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_734ce4de = ("bjUqdGtsXWhrNWRnW1lsXVdkZ1tZZCRcYWtoWWxbYFdoamdbXWtrdFlcWWhsXWo1am1maHFXXF1rW2phaGxnanRrbFlfXV"
    "dbZ21mbDUpdGtxZmxZcDVbZGdrbWpdV15ZW2xnanF0Z1pebWtbWWxhZ2Y1W2BqV2JnYWZ0W1lqamFdajVgWWtgV1pZa11c"
    "V2hxW1dbbWpqXWZsdG9hZlxnb2tXW2BZYWY1aHFsYGdmb1dgYVxcXWZXW2dma2dkXXRbWWVoWWFfZldhXDVbWWVoWWFfZi"
    "UxL14wWitZXTEudF5hZF1XaFlsYDU7MidIamdfalllPFlsWSdAbWZsal1ra0RZWicmbWhcWWxdJTEvXjBaK1ldMS4maHE=")
CODEC_734ce4de = "base64_chunks|subtract_modulo_256|08"

def load_734ce4de():
    return base64.b64decode(MATERIAL_734ce4de)

def decode_734ce4de(EnCoDeD_Bytes):
    return bytes((value + 8) % 256 for value in EnCoDeD_Bytes)

def recover_734ce4de():
    NeUtRaL = None
    DeCoDe_Target = decode_734ce4de
    DeCoDeD_Bytes = DeCoDe_Target(load_734ce4de())
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_734ce4de():
    return recover_734ce4de()

def surface_734ce4de():
    values = ("closure_factory", "chr_join", "hash_based_pyc_current", "pythonw_hidden_console")
    def inner():
        return values
    return inner()

def obfuscation_734ce4de():
    return "".join(chr(value) for value in (99, 104, 114, 95, 106, 111, 105, 110))

def plan_734ce4de():
    fields = dict(item.split("=", 1) for item in inspect_734ce4de().split("|"))
    analysis_surface = surface_734ce4de()
    obfuscation_surface = obfuscation_734ce4de()
    operation_plan = ("runpy_descriptor", ("python3", fields["file_path"]))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_734ce4de())
