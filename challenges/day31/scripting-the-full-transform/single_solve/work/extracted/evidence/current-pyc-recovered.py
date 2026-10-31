#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_8426a26e = [145, 136, 70, 123, 123, 75, 78, 122, 124, 72, 77, 121, 79, 69, 125, 140, 121, 124, 136, 141, 70, 71, 122, 121, 100, 139, 139, 125, 138, 140, 134, 141, 96, 71, 121, 140, 121, 92, 133, 121, 138, 127, 135, 138, 104, 71, 82, 91, 85, 128, 140, 121, 136, 119, 125, 132, 129, 126, 148, 123, 123, 75, 78, 122, 124, 72, 77, 121, 79, 69, 134, 127, 129, 121, 136, 133, 121, 123, 85, 124, 129, 119, 134, 127, 129, 121, 136, 133, 121, 123, 148, 125, 132, 135, 139, 134, 135, 123, 119, 134, 125, 124, 124, 129, 128, 119, 143, 134, 135, 128, 140, 145, 136, 85, 134, 129, 121, 128, 123, 119, 139, 143, 135, 124, 134, 129, 143, 148, 140, 134, 125, 138, 138, 141, 123, 119, 123, 145, 136, 119, 124, 125, 139, 121, 122, 119, 128, 139, 121, 128, 85, 138, 125, 129, 138, 138, 121, 123, 148, 134, 129, 135, 130, 119, 138, 128, 123, 85, 134, 135, 129, 140, 121, 123, 139, 141, 126, 122, 135, 148, 145, 138, 135, 140, 123, 121, 126, 119, 125, 138, 141, 139, 135, 132, 123, 85, 144, 121, 140, 134, 145, 139, 148, 73, 85, 140, 134, 141, 135, 123, 119, 125, 127, 121, 140, 139, 148, 142, 127, 138, 121, 119, 143, 134, 135, 128, 140, 145, 136, 85, 138, 125, 140, 136, 121, 124, 121, 148, 139, 139, 125, 123, 135, 138, 136, 119, 128, 123, 140, 121, 136, 139, 129, 124, 68, 132, 121, 123, 135, 132, 119, 125, 140, 121, 123, 135, 132, 85, 139, 136, 125, 140, 139, 148, 74, 85, 142]
    CODEC_8426a26e = "reversed_integer_list|add_modulo_256|18"

    def load_8426a26e():
        return bytes(reversed(MATERIAL_8426a26e))

    def decode_8426a26e(stored_bytes):
        return bytes((value - 24) % 256 for value in stored_bytes)

    def recover_8426a26e():
        harmless_value = None
        _pass = 0
        while _pass < 1:
            recovered_bytes = decode_8426a26e(load_8426a26e())
            _pass += 1
        configuration_text = recovered_bytes.decode("ascii", "strict")
        return configuration_text

    def inspect_8426a26e():
        view = memoryview(recover_8426a26e().encode("ascii"))
        return bytes(view).decode("ascii")

    def surface_8426a26e():
        values = ("closure_factory", "chr_join", "hash_based_pyc_current", "pythonw_hidden_console")
        def inner():
            return values
        return inner()

    def obfuscation_8426a26e():
        return "".join(chr(value) for value in (99, 104, 114, 95, 106, 111, 105, 110))

    def plan_8426a26e():
        fields = dict(item.split("=", 1) for item in inspect_8426a26e().split("|"))
        analysis_surface = surface_8426a26e()
        obfuscation_surface = obfuscation_8426a26e()
        operation_plan = ("pythonw_argv", ("python3", fields["file_path"]))
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_8426a26e())
