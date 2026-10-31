#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_ec2c4627 = "cDcsdm1uX2ptN21fZl9dbllgY3Jub2xfWWBjZl9tJm5sW2htYGlsZ1ldaWpzJnFsY25fWWxfXWlwX2xzWWhpbl92W15bam5fbDdpbVlxW2ZlWV1panNZamZbaHZtblthX1ldaW9objcrdm1zaG5bcjdeX11pbFtuaWxZcWxbampfbHZpXGBvbV1bbmNpaDdcc25fbVlubFtobWZbbmNpaHZdW2xsY19sN11yWWBsX190X1lfcl9db25bXGZfdnFjaF5pcW1ZXWJbY2g3bV1iX15vZl9eWW5bbWVZXl9tXWxjam5pbHZdW2dqW2NhaFljXjddW2dqW2NhaCdgK11dKltbYGAudl9ybl9obWNpaDcoYCtdXSpbW2BgLihmaV1lX152aGluX1loW2dfN0w_PUlQP0wnYCtdXSpbW2BgLihucm52bltsYV9uWWxpaW43PTQpQm9obmxfbW1GW1wpYCtdXSpbW2BgLg=="
CODEC_ec2c4627 = "urlsafe_base64|subtract_modulo_256|06"

def load_ec2c4627():
    return base64.urlsafe_b64decode(MATERIAL_ec2c4627)

def decode_ec2c4627(e):
    return bytes((value + 6) % 256 for value in e)

def recover_ec2c4627():
    n = None
    try:
        d = decode_ec2c4627(load_ec2c4627())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    t = d.decode("ascii", "strict")
    return t

def inspect_ec2c4627():
    return recover_ec2c4627()

def decorate_surface_ec2c4627(function):
    def wrapped():
        return tuple(function())
    return wrapped

@decorate_surface_ec2c4627
def surface_ec2c4627():
    return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")

def obfuscation_ec2c4627():
    return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")

def plan_ec2c4627():
    fields = dict(item.split("=", 1) for item in inspect_ec2c4627().split("|"))
    analysis_surface = surface_ec2c4627()
    obfuscation_surface = obfuscation_ec2c4627()
    operation_plan = ("os_walk_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_ec2c4627())
