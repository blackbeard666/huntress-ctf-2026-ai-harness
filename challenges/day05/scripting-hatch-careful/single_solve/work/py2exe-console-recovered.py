#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_440d4a19 = "152,145,207,130,130,217,131,135,131,215,132,208,212,204,132,149,128,133,145,148,207,206,131,128,173,146,146,132,147,149,143,148,169,206,128,149,128,165,140,128,147,134,142,147,177,206,219,162,220,137,149,128,145,190,132,141,136,135,157,130,130,217,131,135,131,215,132,208,212,204,143,134,136,128,145,140,128,130,220,133,136,190,143,134,136,128,145,140,128,130,157,147,142,146,146,132,130,132,133,132,147,145,190,211,210,147,151,146,134,132,147,220,143,136,128,137,130,190,146,150,142,133,143,136,150,157,132,141,142,146,143,142,130,190,132,153,132,211,152,145,220,147,132,136,147,147,128,130,157,146,141,141,132,130,190,132,147,148,146,142,141,130,220,143,142,136,149,128,130,146,148,135,131,142,157,132,146,128,130,190,137,130,149,128,140,220,153,128,149,143,152,146,157,208,220,149,143,148,142,130,190,132,134,128,149,146,157,151,134,147,128,190,150,143,142,137,149,152,145,220,147,132,149,145,128,133,128,157,146,146,132,130,142,147,145,190,137,130,149,128,145,146,136,133,205,141,128,130,142,141,190,132,149,128,130,142,141,220,146,145,132,149,146,157,211,220,151"

CODEC_440d4a19 = "decimal_csv|reverse_then_xor|e1"



def load_440d4a19():

    return bytes(int(item) for item in MATERIAL_440d4a19.split(","))



def decode_440d4a19(stored_bytes):

    return bytes(value ^ 225 for value in reversed(stored_bytes))



def recover_440d4a19():

    harmless_value = ":".join(("north", "south"))

    decoder_function = decode_440d4a19

    recovered_bytes = decoder_function(load_440d4a19())

    configuration_text = recovered_bytes.decode("ascii", "strict")

    return configuration_text



def inspect_440d4a19():

    stream = io.BytesIO(recover_440d4a19().encode("ascii"))

    return stream.read().decode("ascii")



def surface_440d4a19():

    selected = "carrier"

    match selected:

        case "carrier":

            return ("match_case", "closure_cells", "py2exe_console", "regsvr32_predecessor")

        case _:

            return ()



def obfuscation_440d4a19():

    value = "closure_cells"

    def recover():

        return value

    return recover()



def plan_440d4a19():

    fields = dict(item.split("=", 1) for item in inspect_440d4a19().split("|"))

    analysis_surface = surface_440d4a19()

    obfuscation_surface = obfuscation_440d4a19()

    operation_plan = ("pythonw_argv", ("python3", fields["file_path"]))

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_440d4a19())

