#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_e20bc590 = "78:3f:34:7e:75:76:67:72:75:3f:63:65:73:77:6b:74:67:61:74:67:6f:71:76:67:2e:79:74:6b:76:67:61:68:6b:6e:67:7e:63:66:63:72:76:67:74:3f:74:67:73:77:67:75:76:61:75:76:74:67:63:6f:61:76:71:61:72:63:76:6a:7e:75:76:63:69:67:61:65:71:77:70:76:3f:33:7e:75:7b:70:76:63:7a:3f:69:67:70:67:74:63:76:71:74:61:72:6b:72:67:6e:6b:70:67:7e:71:64:68:77:75:65:63:76:6b:71:70:3f:68:75:76:74:6b:70:69:61:68:74:63:69:6f:67:70:76:75:7e:65:63:74:74:6b:67:74:3f:72:7b:6b:70:75:76:63:6e:6e:67:74:61:71:70:67:68:6b:6e:67:7e:79:6b:70:66:71:79:75:61:65:6a:63:6b:70:3f:6f:75:6a:76:63:61:76:71:61:72:7b:76:6a:71:70:7e:65:63:6f:72:63:6b:69:70:61:6b:66:3f:65:63:6f:72:63:6b:69:70:2f:67:36:33:35:35:67:36:36:38:35:7e:77:74:6e:3f:6a:76:76:72:75:3c:31:31:67:36:33:35:35:67:36:36:38:35:30:67:7a:63:6f:72:6e:67:30:6b:70:78:63:6e:6b:66:31:68:65:33:33:68:34:37:38:30:72:7b:7e:77:75:67:74:61:63:69:67:70:76:3f:4a:77:70:76:74:67:75:75:52:7b:76:6a:71:70:31:67:36:33:35:35:67:36:36:38:35:7e:68:6b:6e:67:61:72:63:76:6a:3f:45:3c:31:52:74:71:69:74:63:6f:46:63:76:63:31:4a:77:70:76:74:67:75:75:4e:63:64:31:30:77:72:66:63:76:67:2f:67:36:33:35:35:67:36:36:38:35:30:72:7b"
    CODEC_e20bc590 = "hex_colon|add_modulo_256|02"

    def load_e20bc590():
        return bytes.fromhex(MATERIAL_e20bc590.replace(":", " "))

    def decode_e20bc590(stored_bytes):
        return bytes((value - 2) % 256 for value in stored_bytes)

    def recover_e20bc590():
        harmless_value = "left" if 2 > 1 else "right"
        _pass = 0
        while _pass < 1:
            recovered_bytes = decode_e20bc590(load_e20bc590())
            _pass += 1
        configuration_text = recovered_bytes.decode("ascii", "strict")
        return configuration_text

    def inspect_e20bc590():
        stream = io.BytesIO(recover_e20bc590().encode("ascii"))
        return stream.read().decode("ascii")

    def surface_e20bc590():
        stream = (item for item in ("generator_pipeline", "fstring_fragments", "pyinstaller_onefile", "mshta_to_python"))
        return tuple(stream)

    def obfuscation_e20bc590():
        left, right = "fstrin", "g_fragments"
        return f"{left}{right}"

    def plan_e20bc590():
        fields = dict(item.split("=", 1) for item in inspect_e20bc590().split("|"))
        analysis_surface = surface_e20bc590()
        obfuscation_surface = obfuscation_e20bc590()
        operation_plan = ("request_stream_to_path", fields["url"], fields["file_path"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_e20bc590())
