#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_0e061958 = ("h05DjYSFdoGETnV2dIB1dnB2fnN2dXV2dT2Ig3qFdnB3en12jXJ1coGFdoNOgIF2f3Bzen9yg4pwiIN6hXaNhIVyeHZwd"
    "ICGf4VOQo2Ein+FcolOdH1yhIRwhIVyhXp0fnaFeYB1jYBzd4aEdHKFeoB/ToSFg3p/eHCFcnN9do10coODenaDTnlyhH"
    "lwc3KEdnVwgYp0cERJjYh6f3WAiIRwdHlyen9Og3Z/cn52dXB6f4V2g4GDdoV2g410cn6Bcnp4f3B6dU50cn6Bcnp4fz5"
    "HQXNKQkV2SXRCjXd6fXZwgXKFeU5US0Bhg4B4g3J+VXKFckBZhn+Fg3aEhF1yc0A/hoF1coV2PkdBc0pCRXZJdEI/gYo=")
CODEC_0e061958 = "base64_chunks|add_modulo_256|11"

def load_0e061958():
    return base64.b64decode(MATERIAL_0e061958)

def decode_0e061958(e):
    return bytes((value - 17) % 256 for value in e)

def recover_0e061958():
    n = "left" if 2 > 1 else "right"
    d = decode_0e061958(load_0e061958())
    t = d.decode("ascii", "strict")
    return t

def inspect_0e061958():
    stream = io.BytesIO(recover_0e061958().encode("ascii"))
    return stream.read().decode("ascii")

class Surface_surface_0e061958:
    @staticmethod
    def recover():
        return ("class_staticmethod", "string_table", "hash_based_pyc_38", "renamed_interpreter")

def surface_0e061958():
    return Surface_surface_0e061958.recover()

def obfuscation_0e061958():
    table = ("strin", "g_table")
    return "".join(table)

def plan_0e061958():
    fields = dict(item.split("=", 1) for item in inspect_0e061958().split("|"))
    analysis_surface = surface_0e061958()
    obfuscation_surface = obfuscation_0e061958()
    operation_plan = ("open_binary_write", "decode", fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_0e061958())
