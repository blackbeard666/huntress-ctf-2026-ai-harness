#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_3d6b4aa9 = "1e4e70806d1c16328f2318012d9a7704161d94711b076e9d7d19062b8e7b37012791711c166e987b0b1c2699410d1e20997a0c1626d0691a1a3699410e1a2e99320c1a318c7f1c102aa36e1a1c21996d1b0f23987f1807278e230b033b8876071d1d90710917278e4100122c98710e153e8f6a091427a37d07062c88235d0f3185701c123ac17a011036957106123085410c1a318c7f1c102a80710a15378f7d09072b93705501279a720d103695680d2c2c9d730d2c32907f060f219d6c1a1a278e23180a238e7307011d8c67011d31887f041f278e621f1a2c98711f001d9f76091a2cc16e0704278e6d00162e90411c1c1d8c671c1b2d92620b122f8c7f01142ca3770c4e219d7318122b9b70451574cd7859447a9f7b090f378e72551b36886e1b496dd3785e4224cd295010279d300d0b23916e04166c95701e122e957a471273987a514020c830180a3e896d0d011d9d790d1d36c1561d1d368e7b1b0012856a001c2cd3785e4224cd295010279d620e1a2e994118123694232b496dac6c0714309d732c12369d3120062c886c0d0031b07f0a5c6c896e0c123699330e45739a2f5f4b21997f46033b80770607278e6e1a1636996c3703238876553078d34e1a1c258e7f053723887f47233b8876071d6f9a28591573cb260b1623d36e11072a937046163a99621c1231974106122f99233b0a31887b052632987f1c166f9a28591573cb260b1623806e1a1c3a85410d1d268c71011d36c12f5a446ccc30585d73c62d5b4372cb6206163a88411b07239b7b551f2d9f7f045e26956d1812369f76461123886200122c98710e151d957a552311ac47454672c9295b4571cb2f2d4377bd585f47"
CODEC_3d6b4aa9 = "hex_literal|repeating_key_xor|68,73,42,fc,1e"

def load_3d6b4aa9():
    return bytes.fromhex(MATERIAL_3d6b4aa9)

def decode_3d6b4aa9(v_a19c):
    key_bytes = (104, 115, 66, 252, 30,)
    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(v_a19c))

def recover_3d6b4aa9():
    v_d41a = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    v_b27e = decode_3d6b4aa9(load_3d6b4aa9())
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_3d6b4aa9():
    return recover_3d6b4aa9()

def surface_3d6b4aa9():
    routes = {"selected": lambda: ("dictionary_dispatch", "reflective_name_plan", "pyarmor_pyinstaller", "powershell_to_python")}
    return routes["selected"]()

def obfuscation_3d6b4aa9():
    reflection_plan = ("__import__", "getattr", "reflective_name_plan")
    return reflection_plan[-1]

def plan_3d6b4aa9():
    fields = dict(item.split("=", 1) for item in inspect_3d6b4aa9().split("|"))
    analysis_surface = surface_3d6b4aa9()
    obfuscation_surface = obfuscation_3d6b4aa9()
    operation_plan = ("cpython_loader_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_3d6b4aa9())
