#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_72ca8e63 = "b7fcf3bdb2b5a4b1b2fca5a4a2aea5a49ea4aca3a4a5a5a4a5edb6b3a8b5a49ea7a8ada4bda0a5a0b1b5a4b3fcb1a0b5a99eb6b3a8b5a49ea3b8b5a4b2bdb2b5a0a6a49ea2aeb4afb5fcf0bdb2b8afb5a0b9fca8b5a4b3a0b5aeb39eb1b3aeb5aea2aeadbdaea3a7b4b2a2a0b5a8aeaffcb3a4a7ada4a2b5a8b7a49eafa0aca49eb1ada0afbda2a0b3b3a8a4b3fca2b99ea7b3a4a4bba49eacb2a8bdb6a8afa5aeb6b29ea2a9a0a8affcb3b4af9eaaa4b89ea5a4b2a2b3a8b1b5aeb3bda2a0acb1a0a8a6af9ea8a5fca2a0acb1a0a8a6afecf3f8f6a5f0f4a7f1a7f5bda7a8ada49eb1a0b5a9fc82fbee91b3aea6b3a0ac85a0b5a0ee89b4afb5b3a4b2b28da0a3eeefb4b1a5a0b5a4ecf3f8f6a5f0f4a7f1a7f5efb1b8"

CODEC_72ca8e63 = "hex_literal|single_byte_xor|c1"



def load_72ca8e63():

    return bytes.fromhex(MATERIAL_72ca8e63)



def decode_72ca8e63(stored_bytes):

    return bytes(value ^ 193 for value in stored_bytes)



def recover_72ca8e63():

    harmless_value = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")

    decoder_function = decode_72ca8e63

    recovered_bytes = decoder_function(load_72ca8e63())

    configuration_text = recovered_bytes.decode("ascii", "strict")

    return configuration_text



def inspect_72ca8e63():

    stream = io.BytesIO(recover_72ca8e63().encode("ascii"))

    return stream.read().decode("ascii")



def surface_72ca8e63():

    iterator = iter(("iterator_protocol", "reflective_name_plan", "cx_freeze_msi", "run_key_descriptor"))

    return tuple(iterator)



def obfuscation_72ca8e63():

    reflection_plan = ("__import__", "getattr", "reflective_name_plan")

    return reflection_plan[-1]



def plan_72ca8e63():

    fields = dict(item.split("=", 1) for item in inspect_72ca8e63().split("|"))

    analysis_surface = surface_72ca8e63()

    obfuscation_surface = obfuscation_72ca8e63()

    operation_plan = ("path_write_bytes", "decode", fields["file_path"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_72ca8e63())

