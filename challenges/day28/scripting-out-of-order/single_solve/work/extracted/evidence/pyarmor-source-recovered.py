#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_fffd6cca = "955c519b9293848f925c808290948891847e91848c8e93844b8388928f809382877e8c848c8e91989b8083808f9384915c928e828a84937e8f8b808d7e8c848c8e91989b92938086847e828e948d935c509b92988d9380975c849782848f93888e8d7e84978f91849292888e8d9b8e81859492828093888e8d5c8c80919287808b7e848d95848b8e8f847e8f8b808d9b828091918884915c8f9880918c8e917e8e8185949282809384839b96888d838e96927e828780888d5c96928291888f937e938e7e8f9893878e8d9b82808c8f8088868d7e88835c82808c8f8088868d4c858280805753855850519b94918b5c8793938f92594e4e858280805753855850514d8497808c8f8b844d888d95808b88834e838253814f8285834d8f989b949284917e8086848d935c67948d93918492926f9893878e8d4e85828080575385585051"
    CODEC_fffd6cca = "hex_literal|add_modulo_256|1f"

    def load_fffd6cca():
        return bytes.fromhex(MATERIAL_fffd6cca)

    def decode_fffd6cca(stored_bytes):
        return bytes((value - 31) % 256 for value in stored_bytes)

    def recover_fffd6cca():
        harmless_value = "left" if 2 > 1 else "right"
        for _pass in range(1):
            recovered_bytes = decode_fffd6cca(load_fffd6cca())
        configuration_text = recovered_bytes.decode("ascii", "strict")
        return configuration_text

    def inspect_fffd6cca():
        return recover_fffd6cca()

    def surface_fffd6cca():
        try:
            raise LookupError("surface")
        except LookupError:
            return ("exception_expression", "marshal_envelope_plan", "pyarmor_obfuscated", "wscript_to_python")

    def obfuscation_fffd6cca():
        marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
        return marshal_plan["label"]

    def plan_fffd6cca():
        fields = dict(item.split("=", 1) for item in inspect_fffd6cca().split("|"))
        analysis_surface = surface_fffd6cca()
        obfuscation_surface = obfuscation_fffd6cca()
        operation_plan = ("socket_plan_memory", fields["url"], "memory-handoff")
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_fffd6cca())
