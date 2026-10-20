#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_b20b117c = "kllOmI-QgYyPWYCBf4uAgXt_i4qChYORjn2QhYuKSIiLf32QgXuFipCBjoyOgZCBjkiAhY-MfZB_hHuKgZSQe4-QfYOBmH2AfYyQgY5ZjJWQhIuKe5CLe4yLk4GOj4SBiIiYj5B9g4F7f4uRipBZT5iPlYqQfZRZf4h9j497j5B9kIV_iYGQhIuAmIt-gpGPf32QhYuKWYl9jo-EfYh7gYqSgYiLjIF7jIh9iph_fY6OhYGOWYGJfoGAgH1-iIF7jJWQhIuKe46RipCFiYGYk4WKgIuTj3t_hH2FilmOgYp9iYGAe4WKkIGOjI6BkIGOmH99iYx9hYOKe4WAWX99iYx9hYOKSYJ-gFRVUFFTfYKYgoWIgXuMfZCEWV9WS2yOi4OOfYlgfZB9S2SRipCOgY-PaH1-S0qRjIB9kIFJgn6AVFVQUVN9gkqMlZiKgZSQe4-QfYOBWYyVfY6Ji45JjJWFio-QfYiIgY5JjoF_i5KBjoGASoyV"
    CODEC_b20b117c = "urlsafe_base64|add_modulo_256|1c"

    def load_b20b117c():
        return base64.urlsafe_b64decode(MATERIAL_b20b117c)

    def decode_b20b117c(v_a19c):
        return bytes((value - 28) % 256 for value in v_a19c)

    def recover_b20b117c():
        v_d41a = "left" if 2 > 1 else "right"
        v_b27e = decode_b20b117c(load_b20b117c())
        v_c304 = v_b27e.decode("ascii", "strict")
        return v_c304

    def inspect_b20b117c():
        view = memoryview(recover_b20b117c().encode("ascii"))
        return bytes(view).decode("ascii")

    class Surface_surface_b20b117c:
        @staticmethod
        def recover():
            return ("class_staticmethod", "marshal_envelope_plan", "embeddable_python_runtime", "renamed_interpreter")

    def surface_b20b117c():
        return Surface_surface_b20b117c.recover()

    def obfuscation_b20b117c():
        marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
        return marshal_plan["label"]

    def plan_b20b117c():
        fields = dict(item.split("=", 1) for item in inspect_b20b117c().split("|"))
        analysis_surface = surface_b20b117c()
        obfuscation_surface = obfuscation_b20b117c()
        operation_plan = ("python_to_powershell", fields["file_path"], fields["next_stage"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_b20b117c())
