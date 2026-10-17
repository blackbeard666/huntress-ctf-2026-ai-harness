#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_978eedd8 = ("lKmb55TghfWGu8itwaTHs+yK45vvmuiN0rTdsdSni/+N7ILxl/iK57jbtMS9keaU/Ynss8Gkx6jeu8mw74Humv+D4obnl+OG9Mm60qfTutaJ6oX1jNOjz67A"

    "vM+72r3Yh+SL/pDk2eiU557whOWdoMShwq3fvsql14j/jeyc7In7h+iK7Jnqieic9Zr0yavSpsOw75vpiOaV+ZjsheqE+Jv6iPqT9oS52qL9m+mM6ZP2qcy0"

    "0bLHs9Kw3LnFstu10b7JuuWG7o/miLXGpc2ozLnVsNSL/57thtm92KvIutOj17jKttW02anIocao9576x6TFqNi50LfZ9Mz5mKqd/8agw/CM6ZHlgO6d9Jv1"

    "yObe64q4j+3UstHizKDPrMeixrrUu8+q9Zv6l/LPndib1ILHlbiAtdTm0bOK7I+8kuae6pbig/GW84fYqsWq3uOgmrX9iOaS4IX2hcmoyuXd6Im7jO7XsdLh")

CODEC_978eedd8 = "base64_chunks|rolling_xor|e2"



def load_978eedd8():

    return base64.b64decode(MATERIAL_978eedd8)



def decode_978eedd8(item1):

    item2 = bytearray()

    item5 = 226

    for value in item1:

        item2.append(value ^ item5)

        item5 = value

    return bytes(item2)



def recover_978eedd8():

    item4 = ":".join(("north", "south"))

    _pass = 0

    while _pass < 1:

        item2 = decode_978eedd8(load_978eedd8())

        _pass += 1

    item3 = item2.decode("ascii", "strict")

    return item3



def inspect_978eedd8():

    return recover_978eedd8()



def decorate_surface_978eedd8(function):

    def wrapped():

        return tuple(function())

    return wrapped



@decorate_surface_978eedd8

def surface_978eedd8():

    return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")



def obfuscation_978eedd8():

    return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")



def plan_978eedd8():

    fields = dict(item.split("=", 1) for item in inspect_978eedd8().split("|"))

    analysis_surface = surface_978eedd8()

    obfuscation_surface = obfuscation_978eedd8()

    operation_plan = ("shutil_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_978eedd8())

