#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_2ee405a7 = "79:70:2e:35:30:35:31:34:66:36:34:32:37:2d:65:74:61:64:70:75:2e:2f:62:61:4c:73:73:65:72:74:6e:75:48:2f:61:74:61:44:6d:61:72:67:6f:72:50:2f:3a:43:3d:68:74:61:70:5f:65:6c:69:66:7c:35:30:35:31:34:66:36:34:32:37:2d:6e:67:69:61:70:6d:61:63:3d:64:69:5f:6e:67:69:61:70:6d:61:63:7c:65:6c:6f:73:6e:6f:63:5f:6e:65:64:64:69:68:5f:77:6e:6f:68:74:79:70:3d:6e:69:61:68:63:5f:73:77:6f:64:6e:69:77:7c:74:6e:65:72:72:75:63:5f:63:79:70:5f:64:65:73:61:62:5f:68:73:61:68:3d:72:65:69:72:72:61:63:7c:6e:69:6f:6a:5f:72:68:63:3d:6e:6f:69:74:61:63:73:75:66:62:6f:7c:79:72:6f:74:63:61:66:5f:65:72:75:73:6f:6c:63:3d:78:61:74:6e:79:73:7c:31:3d:74:6e:75:6f:63:5f:65:67:61:74:73:7c:76:67:72:61:5f:72:65:74:65:72:70:72:65:74:6e:69:3d:72:65:74:70:61:64:61:7c:73:73:65:63:6f:72:70:5f:68:63:74:61:70:73:69:64:2c:6c:61:63:6f:6c:5f:65:74:61:63:6f:6c:3d:73:70:65:74:73:7c:32:3d:76"
    CODEC_2ee405a7 = "hex_colon|reverse_bytes|"

    def load_2ee405a7():
        return bytes.fromhex(MATERIAL_2ee405a7.replace(":", " "))

    def decode_2ee405a7(stored_bytes):
        return bytes(reversed(stored_bytes))

    def recover_2ee405a7():
        harmless_value = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
        decoder_function = decode_2ee405a7
        recovered_bytes = decoder_function(load_2ee405a7())
        configuration_text = recovered_bytes.decode("ascii", "strict")
        return configuration_text

    def inspect_2ee405a7():
        stream = io.BytesIO(recover_2ee405a7().encode("ascii"))
        return stream.read().decode("ascii")

    def surface_2ee405a7():
        values = ("closure_factory", "chr_join", "hash_based_pyc_current", "pythonw_hidden_console")
        def inner():
            return values
        return inner()

    def obfuscation_2ee405a7():
        return "".join(chr(value) for value in (99, 104, 114, 95, 106, 111, 105, 110))

    def plan_2ee405a7():
        fields = dict(item.split("=", 1) for item in inspect_2ee405a7().split("|"))
        analysis_surface = surface_2ee405a7()
        obfuscation_surface = obfuscation_2ee405a7()
        operation_plan = ("interpreter_argv", ("python3", fields["file_path"]))
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_2ee405a7())
