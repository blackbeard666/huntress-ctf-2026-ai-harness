#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_41064131 = ("ZSwha2JjVF9iLFteUlBjVE5bXlJQWxtTWGJfUGNSV05fYV5SVGJia1BTUF9jVGEsYVRdUFxUU05YXWNUYV9hVGNUYU5QYVZla"
        "2JjUFZUTlJeZF1jLCBrYmhdY1BnLFJbXmJkYVROVVBSY15haGteUVVkYlJQY1heXSxSV2FOWV5YXWtSUGFhWFRhLFdQYldOUV"
        "BiVFNOX2hSTlJkYWFUXWNrZlhdU15mYk5SV1BYXSxfaGNXXl1mTldYU1NUXU5SXl1iXltUa1JQXF9QWFZdTlhTLFJQXF9QWFZ"
        "dHChUICFQIFJUJFRrVVhbVE5fUGNXLDIpHj9hXlZhUFwzUGNQHjdkXWNhVGJiO1BRHh1kX1NQY1QcKFQgIVAgUlQkVB1faA==")
    CODEC_41064131 = "base64_chunks|subtract_modulo_256|11"

    def load_41064131():
        return base64.b64decode(MATERIAL_41064131)

    def decode_41064131(stored_bytes):
        return bytes((value + 17) % 256 for value in stored_bytes)

    def recover_41064131():
        harmless_value = "left" if 2 > 1 else "right"
        _pass = 0
        while _pass < 1:
            recovered_bytes = decode_41064131(load_41064131())
            _pass += 1
        configuration_text = recovered_bytes.decode("ascii", "strict")
        return configuration_text

    def inspect_41064131():
        view = memoryview(recover_41064131().encode("ascii"))
        return bytes(view).decode("ascii")

    def surface_41064131():
        values = ("closure_factory", "chr_join", "hash_based_pyc_current", "pythonw_hidden_console")
        def inner():
            return values
        return inner()

    def obfuscation_41064131():
        return "".join(chr(value) for value in (99, 104, 114, 95, 106, 111, 105, 110))

    def plan_41064131():
        fields = dict(item.split("=", 1) for item in inspect_41064131().split("|"))
        analysis_surface = surface_41064131()
        obfuscation_surface = obfuscation_41064131()
        operation_plan = ("renamed_interpreter_argv", ("python3", fields["file_path"]))
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_41064131())
