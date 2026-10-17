#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_e8e4ae1b = ("dj0yfHN0ZXBzPWRlY29kZV9lbWJlZGRlZCx3cml0ZV9maWxlfGFkYXB0ZXI9b3Blbl9iaW5hcnlfd3JpdGV8c3RhZ2VfY"

    "291bnQ9MXxzeW50YXg9Y2xhc3Nfc3RhdGljbWV0aG9kfG9iZnVzY2F0aW9uPXN0cmluZ190YWJsZXxjYXJyaWVyPWhhc2"

    "hfYmFzZWRfcHljXzM4fHdpbmRvd3NfY2hhaW49cmVuYW1lZF9pbnRlcnByZXRlcnxjYW1wYWlnbl9pZD1jYW1wYWlnbi0"

    "1ZjIwODYyMjQ5fGZpbGVfcGF0aD1DOi9Qcm9ncmFtRGF0YS9IdW50cmVzc0xhYi8udXBkYXRlLTVmMjA4NjIyNDkucHk=")

CODEC_e8e4ae1b = "base64_chunks|identity|"



def load_e8e4ae1b():

    return base64.b64decode(MATERIAL_e8e4ae1b)



def decode_e8e4ae1b(stored_bytes):

    return bytes(stored_bytes)



def recover_e8e4ae1b():

    harmless_value = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")

    decode_state = "decode"

    while decode_state != "done":

        if decode_state == "decode":

            recovered_bytes = decode_e8e4ae1b(load_e8e4ae1b())

            decode_state = "done"

    configuration_text = recovered_bytes.decode("ascii", "strict")

    return configuration_text



def inspect_e8e4ae1b():

    return recover_e8e4ae1b()



class Surface_surface_e8e4ae1b:

    @staticmethod

    def recover():

        return ("class_staticmethod", "string_table", "hash_based_pyc_38", "renamed_interpreter")



def surface_e8e4ae1b():

    return Surface_surface_e8e4ae1b.recover()



def obfuscation_e8e4ae1b():

    table = ("strin", "g_table")

    return "".join(table)



def plan_e8e4ae1b():

    fields = dict(item.split("=", 1) for item in inspect_e8e4ae1b().split("|"))

    analysis_surface = surface_e8e4ae1b()

    obfuscation_surface = obfuscation_e8e4ae1b()

    operation_plan = ("open_binary_write", "decode", fields["file_path"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_e8e4ae1b())

