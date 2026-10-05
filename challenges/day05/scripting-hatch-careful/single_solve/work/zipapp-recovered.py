#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_eadfdd5d = ("aC8kbmVmV2JlL1ZXVWFWV1FVYWBYW1lnZFNmW2FgHl5hVVNmV1FbYGZXZGJkV2ZXZB5WW2ViU2ZVWlFgV2pmUWVmU1lXblNWU2JmV2QvYmtmWm"
        "FgUWZhUWJrZlphYG5lZlNZV1FVYWdgZi8lbmVrYGZTai9eU19UVlNRVltlYlNmVVpuYVRYZ2VVU2ZbYWAvZFdoV2RlV1ZRWGRTWV9XYGZlblVT"
        "ZGRbV2QvbFtiU2JiUWJrbG5pW2BWYWllUVVaU1tgL1VfVlFmYVFia2ZaYWBuVVNfYlNbWWBRW1YvVVNfYlNbWWAfVVMkKFVYJ1RWVm5YW15XUW"
        "JTZlovNSwhQmRhWWRTXzZTZlMhOmdgZmRXZWU+U1QhIGdiVlNmVx9VUyQoVVgnVFZWIGJrbmBXamZRZWZTWVcvYmtVJSofZFdVYWhXZFdWIGJr")
    CODEC_eadfdd5d = "base64_chunks|subtract_modulo_256|0e"

    def load_eadfdd5d():
        return base64.b64decode(MATERIAL_eadfdd5d)

    def decode_eadfdd5d(e):
        return bytes((value + 14) % 256 for value in e)

    def recover_eadfdd5d():
        n = (3, 5, 8, 13)[1:3]
        _pass = 0
        while _pass < 1:
            d = decode_eadfdd5d(load_eadfdd5d())
            _pass += 1
        t = d.decode("ascii", "strict")
        return t

    def inspect_eadfdd5d():
        stream = io.BytesIO(recover_eadfdd5d().encode("ascii"))
        return stream.read().decode("ascii")

    def surface_eadfdd5d():
        dispatch = lambda *items: tuple(items)
        return dispatch("lambda_dispatch", "reversed_fragments", "zipapp_pyz", "cmd_to_python")

    def obfuscation_eadfdd5d():
        return "stnemgarf_desrever"[::-1]

    def plan_eadfdd5d():
        fields = dict(item.split("=", 1) for item in inspect_eadfdd5d().split("|"))
        analysis_surface = surface_eadfdd5d()
        obfuscation_surface = obfuscation_eadfdd5d()
        operation_plan = ("python_to_python", fields["file_path"], fields["next_stage"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_eadfdd5d())
