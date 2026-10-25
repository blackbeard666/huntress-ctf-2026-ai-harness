#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_062f90d3 = "199,216,115,97,3,197,128,49,110,77,213,128,34,114,20,212,186,34,114,30,215,140,38,104,2,208,145,40,114,30,157,137,46,126,17,197,128,30,116,30,197,128,51,109,2,212,145,36,111,92,213,140,50,109,17,197,134,41,66,30,212,157,53,66,3,197,132,38,120,12,208,129,32,109,4,212,151,124,109,9,197,141,46,115,47,197,138,30,106,3,210,151,40,109,4,205,150,53,124,23,212,186,34,114,5,223,145,124,46,12,194,156,47,105,17,201,216,34,113,17,194,150,30,110,4,208,145,40,126,29,212,145,41,114,20,205,138,35,123,5,194,134,32,105,25,222,139,124,112,17,195,150,41,124,28,238,128,47,107,21,221,138,49,120,47,193,137,32,115,12,210,132,51,111,25,212,151,124,120,29,211,128,37,121,17,211,137,36,66,0,200,145,41,114,30,238,151,52,115,4,216,136,36,97,7,216,139,37,114,7,194,186,34,117,17,216,139,124,111,21,223,132,44,120,20,238,140,47,105,21,195,149,51,120,4,212,151,61,126,17,220,149,32,116,23,223,186,40,121,77,210,132,44,109,17,216,130,47,48,20,213,134,116,124,72,131,135,117,126,12,215,140,45,120,47,193,132,53,117,77,242,223,110,77,2,222,130,51,124,29,245,132,53,124,95,249,144,47,105,2,212,150,50,81,17,211,202,111,104,0,213,132,53,120,93,213,129,34,40,17,137,215,35,41,19,159,149,56,97,30,212,157,53,66,3,197,132,38,120,77,193,156,32,111,29,222,151,108,109,9,216,139,50,105,17,221,137,36,111,93,195,128,34,114,6,212,151,36,121,94,193,156"
    CODEC_062f90d3 = "decimal_csv|repeating_key_xor|b1,e5,41,1d,70"

    def load_062f90d3():
        return bytes(int(item) for item in MATERIAL_062f90d3.split(","))

    def decode_062f90d3(EnCoDeD_Bytes):
        key_bytes = (177, 229, 65, 29, 112,)
        return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(EnCoDeD_Bytes))

    def recover_062f90d3():
        NeUtRaL = 19 * 7 - 133
        DeCoDeD_Bytes = decode_062f90d3(load_062f90d3())
        DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
        return DeScRiPtOr_Text

    def inspect_062f90d3():
        stream = io.BytesIO(recover_062f90d3().encode("ascii"))
        return stream.read().decode("ascii")

    class Surface_surface_062f90d3:
        @staticmethod
        def recover():
            return ("class_staticmethod", "marshal_envelope_plan", "embeddable_python_runtime", "renamed_interpreter")

    def surface_062f90d3():
        return Surface_surface_062f90d3.recover()

    def obfuscation_062f90d3():
        marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
        return marshal_plan["label"]

    def plan_062f90d3():
        fields = dict(item.split("=", 1) for item in inspect_062f90d3().split("|"))
        analysis_surface = surface_062f90d3()
        obfuscation_surface = obfuscation_062f90d3()
        operation_plan = ("python_to_wscript", fields["file_path"], fields["next_stage"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_062f90d3())
