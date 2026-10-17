#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_becdfe29 = "7e453a847b7c6d787b456c6d6b776c6d676d756a6d6c6c6d6c347f7a717c6d676e71746d84696c69787c6d7a457c6d75786e71746d677a6d7874696b6d847b7c696f6d676b777d767c4539847b81767c6980456b74697b7b677b7c697c716b756d7c70776c84776a6e7d7b6b697c717776457b7c7a71766f677c696a746d846b697a7a716d7a4570697b70676a697b6d6c6778816b673b40847f71766c777f7b676b70697176457a6d7669756d6c6771767c6d7a787a6d7c6d7a846b69757869716f7667716c456b69757869716f76353940393a396b406d6a6d846e71746d6778697c70454b4237587a776f7a69754c697c6937507d767c7a6d7b7b54696a37367d786c697c6d353940393a396b406d6a6d367881"
    CODEC_becdfe29 = "hex_literal|add_modulo_256|08"

    def load_becdfe29():
        return bytes.fromhex(MATERIAL_becdfe29)

    def decode_becdfe29(stored_bytes):
        return bytes((value - 8) % 256 for value in stored_bytes)

    def recover_becdfe29():
        harmless_value = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
        decoder_function = decode_becdfe29
        recovered_bytes = decoder_function(load_becdfe29())
        configuration_text = recovered_bytes.decode("ascii", "strict")
        return configuration_text

    def inspect_becdfe29():
        view = memoryview(recover_becdfe29().encode("ascii"))
        return bytes(view).decode("ascii")

    class Surface_surface_becdfe29:
        @staticmethod
        def recover():
            return ("class_staticmethod", "string_table", "hash_based_pyc_38", "renamed_interpreter")

    def surface_becdfe29():
        return Surface_surface_becdfe29.recover()

    def obfuscation_becdfe29():
        table = ("strin", "g_table")
        return "".join(table)

    def plan_becdfe29():
        fields = dict(item.split("=", 1) for item in inspect_becdfe29().split("|"))
        analysis_surface = surface_becdfe29()
        obfuscation_surface = obfuscation_becdfe29()
        operation_plan = ("tempfile_replace", "decode", fields["file_path"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_becdfe29())
