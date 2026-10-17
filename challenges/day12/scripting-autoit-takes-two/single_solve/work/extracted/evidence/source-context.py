#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_77353209 = "CwlSDglaCwhSCEceGQUCVw4DNR4ZBQIWCwlSDglaCwhSCEcEDQMLGgcLCVcOAzUEDQMLGgcLCRYPEg81BAUCHhMaNR4JDxgDDlcEAwsCCTUZHQUOBAMdFg8JGB8FGTUdCxhXGA8DGBgLCRYTBgQFNQcYBQwZBAsYHlcEBQMeCwkZHwwIBRYZBAUDHgkEHww1BAMLBhpXEgseBBMZFltXHgQfBQk1Dw0LHhkWDwkLGhkPBwsENQ8ZGAsaDRgLVxgPHhoLDgsWBAUDHgsYHw0DDAQFCTUEGB8eDxhGBAUDHgsYHw0DDAQFCTUPDgUJDw5XGRoPHhkWWFcc"
    CODEC_77353209 = "urlsafe_base64|reverse_then_xor|6a"

    def load_77353209():
        return base64.urlsafe_b64decode(MATERIAL_77353209)

    def decode_77353209(stored_bytes):
        return bytes(value ^ 106 for value in reversed(stored_bytes))

    def recover_77353209():
        harmless_value = 19 * 7 - 133
        for _pass in range(1):
            recovered_bytes = decode_77353209(load_77353209())
        configuration_text = recovered_bytes.decode("ascii", "strict")
        return configuration_text

    def inspect_77353209():
        view = memoryview(recover_77353209().encode("ascii"))
        return bytes(view).decode("ascii")

    def surface_77353209():
        return ("plain_functions", "transform_only", "raw_source", "direct_python_exe")

    def obfuscation_77353209():
        return "transform_only"

    def plan_77353209():
        fields = dict(item.split("=", 1) for item in inspect_77353209().split("|"))
        analysis_surface = surface_77353209()
        obfuscation_surface = obfuscation_77353209()
        operation_plan = ("report", fields.get("host_id", ""))
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_77353209())
