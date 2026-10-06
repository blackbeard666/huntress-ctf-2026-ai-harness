#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_6218c88f = "118,61,50,124,115,116,101,112,115,61,100,101,99,111,100,101,95,99,111,110,102,105,103,117,114,97,116,105,111,110,44,108,111,99,97,116,101,95,105,110,116,101,114,112,114,101,116,101,114,44,100,105,115,112,97,116,99,104,95,110,101,120,116,95,115,116,97,103,101,124,97,100,97,112,116,101,114,61,112,121,116,104,111,110,95,116,111,95,112,121,116,104,111,110,124,115,116,97,103,101,95,99,111,117,110,116,61,51,124,115,121,110,116,97,120,61,108,97,109,98,100,97,95,100,105,115,112,97,116,99,104,124,111,98,102,117,115,99,97,116,105,111,110,61,114,101,118,101,114,115,101,100,95,102,114,97,103,109,101,110,116,115,124,99,97,114,114,105,101,114,61,122,105,112,97,112,112,95,112,121,122,124,119,105,110,100,111,119,115,95,99,104,97,105,110,61,99,109,100,95,116,111,95,112,121,116,104,111,110,124,99,97,109,112,97,105,103,110,95,105,100,61,99,97,109,112,97,105,103,110,45,57,49,54,101,50,97,53,99,48,51,124,102,105,108,101,95,112,97,116,104,61,67,58,47,80,114,111,103,114,97,109,68,97,116,97,47,72,117,110,116,114,101,115,115,76,97,98,47,46,117,112,100,97,116,101,45,57,49,54,101,50,97,53,99,48,51,46,112,121,124,110,101,120,116,95,115,116,97,103,101,61,112,121,99,51,56,45,114,101,99,111,118,101,114,101,100,46,112,121"
    CODEC_6218c88f = "decimal_csv|identity|"

    def load_6218c88f():
        return bytes(int(item) for item in MATERIAL_6218c88f.split(","))

    def decode_6218c88f(stored_bytes):
        return bytes(stored_bytes)

    def recover_6218c88f():
        harmless_value = None
        decode_state = "decode"
        while decode_state != "done":
            if decode_state == "decode":
                recovered_bytes = decode_6218c88f(load_6218c88f())
                decode_state = "done"
        configuration_text = recovered_bytes.decode("ascii", "strict")
        return configuration_text

    def inspect_6218c88f():
        view = memoryview(recover_6218c88f().encode("ascii"))
        return bytes(view).decode("ascii")

    def surface_6218c88f():
        dispatch = lambda *items: tuple(items)
        return dispatch("lambda_dispatch", "reversed_fragments", "zipapp_pyz", "cmd_to_python")

    def obfuscation_6218c88f():
        return "stnemgarf_desrever"[::-1]

    def plan_6218c88f():
        fields = dict(item.split("=", 1) for item in inspect_6218c88f().split("|"))
        analysis_surface = surface_6218c88f()
        obfuscation_surface = obfuscation_6218c88f()
        operation_plan = ("python_to_python", fields["file_path"], fields["next_stage"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_6218c88f())
