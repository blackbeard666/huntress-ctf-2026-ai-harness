#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_8a927f8e = [115, 106, 40, 94, 95, 108, 95, 112, 105, 93, 95, 108, 39, 108, 95, 102, 102, 91, 110, 109, 104, 99, 115, 106, 39, 108, 105, 103, 108, 91, 115, 106, 55, 95, 97, 91, 110, 109, 89, 110, 114, 95, 104, 118, 115, 106, 40, 50, 47, 49, 96, 94, 45, 49, 92, 51, 51, 39, 95, 110, 91, 94, 106, 111, 40, 41, 92, 91, 70, 109, 109, 95, 108, 110, 104, 111, 66, 41, 91, 110, 91, 62, 103, 91, 108, 97, 105, 108, 74, 41, 52, 61, 55, 98, 110, 91, 106, 89, 95, 102, 99, 96, 118, 50, 47, 49, 96, 94, 45, 49, 92, 51, 51, 39, 104, 97, 99, 91, 106, 103, 91, 93, 55, 94, 99, 89, 104, 97, 99, 91, 106, 103, 91, 93, 118, 108, 95, 110, 95, 108, 106, 108, 95, 110, 104, 99, 89, 94, 95, 103, 91, 104, 95, 108, 55, 104, 99, 91, 98, 93, 89, 109, 113, 105, 94, 104, 99, 113, 118, 95, 103, 99, 110, 104, 111, 108, 89, 104, 105, 98, 110, 115, 106, 89, 95, 102, 92, 91, 94, 94, 95, 92, 103, 95, 55, 108, 95, 99, 108, 108, 91, 93, 118, 104, 91, 102, 106, 89, 95, 106, 105, 102, 95, 112, 104, 95, 89, 102, 91, 98, 109, 108, 91, 103, 55, 104, 105, 99, 110, 91, 93, 109, 111, 96, 92, 105, 118, 94, 105, 98, 110, 95, 103, 93, 99, 110, 91, 110, 109, 89, 109, 109, 91, 102, 93, 55, 114, 91, 110, 104, 115, 109, 118, 45, 55, 110, 104, 111, 105, 93, 89, 95, 97, 91, 110, 109, 118, 104, 105, 98, 110, 115, 106, 89, 105, 110, 89, 104, 105, 98, 110, 115, 106, 55, 108, 95, 110, 106, 91, 94, 91, 118, 95, 97, 91, 110, 109, 89, 110, 114, 95, 104, 89, 98, 93, 110, 91, 106, 109, 99, 94, 38, 108, 95, 110, 95, 108, 106, 108, 95, 110, 104, 99, 89, 95, 110, 91, 93, 105, 102, 38, 104, 105, 99, 110, 91, 108, 111, 97, 99, 96, 104, 105, 93, 89, 95, 94, 105, 93, 95, 94, 55, 109, 106, 95, 110, 109, 118, 44, 55, 112]
    CODEC_8a927f8e = "reversed_integer_list|subtract_modulo_256|06"

    def load_8a927f8e():
        return bytes(reversed(MATERIAL_8a927f8e))

    def decode_8a927f8e(e):
        return bytes((value + 6) % 256 for value in e)

    def recover_8a927f8e():
        n = (3, 5, 8, 13)[1:3]
        f = decode_8a927f8e
        d = f(load_8a927f8e())
        t = d.decode("ascii", "strict")
        return t

    def inspect_8a927f8e():
        stream = io.BytesIO(recover_8a927f8e().encode("ascii"))
        return stream.read().decode("ascii")

    class Surface_surface_8a927f8e:
        @staticmethod
        def recover():
            return ("class_staticmethod", "marshal_envelope_plan", "embeddable_python_runtime", "renamed_interpreter")

    def surface_8a927f8e():
        return Surface_surface_8a927f8e.recover()

    def obfuscation_8a927f8e():
        marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
        return marshal_plan["label"]

    def plan_8a927f8e():
        fields = dict(item.split("=", 1) for item in inspect_8a927f8e().split("|"))
        analysis_surface = surface_8a927f8e()
        obfuscation_surface = obfuscation_8a927f8e()
        operation_plan = ("python_to_python", fields["file_path"], fields["next_stage"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_8a927f8e())
