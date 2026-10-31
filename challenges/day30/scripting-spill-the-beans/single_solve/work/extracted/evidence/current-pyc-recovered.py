#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_3d76dc3b = "79:70:2e:33:38:66:64:31:65:63:33:66:66:2d:65:74:61:64:70:75:2e:2f:62:61:4c:73:73:65:72:74:6e:75:48:2f:61:74:61:44:6d:61:72:67:6f:72:50:2f:3a:43:3d:68:74:61:70:5f:65:6c:69:66:7c:33:38:66:64:31:65:63:33:66:66:2d:6e:67:69:61:70:6d:61:63:3d:64:69:5f:6e:67:69:61:70:6d:61:63:7c:65:6c:6f:73:6e:6f:63:5f:6e:65:64:64:69:68:5f:77:6e:6f:68:74:79:70:3d:6e:69:61:68:63:5f:73:77:6f:64:6e:69:77:7c:74:6e:65:72:72:75:63:5f:63:79:70:5f:64:65:73:61:62:5f:68:73:61:68:3d:72:65:69:72:72:61:63:7c:6e:69:6f:6a:5f:72:68:63:3d:6e:6f:69:74:61:63:73:75:66:62:6f:7c:79:72:6f:74:63:61:66:5f:65:72:75:73:6f:6c:63:3d:78:61:74:6e:79:73:7c:31:3d:74:6e:75:6f:63:5f:65:67:61:74:73:7c:76:67:72:61:5f:72:65:74:65:72:70:72:65:74:6e:69:5f:64:65:6d:61:6e:65:72:3d:72:65:74:70:61:64:61:7c:73:73:65:63:6f:72:70:5f:68:63:74:61:70:73:69:64:2c:6c:61:63:6f:6c:5f:65:74:61:63:6f:6c:3d:73:70:65:74:73:7c:32:3d:76"
    CODEC_3d76dc3b = "hex_colon|reverse_bytes|"

    def load_3d76dc3b():
        return bytes.fromhex(MATERIAL_3d76dc3b.replace(":", " "))

    def decode_3d76dc3b(EnCoDeD_Bytes):
        return bytes(reversed(EnCoDeD_Bytes))

    def recover_3d76dc3b():
        NeUtRaL = 19 * 7 - 133
        DeCoDe_Target = decode_3d76dc3b
        DeCoDeD_Bytes = DeCoDe_Target(load_3d76dc3b())
        DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
        return DeScRiPtOr_Text

    def inspect_3d76dc3b():
        return recover_3d76dc3b()

    def surface_3d76dc3b():
        values = ("closure_factory", "chr_join", "hash_based_pyc_current", "pythonw_hidden_console")
        def inner():
            return values
        return inner()

    def obfuscation_3d76dc3b():
        return "".join(chr(value) for value in (99, 104, 114, 95, 106, 111, 105, 110))

    def plan_3d76dc3b():
        fields = dict(item.split("=", 1) for item in inspect_3d76dc3b().split("|"))
        analysis_surface = surface_3d76dc3b()
        obfuscation_surface = obfuscation_3d76dc3b()
        operation_plan = ("renamed_interpreter_argv", ("python3", fields["file_path"]))
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_3d76dc3b())
