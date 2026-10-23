#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_df21c36a = "a2toPj8/Mz87PyVkZWJ+c1p5eW94fmR/Qjd+ZG9ta1V4b3l/dnN6JDkyPm9uPWw+JW5jZmt8ZGMkb2Z6Z2tybyRra2g+Pz8zPzs/JSUweXp+fmI3Znh/dmtraD4/PzM/Oz8nZG1ja3pna2k3bmNVZG1ja3pna2l2ZGVifnN6VWV+VWZmb2J5eG99ZXo3ZGNrYmlVeX1lbmRjfXZvfGNiaXhrVWZvb2J9N3hvY3h4a2l2emtnVX5rZ3hlbDdkZWN+a2l5f2xoZXZkZWN5ZG9ib3h6Z2VpVX55Y2Y3cmt+ZHN5djs3fmR/ZWlVb21rfnl2c3hlZ29nVX5kb2NmaVV6fn5iN3hvfnprbmt2c3hlZ29nVWJpfmt6eWNuJm9+ZWdveFVveGN/e2lrN3l6b355djg3fA=="

CODEC_df21c36a = "base64_literal|reverse_then_xor|0a"



def load_df21c36a():

    return base64.b64decode(MATERIAL_df21c36a)



def decode_df21c36a(v_a19c):

    return bytes(value ^ 10 for value in reversed(v_a19c))



def recover_df21c36a():

    v_d41a = "left" if 2 > 1 else "right"

    v_a702 = "decode"

    while v_a702 != "done":

        if v_a702 == "decode":

            v_b27e = decode_df21c36a(load_df21c36a())

            v_a702 = "done"

    v_c304 = v_b27e.decode("ascii", "strict")

    return v_c304



def inspect_df21c36a():

    return recover_df21c36a()



def surface_df21c36a():

    return tuple(item for item in ("list_comprehension", "format_map", "wheel_archive", "powershell_to_python"))



def obfuscation_df21c36a():

    return "{left}{right}".format_map({"left": "format_", "right": "map"})



def plan_df21c36a():

    fields = dict(item.split("=", 1) for item in inspect_df21c36a().split("|"))

    analysis_surface = surface_df21c36a()

    obfuscation_surface = obfuscation_df21c36a()

    operation_plan = ("http_client_memory", fields["url"], "memory-handoff")

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_df21c36a())

