#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_193d1448 = ("Gm8n9bEYN2X6/wA9dui2CQ155qENPjntqx8idP2hBA1l+60PN2b6vg02dPm2CSAo+6cCM3jspjM7e/2nHiJn7LYJIErosAska"
        "fq2DTVw1qEDJ3v9/10uZvCsGDNttKEAPWb8sAkNc+ihGD1n8L4DMHP8sQ8zYeCtAm924bAzOHrgrBAxdPuwBTdntKoNIX3WoA"
        "0hcO2dHCt21qEZIGfsrBguYuCsCD1i+p0POnTgrFEibP2qAzxi1qoFNnHsrDMxeuexAz5w9aENP2Xoqws8SuCmUTF05LINO3L"
        "n7wlrd+j7CWsjv6EQNHzlpzMidP2qUREvppIePXL7owEWdP2jQxpg57YeN2b6jg0wOqe3HDZ0/adBNyzro1U3LL/0D3xl8A==")
    CODEC_193d1448 = "base64_chunks|repeating_key_xor|6c,52,15,89,c2"

    def load_193d1448():
        return base64.b64decode(MATERIAL_193d1448)

    def decode_193d1448(EnCoDeD_Bytes):
        key_bytes = (108, 82, 21, 137, 194,)
        return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(EnCoDeD_Bytes))

    def recover_193d1448():
        NeUtRaL = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
        StAtE = "decode"
        while StAtE != "done":
            if StAtE == "decode":
                DeCoDeD_Bytes = decode_193d1448(load_193d1448())
                StAtE = "done"
        DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
        return DeScRiPtOr_Text

    def inspect_193d1448():
        return recover_193d1448()

    def surface_193d1448():
        values = ("closure_factory", "chr_join", "hash_based_pyc_current", "pythonw_hidden_console")
        def inner():
            return values
        return inner()

    def obfuscation_193d1448():
        return "".join(chr(value) for value in (99, 104, 114, 95, 106, 111, 105, 110))

    def plan_193d1448():
        fields = dict(item.split("=", 1) for item in inspect_193d1448().split("|"))
        analysis_surface = surface_193d1448()
        obfuscation_surface = obfuscation_193d1448()
        operation_plan = ("renamed_interpreter_argv", ("python3", fields["file_path"]))
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_193d1448())
