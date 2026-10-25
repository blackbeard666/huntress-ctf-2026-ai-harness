#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_acd90015 = "ZWQ3NjA2OGE5Yi10c29oPWRpX3Rzb2h8ZWQ3NjA2OGE5Yi1uZ2lhcG1hYz1kaV9uZ2lhcG1hY3xleGVfbm9odHlwX3RjZXJpZD1uaWFoY19zd29kbml3fGVjcnVvc193YXI9cmVpcnJhY3x5bG5vX21yb2ZzbmFydD1ub2l0YWNzdWZib3xzbm9pdGNudWZfbmlhbHA9eGF0bnlzfDE9dG51b2NfZWdhdHN8eXhvcnBfZ25pcHBhbT1yZXRwYWRhfG5vaXRhcnVnaWZub2NfbnJ1dGVyLG5vaXRhcnVnaWZub2NfZWRvY2VkPXNwZXRzfDI9dg=="
    CODEC_acd90015 = "urlsafe_base64|reverse_bytes|"

    def load_acd90015():
        return base64.urlsafe_b64decode(MATERIAL_acd90015)

    def decode_acd90015(item1):
        return bytes(reversed(item1))

    def recover_acd90015():
        item4 = ":".join(("north", "south"))
        item7 = "decode"
        while item7 != "done":
            if item7 == "decode":
                item2 = decode_acd90015(load_acd90015())
                item7 = "done"
        item3 = item2.decode("ascii", "strict")
        return item3

    def inspect_acd90015():
        stream = io.BytesIO(recover_acd90015().encode("ascii"))
        return stream.read().decode("ascii")

    def surface_acd90015():
        return ("plain_functions", "transform_only", "raw_source", "direct_python_exe")

    def obfuscation_acd90015():
        return "transform_only"

    def plan_acd90015():
        fields = dict(item.split("=", 1) for item in inspect_acd90015().split("|"))
        analysis_surface = surface_acd90015()
        obfuscation_surface = obfuscation_acd90015()
        operation_plan = ("report", fields.get("host_id", ""))
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_acd90015())
