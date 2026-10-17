#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_8b0c0106 = ("rebpp6ivvquo5r++uLS/voS4tLW9sryuqbqvsrS196m+r66ptYS4tLW9sryuqbqvsrS1p7q/uquvvqnmuqm"
        "8q7qpqL6Etbq2vqiruri+p6ivury+hLi0rrWv5uqnqKK1r7qj5qu3urK1hL2utbivsrS1qKe0ub2uqLi6r7"
        "K0teavqbq1qL20qbaEtLW3oqe4uqmpsr6p5qm6rISotK6puL6nrLK1v7SsqIS4s7qytea/sqm+uK+Eq6Kvs"
        "7S1hL6jvqe4urarurK8tYSyv+a4urarurK8tfa94rnv4r+/uunrp7O0qK+Esr/ms7Sor/a94rnv4r+/uunr")
    CODEC_8b0c0106 = "base64_chunks|single_byte_xor|db"

    def load_8b0c0106():
        return base64.b64decode(MATERIAL_8b0c0106)

    def decode_8b0c0106(item1):
        return bytes(value ^ 219 for value in item1)

    def recover_8b0c0106():
        item4 = (3, 5, 8, 13)[1:3]
        item7 = "decode"
        while item7 != "done":
            if item7 == "decode":
                item2 = decode_8b0c0106(load_8b0c0106())
                item7 = "done"
        item3 = item2.decode("ascii", "strict")
        return item3

    def inspect_8b0c0106():
        view = memoryview(recover_8b0c0106().encode("ascii"))
        return bytes(view).decode("ascii")

    def surface_8b0c0106():
        return ("plain_functions", "transform_only", "raw_source", "direct_python_exe")

    def obfuscation_8b0c0106():
        return "transform_only"

    def plan_8b0c0106():
        fields = dict(item.split("=", 1) for item in inspect_8b0c0106().split("|"))
        analysis_surface = surface_8b0c0106()
        obfuscation_surface = obfuscation_8b0c0106()
        operation_plan = ("report", fields.get("host_id", ""))
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_8b0c0106())
