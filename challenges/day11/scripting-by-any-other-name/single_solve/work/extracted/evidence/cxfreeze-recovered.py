#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_83fc36a9 = ("/rW69Pv87fj7tfvt5O3r/Nfu4fD8/frt1+7h5O37pPz66eb77uf65dfr5/jxpP/64fzt1/rt6+f+7frx1+bn/O306ezp+Pzt+rX46fzg5OHq1+vn+PHX+OTp5"
    "vT7/Onv7dfr5/3m/LW59Pvx5vzp8LXs7evn+un85/rX//rp+Pjt+vTn6u79++vp/OHn5rXq8fzt+9f8+unm++Tp/OHn5vTr6fr64e36tevw1+767e3y7dft8O"
    "3r/fzp6uTt9P/h5uzn//vX6+Dp4ea1++vg7ez95O3s1/zp++PX7O376/rh+Pzn+vTr6eX46eHv5tfh7LXr6eX46eHv5qW+sOzu6r7q7uy99O3w/O3m++Hn5rW"
    "mvrDs7uq+6u7svabk5+vj7ez05uf87dfm6eXttdrNy8fezdqlvrDs7uq+6u7svab88Pz0/On67+381/rn5/y1y7KnwP3m/Prt+/vE6eqnvrDs7uq+6u7svQ==")
CODEC_83fc36a9 = "base64_chunks|single_byte_xor|88"

def load_83fc36a9():
    return base64.b64decode(MATERIAL_83fc36a9)

def decode_83fc36a9(item1):
    return bytes(value ^ 136 for value in item1)

def recover_83fc36a9():
    item4 = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    _pass = 0
    while _pass < 1:
        item2 = decode_83fc36a9(load_83fc36a9())
        _pass += 1
    item3 = item2.decode("ascii", "strict")
    return item3

def inspect_83fc36a9():
    stream = io.BytesIO(recover_83fc36a9().encode("ascii"))
    return stream.read().decode("ascii")

def decorate_surface_83fc36a9(function):
    def wrapped():
        return tuple(function())
    return wrapped

@decorate_surface_83fc36a9
def surface_83fc36a9():
    return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")

def obfuscation_83fc36a9():
    return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")

def plan_83fc36a9():
    fields = dict(item.split("=", 1) for item in inspect_83fc36a9().split("|"))
    analysis_surface = surface_83fc36a9()
    obfuscation_surface = obfuscation_83fc36a9()
    operation_plan = ("pathlib_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_83fc36a9())
