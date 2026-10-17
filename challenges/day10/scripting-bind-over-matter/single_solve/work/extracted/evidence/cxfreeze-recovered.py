#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_804db0b7 = "g0o/iYCBcn2ASoByeXJwgWxzdoWBgn9ybHN2eXKAOYF/bnuAc3x/emxwfH2GOYR/doFybH9ycHyDcn+GbHt8gXKJbnFufYFyf0qAdYKBdnlscHx9hmx9eW57iYCBbnRybHB8gnuBSj6JgIZ7gW6FSnFycHx/boF8f2yEf259fXJ/iXxvc4KAcG6Bdnx7Sm+GgXKAbIF/bnuAeW6Bdnx7iXBuf392cn9KcIVsc39ycodybHKFcnCCgW5veXKJhHZ7cXyEgGxwdW52e0qAcHVycYJ5cnFsgW6AeGxxcoBwf3Z9gXx/iXBuen1udnR7bHZxSnBuen1udnR7Oj4+RkM+PXJDPXKJcoWBcnuAdnx7Sjs+PkZDPj1yQz1yO3l8cHhycYl7fIFybHtuenJKX1JQXGNSXzo+PkZDPj1yQz1yO4GFgYmBbn90coFsf3x8gUpQRzxVgnuBf3KAgFlubzw+PkZDPj1yQz1y"

CODEC_804db0b7 = "base64_literal|add_modulo_256|0d"



def load_804db0b7():

    return base64.b64decode(MATERIAL_804db0b7)



def decode_804db0b7(item1):

    return bytes((value - 13) % 256 for value in item1)



def recover_804db0b7():

    item4 = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")

    for _pass in range(1):

        item2 = decode_804db0b7(load_804db0b7())

    item3 = item2.decode("ascii", "strict")

    return item3



def inspect_804db0b7():

    return recover_804db0b7()



def decorate_surface_804db0b7(function):

    def wrapped():

        return tuple(function())

    return wrapped



@decorate_surface_804db0b7

def surface_804db0b7():

    return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")



def obfuscation_804db0b7():

    return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")



def plan_804db0b7():

    fields = dict(item.split("=", 1) for item in inspect_804db0b7().split("|"))

    analysis_surface = surface_804db0b7()

    obfuscation_surface = obfuscation_804db0b7()

    operation_plan = ("shutil_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_804db0b7())

