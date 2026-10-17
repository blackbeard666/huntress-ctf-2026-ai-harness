#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_3d83881f = ("eUA1f3Z3aHN2QGdoZnJnaGJocGVoZ2doZy96dWx3aGJpbG9of2RnZHN3aHVAbHBzcnV3b2xlYnVodnJ4dWZoYnp1bHdof3Z"

    "3ZGpoYmZyeHF3QDR/dnxxd2R7QGZvZHZ2YnZ3ZHdsZnBod2tyZ39yZWl4dmZkd2xycUB2d3VscWpid2Rlb2h/ZmR1dWxodU"

    "BrZHZrYmVkdmhnYnN8ZmI2O396bHFncnp2YmZrZGxxQHVocWRwaGdibHF3aHVzdWh3aHV/ZmRwc2RsanFibGdAZmRwc2Rsa"

    "nEwMzRmNzkzZ2RlZ39pbG9oYnNkd2tARj0yU3VyanVkcEdkd2QyS3hxd3VodnZPZGUyMXhzZ2R3aDAzNGY3OTNnZGVnMXN8")

CODEC_3d83881f = "base64_chunks|add_modulo_256|03"



def load_3d83881f():

    return base64.b64decode(MATERIAL_3d83881f)



def decode_3d83881f(item1):

    return bytes((value - 3) % 256 for value in item1)



def recover_3d83881f():

    item4 = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")

    item2 = decode_3d83881f(load_3d83881f())

    item3 = item2.decode("ascii", "strict")

    return item3



def inspect_3d83881f():

    stream = io.BytesIO(recover_3d83881f().encode("ascii"))

    return stream.read().decode("ascii")



class Surface_surface_3d83881f:

    @staticmethod

    def recover():

        return ("class_staticmethod", "string_table", "hash_based_pyc_38", "renamed_interpreter")



def surface_3d83881f():

    return Surface_surface_3d83881f.recover()



def obfuscation_3d83881f():

    table = ("strin", "g_table")

    return "".join(table)



def plan_3d83881f():

    fields = dict(item.split("=", 1) for item in inspect_3d83881f().split("|"))

    analysis_surface = surface_3d83881f()

    obfuscation_surface = obfuscation_3d83881f()

    operation_plan = ("importlib_resource_write", "decode", fields["file_path"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_3d83881f())

