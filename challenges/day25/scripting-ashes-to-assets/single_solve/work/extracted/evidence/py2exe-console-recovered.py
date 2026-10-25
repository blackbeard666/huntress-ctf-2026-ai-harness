#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_b31315dc = ("eXAuMWI0N2ZkMjViYi1ldGFkcHUuL2JhTHNzZXJ0bnVIL2F0YURtYXJnb3JQLzpDPWh0YXBfZWxpZnwxYjQ3ZmQyNWJ"
        "iLW5naWFwbWFjPWRpX25naWFwbWFjfHJvc3NlY2VkZXJwXzIzcnZzZ2VyPW5pYWhjX3N3b2RuaXd8ZWxvc25vY19leG"
        "UyeXA9cmVpcnJhY3xzbGxlY19lcnVzb2xjPW5vaXRhY3N1ZmJvfGVzYWNfaGN0YW09eGF0bnlzfDE9dG51b2NfZWdhd"
        "HN8dmdyYV9yZXRlcnByZXRuaT1yZXRwYWRhfHNzZWNvcnBfaGN0YXBzaWQsbGFjb2xfZXRhY29sPXNwZXRzfDI9dg==")
    CODEC_b31315dc = "base64_chunks|reverse_bytes|"

    def load_b31315dc():
        return base64.b64decode(MATERIAL_b31315dc)

    def decode_b31315dc(EnCoDeD_Bytes):
        return bytes(reversed(EnCoDeD_Bytes))

    def recover_b31315dc():
        NeUtRaL = (3, 5, 8, 13)[1:3]
        for _pass in range(1):
            DeCoDeD_Bytes = decode_b31315dc(load_b31315dc())
        DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
        return DeScRiPtOr_Text

    def inspect_b31315dc():
        return recover_b31315dc()

    def surface_b31315dc():
        selected = "carrier"
        match selected:
            case "carrier":
                return ("match_case", "closure_cells", "py2exe_console", "regsvr32_predecessor")
            case _:
                return ()

    def obfuscation_b31315dc():
        value = "closure_cells"
        def recover():
            return value
        return recover()

    def plan_b31315dc():
        fields = dict(item.split("=", 1) for item in inspect_b31315dc().split("|"))
        analysis_surface = surface_b31315dc()
        obfuscation_surface = obfuscation_b31315dc()
        operation_plan = ("interpreter_argv", ("python3", fields["file_path"]))
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_b31315dc())
