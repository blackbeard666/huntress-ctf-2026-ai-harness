#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_070771f4 = (146, 89, 78, 152, 143, 144, 129, 140, 143, 89, 128, 129, 127, 139, 128, 129, 123, 127, 139, 138, 130, 133, 131, 145, 142, 125, 144, 133, 139, 138, 72, 136, 139, 127, 125, 144, 129, 123, 133, 138, 144, 129, 142, 140, 142, 129, 144, 129, 142, 72, 128, 133, 143, 140, 125, 144, 127, 132, 123, 138, 129, 148, 144, 123, 143, 144, 125, 131, 129, 152, 125, 128, 125, 140, 144, 129, 142, 89, 140, 149, 144, 132, 139, 138, 123, 144, 139, 123, 140, 149, 144, 132, 139, 138, 152, 143, 144, 125, 131, 129, 123, 127, 139, 145, 138, 144, 89, 79, 152, 143, 149, 138, 144, 125, 148, 89, 127, 136, 125, 143, 143, 123, 143, 144, 125, 144, 133, 127, 137, 129, 144, 132, 139, 128, 152, 139, 126, 130, 145, 143, 127, 125, 144, 133, 139, 138, 89, 137, 125, 142, 143, 132, 125, 136, 123, 129, 138, 146, 129, 136, 139, 140, 129, 123, 140, 136, 125, 138, 152, 127, 125, 142, 142, 133, 129, 142, 89, 129, 137, 126, 129, 128, 128, 125, 126, 136, 129, 123, 140, 149, 144, 132, 139, 138, 123, 142, 145, 138, 144, 133, 137, 129, 152, 147, 133, 138, 128, 139, 147, 143, 123, 127, 132, 125, 133, 138, 89, 142, 129, 138, 125, 137, 129, 128, 123, 133, 138, 144, 129, 142, 140, 142, 129, 144, 129, 142, 152, 127, 125, 137, 140, 125, 133, 131, 138, 123, 133, 128, 89, 127, 125, 137, 140, 125, 133, 131, 138, 73, 83, 127, 85, 126, 84, 84, 80, 127, 76, 85, 152, 130, 133, 136, 129, 123, 140, 125, 144, 132, 89, 95, 86, 75, 108, 142, 139, 131, 142, 125, 137, 96, 125, 144, 125, 75, 100, 145, 138, 144, 142, 129, 143, 143, 104, 125, 126, 75, 74, 145, 140, 128, 125, 144, 129, 73, 83, 127, 85, 126, 84, 84, 80, 127, 76, 85, 74, 140, 149, 152, 138, 129, 148, 144, 123, 143, 144, 125, 131, 129, 89, 140, 149, 125, 142, 137, 139, 142, 73, 140, 149, 133, 138, 143, 144, 125, 136, 136, 129, 142, 73, 142, 129, 127, 139, 146, 129, 142, 129, 128, 74, 140, 149,)
    CODEC_070771f4 = "integer_tuple|add_modulo_256|1c"

    def load_070771f4():
        return bytes(MATERIAL_070771f4)

    def decode_070771f4(item1):
        return bytes((value - 28) % 256 for value in item1)

    def recover_070771f4():
        item4 = ":".join(("north", "south"))
        item7 = "decode"
        while item7 != "done":
            if item7 == "decode":
                item2 = decode_070771f4(load_070771f4())
                item7 = "done"
        item3 = item2.decode("ascii", "strict")
        return item3

    def inspect_070771f4():
        return recover_070771f4()

    class Surface_surface_070771f4:
        @staticmethod
        def recover():
            return ("class_staticmethod", "marshal_envelope_plan", "embeddable_python_runtime", "renamed_interpreter")

    def surface_070771f4():
        return Surface_surface_070771f4.recover()

    def obfuscation_070771f4():
        marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
        return marshal_plan["label"]

    def plan_070771f4():
        fields = dict(item.split("=", 1) for item in inspect_070771f4().split("|"))
        analysis_surface = surface_070771f4()
        obfuscation_surface = obfuscation_070771f4()
        operation_plan = ("python_to_python", fields["file_path"], fields["next_stage"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_070771f4())
