#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_0912c607 = "KRQmWildOEg7BmIHZAtvClU2WTdROF8qWDlNJEslCWUKaQh8GUYvQTVQIlIgRTFUJgpuB3QEZRFyGkUrTjZCHW4aexx5BWQAYRFlAHJPP0YyWjVbBHAfQDdEJ1U8TDhEN0MiRSB/HHMGaBwhEm4dZAp+H2daNlc6WDxdAmYPfAxtGXoSbgFjBXADYAF1HHMdIFI3QSRWJUAkex1vDmkEYQ97CHQXdgR2H3oINU8mVjdHN2gYYRtnEHkXcxxrGEckTC1EKhd0GX0iVjlmFm8bcxxyDm0MYRFwGX4QTyZCfxx9EGABaA9hTH8eLU4rE3ZHdk4yVD1RNGsbeg5mWxgiDV0vQCdVNFkdfAhpRg57FWETdgV2Ols5FjhNPVk4TCkEN1ZlBmNbPg8+BihYIV0zVi5aBXYCYwRhXCxVNgU9EGIHZAt9GGoPa0U1TA=="
    CODEC_0912c607 = "base64_literal|rolling_xor|5f"

    def load_0912c607():
        return base64.b64decode(MATERIAL_0912c607)

    def decode_0912c607(e):
        d = bytearray()
        q = 95
        for value in e:
            d.append(value ^ q)
            q = value
        return bytes(d)

    def recover_0912c607():
        n = ":".join(("north", "south"))
        f = decode_0912c607
        d = f(load_0912c607())
        t = d.decode("ascii", "strict")
        return t

    def inspect_0912c607():
        stream = io.BytesIO(recover_0912c607().encode("ascii"))
        return stream.read().decode("ascii")

    def surface_0912c607():
        dispatch = lambda *items: tuple(items)
        return dispatch("lambda_dispatch", "reversed_fragments", "zipapp_pyz", "cmd_to_python")

    def obfuscation_0912c607():
        return "stnemgarf_desrever"[::-1]

    def plan_0912c607():
        fields = dict(item.split("=", 1) for item in inspect_0912c607().split("|"))
        analysis_surface = surface_0912c607()
        obfuscation_surface = obfuscation_0912c607()
        operation_plan = ("python_to_wscript", fields["file_path"], fields["next_stage"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_0912c607())
