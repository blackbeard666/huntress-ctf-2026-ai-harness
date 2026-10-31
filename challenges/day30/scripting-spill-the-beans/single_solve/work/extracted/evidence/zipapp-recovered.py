#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_71bafc9c = "UhkWWFdQQVRXGUBBR0tAQXtHS0pCTUNRVkVQTUtKCEhLR0VQQXtNSlBBVlRWQVBBVghATVdURVBHTHtKQVxQe1dQRUNBWEVARVRQQVYZVF1QTEtKe1BLe0dJQFhXUEVDQXtHS1FKUBkXWFddSlBFXBlIRUlGQEV7QE1XVEVQR0xYS0ZCUVdHRVBNS0oZVkFSQVZXQUB7QlZFQ0lBSlBXWEdFVlZNQVYZXk1URVRUe1RdXlhTTUpAS1NXe0dMRU1KGUdJQHtQS3tUXVBMS0pYR0VJVEVNQ0p7TUAZR0VJVEVNQ0oJFxATHRAWEhQcFFhCTUhBe1RFUEwZZx4LdFZLQ1ZFSWBFUEULbFFKUFZBV1doRUYLClFUQEVQQQkXEBMdEBYSFBwUClRdWEpBXFB7V1BFQ0EZVF1HFxwJVkFHS1JBVkFAClRd"
CODEC_71bafc9c = "base64_literal|single_byte_xor|24"

def load_71bafc9c():
    return base64.b64decode(MATERIAL_71bafc9c)

def decode_71bafc9c(v_a19c):
    return bytes(value ^ 36 for value in v_a19c)

def recover_71bafc9c():
    v_d41a = ":".join(("north", "south"))
    v_b27e = decode_71bafc9c(load_71bafc9c())
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_71bafc9c():
    view = memoryview(recover_71bafc9c().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_71bafc9c():
    dispatch = lambda *items: tuple(items)
    return dispatch("lambda_dispatch", "reversed_fragments", "zipapp_pyz", "cmd_to_python")

def obfuscation_71bafc9c():
    return "stnemgarf_desrever"[::-1]

def plan_71bafc9c():
    fields = dict(item.split("=", 1) for item in inspect_71bafc9c().split("|"))
    analysis_surface = surface_71bafc9c()
    obfuscation_surface = obfuscation_71bafc9c()
    operation_plan = ("python_to_cmd", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_71bafc9c())
