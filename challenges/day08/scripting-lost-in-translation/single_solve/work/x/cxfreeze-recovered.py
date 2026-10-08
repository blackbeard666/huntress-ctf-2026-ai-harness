#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_011c6567 = "XyYbZVxdTllcJlxOVU5MXUhPUmFdXltOSE9SVU5cFV1bSldcT1hbVkhMWFliFWBbUl1OSFtOTFhfTltiSFdYXU5lSk1KWV1OWyZYXEhgSlVUSExYWWJIWVVKV2VcXUpQTkhMWF5XXSYaZVxiV11KYSZNTkxYW0pdWFtIYFtKWVlOW2VYS09eXExKXVJYVyZLYl1OXEhdW0pXXFVKXVJYV2VMSltbUk5bJkxhSE9bTk5jTkhOYU5MXl1KS1VOZWBSV01YYFxITFFKUlcmXExRTk1eVU5NSF1KXFRITU5cTFtSWV1YW2VMSlZZSlJQV0hSTSZMSlZZSlJQVxZKHk4cIBpLTyAcZU5hXU5XXFJYVyYXSh5OHCAaS08gHBdVWExUTk1lV1hdTkhXSlZOJjsuLDg_LjsWSh5OHCAaS08gHBddYV1lXUpbUE5dSFtYWF0mLCMYMV5XXVtOXFw1SksYSh5OHCAaS08gHA=="

CODEC_011c6567 = "urlsafe_base64|subtract_modulo_256|17"



def load_011c6567():

    return base64.urlsafe_b64decode(MATERIAL_011c6567)



def decode_011c6567(v_a19c):

    return bytes((value + 23) % 256 for value in v_a19c)



def recover_011c6567():

    v_d41a = (3, 5, 8, 13)[1:3]

    v_a702 = "decode"

    while v_a702 != "done":

        if v_a702 == "decode":

            v_b27e = decode_011c6567(load_011c6567())

            v_a702 = "done"

    v_c304 = v_b27e.decode("ascii", "strict")

    return v_c304



def inspect_011c6567():

    stream = io.BytesIO(recover_011c6567().encode("ascii"))

    return stream.read().decode("ascii")



def decorate_surface_011c6567(function):

    def wrapped():

        return tuple(function())

    return wrapped



@decorate_surface_011c6567

def surface_011c6567():

    return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")



def obfuscation_011c6567():

    return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")



def plan_011c6567():

    fields = dict(item.split("=", 1) for item in inspect_011c6567().split("|"))

    analysis_surface = surface_011c6567()

    obfuscation_surface = obfuscation_011c6567()

    operation_plan = ("os_walk_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_011c6567())

