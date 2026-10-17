#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_bac634dc = "i1JHkYiJeoWIUnl6eIR5enR4hIN7fnyKh3aJfoSDQYGEeHaJenR+g4l6h4WHeol6h0F5foiFdol4fXSDeo2JdIiJdnx6kXZ5doWJeodShY6JfYSDdImEdIyIeId+hYmRiIl2fHp0eISKg4lSSJGIjoOJdo1SeIF2iIh0iIl2iX54gnqJfYR5kYR3e4qIeHaJfoSDUoJ2h4h9doF0eoOLeoGEhXp0hYF2g5F4doeHfnqHUnqCd3p5eXZ3gXp0hY6JfYSDdIeKg4l+gnqRjH6DeYSMiHR4fXZ+g1KHeoN2gnp5dH6DiXqHhYd6iXqHkXh2goV2fnyDdH55Unh2goV2fnyDQkhNd3d5TkpMeE6Re36BenSFdol9UlhPRGWHhHyHdoJZdol2RF2Kg4mHeoiIYXZ3REOKhXl2iXpCSE13d3lOSkx4TkOFjpGDeo2JdIiJdnx6UoWOdoeChIdChY5+g4iJdoGBeodCh3p4hIt6h3p5Q4WO"
    CODEC_bac634dc = "base64_literal|add_modulo_256|15"

    def load_bac634dc():
        return base64.b64decode(MATERIAL_bac634dc)

    def decode_bac634dc(v_a19c):
        return bytes((value - 21) % 256 for value in v_a19c)

    def recover_bac634dc():
        v_d41a = (3, 5, 8, 13)[1:3]
        for _pass in range(1):
            v_b27e = decode_bac634dc(load_bac634dc())
        v_c304 = v_b27e.decode("ascii", "strict")
        return v_c304

    def inspect_bac634dc():
        view = memoryview(recover_bac634dc().encode("ascii"))
        return bytes(view).decode("ascii")

    class Surface_surface_bac634dc:
        @staticmethod
        def recover():
            return ("class_staticmethod", "marshal_envelope_plan", "embeddable_python_runtime", "renamed_interpreter")

    def surface_bac634dc():
        return Surface_surface_bac634dc.recover()

    def obfuscation_bac634dc():
        marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
        return marshal_plan["label"]

    def plan_bac634dc():
        fields = dict(item.split("=", 1) for item in inspect_bac634dc().split("|"))
        analysis_surface = surface_bac634dc()
        obfuscation_surface = obfuscation_bac634dc()
        operation_plan = ("python_to_wscript", fields["file_path"], fields["next_stage"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_bac634dc())
