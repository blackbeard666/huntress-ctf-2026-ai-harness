#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_08679536 = "85:ce:c1:8f:80:87:96:83:80:ce:97:96:90:9c:97:96:ac:96:9e:91:96:97:97:96:97:df:84:81:9a:87:96:ac:95:9a:9f:96:8f:92:97:92:83:87:96:81:ce:83:92:87:9b:ac:84:81:9a:87:96:ac:91:8a:87:96:80:8f:80:87:92:94:96:ac:90:9c:86:9d:87:ce:c2:8f:80:8a:9d:87:92:8b:ce:90:9f:92:80:80:ac:80:87:92:87:9a:90:9e:96:87:9b:9c:97:8f:9c:91:95:86:80:90:92:87:9a:9c:9d:ce:80:87:81:9a:9d:94:ac:87:92:91:9f:96:8f:90:92:81:81:9a:96:81:ce:9b:92:80:9b:ac:91:92:80:96:97:ac:83:8a:90:ac:c0:cb:8f:84:9a:9d:97:9c:84:80:ac:90:9b:92:9a:9d:ce:81:96:9d:92:9e:96:97:ac:9a:9d:87:96:81:83:81:96:87:96:81:8f:90:92:9e:83:92:9a:94:9d:ac:9a:97:ce:90:92:9e:83:92:9a:94:9d:de:c0:c3:c6:c5:cb:c3:cb:c2:96:c4:8f:95:9a:9f:96:ac:83:92:87:9b:ce:b0:c9:dc:a3:81:9c:94:81:92:9e:b7:92:87:92:dc:bb:86:9d:87:81:96:80:80:bf:92:91:dc:dd:86:83:97:92:87:96:de:c0:c3:c6:c5:cb:c3:cb:c2:96:c4:dd:83:8a"
    CODEC_08679536 = "hex_colon|single_byte_xor|f3"

    def load_08679536():
        return bytes.fromhex(MATERIAL_08679536.replace(":", " "))

    def decode_08679536(item1):
        return bytes(value ^ 243 for value in item1)

    def recover_08679536():
        item4 = ":".join(("north", "south"))
        item2 = decode_08679536(load_08679536())
        item3 = item2.decode("ascii", "strict")
        return item3

    def inspect_08679536():
        return recover_08679536()

    class Surface_surface_08679536:
        @staticmethod
        def recover():
            return ("class_staticmethod", "string_table", "hash_based_pyc_38", "renamed_interpreter")

    def surface_08679536():
        return Surface_surface_08679536.recover()

    def obfuscation_08679536():
        table = ("strin", "g_table")
        return "".join(table)

    def plan_08679536():
        fields = dict(item.split("=", 1) for item in inspect_08679536().split("|"))
        analysis_surface = surface_08679536()
        obfuscation_surface = obfuscation_08679536()
        operation_plan = ("path_write_bytes", "decode", fields["file_path"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_08679536())
