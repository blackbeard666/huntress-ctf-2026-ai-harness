#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_cb8a5dda = "XyYbZVxdTllcJk1OTFhNTkhOVktOTU1OTRVgW1JdTkhPUlVOZUpNSlldTlsmWUpdUUhgW1JdTkhLYl1OXGVcXUpQTkhMWF5XXSYaZVxiV11KYSZSXU5bSl1YW0hZW1hdWExYVWVYS09eXExKXVJYVyZbTk9VTkxdUl9OSFdKVk5IWVVKV2VMSltbUk5bJkxhSE9bTk5jTkhWXFJlYFJXTVhgXEhMUUpSVyZbXldIVE5iSE1OXExbUlldWFtlTEpWWUpSUFdIUk0mTEpWWUpSUFcWH0oeSh9PSh1PHmVPUlVOSFlKXVEmLCMYOVtYUFtKVi1KXUoYMV5XXVtOXFw1SksYF15ZTUpdThYfSh5KH09KHU8eF1li"
CODEC_cb8a5dda = "base64_literal|subtract_modulo_256|17"

def load_cb8a5dda():
    return base64.b64decode(MATERIAL_cb8a5dda)

def decode_cb8a5dda(item1):
    return bytes((value + 23) % 256 for value in item1)

def recover_cb8a5dda():
    item4 = 19 * 7 - 133
    try:
        item2 = decode_cb8a5dda(load_cb8a5dda())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    item3 = item2.decode("ascii", "strict")
    return item3

def inspect_cb8a5dda():
    return recover_cb8a5dda()

def surface_cb8a5dda():
    iterator = iter(("iterator_protocol", "reflective_name_plan", "cx_freeze_msi", "run_key_descriptor"))
    return tuple(iterator)

def obfuscation_cb8a5dda():
    reflection_plan = ("__import__", "getattr", "reflective_name_plan")
    return reflection_plan[-1]

def plan_cb8a5dda():
    fields = dict(item.split("=", 1) for item in inspect_cb8a5dda().split("|"))
    analysis_surface = surface_cb8a5dda()
    obfuscation_surface = obfuscation_cb8a5dda()
    operation_plan = ("path_write_bytes", "decode", fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_cb8a5dda())
